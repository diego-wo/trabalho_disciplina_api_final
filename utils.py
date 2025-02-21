import os
import logging
from fastapi import HTTPException
from groq import Groq
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Configuração do logger global
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s - %(message)s"
)
logger = logging.getLogger("fastapi")

# Lê o token de API a partir das variáveis de ambiente (fallback para demonstração)
API_TOKEN: str = os.getenv("API_TOKEN", "123456")

def obter_logger_e_configuracao() -> logging.Logger:
    """
    Retorna o logger configurado globalmente.
    """
    return logger

def verify_token(x_api_token: str) -> None:
    """
    Verifica se o token fornecido é válido.
    
    Args:
        x_api_token (str): Token enviado na requisição.
    
    Raises:
        HTTPException: Se o token for inválido.
    """
    if x_api_token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Token inválido")

def executar_prompt(prompt: str, model: str = "gpt-4") -> dict:
    """
    Executa um prompt utilizando as APIs Groq e OpenAI (se configuradas) e retorna os resultados.
    
    Args:
        prompt (str): O prompt a ser enviado.
        model (str): Modelo a ser utilizado (default "gpt-4").
    
    Returns:
        dict: Dicionário com as respostas e dados de tokens de cada serviço.
    """
    resultados = {}

    # Chamada via Groq (se configurada)
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key:
        try:
            client_groq = Groq(api_key=groq_api_key)
            response_groq = client_groq.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=os.getenv("GROQ_MODEL", "mixtral-8x7b-32768"),
            )
            resultados["GROQ"] = {
                "historia": response_groq.choices[0].message.content,
                "tokens": response_groq.usage.__dict__
            }
        except Exception as e:
            logger.error(f"Erro na chamada Groq: {e}")

    # Chamada via OpenAI (se configurada)
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if openai_api_key:
        try:
            client_openai = OpenAI(api_key=openai_api_key)
            response_openai = client_openai.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            )
            usage_dict = response_openai.usage.__dict__
            usage_dict.pop("completion_tokens_details", None)
            usage_dict.pop("prompt_tokens_details", None)
            resultados["OPENAI"] = {
                "historia": response_openai.choices[0].message.content,
                "tokens": usage_dict
            }
        except Exception as e:
            logger.error(f"Erro na chamada OpenAI: {e}")
    
    return resultados
