"""
Aplicación principal de FastAPI para el sistema de generación de leads.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import jobs, stats
from .database.database import create_tables
from .core.config import settings

# Crear la aplicación FastAPI
app = FastAPI(
    title="Leads Generator API",
    description="API REST para el sistema de generación de leads",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(
    jobs.router,
    prefix="/api/v1/jobs",
    tags=["jobs"]
)

app.include_router(
    stats.router,
    prefix="/api/v1/leads",
    tags=["leads"]
)


@app.on_event("startup")
async def startup_event():
    """Evento que se ejecuta al iniciar la aplicación."""
    # Crear las tablas de la base de datos
    create_tables()
    print("✅ Base de datos inicializada correctamente")


@app.get("/api/v1/health")
async def health_check():
    """Endpoint para verificar el estado de la API."""
    return {"status": "healthy", "message": "Leads Generator API is running"}


@app.get("/")
async def root():
    """Endpoint raíz."""
    return {
        "message": "Welcome to Leads Generator API",
        "version": "1.0.0",
        "docs": "/docs"
    }