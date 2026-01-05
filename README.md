# 🏡 Chá de Casa Nova - Sistema RSVP

Sistema completo de confirmação de presença para Chá de Casa Nova / Chá de Casamento com design ilustrado e funcionalidades administrativas.

## 📋 Funcionalidades

### Para Convidados
- ✅ Confirmação de presença simples e intuitiva
- 📍 Localização clicável com links para Google Maps e Waze
- 📱 Design responsivo para celular
- 🎨 Interface amigável com tema de cozinha

### Para Organizadores
- 📊 Painel administrativo para visualizar confirmações
- 📥 Exportação de lista em CSV
- 📧 Notificações automáticas por e-mail
- 🔒 Área protegida por senha
- 🚫 Prevenção de confirmações duplicadas

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.9 ou superior
- pip (gerenciador de pacotes Python)

### Passo 1: Instalar dependências

```powershell
pip install -r requirements.txt
```

### Passo 2: Configurar variáveis de ambiente

1. Copie o arquivo de exemplo:
```powershell
Copy-Item .env.example .env
```

2. Edite o arquivo `.env` e configure:
   - `ADMIN_PASSWORD`: Senha para acessar área administrativa
   - `SMTP_USER`: Seu e-mail para envio (ex: Gmail)
   - `SMTP_PASSWORD`: Senha de app do Gmail
   - `EMAIL_DESTINATARIO`: E-mail que receberá as notificações

**Importante para Gmail:**
- Ative a verificação em duas etapas
- Gere uma "Senha de app" em https://myaccount.google.com/apppasswords
- Use essa senha no campo `SMTP_PASSWORD`

### Passo 3: Executar a aplicação

```powershell
python main.py
```

Ou com Uvicorn:

```powershell
uvicorn main:app --reload
```

A aplicação estará disponível em: **http://localhost:8000**

## 🌐 Endpoints

### Página Principal
- **URL**: `http://localhost:8000/`
- **Descrição**: Página de confirmação de presença para convidados

### Área Administrativa
- **URL**: `http://localhost:8000/admin`
- **Descrição**: Painel administrativo (requer senha)
- **Senha padrão**: `admin123` (altere no arquivo `.env`)

### API REST

#### Confirmar Presença
```http
POST /confirmar-presenca
Content-Type: application/json

{
  "nome": "Nome do Convidado"
}
```

#### Listar Confirmados (Admin)
```http
GET /admin/confirmados?senha=admin123
```

#### Exportar CSV (Admin)
```http
GET /admin/confirmados/csv?senha=admin123
```

## 📁 Estrutura do Projeto

```
Casa/
├── main.py                 # Aplicação FastAPI
├── requirements.txt        # Dependências Python
├── .env                    # Configurações (não versionado)
├── .env.example           # Exemplo de configurações
├── README.md              # Este arquivo
├── confirmacoes.db        # Banco SQLite (criado automaticamente)
├── templates/
│   ├── index.html         # Página principal
│   └── admin.html         # Painel administrativo
└── static/
    ├── css/
    │   └── style.css      # Estilos
    └── js/
        └── script.js      # JavaScript do formulário
```

## 🎨 Design

### Cores
- **Primária**: `#d4a5a5` (rosa suave)
- **Secundária**: `#f0d9da` (rosa claro)
- **Terciária**: `#f5e6e8` (rosa bem claro)
- **Destaque**: `#c69090` (rosa médio)

### Fontes
- **Títulos**: Dancing Script (Google Fonts)
- **Texto**: Quicksand (Google Fonts)

### Elementos
- Ícones de utensílios de cozinha (emojis)
- Animações suaves de flutuação
- Cards arredondados com sombras
- Design totalmente responsivo

## 🔧 Tecnologias Utilizadas

- **Backend**: FastAPI (Python)
- **Banco de Dados**: SQLite com SQLAlchemy async
- **Frontend**: HTML5, CSS3, JavaScript vanilla
- **Template Engine**: Jinja2
- **E-mail**: aiosmtplib (SMTP assíncrono)

## 📊 Banco de Dados

### Model: Confirmacao
- `id`: Integer (Primary Key)
- `nome`: String (Unique, Not Null)
- `data_confirmacao`: DateTime (Auto)
- `status`: String (Default: "Confirmado")

## 🔒 Segurança

- Validação de entrada (nome mínimo 3 caracteres)
- Prevenção de SQL injection (SQLAlchemy ORM)
- Área administrativa protegida por senha
- Validação de e-mails duplicados
- Variáveis sensíveis em arquivo `.env`

## 🚀 Deploy

### Opções de Deploy

#### 1. Render.com (Recomendado)
```bash
# Adicionar ao projeto:
# - Procfile: web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### 2. Railway.app
```bash
# Adicionar start command:
# uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### 3. Heroku
```bash
# Adicionar Procfile:
# web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### 4. DigitalOcean / VPS
```bash
# Usar nginx + uvicorn com systemd
```

**Importante**: Configure as variáveis de ambiente no painel do serviço de deploy.

## 📝 Personalização

### Alterar Informações do Evento

Edite o arquivo `templates/index.html`:
- Linha 21: Título do evento
- Linha 22: Nomes dos noivos
- Linhas 34-42: Data, hora e local

### Alterar Cores

Edite o arquivo `static/css/style.css` (variáveis CSS):
```css
:root {
    --cor-primaria: #d4a5a5;
    --cor-secundaria: #f0d9da;
    /* ... outras cores ... */
}
```

### Adicionar Logo ou Imagens

1. Adicione imagens em `static/images/`
2. Referencie no HTML:
```html
<img src="/static/images/logo.png" alt="Logo">
```

## 🐛 Troubleshooting

### E-mail não está sendo enviado
1. Verifique as configurações SMTP no `.env`
2. Confirme que está usando "Senha de app" do Gmail
3. Verifique os logs no terminal

### Erro de banco de dados
1. Delete o arquivo `confirmacoes.db`
2. Reinicie a aplicação (será recriado automaticamente)

### Porta já em uso
```powershell
# Use outra porta
uvicorn main:app --port 8001
```

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique os logs no terminal
2. Confirme todas as dependências instaladas
3. Revise o arquivo `.env`

## 📄 Licença

Este projeto é de uso pessoal para o Chá de Casa Nova de Manu e Gabriel.

---

**Data do Evento**: 10 de Janeiro de 2026 | 13h  
**Local**: Rua Alameda dos Lagos, 571 – Esmeraldas (Sítio da Tia Ceia)

✨ Feito com carinho para Manu e Gabriel ✨
