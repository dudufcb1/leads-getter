"""
Endpoints para obtener leads y estadísticas.
"""

from typing import List, Optional
from fastapi import APIRouter, Query, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..database.models import Website, Email

router = APIRouter()


class LeadInfo(BaseModel):
    """Información de un lead encontrado."""
    id: int
    url: str
    contact_email: Optional[str] = None
    language: Optional[str] = None
    status: str
    source_url: Optional[str] = None


class LeadsResponse(BaseModel):
    """Respuesta paginada con leads."""
    pagination: dict
    leads: List[LeadInfo]


@router.get("/", response_model=LeadsResponse)
async def get_leads(
    page: int = Query(1, description="Número de página", ge=1),
    limit: int = Query(50, description="Elementos por página", ge=1, le=100),
    language: Optional[str] = Query(None, description="Filtrar por idioma"),
    domain: Optional[str] = Query(None, description="Filtrar por dominio"),
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de leads encontrados con paginación y filtros.

    - **page**: Número de página (empieza en 1)
    - **limit**: Número de elementos por página (1-100)
    - **language**: Filtrar por idioma (opcional)
    - **domain**: Filtrar por dominio (opcional)
    """
    try:
        # Calcular offset
        offset = (page - 1) * limit

        # Construir query base
        query = db.query(Website)

        # Aplicar filtros
        if language:
            query = query.filter(Website.language == language)
        if domain:
            query = query.filter(Website.domain.contains(domain))

        # Obtener total de resultados
        total_items = query.count()

        # Obtener resultados paginados
        websites = query.offset(offset).limit(limit).all()

        # Convertir a formato de respuesta
        leads = []
        for website in websites:
            # Obtener el primer email encontrado para este sitio (si existe)
            email = db.query(Email).filter(Email.website_id == website.id).first()
            contact_email = email.email if email else None

            leads.append(LeadInfo(
                id=website.id,
                url=website.url,
                contact_email=contact_email,
                language=website.language,
                status=website.status,
                source_url=website.source_url
            ))

        # Calcular información de paginación
        total_pages = (total_items + limit - 1) // limit  # Ceiling division

        return LeadsResponse(
            pagination={
                "total_items": total_items,
                "total_pages": total_pages,
                "current_page": page,
                "items_per_page": limit
            },
            leads=leads
        )

    except Exception as e:
        # En una implementación completa, manejar errores específicos
        raise HTTPException(status_code=500, detail=f"Error retrieving leads: {str(e)}")