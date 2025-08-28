"""
Sistema de caching para mejorar el rendimiento de las consultas.
"""

import time
from typing import Any, Dict, Optional
from functools import wraps

class Cache:
    """Clase para manejar el caching de datos."""
    
    def __init__(self, default_ttl: int = 300):
        """
        Inicializa el sistema de caching.
        
        Args:
            default_ttl: Tiempo de vida por defecto en segundos (5 minutos)
        """
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Guarda un valor en el cache.
        
        Args:
            key: Clave para identificar el valor
            value: Valor a guardar
            ttl: Tiempo de vida en segundos (opcional)
        """
        if ttl is None:
            ttl = self.default_ttl
            
        self._cache[key] = {
            'value': value,
            'expires_at': time.time() + ttl
        }
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene un valor del cache.
        
        Args:
            key: Clave del valor a obtener
            
        Returns:
            Valor del cache o None si no existe o ha expirado
        """
        if key not in self._cache:
            return None
            
        cache_entry = self._cache[key]
        
        # Verificar si ha expirado
        if time.time() > cache_entry['expires_at']:
            # Eliminar entrada expirada
            del self._cache[key]
            return None
            
        return cache_entry['value']
    
    def delete(self, key: str) -> bool:
        """
        Elimina un valor del cache.
        
        Args:
            key: Clave del valor a eliminar
            
        Returns:
            True si se eliminó, False si no existía
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Limpia todo el cache."""
        self._cache.clear()
    
    def cleanup(self) -> int:
        """
        Limpia las entradas expiradas del cache.
        
        Returns:
            Número de entradas eliminadas
        """
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time > entry['expires_at']
        ]
        
        for key in expired_keys:
            del self._cache[key]
            
        return len(expired_keys)
    
    def size(self) -> int:
        """Devuelve el número de entradas en el cache."""
        return len(self._cache)

# Instancia global del cache
cache = Cache()

def cached(ttl: Optional[int] = None):
    """
    Decorador para cachear resultados de funciones.
    
    Args:
        ttl: Tiempo de vida en segundos (opcional)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Crear clave única basada en nombre de función y argumentos
            key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Intentar obtener del cache
            cached_value = cache.get(key)
            if cached_value is not None:
                return cached_value
            
            # Ejecutar función y guardar resultado en cache
            result = func(*args, **kwargs)
            cache.set(key, result, ttl)
            return result
        return wrapper
    return decorator

# Funciones auxiliares para operaciones comunes de cache
def get_cached_stats(stats_type: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene estadísticas del cache.
    
    Args:
        stats_type: Tipo de estadísticas a obtener
        
    Returns:
        Estadísticas en caché o None si no existen
    """
    key = f"stats:{stats_type}"
    return cache.get(key)

def set_cached_stats(stats_type: str, stats: Dict[str, Any], ttl: Optional[int] = None) -> None:
    """
    Guarda estadísticas en el cache.
    
    Args:
        stats_type: Tipo de estadísticas
        stats: Estadísticas a guardar
        ttl: Tiempo de vida en segundos (opcional)
    """
    key = f"stats:{stats_type}"
    cache.set(key, stats, ttl)

def invalidate_stats_cache(stats_type: str) -> bool:
    """
    Invalida las estadísticas en caché.
    
    Args:
        stats_type: Tipo de estadísticas a invalidar
        
    Returns:
        True si se invalidó, False si no existía
    """
    key = f"stats:{stats_type}"
    return cache.delete(key)

def get_cache_info() -> Dict[str, Any]:
    """
    Obtiene información sobre el estado del cache.
    
    Returns:
        Información del cache
    """
    return {
        "size": cache.size(),
        "default_ttl": cache.default_ttl
    }