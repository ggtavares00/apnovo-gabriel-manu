# Deploy no Render - Instruções

## Variáveis de Ambiente no Render

Configure estas variáveis no painel do Render (Settings → Environment):

```
DATABASE_URL=postgresql+asyncpg://cha_panela_bd_user:HZ7Od1HCja6XeCdGBy44Rld5fLPDKlqO@dpg-d5dhi82li9vc73dig570-a.oregon-postgres.render.com/cha_panela_bd

ADMIN_PASSWORD=apnovo123

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=contatogtavares@gmail.com
SMTP_PASSWORD=knwr jbsn bmzr mqym
EMAIL_DESTINATARIO=contatogtavares@gmail.com
```

## Configuração do Web Service

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Runtime**: Python 3

## ⚠️ IMPORTANTE

- O arquivo `.env` NÃO é enviado para o GitHub (está no .gitignore)
- Configure TODAS as variáveis de ambiente no painel do Render
- Após o primeiro deploy, o banco de dados será criado automaticamente
