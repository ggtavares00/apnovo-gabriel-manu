"""
Sistema de Confirmação de Presença (RSVP)
Chá de Casa Nova - Manu e Gabriel
"""
import os
import csv
from datetime import datetime
from io import StringIO
from typing import List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.future import select
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./confirmacoes.db")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_DESTINATARIO = os.getenv("EMAIL_DESTINATARIO", "")

# Database setup
Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Confirmacao(Base):
    """Model para confirmações de presença"""
    __tablename__ = "confirmacoes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, index=True, nullable=False)
    data_confirmacao = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String, default="Confirmado", nullable=False)


# Pydantic models
class ConfirmacaoCreate(BaseModel):
    nome: str = Field(..., min_length=3, max_length=100, description="Nome completo do convidado")


class ConfirmacaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    nome: str
    data_confirmacao: datetime
    status: str


# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: criar tabelas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: nada a fazer


# FastAPI app
app = FastAPI(title="Chá de Casa Nova - RSVP", lifespan=lifespan)

# Templates
templates = Jinja2Templates(directory="templates")

# Static files (depois das rotas para evitar conflitos)
@app.on_event("startup")
async def configure_static_files():
    pass

app.mount("/static", StaticFiles(directory="static"), name="static")


# Database dependency
async def get_db():
    async with async_session() as session:
        yield session


# Serviço de e-mail
async def enviar_email_confirmacao(nome: str):
    """Envia e-mail para o organizador informando sobre a confirmação"""
    if not all([SMTP_USER, SMTP_PASSWORD, EMAIL_DESTINATARIO]):
        print("⚠️  Configurações de e-mail não definidas. E-mail não enviado.")
        return

    try:
        mensagem = MIMEMultipart()
        mensagem["From"] = SMTP_USER
        mensagem["To"] = EMAIL_DESTINATARIO
        mensagem["Subject"] = f"✅ Nova Confirmação - {nome}"

        corpo = f"""
        <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #d4a5a5;">🎉 Nova Confirmação de Presença!</h2>
            <p><strong>Convidado:</strong> {nome}</p>
            <p><strong>Data e Hora:</strong> {datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
            <p><strong>Status:</strong> Confirmado</p>
            <hr>
            <p style="color: #888; font-size: 12px;">
                Chá de Casa Nova - Manu e Gabriel<br>
                10 de Janeiro de 2026 | 13h
            </p>
        </body>
        </html>
        """

        mensagem.attach(MIMEText(corpo, "html"))

        await aiosmtplib.send(
            mensagem,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
            start_tls=True,
            timeout=10,  # Timeout de 10 segundos
        )
        print(f"✅ E-mail enviado para {EMAIL_DESTINATARIO}")
    except TimeoutError:
        print(f"⚠️ Timeout ao enviar e-mail - ignorando para não bloquear confirmação")
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e} - ignorando para não bloquear confirmação")


# Rotas principais
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Página principal do RSVP"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/confirmar-presenca", response_model=ConfirmacaoResponse)
async def confirmar_presenca(
    confirmacao: ConfirmacaoCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Confirma presença de um convidado
    - Valida nome
    - Previne duplicatas
    - Envia e-mail
    """
    # Verificar se já existe confirmação com esse nome
    result = await db.execute(
        select(Confirmacao).where(Confirmacao.nome == confirmacao.nome.strip())
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Este nome já confirmou presença!"
        )

    # Criar nova confirmação
    nova_confirmacao = Confirmacao(
        nome=confirmacao.nome.strip(),
        data_confirmacao=datetime.now(),
        status="Confirmado"
    )

    db.add(nova_confirmacao)
    await db.commit()
    await db.refresh(nova_confirmacao)

    # Enviar e-mail em background (não bloqueia a resposta)
    import asyncio
    asyncio.create_task(enviar_email_confirmacao(nova_confirmacao.nome))

    return nova_confirmacao


@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, senha: str = ""):
    """Página administrativa"""
    if senha != ADMIN_PASSWORD:
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Admin - Acesso Restrito</title>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
                <style>
                    * {
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }
                    body {
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: linear-gradient(135deg, #f5f9f6 0%, #e8f3ea 50%, #d4e8d9 100%);
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }
                    .login-box {
                        background: white;
                        padding: 50px 40px;
                        border-radius: 20px;
                        box-shadow: 0 15px 40px rgba(126, 175, 134, 0.2);
                        text-align: center;
                        max-width: 420px;
                        width: 90%;
                    }
                    .lock-icon {
                        font-size: 3.5rem;
                        color: #7eaf86;
                        margin-bottom: 20px;
                        animation: pulse 2s ease-in-out infinite;
                    }
                    @keyframes pulse {
                        0%, 100% { transform: scale(1); }
                        50% { transform: scale(1.05); }
                    }
                    h2 { 
                        color: #7eaf86; 
                        margin-bottom: 15px;
                        font-size: 1.8rem;
                        font-weight: 600;
                    }
                    p {
                        color: #3d4f42;
                        margin-bottom: 30px;
                        font-size: 1rem;
                    }
                    input {
                        width: 100%;
                        padding: 15px;
                        margin: 15px 0;
                        border: 2px solid #a8c9b0;
                        border-radius: 12px;
                        font-size: 16px;
                        transition: all 0.3s ease;
                        background: #f5f9f6;
                    }
                    input:focus {
                        outline: none;
                        border-color: #7eaf86;
                        box-shadow: 0 0 0 4px rgba(126, 175, 134, 0.15);
                        background: white;
                    }
                    button {
                        width: 100%;
                        padding: 15px;
                        background: linear-gradient(135deg, #7eaf86 0%, #5a8c64 100%);
                        color: white;
                        border: none;
                        border-radius: 12px;
                        font-size: 16px;
                        font-weight: 600;
                        cursor: pointer;
                        margin-top: 15px;
                        transition: all 0.3s ease;
                        box-shadow: 0 5px 20px rgba(126, 175, 134, 0.3);
                        display: inline-flex;
                        align-items: center;
                        justify-content: center;
                        gap: 10px;
                    }
                    button:hover { 
                        background: linear-gradient(135deg, #5a8c64 0%, #7eaf86 100%);
                        transform: translateY(-2px);
                        box-shadow: 0 8px 25px rgba(126, 175, 134, 0.4);
                    }
                    button:active {
                        transform: translateY(0);
                    }
                </style>
            </head>
            <body>
                <div class="login-box">
                    <i class="fas fa-lock lock-icon"></i>
                    <h2>Área Administrativa</h2>
                    <p>Digite a senha para acessar:</p>
                    <form method="get">
                        <input type="password" name="senha" placeholder="Senha" required autofocus>
                        <button type="submit">
                            <i class="fas fa-sign-in-alt"></i> Entrar
                        </button>
                    </form>
                </div>
            </body>
            </html>
            """,
            status_code=401
        )
    
    return templates.TemplateResponse("admin.html", {"request": request, "senha": senha})


@app.get("/admin/confirmados")
async def listar_confirmados(
    senha: str = "",
    db: AsyncSession = Depends(get_db)
):
    """Lista todos os confirmados (requer senha)"""
    if senha != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Senha incorreta")

    result = await db.execute(
        select(Confirmacao).order_by(Confirmacao.data_confirmacao.desc())
    )
    confirmacoes = result.scalars().all()

    return {
        "total": len(confirmacoes),
        "confirmacoes": [
            {
                "id": c.id,
                "nome": c.nome,
                "data_confirmacao": c.data_confirmacao.strftime("%d/%m/%Y %H:%M"),
                "status": c.status
            }
            for c in confirmacoes
        ]
    }


@app.get("/admin/confirmados/csv")
async def exportar_csv(
    senha: str = "",
    db: AsyncSession = Depends(get_db)
):
    """Exporta confirmados em CSV (requer senha)"""
    if senha != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Senha incorreta")

    result = await db.execute(
        select(Confirmacao).order_by(Confirmacao.data_confirmacao.desc())
    )
    confirmacoes = result.scalars().all()

    # Criar CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Nome", "Data Confirmação", "Status"])

    for c in confirmacoes:
        writer.writerow([
            c.id,
            c.nome,
            c.data_confirmacao.strftime("%d/%m/%Y %H:%M"),
            c.status
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=confirmacoes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
