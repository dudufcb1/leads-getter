"""
Aplicación principal de FastAPI para el sistema de generación de leads.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import jobs, stats, leads, control, advanced_stats, auth, config, realtime_dashboard
from .database.database import create_tables
from .core.config import settings
from .core.error_handler_new import add_error_handlers
from .core.logging_config import setup_logging

# Configurar logging
setup_logging()

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

# Agregar handlers de error
add_error_handlers(app)

# Incluir routers
app.include_router(
    jobs.router,
    prefix="/api/v1/jobs",
    tags=["jobs"]
)

app.include_router(
    stats.router,
    prefix="/api/v1/stats",
    tags=["stats"]
)

app.include_router(
    leads.router,
    prefix="/api/v1/leads",
    tags=["leads"]
)

app.include_router(
    control.router,
    prefix="/api/v1/control",
    tags=["control"]
)

app.include_router(
    advanced_stats.router,
    prefix="/api/v1/advanced-stats",
    tags=["advanced-stats"]
)

app.include_router(
    auth.router,
    prefix="/api/v1/auth",
    tags=["auth"]
)

app.include_router(
    config.router,
    prefix="/api/v1/config",
    tags=["config"]
)

app.include_router(
    realtime_dashboard.router,
    prefix="/api/v1/dashboard",
    tags=["dashboard"]
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