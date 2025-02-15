import openai
import tiktoken  # Para contagem de tokens
import sqlite3
from datetime import datetime
from typing import Dict, Any

# Defina a sua chave de API (lembre-se de não expor informações sensíveis em produção)
OPENAI_API_KEY: str = "your-api-key-here"


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """
    Conta o número de tokens de um texto utilizando a codificação do modelo especificado.
    
    Args:
        text: Texto a ser tokenizado.
        model: Modelo de referência (default "gpt-4").
    
    Returns:
        Número de tokens contados.
    """
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def save_to_database(prompt_tokens: int, answer_tokens: int) -> None:
    """
    Salva as informações de uso de tokens em um banco de dados SQLite.
    
    Args:
        prompt_tokens: Número de tokens do prompt.
        answer_tokens: Número de tokens da resposta.
    """
    query_create = """
        CREATE TABLE IF NOT EXISTS token_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            prompt_tokens INTEGER,
            answer_tokens INTEGER
        )
    """
    query_insert = """
        INSERT INTO token_usage (date, prompt_tokens, answer_tokens) VALUES (?, ?, ?)
    """
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Uso de context manager para garantir o fechamento da conexão
    with sqlite3.connect("chat_tokens.db") as conn:
        cursor = conn.cursor()
        cursor.execute(query_create)
        cursor.execute(query_insert, (current_date, prompt_tokens, answer_tokens))
        conn.commit()


def chat_with_gpt(prompt: str, model: str = "gpt-4") -> Dict[str, Any]:
    """
    Envia um prompt para a API da OpenAI e retorna a resposta juntamente com a contagem de tokens.
    
    Args:
        prompt: O prompt a ser enviado para o modelo.
        model: O modelo a ser utilizado (default "gpt-4").
    
    Returns:
        Um dicionário com a resposta e a contagem de tokens do prompt e da resposta.
    """
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    response = client.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    answer = response["choices"][0]["message"]["content"]
    prompt_tokens = count_tokens(prompt, model)
    answer_tokens = count_tokens(answer, model)
    total_tokens = prompt_tokens + answer_tokens
    
    # Salva os dados de tokens no banco de dados
    save_to_database(prompt_tokens, answer_tokens)
    
    return {
        "prompt_tokens": prompt_tokens,
        "answer_tokens": answer_tokens,
        "total_tokens": total_tokens,
        "answer": answer
    }


if __name__ == "__main__":
    sample_prompt = "What is the capital of France?"
    result = chat_with_gpt(sample_prompt)
    print(f"Prompt Tokens: {result['prompt_tokens']}")
    print(f"Answer Tokens: {result['answer_tokens']}")
    print(f"Total Tokens: {result['total_tokens']}")
    print(f"Answer: {result['answer']}")
