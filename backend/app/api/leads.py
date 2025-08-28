"""
API para manejar leads encontrados por el sistema de generación de leads.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database.database import get_db
from ..database.models import Website, Email

print("Cargando módulo de leads...")  # Mensaje de registro

router = APIRouter(tags=["leads"], redirect_slashes=False)

class LeadResponse(BaseModel):
    """Modelo de respuesta para un lead."""
    id: int
    url: str
    contact_email: Optional[str] = None
    language: str
    status: str
    source_url: Optional[str] = None

class LeadsResponse(BaseModel):
    """Modelo de respuesta para una lista de leads."""
    leads: List[LeadResponse]
    pagination: dict

@router.get("", response_model=LeadsResponse)
async def get_leads(
    page: int = Query(1, ge=1),
    limit: int = Query(50, le=100),
    language: Optional[str] = Query(None),
    domain: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de leads encontrados.
    
    Args:
        page: Número de página (comenzando desde 1)
        limit: Número de leads por página (máximo 100)
        language: Filtrar por idioma
        domain: Filtrar por dominio
        
    Returns:
        Lista de leads y información de paginación
    """
    print(f"Recibiendo solicitud para obtener leads: page={page}, limit={limit}, language={language}, domain={domain}")
    try:
        # Construir consulta base para websites con emails
        query = db.query(Website).join(Email, Website.id == Email.website_id)
        print("Consulta base construida")
        
        # Aplicar filtros si se proporcionan
        if language:
            query = query.filter(Website.language == language)
            print(f"Aplicando filtro de idioma: {language}")
        
        if domain:
            query = query.filter(Website.domain.contains(domain))
            print(f"Aplicando filtro de dominio: {domain}")
        
        # Filtrar solo websites con emails válidos
        query = query.filter(Email.is_valid == 1)
        print("Aplicando filtro de emails válidos")
        
        # Calcular offset para paginación
        offset = (page - 1) * limit
        print(f"Calculando offset: {offset}")
        
        # Ejecutar consulta con paginación
        websites = query.offset(offset).limit(limit).all()
        print(f"Consulta ejecutada, obtenidos {len(websites)} websites")
        
        # Contar total de registros para paginación
        total = query.count()
        total_pages = (total + limit - 1) // limit  # Redondeo hacia arriba
        print(f"Total de registros: {total}, total de páginas: {total_pages}")
        
        # Convertir websites a modelo de respuesta
        lead_responses = []
        for website in websites:
            # Tomar el primer email válido encontrado
            email = website.emails[0] if website.emails else None
            
            lead_responses.append(
                LeadResponse(
                    id=website.id,
                    url=website.url,
                    contact_email=email.email if email else None,
                    language=website.language or "unknown",
                    status=website.status,
                    source_url=website.source_url
                )
            )
        
        print(f"Preparando respuesta con {len(lead_responses)} leads")
        return LeadsResponse(
            leads=lead_responses,
            pagination={
                "current_page": page,
                "total_pages": total_pages,
                "total_items": total,
                "items_per_page": limit
            }
        )
    except Exception as e:
        print(f"Error al obtener leads: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener leads: {str(e)}")

@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un lead específico por su ID.
    
    Args:
        lead_id: ID del lead a obtener
        
    Returns:
        Información del lead solicitado
    """
    try:
        # Obtener website con sus emails
        website = db.query(Website).filter(Website.id == lead_id).first()
        if not website:
            raise HTTPException(status_code=404, detail="Lead no encontrado")
        
        # Tomar el primer email válido encontrado
        email = website.emails[0] if website.emails else None
        
        return LeadResponse(
            id=website.id,
            url=website.url,
            contact_email=email.email if email else None,
            language=website.language or "unknown",
            status=website.status,
            source_url=website.source_url
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener lead: {str(e)}")