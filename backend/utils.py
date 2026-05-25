"""
utils.py - Utility functions used across the backend.
"""

import uuid
import os
import json
from datetime import datetime


def generate_session_id() -> str:
    """Generate a unique session ID for each user planning session."""
    return str(uuid.uuid4()).replace("-", "")[:16]


def get_timestamp() -> str:
    """Get current timestamp as ISO string."""
    return datetime.now().isoformat()


def ensure_dir(path: str):
    """Create directory if it doesn't exist."""
    os.makedirs(path, exist_ok=True)


def safe_float(value, default: float = 0.0) -> float:
    """Safely convert a value to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value, default: int = 0) -> int:
    """Safely convert a value to int."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def format_area(width: float, height: float) -> str:
    """Format room area as string."""
    area = width * height
    return f"{area:.1f} sq.ft"


def validate_plot_size(width: float, height: float) -> tuple:
    """
    Validate and clamp plot dimensions to reasonable values.
    Returns (width, height) tuple.
    """
    # Minimum plot: 15x20 feet
    # Maximum plot: 200x200 feet (practical limit for this tool)
    width = max(15, min(200, width))
    height = max(20, min(200, height))
    return width, height


def get_bhk_description(room_specs: list) -> str:
    """Convert room specs to BHK description (e.g., '2BHK', '3BHK')."""
    bedroom_count = 0
    for spec in room_specs:
        if spec.get("type") in ["master_bedroom", "bedroom"]:
            bedroom_count += spec.get("count", 1)
    
    if bedroom_count == 0:
        return "Studio"
    return f"{bedroom_count}BHK"


def estimate_construction_cost(rooms: list, quality: str = "standard") -> dict:
    """
    Rough cost estimation based on total area.
    Very approximate — for reference only.
    
    Args:
        rooms: List of room dicts with width/height
        quality: "budget", "standard", or "premium"
    
    Returns:
        Dict with total_area, cost_per_sqft, estimated_cost
    """
    total_area = sum(r.get("width", 0) * r.get("height", 0) for r in rooms)
    
    # Cost per square foot in INR (approximate 2024 rates)
    rates = {
        "budget":   1800,
        "standard": 2500,
        "premium":  3500
    }
    
    rate = rates.get(quality, 2500)
    estimated_cost = total_area * rate
    
    return {
        "total_covered_area": round(total_area, 1),
        "cost_per_sqft_inr": rate,
        "estimated_cost_inr": round(estimated_cost),
        "estimated_cost_lakhs": round(estimated_cost / 100000, 2),
        "quality_level": quality,
        "disclaimer": "Approximate estimate only. Actual costs vary by location and specifications."
    }
