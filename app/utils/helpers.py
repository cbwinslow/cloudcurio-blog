from typing import Optional, Dict, Any
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_json_loads(json_str: Optional[str], default: Any = None) -> Any:
    """Safely load JSON string, return default if parsing fails"""
    if not json_str:
        return default
    
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default

def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """Safely dump object to JSON string"""
    try:
        return json.dumps(obj, default=str)
    except (TypeError, ValueError):
        return default

def log_error(message: str, error: Exception, extra_data: Dict[str, Any] = None):
    """Log error with context"""
    error_data = {
        "message": message,
        "error": str(error),
        "timestamp": datetime.utcnow().isoformat()
    }
    if extra_data:
        error_data.update(extra_data)
    
    logger.error(json.dumps(error_data))

def log_info(message: str, extra_data: Dict[str, Any] = None):
    """Log info with context"""
    info_data = {
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    if extra_data:
        info_data.update(extra_data)
    
    logger.info(json.dumps(info_data))