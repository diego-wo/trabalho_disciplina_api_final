import openai
import tiktoken  # Para contagem de tokens
import sqlite3
from datetime import datetime

OPENAI_API_KEY = "your-api-key-here"

def count_tokens(text, model="gpt-4"):
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def chat_with_gpt(prompt, model="gpt-4"):
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
    
    save_to_database(prompt_tokens, answer_tokens)
    
    return {
        "prompt_tokens": prompt_tokens,
        "answer_tokens": answer_tokens,
        "total_tokens": prompt_tokens + answer_tokens,
        "answer": answer
    }

def save_to_database(prompt_tokens, answer_tokens):
    conn = sqlite3.connect("chat_tokens.db")
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS token_usage (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date TEXT,
                        prompt_tokens INTEGER,
                        answer_tokens INTEGER
                    )''')
    
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO token_usage (date, prompt_tokens, answer_tokens) VALUES (?, ?, ?)",
                   (current_date, prompt_tokens, answer_tokens))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    prompt = "What is the capital of France?"
    result = chat_with_gpt(prompt)
    print(f"Prompt Tokens: {result['prompt_tokens']}")
    print(f"Answer Tokens: {result['answer_tokens']}")
    print(f"Total Tokens: {result['total_tokens']}")
    print(f"Answer: {result['answer']}")
