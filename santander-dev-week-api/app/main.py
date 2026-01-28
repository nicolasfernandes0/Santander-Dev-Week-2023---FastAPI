from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import engine, get_db
from app import models, crud
from app.routers import users

# ========== LIFESPAN ==========
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Iniciando Santander Dev Week API...")
    
    # Criar tabelas
    models.Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas")
    
    # Popular dados iniciais
    print("🌱 Populando dados iniciais...")
    db: Session = next(get_db())
    try:
        crud.seed_initial_data(db)
        print("✅ Dados iniciais criados")
    except Exception as e:
        print(f"⚠️  Erro: {e}")
    finally:
        db.close()
    
    print("✅ API pronta!")
    print("📚 Documentação: http://localhost:8000/docs")
    print("🌐 Endpoints disponíveis:")
    print("   • GET  /           - Página inicial")
    print("   • GET  /health     - Health check")
    print("   • GET  /users      - Listar usuários")
    print("   • GET  /users/{id} - Buscar usuário")
    print("   • POST /users      - Criar usuário")
    print("   • POST /users/{id}/deposit  - Depósito")
    print("   • POST /users/{id}/withdraw - Saque")
    print("   • POST /users/{id}/transfer - Transferência")
    print("=" * 50)
    
    yield
    
    print("🔴 Encerrando API...")

# ========== APLICAÇÃO FASTAPI ==========
app = FastAPI(
    title="Santander Dev Week 2023 - FastAPI",
    description="API RESTful convertida de Java/Spring Boot para Python/FastAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configurar CORS para permitir frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rotas
app.include_router(users.router)

# ========== ROTAS GLOBAIS ==========

@app.get("/")
async def root():
    """Página inicial da API"""
    return {
        "message": "🏦 Bem-vindo à Santander Dev Week 2023 API",
        "description": "API RESTful convertida de Java/Spring Boot para Python/FastAPI",
        "version": "1.0.0",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        "endpoints": {
            "users": {
                "list": "GET /users",
                "get": "GET /users/{id}",
                "create": "POST /users",
                "create_simple": "POST /users/simple",
                "update": "PUT /users/{id}",
                "delete": "DELETE /users/{id}",
                "balance": "GET /users/{id}/balance",
                "deposit": "POST /users/{id}/deposit",
                "withdraw": "POST /users/{id}/withdraw",
                "transfer": "POST /users/{id}/transfer"
            }
        }
    }

@app.get("/health")
async def health_check():
    """Health check da API"""
    return {
        "status": "healthy",
        "service": "santander-dev-week-api",
        "timestamp": "2023-10-01T12:00:00Z"
    }

# ========== EXECUÇÃO ==========
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)