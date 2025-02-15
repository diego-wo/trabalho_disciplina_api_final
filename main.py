from fastapi import FastAPI, Depends
from fastapi.openapi.utils import get_openapi
from routers.v1 import llm_router as llm_router_v1
from routers.v2 import llm_router as llm_router_v2
from utils import verify_token

description = """ 
    Trabalho da disciplina de API da Pós-graduação em Sistemas e Agentes Inteligentes
    Prof. Rogério Rodrigues
    
    **v1:**
    - /v1/llm/gerar_historia: Gera uma história básica
    - /v1/llm/resumir_texto: Resume um texto simples
    
    **v2:**
    - /v2/llm/gerar_historia_evolutiva: Gera uma história evolutiva utilizando uma abordagem em cadeia
    - /v2/llm/resumir_texto_avancado: Resume e analisa um texto
"""

app = FastAPI(
    title="API para IA",
    description=description,
    version="1.0",
    terms_of_service="https://en.wikipedia.org/wiki/WTFPL",
    contact={
        "name": "Diego Oliveira e Jorge Ferla",
        "url": "http://github.com/GansoUK/",
        "email": "jfxxi@hotmail.com",
    },
    license_info={
        "name": "Do What The F*ck You Want To Public License",
        "url": "https://github.com/geeksam/wtf/blob/master/LICENSE",
    },
    dependencies=[Depends(verify_token)]
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # Adiciona os metadados adicionais manualmente
    openapi_schema["info"]["termsOfService"] = "https://en.wikipedia.org/wiki/WTFPL"
    openapi_schema["info"]["contact"] = {
        "name": "Diego Oliveira e Jorge Ferla",
        "url": "http://github.com/GansoUK/",
        "email": "jfxxi@hotmail.com",
    }
    openapi_schema["info"]["license"] = {
        "name": "Do What The F*ck You Want To Public License",
        "url": "https://github.com/geeksam/wtf/blob/master/LICENSE",
    }
    # Define o esquema de segurança
    openapi_schema["components"]["securitySchemes"] = {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "x-api-token"
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"ApiKeyAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(llm_router_v1.router, prefix="/v1/llm")
app.include_router(llm_router_v2.router, prefix="/v2/llm")
