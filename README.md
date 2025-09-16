# projetoTypeBot

![Python](https://img.shields.io/badge/python-3.x-blue.svg)
![Flask](https://img.shields.io/badge/flask-webframework-green.svg)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)

-----------------------------------------------------------------------------------------------------------

## 🔍 Descrição

`projetoTypeBot` é uma aplicação em Python que integra **embeddings** com o **Typebot**, permitindo a criação de fluxos inteligentes de chatbot e processamento de linguagem natural (NLP).  

O projeto foi desenvolvido como parte de estudos e prática em **APIs, NLP e integrações com Typebot**, aplicando conceitos de **back-end, serviços REST, armazenamento e manipulação de dados**.  

-----------------------------------------------------------------------------------------------------------

## 📁 Estrutura do projeto


projetoTypeBot/
│── app.py # Arquivo principal que inicia a aplicação
│── requirements.txt # Dependências do Python
│── .env_example # Exemplo de variáveis de ambiente
│
├── routes/ # Define as rotas de API
├── services/ # Serviços e integrações (embeddings, Typebot etc.)
└── utils/ # Funções utilitárias


-----------------------------------------------------------------------------------------------------------

## ⚙️ Pré-requisitos

Antes de rodar localmente, você vai precisar:

- **Python 3.x**  
- **pip** para instalar dependências  
- Criar um arquivo `.env` baseado no `.env_example` e configurar suas credenciais  
- Ter o **ngrok** instalado (para expor o servidor local na web)  

-----------------------------------------------------------------------------------------------------------

## 🚀 Como executar

```
# clonar o repositório
git clone https://github.com/Guilherme-Fadel/projetoTypeBot.git

# entrar na pasta do projeto
cd projetoTypeBot

# criar ambiente virtual
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# instalar dependências
pip install -r requirements.txt

# configurar variáveis de ambiente
cp .env_example .env
# editar .env com suas credenciais

# executar aplicação
python app.py
````
-----------------------------------------------------------------------------------------------------------
Após rodar, o servidor estará disponível em:

👉 http://localhost:5000

⚠️ Importante: Para que o Typebot consiga acessar o servidor, ele precisa estar hospedado na web.
No projeto, está sendo utilizado o ngrok
 para simular essa funcionalidade:

```ngrok http 5000```
Isso irá gerar um link público, por exemplo:
```https://xxxx-xxx-xxx.ngrok-free.app```

Esse link deve ser configurado no Typebot para permitir a comunicação.
-----------------------------------------------------------------------------------------------------------
Dependências principais:

- Flask → Framework web
- SentenceTransformers → Embeddings
- Requests → Requisições HTTP
- ngrok → Exposição do servidor local na web
- S3 (AWS) → Armazenamento de arquivos de teste (será substituído futuramente por banco de dados)
- Groq API → Processamento e embeddings via chave de API
- Outras listadas em requirements.txt
-----------------------------------------------------------------------------------------------------------

Funcionalidades

✔️ Geração e consulta de embeddings
✔️ Integração com Typebot
✔️ API REST para interações externas
✔️ Utilitários para processamento de texto
✔️ Hospedagem simulada via ngrok
-----------------------------------------------------------------------------------------------------------
Exemplo de uso

Requisição POST para o endpoint de resposta:

```
POST /responder
Content-Type: application/json

{
  "pergunta": "Qual a capital da França?"
}
```

Resposta esperada:
```
{
  "resposta": "A capital da França é Paris."
}
```
Desenvolvido por Guilherme Fadel
