from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import insert
from typing import Dict, Any
import os

from models import database, historias
from utils import obter_logger_e_configuracao, verify_token, executar_prompt
from openai import OpenAI

logger = obter_logger_e_configuracao()
router = APIRouter()


@router.post(
    "/gerar_historia",
    summary="Gera uma história básica",
    description=(
        "Recebe um tema e retorna uma história gerada por modelos de linguagem (Groq e OpenAI), "
        "incluindo informações de contagem de tokens."
    ),
)
async def gerar_historia_v1(tema: str, x_api_token: str = Query(...)) -> Dict[str, Any]:
    """
    Gera uma história básica a partir do tema fornecido.

    Args:
        tema (str): Tema da história.
        x_api_token (str): Token de autenticação fornecido via query.

    Returns:
        dict: Dicionário contendo as respostas dos serviços Groq e OpenAI.
    """
    logger.info(f"[v1] Tema informado: {tema}")
    try:
        prompt: str = f"Escreva uma história sobre {tema}"
        response: Dict[str, Any] = executar_prompt(prompt)
        
        if not response.get("GROQ") and not response.get("OPENAI"):
            raise HTTPException(status_code=400, detail="Nenhum serviço retornou resposta válida.")
        
        # Inserção dos dados no banco
        query = insert(historias).values(
            prompt=tema,
            groq=response.get("GROQ"),
            openai=response.get("OPENAI"),
        )
        await database.execute(query)
    except Exception as e:
        logger.error(f"[v1] Erro ao gerar história: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao gerar história")
    
    return {"historia": {"Groq": response.get("GROQ"), "OpenAI": response.get("OPENAI")}}

@router.post(
    "/resumir_texto",
    summary="Resume um texto básico",
    description=(
        "Recebe um texto e retorna um resumo simples utilizando a API OpenAI, "
        "incluindo dados de tokenização."
    ),
)
async def resumir_texto_v1(texto: str, x_api_token: str = Query(...)) -> Dict[str, Any]:
    """
    Resume um texto utilizando a API OpenAI.

    Args:
        texto (str): Texto a ser resumido.
        x_api_token (str): Token de autenticação fornecido via query.

    Returns:
        dict: Dicionário contendo o resumo e os dados de tokenização.
    """
    logger.info(f"[v1] Texto para resumo recebido: {texto[:30]}...")
    try:
        prompt: str = f"Resuma o seguinte texto: {texto}"
        client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client_openai.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        )
        resumo: str = response.choices[0].message.content
        tokens: Dict[str, Any] = response.usage.__dict__
    except Exception as e:
        logger.error(f"[v1] Erro ao resumir texto: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao resumir texto")
    
    return {"resumo": resumo, "tokens": tokens}
