from functools import wraps
import json
import asyncio
from typing import Callable, Any, Dict, Optional
from pathlib import Path

WIDGETS: Dict[str, Dict[str, Any]] = {}
TEMPLATES: Dict[str, Any] = {}


def register_widget(widget_config: Dict[str, Any]):
    """
    Decorator that registers a widget configuration in the WIDGETS dictionary.
    
    Args:
        widget_config (dict): The widget configuration following OpenBB Workspace format.
            Required fields: name, description, category, type, endpoint, gridData, source, data, params
    
    Returns:
        function: The decorated function.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
            
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        endpoint = widget_config.get("endpoint")
        if endpoint:
            if "id" not in widget_config:
                widget_config["id"] = endpoint
            WIDGETS[endpoint] = widget_config
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator


def load_templates_from_file(filepath: str = "templates.json") -> Dict[str, Any]:
    """Load templates from JSON file."""
    path = Path(filepath)
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return {}


def save_templates_to_file(templates: Dict[str, Any], filepath: str = "templates.json") -> None:
    """Save templates to JSON file."""
    with open(filepath, "w") as f:
        json.dump(templates, f, indent=2)


def get_widgets() -> Dict[str, Any]:
    """Get all registered widgets."""
    return WIDGETS


def get_widget(endpoint: str) -> Optional[Dict[str, Any]]:
    """Get a specific widget by endpoint."""
    return WIDGETS.get(endpoint)


def get_templates() -> Dict[str, Any]:
    """Get all templates."""
    return TEMPLATES


def set_templates(templates: Dict[str, Any]) -> None:
    """Set templates from external source."""
    global TEMPLATES
    TEMPLATES = templates


class WidgetResponse:
    """Standard widget response formatter."""
    
    @staticmethod
    def chart(data: Any, chart_type: str = "line") -> Dict[str, Any]:
        return {
            "type": "chart",
            "data": {"chart": {"type": chart_type, **data}} if isinstance(data, dict) else data
        }
    
    @staticmethod
    def table(data: Any, columns_defs: Optional[list] = None, show_all: bool = True) -> Dict[str, Any]:
        return {
            "type": "table",
            "data": {
                "table": {
                    "showAll": show_all,
                    "columnsDefs": columns_defs or [],
                    "data": data
                }
            }
        }
    
    @staticmethod
    def error(message: str, status_code: int = 500) -> Dict[str, Any]:
        return {
            "type": "error",
            "error": message,
            "status_code": status_code
        }


def create_base_widget_config(
    name: str,
    description: str,
    category: str,
    endpoint: str,
    widget_type: str = "chart",
    chart_type: str = "line",
    grid_w: int = 40,
    grid_h: int = 15,
    source: str = "OpenBB",
    params: Optional[list] = None,
) -> Dict[str, Any]:
    """Create a base widget configuration following OpenBB Workspace spec."""
    return {
        "name": name,
        "description": description,
        "category": category,
        "type": widget_type,
        "endpoint": endpoint,
        "gridData": {"w": grid_w, "h": grid_h},
        "source": source,
        "data": {"chart": {"type": chart_type}} if widget_type == "chart" else {"table": {"showAll": True}},
        "params": params or [],
    }