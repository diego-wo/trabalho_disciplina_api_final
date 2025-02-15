import os
import time
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import insert
from models import database, historias
from utils import obter_logger_e_configuracao, executar_prompt
from openai import OpenAI

logger = obter_logger_e_configuracao()
router = APIRouter()


def _serialize_tokens(tokens: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converte os valores do dicionário de tokens para tipos serializáveis (int, float, str, bool, list ou dict).
    Caso contrário, converte para string.
    """
    return {
        k: (v if isinstance(v, (int, float, str, bool, list, dict)) else str(v))
        for k, v in tokens.items()
    }


@router.post(
    "/gerar_historia_evolutiva",
    summary="Gera uma história evolutiva avançada",
    description=(
        "Demonstra uma abordagem em cadeia: primeiro, um modelo (Groq) gera um esboço da história; "
        "depois, o esboço é refinado por um segundo modelo (OpenAI) para produzir uma narrativa final aprimorada. "
        "Parâmetros opcionais permitem customização da saída."
    ),
)
async def gerar_historia_evolutiva(
    tema: str,
    estilo: str = "aventura",
    genero: str = "ficção",
    extensao: str = "media",
    x_api_token: str = Query(...),
) -> Dict[str, Any]:
    """
    Gera uma história evolutiva a partir de um tema, utilizando duas LLMs em cadeia.

    Args:
        tema (str): Tema da história.
        estilo (str): Estilo desejado (default: "aventura").
        genero (str): Gênero da história (default: "ficção").
        extensao (str): Extensão desejada (default: "media").
        x_api_token (str): Token de autenticação.

    Returns:
        dict: Contém o esboço, a história refinada, tempos de execução e dados de tokens da OpenAI.
    """
    logger.info(f"[v2] Tema: {tema} | Estilo: {estilo} | Gênero: {genero} | Extensão: {extensao}")
    try:
        # Etapa 1: Gerar esboço com Groq
        prompt_esboco = (
            f"Escreva um esboço de uma história sobre {tema} com estilo {estilo}, "
            f"gênero {genero} e extensão {extensao}."
        )
        start_groq = time.time()
        resposta_esboco = executar_prompt(prompt_esboco).get("GROQ")
        elapsed_groq = time.time() - start_groq

        if not resposta_esboco:
            raise HTTPException(status_code=400, detail="Falha ao gerar esboço com Groq.")

        logger.info(f"[v2] Esboço gerado (Groq) em {elapsed_groq:.2f} segundos.")

        # Etapa 2: Refinar esboço com OpenAI
        prompt_refinado = f"Refine e amplie o seguinte esboço de história: {resposta_esboco}"
        client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        start_openai = time.time()
        response_refinado = client_openai.chat.completions.create(
            messages=[{"role": "user", "content": prompt_refinado}],
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        )
        elapsed_openai = time.time() - start_openai
        historia_final = response_refinado.choices[0].message.content

        tokens_refinado_raw = response_refinado.usage.__dict__
        tokens_refinado = _serialize_tokens(tokens_refinado_raw)

        logger.info(f"[v2] História refinada (OpenAI) em {elapsed_openai:.2f} segundos.")

        # Inserir dados no banco
        query = insert(historias).values(
            prompt=tema,
            groq={"esboco": resposta_esboco, "tempo": elapsed_groq},
            openai={"historia_final": historia_final, "tokens": tokens_refinado, "tempo": elapsed_openai},
        )
        await database.execute(query)

    except Exception as e:
        logger.error(f"[v2] Erro ao gerar história evolutiva: {repr(e)}")
        raise HTTPException(status_code=500, detail="Erro interno ao gerar história evolutiva")

    return {
        "esboco": resposta_esboco,
        "historia_evolutiva": historia_final,
        "tempo_groq": elapsed_groq,
        "tempo_openai": elapsed_openai,
        "tokens_openai": tokens_refinado,
    }


@router.post(
    "/resumir_texto_avancado",
    summary="Resume e analisa um texto",
    description=(
        "Recebe um texto e retorna um resumo avançado, incluindo uma análise de sentimento e extração de palavras-chave. "
        "Demonstra a aplicação complementar de LLMs."
    ),
)
async def resumir_texto_avancado(
    texto: str,
    tamanho: str = "conciso",
    x_api_token: str = Query(...),
) -> Dict[str, Any]:
    """
    Resume e analisa um texto, retornando um resumo avançado com informações de tempo e tokenização.

    Args:
        texto (str): Texto a ser resumido.
        tamanho (str): Extensão do resumo (default: "conciso").
        x_api_token (str): Token de autenticação.

    Returns:
        dict: Contém o resumo, o tempo de execução e os dados de tokens.
    """
    logger.info(f"[v2] Texto para resumo avançado recebido: {texto[:30]}... | Tamanho: {tamanho}")
    try:
        prompt = (
            f"Resuma o seguinte texto de forma {tamanho} e extraia as principais palavras-chave "
            f"e o sentimento (positivo, negativo ou neutro): {texto}"
        )
        client_openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        start_time = time.time()
        response = client_openai.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        )
        elapsed_time = time.time() - start_time
        resumo = response.choices[0].message.content
        tokens_raw = response.usage.__dict__
        tokens = _serialize_tokens(tokens_raw)
    except Exception as e:
        logger.error(f"[v2] Erro ao resumir texto avançado: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao resumir texto avançado")

    return {"resumo": resumo, "tempo": elapsed_time, "tokens": tokens}
