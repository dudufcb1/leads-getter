"""
Cliente API para comunicarse con el backend del sistema de generación de leads.
"""

import requests
import json
import sys
import os

# Agregar el directorio frontend al path para resolver importaciones relativas
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import FrontendConfig
from typing import Dict, Any, Optional, List, Union

class APIClient:
    """Cliente para interactuar con la API REST del backend."""
    
    def __init__(self):
        self.base_url = FrontendConfig.API_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'LeadsGenerator-Frontend/1.0'
        })
        self._app = None # Referencia a la aplicación principal
    
    def set_app(self, app):
        """Establece la referencia a la aplicación principal."""
        self._app = app
    
    def _log_error(self, message):
        """Registra un mensaje de error en la pestaña de logs de la aplicación."""
        if self._app:
            self._app.add_log_message(f"ERROR: {message}")
    
    def _make_request(self, method: str, endpoint: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Realiza una solicitud HTTP al backend.
        
        Args:
            method: Método HTTP (GET, POST, etc.)
            endpoint: Endpoint de la API
            **kwargs: Argumentos adicionales para la solicitud
            
        Returns:
            Dict con la respuesta de la API
            
        Raises:
            Exception: Si hay un error en la solicitud
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Manejar específicamente los errores 400
            if response.status_code == 400:
                try:
                    error_detail = response.json().get("detail", "Solicitud incorrecta")
                    error_msg = f"Error 400: {error_detail}"
                except:
                    error_msg = f"Error 400: Solicitud incorrecta"
                # Registrar el error en los logs si hay una referencia a la aplicación
                if hasattr(self, '_log_error'):
                    self._log_error(error_msg)
                raise Exception(error_msg)
            
            # Manejar otros errores HTTP
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # Si ya manejamos el error 400 específicamente, no lo manejamos aquí
            if isinstance(e, requests.exceptions.HTTPError) and e.response.status_code == 400:
                # El error 400 ya fue manejado arriba
                raise
            
            error_msg = f"Error en la solicitud a {url}: {str(e)}"
            # Registrar el error en los logs si hay una referencia a la aplicación
            if hasattr(self, '_log_error'):
                self._log_error(error_msg)
            raise Exception(error_msg)
        except json.JSONDecodeError as e:
            error_msg = f"Error al decodificar la respuesta JSON: {str(e)}"
            # Registrar el error en los logs si hay una referencia a la aplicación
            if hasattr(self, '_log_error'):
                self._log_error(error_msg)
            raise Exception(error_msg)
    
    def start_scraping_job(self, start_url: str, depth: int = 3, 
                          languages: Optional[List[str]] = None, delay: float = 2.0) -> Dict[str, Any]:
        """
        Inicia un nuevo trabajo de scraping.
        
        Args:
            start_url: URL inicial para el scraping
            depth: Profundidad máxima de scraping
            languages: Lista de idiomas a buscar
            delay: Delay entre requests
            
        Returns:
            Dict con la respuesta de la API
        """
        if languages is None:
            languages = FrontendConfig.DEFAULT_LANGUAGES
            
        payload = {
            "start_url": start_url,
            "depth": depth,
            "languages": languages,
            "delay": delay
        }
        
        return self._make_request("POST", "/jobs", json=payload)
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Obtiene el estado de un trabajo de scraping.
        
        Args:
            job_id: ID del trabajo
            
        Returns:
            Dict con el estado del trabajo
        """
        # Usar el nuevo endpoint con job_id en la ruta
        return self._make_request("GET", f"/jobs/{job_id}")
    
    def stop_scraping_job(self, job_id: str) -> Dict[str, Any]:
        """
        Detiene un trabajo de scraping en ejecución.
        
        Args:
            job_id: ID del trabajo a detener
            
        Returns:
            Dict con la respuesta de la API
        """
        return self._make_request("DELETE", f"/jobs/{job_id}")
    
    def get_leads(self, page: int = 1, limit: int = 50, 
                  language: Optional[str] = None, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene la lista de leads encontrados.
        
        Args:
            page: Número de página
            limit: Elementos por página
            language: Filtrar por idioma
            domain: Filtrar por dominio
            
        Returns:
            Dict con la lista de leads y paginación
        """
        params = {
            "page": page,
            "limit": limit
        }
        
        if language:
            params["language"] = language
        if domain:
            params["domain"] = domain
            
        return self._make_request("GET", "/leads", params=params)
    
    def health_check(self) -> Dict[str, Any]:
        """
        Verifica el estado de la API.
        
        Returns:
            Dict con el estado de la API
        """
        try:
            return self._make_request("GET", "/health")
        except Exception:
            return {"status": "unhealthy", "message": "No se puede conectar con la API"}
    
    def pause_job(self, job_id: str) -> Dict[str, Any]:
        """
        Pausa un job específico.
        
        Args:
            job_id: ID del job a pausar
            
        Returns:
            Dict con la respuesta de la API
        """
        return self._make_request("PUT", f"/jobs/{job_id}/pause")
    
    def resume_job(self, job_id: str) -> Dict[str, Any]:
        """
        Reanuda un job pausado.
        
        Args:
            job_id: ID del job a reanudar
            
        Returns:
            Dict con la respuesta de la API
        """
        return self._make_request("PUT", f"/jobs/{job_id}/resume")
    
    def update_job_priority(self, job_id: str, priority: int) -> Dict[str, Any]:
        """
        Actualiza la prioridad de un job.
        
        Args:
            job_id: ID del job a actualizar
            priority: Nueva prioridad (0-10)
            
        Returns:
            Dict con la respuesta de la API
        """
        payload = {"priority": priority}
        return self._make_request("PUT", f"/jobs/{job_id}/priority", json=payload)
    
    def get_queue_status(self) -> Dict[str, Any]:
        """
        Obtiene el estado de la cola de jobs.
        
        Returns:
            Dict con el estado de la cola
        """
        return self._make_request("GET", "/jobs/queue")
    
    def pause_all_jobs(self) -> Dict[str, Any]:
        """
        Pausa todos los jobs activos.
        
        Returns:
            Dict con la respuesta de la API
        """
        return self._make_request("PUT", "/jobs/pause-all")
    
    def resume_all_jobs(self) -> Dict[str, Any]:
        """
        Reanuda todos los jobs pausados.
        
        Returns:
            Dict con la respuesta de la API
        """
        return self._make_request("PUT", "/jobs/resume-all")
    
    def cancel_all_active_jobs(self) -> Dict[str, Any]:
        """
        Cancela todos los jobs activos.
        
        Returns:
            Dict con la respuesta de la API
        """
        return self._make_request("DELETE", "/jobs/active")
    
    def clear_queue(self) -> Dict[str, Any]:
        """
        Limpia la cola de jobs pendientes.
        
        Returns:
            Dict con la respuesta de la API
        """
        return self._make_request("PUT", "/jobs/queue/clear")
    
    def reorder_queue(self, items: List[Dict[str, Union[str, int]]]) -> Dict[str, Any]:
        """
        Reordena los jobs en la cola.
        
        Args:
            items: Lista de items con job_id y nueva prioridad
            
        Returns:
            Dict con la respuesta de la API
        """
        payload = {"items": items}
        return self._make_request("PUT", "/jobs/queue/reorder", json=payload)
    
    def get_job_progress(self, job_id: str) -> Dict[str, Any]:
        """
        Obtiene el progreso detallado de un job.
        
        Args:
            job_id: ID del job
            
        Returns:
            Dict con el progreso del job
        """
        return self._make_request("GET", f"/jobs/{job_id}/progress")
    
    def get_job_logs(self, job_id: str) -> Dict[str, Any]:
        """
        Obtiene los logs específicos de un job.
        
        Args:
            job_id: ID del job
            
        Returns:
            Dict con los logs del job
        """
        return self._make_request("GET", f"/jobs/{job_id}/logs")