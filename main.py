from fastapi import FastAPI, Depends
from fastapi.openapi.utils import get_openapi
from routers.v1 import llm_router as llm_router_v1
from routers.v2 import llm_router as llm_router_v2
from utils import verify_token

# Metadados da API
API_TITLE = "API para IA"
API_VERSION = "1.0"
TERMS_OF_SERVICE = "https://en.wikipedia.org/wiki/WTFPL"
CONTACT_INFO = {
    "name": "Diego Oliveira e Jorge Ferla",
    "url": "http://github.com/GansoUK/",
    "email": "jfxxi@hotmail.com",
}
LICENSE_INFO = {
    "name": "Do What The F*ck You Want To Public License",
    "url": "https://github.com/geeksam/wtf/blob/master/LICENSE",
}
API_DESCRIPTION = """ 
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
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    terms_of_service=TERMS_OF_SERVICE,
    contact=CONTACT_INFO,
    license_info=LICENSE_INFO,
    dependencies=[Depends(verify_token)]
)

def custom_openapi() -> dict:
    """
    Customiza o esquema OpenAPI para incluir metadados e configurações de segurança.
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # Adiciona metadados adicionais
    openapi_schema["info"].update({
        "termsOfService": TERMS_OF_SERVICE,
        "contact": CONTACT_INFO,
        "license": LICENSE_INFO,
    })
    # Define o esquema de segurança
    openapi_schema.setdefault("components", {}).setdefault("securitySchemes", {
        "ApiKeyAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "x-api-token"
        }
    })
    # Aplica a segurança a todos os endpoints
    for path in openapi_schema.get("paths", {}):
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"ApiKeyAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Inclui os routers para as versões 1 e 2
app.include_router(llm_router_v1.router, prefix="/v1/llm")
app.include_router(llm_router_v2.router, prefix="/v2/llm")
