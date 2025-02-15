# Trabalho FastAPI - 15FEV25

Esta API foi desenvolvida para a disciplina de API na Pós-graduação em Sistemas e Agentes Inteligentes, sob a orientação do Prof. Rogério Rodrigues. O projeto demonstra a construção de uma API com dois serviços de IA, evolução de versão (v1 e v2), autenticação simples e boas práticas de desenvolvimento.

## Tecnologias Utilizadas

- **Linguagem:** Python 3.10 ou superior
- **Framework:** FastAPI
- **Banco de Dados:** SQLite (utilizando SQLAlchemy e databases)
- **Modelos de IA:** Integração com Groq e OpenAI
- **Outras Bibliotecas:** tiktoken, entre outras (consulte o `requirements.txt`)

## Estrutura do Projeto

```
.
├── main.py                 # Arquivo principal da API
├── models.py               # Definição de modelos e configuração do banco de dados
├── utils.py                # Funções utilitárias (ex.: autenticação, logging, execução de prompt)
├── token_count.py          # Função para contagem de tokens (monitoramento)
├── routers/
│   ├── v1/
│   │    └── llm_router.py  # Endpoints v1 (geração de história e resumo básico)
│   └── v2/
│        └── llm_router.py  # Endpoints v2 (geração evolutiva e resumo avançado)
├── requirements.txt        # Lista de dependências
├── .env.sample             # Exemplo de arquivo de variáveis de ambiente
└── README.md               # Este arquivo
```

## Configuração do Ambiente

1. **Instalação do Python:**  
   Recomenda-se utilizar Python 3.10 ou superior.

2. **Criar Ambiente Virtual:**

   - No terminal, na pasta do projeto, execute:
     ```bash
     python -m venv venv
     ```

3. **Ativar o Ambiente Virtual:**

   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **Linux/Mac:**
     ```bash
     source venv/bin/activate
     ```

4. **Instalar Dependências:**

   ```bash
   pip install -r requirements.txt
   ```

5. **Configurar Variáveis de Ambiente:**

   - Copie o arquivo `.env.sample` para `.env`:
     ```bash
     cp .env.sample .env
     ```
   - Preencha as variáveis necessárias (ex.: `OPENAI_API_KEY`, `GROQ_API_KEY`, `OPENAI_MODEL`, `GROQ_MODEL`, etc.).

## Execução da API

### Ambiente de Desenvolvimento

Para executar a API em modo desenvolvimento (com auto-reload), utilize:

```bash
uvicorn main:app --reload
```

> **Observação:** Algumas instruções anteriores usavam comandos como `fastapi dev main.py`, mas a prática comum é usar o Uvicorn para rodar a aplicação.

### Ambiente de Produção

Para executar a API em produção, utilize:

```bash
uvicorn main:app
```

## Documentação Interativa

Após iniciar a API, acesse a documentação automática gerada pelo Swagger em:

[http://localhost:8000/docs](http://localhost:8000/docs)

Na interface do Swagger, clique em **Authorize** e insira o token (por exemplo, `123456`) no header `x-api-token` para autenticar suas requisições.

## Endpoints Principais

### Versão 1 (v1)

- **Gerar História Básica:**
  - **URL:** `/v1/llm/gerar_historia`
  - **Descrição:** Recebe um tema e retorna uma história gerada por Groq e OpenAI, juntamente com informações de uso (contagem de tokens, tempo de execução, etc.).

- **Resumir Texto Simples:**
  - **URL:** `/v1/llm/resumir_texto`
  - **Descrição:** Recebe um texto e retorna um resumo simples utilizando a API OpenAI.

### Versão 2 (v2)

- **Gerar História Evolutiva:**
  - **URL:** `/v2/llm/gerar_historia_evolutiva`
  - **Descrição:** Utiliza uma abordagem em cadeia: primeiro gera um esboço com Groq e, em seguida, refina esse esboço com OpenAI. Permite customização via parâmetros opcionais como estilo, gênero e extensão.

- **Resumir Texto Avançado:**
  - **URL:** `/v2/llm/resumir_texto_avancado`
  - **Descrição:** Recebe um texto e retorna um resumo avançado que pode incluir análise de sentimento e extração de palavras-chave.

## Boas Práticas Adotadas

- **Validação de Dados:** Uso do FastAPI e Pydantic para validar entradas.
- **Tratamento de Erros:** Blocos try/except e HTTPException para lidar com falhas.
- **Logging:** Sistema de logging configurado para monitorar requisições e erros.
- **Segurança:** Autenticação global via header `x-api-token` e esquema de segurança configurado para o Swagger.
- **Versionamento:** Estrutura de endpoints organizada em v1 e v2 para demonstrar evolução.
- **Monitoramento de Tokens:** Integração com contagem de tokens para avaliar o uso e desempenho das LLMs.

## Uso do Postman

- Exporte o arquivo `openapi.json` da API (disponível em [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)) e importe no Postman para testar os endpoints.
- Configure o header `x-api-token` com o valor correto para autenticação.

## Uso do GitHub Desktop

- Mantenha commits frequentes com mensagens descritivas.
- Verifique se o `.gitignore` está configurado para ignorar a pasta do ambiente virtual (venv) e outros arquivos temporários.
- Atualize o README.md com instruções claras para facilitar o entendimento e a execução do projeto.
