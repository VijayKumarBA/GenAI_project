"""
constraints.py - Defines minimum room sizes, placement rules, and Vastu guidelines.
This is the rule-based engine that ensures generated plans are valid and livable.
"""

# ============================================================
# MINIMUM ROOM DIMENSIONS (in feet)
# Based on standard Indian residential building codes
# ============================================================

MIN_ROOM_SIZES = {
    "master_bedroom":   {"width": 10, "height": 12},
    "bedroom":          {"width": 9,  "height": 10},
    "bathroom":         {"width": 4,  "height": 6},
    "kitchen":          {"width": 8,  "height": 8},
    "hall":             {"width": 12, "height": 14},
    "dining":           {"width": 8,  "height": 10},
    "parking":          {"width": 9,  "height": 18},
    "staircase":        {"width": 4,  "height": 8},
    "balcony":          {"width": 4,  "height": 6},
    "corridor":         {"width": 3,  "height": 4},
    "pooja_room":       {"width": 4,  "height": 5},
    "study":            {"width": 8,  "height": 8},
    "store":            {"width": 4,  "height": 6},
    "garage":           {"width": 10, "height": 20},
}

# ============================================================
# DEFAULT ROOM SIZES (used when no specific constraint given)
# ============================================================

DEFAULT_ROOM_SIZES = {
    "master_bedroom":   {"width": 12, "height": 14},
    "bedroom":          {"width": 10, "height": 12},
    "bathroom":         {"width": 5,  "height": 7},
    "kitchen":          {"width": 10, "height": 10},
    "hall":             {"width": 14, "height": 16},
    "dining":           {"width": 10, "height": 12},
    "parking":          {"width": 10, "height": 20},
    "staircase":        {"width": 5,  "height": 10},
    "balcony":          {"width": 5,  "height": 8},
    "corridor":         {"width": 4,  "height": 6},
    "pooja_room":       {"width": 5,  "height": 6},
    "study":            {"width": 9,  "height": 10},
    "store":            {"width": 5,  "height": 7},
    "garage":           {"width": 12, "height": 22},
}

# ============================================================
# VASTU SHASTRA PLACEMENT GUIDELINES
# Preferred zones for each room based on compass direction
# ============================================================

VASTU_PREFERENCES = {
    # Room type -> list of preferred compass positions (NW, N, NE, E, SE, S, SW, W, CENTER)
    "master_bedroom":   ["SW", "S", "W"],
    "bedroom":          ["NW", "W", "S"],
    "kitchen":          ["SE", "NW"],
    "hall":             ["NE", "N", "E"],
    "bathroom":         ["NW", "W", "SE"],
    "parking":          ["NW", "SE"],
    "staircase":        ["S", "SW", "W"],
    "pooja_room":       ["NE", "N", "E"],
    "dining":           ["W", "E"],
    "study":            ["W", "NE"],
    "balcony":          ["N", "E", "NE"],
    "store":            ["NW", "SW"],
}

# ============================================================
# ENTRANCE PLACEMENT BASED ON FACING DIRECTION
# Which side of the plot the main entrance should be on
# ============================================================

ENTRANCE_PLACEMENT = {
    "north":     {"side": "top",    "position": "center"},
    "south":     {"side": "bottom", "position": "center"},
    "east":      {"side": "right",  "position": "center"},
    "west":      {"side": "left",   "position": "center"},
    "northeast": {"side": "top",    "position": "right"},
    "northwest": {"side": "top",    "position": "left"},
    "southeast": {"side": "bottom", "position": "right"},
    "southwest": {"side": "bottom", "position": "left"},
}

# ============================================================
# ADJACENCY RULES
# Rooms that should ideally be placed next to each other
# ============================================================

ADJACENCY_RULES = [
    # (room1, room2, priority)  -- higher priority = more important
    ("bathroom",       "master_bedroom", 3),
    ("bathroom",       "bedroom",        3),
    ("kitchen",        "dining",         2),
    ("kitchen",        "hall",           2),
    ("hall",           "master_bedroom", 1),
    ("parking",        "garage",         1),
    ("staircase",      "hall",           2),
    ("balcony",        "master_bedroom", 1),
    ("pooja_room",     "hall",           1),
]

# ============================================================
# ROOM COLORS (used in SVG/matplotlib visualization)
# ============================================================

ROOM_COLORS = {
    "master_bedroom":  "#FFB3BA",   # Soft pink
    "bedroom":         "#FFDFBA",   # Soft orange
    "bathroom":        "#B3ECFF",   # Light blue
    "kitchen":         "#BAFFC9",   # Light green
    "hall":            "#FFFFBA",   # Light yellow
    "dining":          "#E8BAFF",   # Light purple
    "parking":         "#D3D3D3",   # Light gray
    "staircase":       "#C4A882",   # Tan/brown
    "balcony":         "#B3FFD9",   # Mint green
    "corridor":        "#F0F0F0",   # Very light gray
    "pooja_room":      "#FFD700",   # Gold
    "study":           "#DEB887",   # Burlywood
    "store":           "#BC8F8F",   # Rosy brown
    "garage":          "#A9A9A9",   # Dark gray
    "entrance":        "#FF6B6B",   # Red for entrance marker
}

# ============================================================
# PLOT MARGIN (minimum gap between rooms and plot boundary)
# ============================================================
PLOT_MARGIN = 2  # feet

# ============================================================
# WALL THICKNESS for visualization
# ============================================================
WALL_THICKNESS = 1  # foot


def get_room_size(room_type: str, constraints: dict = None) -> dict:
    """
    Get the dimensions for a room type.
    Checks user constraints first, then defaults.
    
    Args:
        room_type: Type of room (e.g., "bedroom", "kitchen")
        constraints: User-specified constraints that may override defaults
    
    Returns:
        Dict with 'width' and 'height' in feet
    """
    # Check if user specified a size override in constraints
    if constraints and "room_sizes" in constraints:
        room_sizes = constraints["room_sizes"]
        if room_type in room_sizes:
            return room_sizes[room_type]

    # Fall back to defaults
    if room_type in DEFAULT_ROOM_SIZES:
        return DEFAULT_ROOM_SIZES[room_type].copy()

    # Generic fallback
    return {"width": 10, "height": 10}


def validate_room_size(room_type: str, width: float, height: float) -> bool:
    """
    Check if a room meets minimum size requirements.
    
    Returns:
        True if the room meets minimums, False otherwise
    """
    if room_type in MIN_ROOM_SIZES:
        min_w = MIN_ROOM_SIZES[room_type]["width"]
        min_h = MIN_ROOM_SIZES[room_type]["height"]
        return width >= min_w and height >= min_h
    return True  # Unknown room types pass validation


def get_entrance_info(facing: str) -> dict:
    """
    Get entrance placement info for a given facing direction.
    
    Args:
        facing: Direction the house faces (north, south, east, west, etc.)
    
    Returns:
        Dict with 'side' and 'position' keys
    """
    facing_lower = facing.lower().replace("-", "").replace(" ", "")
    return ENTRANCE_PLACEMENT.get(facing_lower, ENTRANCE_PLACEMENT["north"])


def get_room_color(room_type: str) -> str:
    """Get the display color for a room type."""
    return ROOM_COLORS.get(room_type, "#E0E0E0")
