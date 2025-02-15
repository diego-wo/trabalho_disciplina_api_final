import os
import logging
from fastapi import HTTPException
from groq import Groq
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Lê o token de API a partir das variáveis de ambiente (fallback para "123456" para demonstração)
API_TOKEN = os.getenv("API_TOKEN", "123456")

def obter_logger_e_configuracao():
    logging.basicConfig(
        level=logging.INFO, format="[%(levelname)s] %(asctime)s - %(message)s"
    )
    logger = logging.getLogger("fastapi")
    return logger

def verify_token(x_api_token: str):
    if x_api_token != API_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Token inválido"
        )

def executar_prompt(prompt: str):
    resultados = {}
    logger = obter_logger_e_configuracao()
    
    # Chamada via Groq, se a chave estiver configurada
    if os.getenv("GROQ_API_KEY"):
        try:
            client_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
            response_groq = client_groq.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=os.getenv("GROQ_MODEL", "mixtral-8x7b-32768"),
            )
            # Obtém o conteúdo e a contagem de tokens (se disponível)
            resultados["GROQ"] = {
                "historia": response_groq.choices[0].message.content,
                "tokens": response_groq.usage.__dict__  # Dados de uso/token
            }
        except Exception as e:
            logger.error(f"Erro na chamada Groq: {e}")
    
    # Chamada via OpenAI, se a chave estiver configurada
    if os.getenv("OPENAI_API_KEY"):
        try:
            client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            response_openai = client_openai.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            )
            # Removendo chaves indesejadas para evitar erros
            response_openai.usage.__dict__.pop("completion_tokens_details", None)
            response_openai.usage.__dict__.pop("prompt_tokens_details", None)
            resultados["OPENAI"] = {
                "historia": response_openai.choices[0].message.content,
                "tokens": response_openai.usage.__dict__
            }
        except Exception as e:
            logger.error(f"Erro na chamada OpenAI: {e}")
    
    return resultados

