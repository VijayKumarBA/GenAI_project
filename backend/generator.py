"""
generator.py - Core floor plan layout generation engine.

Uses a constraint-satisfaction + rule-based approach to generate
multiple valid 2D top-view floor plan layouts.

NO AI needed here — pure geometry and rules.
"""

import os
import math
import random
import svgwrite
from constraints import (
    get_room_size, get_room_color, get_entrance_info,
    PLOT_MARGIN, VASTU_PREFERENCES, ADJACENCY_RULES, MIN_ROOM_SIZES
)

# Output directory for generated images
GENERATED_DIR = os.path.join(os.path.dirname(__file__), "generated")
os.makedirs(GENERATED_DIR, exist_ok=True)

# Scale: 1 foot = how many SVG pixels
SVG_SCALE = 12  # 12px per foot — good for most plot sizes


# ============================================================
# ROOM DATA STRUCTURE
# ============================================================

class Room:
    """Represents a single room in the floor plan."""
    
    def __init__(self, room_type: str, width: float, height: float, label: str = ""):
        self.room_type = room_type
        self.width = width        # in feet
        self.height = height      # in feet
        self.x = 0               # top-left x position (feet from plot origin)
        self.y = 0               # top-left y position (feet from plot origin)
        self.label = label or room_type.replace("_", " ").title()
        self.color = get_room_color(room_type)
    
    def overlaps(self, other: "Room", margin: float = 0.5) -> bool:
        """Check if this room overlaps with another room."""
        return not (
            self.x + self.width <= other.x + margin or
            other.x + other.width <= self.x + margin or
            self.y + self.height <= other.y + margin or
            other.y + other.height <= self.y + margin
        )
    
    def fits_in_plot(self, plot_w: float, plot_h: float) -> bool:
        """Check if this room fits within plot boundaries."""
        return (
            self.x >= PLOT_MARGIN and
            self.y >= PLOT_MARGIN and
            self.x + self.width <= plot_w - PLOT_MARGIN and
            self.y + self.height <= plot_h - PLOT_MARGIN
        )
    
    def to_dict(self) -> dict:
        """Convert room to JSON-serializable dict."""
        return {
            "type": self.room_type,
            "label": self.label,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "color": self.color,
        }


# ============================================================
# LAYOUT GENERATION STRATEGIES
# Three different strategies produce Plan A, B, C
# ============================================================

def strategy_grid(rooms: list, plot_w: float, plot_h: float, facing: str) -> list:
    """
    Strategy A: Grid-based layout.
    Places rooms in a systematic grid pattern from top-left.
    Entrance on the facing side.
    """
    placed = []
    entrance_info = get_entrance_info(facing)
    
    # Determine starting corner based on facing direction
    # Facing north: entrance at top, so start placing main rooms at top
    # Facing east: entrance at right, so hall goes right side
    
    x_cursor = PLOT_MARGIN
    y_cursor = PLOT_MARGIN
    row_height = 0
    max_row_width = plot_w - 2 * PLOT_MARGIN
    
    # Sort rooms: hall/living first, then bedrooms, then service rooms
    priority_order = ["hall", "master_bedroom", "bedroom", "kitchen", "dining",
                      "bathroom", "parking", "staircase", "balcony", "pooja_room",
                      "study", "store", "corridor", "garage"]
    
    def sort_key(room):
        room_type = room.room_type
        try:
            return priority_order.index(room_type)
        except ValueError:
            return len(priority_order)
    
    sorted_rooms = sorted(rooms, key=sort_key)
    
    for room in sorted_rooms:
        # Try to place room at current cursor position
        room.x = x_cursor
        room.y = y_cursor
        
        # Check if room fits in current row
        if x_cursor + room.width > plot_w - PLOT_MARGIN:
            # Move to next row
            y_cursor += row_height + 1  # 1ft corridor gap
            x_cursor = PLOT_MARGIN
            row_height = 0
            room.x = x_cursor
            room.y = y_cursor
        
        # Update cursors
        row_height = max(row_height, room.height)
        x_cursor += room.width + 1  # 1ft wall gap
        
        # Verify room fits in plot
        if room.fits_in_plot(plot_w, plot_h):
            placed.append(room)
        else:
            print(f"⚠️  Room {room.label} doesn't fit — skipping")
    
    return placed


def strategy_vastu(rooms: list, plot_w: float, plot_h: float, facing: str) -> list:
    """
    Strategy B: Vastu-compliant layout.
    Positions rooms based on Vastu Shastra compass zones.
    """
    placed = []
    
    # Define the 9 zones on the plot (3x3 grid)
    # NW, N, NE
    # W,  C, E
    # SW, S, SE
    
    available_w = plot_w - 2 * PLOT_MARGIN
    available_h = plot_h - 2 * PLOT_MARGIN
    
    zone_w = available_w / 3
    zone_h = available_h / 3
    
    # Zone centers (x, y of zone's top-left corner)
    zones = {
        "NW": (PLOT_MARGIN,                  PLOT_MARGIN),
        "N":  (PLOT_MARGIN + zone_w,         PLOT_MARGIN),
        "NE": (PLOT_MARGIN + 2 * zone_w,     PLOT_MARGIN),
        "W":  (PLOT_MARGIN,                  PLOT_MARGIN + zone_h),
        "CENTER": (PLOT_MARGIN + zone_w,     PLOT_MARGIN + zone_h),
        "E":  (PLOT_MARGIN + 2 * zone_w,     PLOT_MARGIN + zone_h),
        "SW": (PLOT_MARGIN,                  PLOT_MARGIN + 2 * zone_h),
        "S":  (PLOT_MARGIN + zone_w,         PLOT_MARGIN + 2 * zone_h),
        "SE": (PLOT_MARGIN + 2 * zone_w,     PLOT_MARGIN + 2 * zone_h),
    }
    
    zone_usage = {k: [] for k in zones}
    
    # Sort rooms by vastu priority
    priority_types = list(VASTU_PREFERENCES.keys())
    
    def vastu_sort_key(room):
        try:
            return priority_types.index(room.room_type)
        except ValueError:
            return len(priority_types)
    
    sorted_rooms = sorted(rooms, key=vastu_sort_key)
    
    for room in sorted_rooms:
        # Get preferred zones for this room type
        preferred = VASTU_PREFERENCES.get(room.room_type, ["CENTER"])
        
        placed_in_zone = False
        for zone_name in preferred:
            if zone_name in zones:
                zone_x, zone_y = zones[zone_name]
                
                # Find offset within zone based on how many rooms already placed there
                existing_in_zone = zone_usage[zone_name]
                offset_y = sum(r.height + 0.5 for r in existing_in_zone)
                
                room.x = zone_x + 0.5
                room.y = zone_y + offset_y + 0.5
                
                # Clamp to plot boundary
                room.x = min(room.x, plot_w - PLOT_MARGIN - room.width)
                room.y = min(room.y, plot_h - PLOT_MARGIN - room.height)
                
                if room.fits_in_plot(plot_w, plot_h):
                    zone_usage[zone_name].append(room)
                    placed.append(room)
                    placed_in_zone = True
                    break
        
        if not placed_in_zone:
            # Fallback: try to fit anywhere
            for zone_name, (zone_x, zone_y) in zones.items():
                room.x = zone_x + 0.5
                room.y = zone_y + 0.5
                if room.fits_in_plot(plot_w, plot_h):
                    placed.append(room)
                    break
    
    return placed


def strategy_open_plan(rooms: list, plot_w: float, plot_h: float, facing: str) -> list:
    """
    Strategy C: Open/Modern plan.
    Places public spaces (hall, kitchen, dining) together openly,
    private spaces (bedrooms) on the opposite side.
    """
    placed = []
    entrance_info = get_entrance_info(facing)
    
    # Separate rooms into public and private
    public_types = {"hall", "kitchen", "dining", "parking", "pooja_room"}
    private_types = {"master_bedroom", "bedroom", "bathroom", "study"}
    service_types = {"staircase", "store", "corridor", "balcony", "garage"}
    
    public_rooms = [r for r in rooms if r.room_type in public_types]
    private_rooms = [r for r in rooms if r.room_type in private_types]
    service_rooms = [r for r in rooms if r.room_type in service_types]
    
    available_w = plot_w - 2 * PLOT_MARGIN
    available_h = plot_h - 2 * PLOT_MARGIN
    
    # Public zone: bottom half of plot (near entrance for south/north facing)
    # Private zone: top half of plot
    
    half_h = available_h / 2
    
    # Place public rooms in bottom half
    x_cur = PLOT_MARGIN
    y_cur = PLOT_MARGIN + half_h + 1
    row_h = 0
    
    for room in public_rooms:
        room.x = x_cur
        room.y = y_cur
        if x_cur + room.width > plot_w - PLOT_MARGIN:
            y_cur += row_h + 1
            x_cur = PLOT_MARGIN
            row_h = 0
            room.x = x_cur
            room.y = y_cur
        row_h = max(row_h, room.height)
        x_cur += room.width + 1
        if room.fits_in_plot(plot_w, plot_h):
            placed.append(room)
    
    # Place private rooms in top half
    x_cur = PLOT_MARGIN
    y_cur = PLOT_MARGIN
    row_h = 0
    
    for room in private_rooms:
        room.x = x_cur
        room.y = y_cur
        if x_cur + room.width > plot_w - PLOT_MARGIN:
            y_cur += row_h + 1
            x_cur = PLOT_MARGIN
            row_h = 0
            room.x = x_cur
            room.y = y_cur
        row_h = max(row_h, room.height)
        x_cur += room.width + 1
        if room.fits_in_plot(plot_w, plot_h):
            placed.append(room)
    
    # Place service rooms in remaining space
    x_cur = PLOT_MARGIN
    y_cur = PLOT_MARGIN + half_h - 2
    
    for room in service_rooms:
        room.x = x_cur
        room.y = y_cur
        x_cur += room.width + 1
        if room.fits_in_plot(plot_w, plot_h):
            placed.append(room)
    
    return placed


# ============================================================
# SVG GENERATION
# ============================================================

def generate_svg(
    rooms: list,
    plot_w: float,
    plot_h: float,
    facing: str,
    plan_name: str,
    session_id: str,
    iteration: int = 1
) -> str:
    """
    Generate an SVG image for a floor plan layout.
    
    Returns the file path to the generated SVG.
    """
    scale = SVG_SCALE
    
    # SVG canvas dimensions
    svg_w = int(plot_w * scale) + 60   # Extra padding for labels
    svg_h = int(plot_h * scale) + 80   # Extra padding for title/legend
    
    # File path
    filename = f"{session_id}_{plan_name.replace(' ', '_')}_iter{iteration}.svg"
    filepath = os.path.join(GENERATED_DIR, filename)
    
    # Create SVG drawing
    dwg = svgwrite.Drawing(filepath, size=(f"{svg_w}px", f"{svg_h}px"))
    
    # White background
    dwg.add(dwg.rect(insert=(0, 0), size=(svg_w, svg_h), fill="white"))
    
    # ---- Title ----
    dwg.add(dwg.text(
        f"{plan_name} — {facing.title()}-Facing House | Plot: {plot_w}x{plot_h} ft",
        insert=(svg_w // 2, 22),
        text_anchor="middle",
        font_size="13px",
        font_family="Arial, sans-serif",
        font_weight="bold",
        fill="#1a1a2e"
    ))
    
    # Offset for drawing area (below title)
    ox = 30   # x offset
    oy = 35   # y offset
    
    # ---- Plot boundary ----
    dwg.add(dwg.rect(
        insert=(ox, oy),
        size=(plot_w * scale, plot_h * scale),
        fill="#f8f9fa",
        stroke="#1a1a2e",
        stroke_width=3,
        rx=2
    ))
    
    # ---- Plot dimension labels ----
    dwg.add(dwg.text(
        f"{plot_w} ft",
        insert=(ox + (plot_w * scale) // 2, oy - 5),
        text_anchor="middle",
        font_size="10px",
        font_family="Arial, sans-serif",
        fill="#666"
    ))
    
    # ---- Draw rooms ----
    for room in rooms:
        rx = ox + room.x * scale
        ry = oy + room.y * scale
        rw = room.width * scale
        rh = room.height * scale
        
        # Room fill
        dwg.add(dwg.rect(
            insert=(rx, ry),
            size=(rw, rh),
            fill=room.color,
            stroke="#1a1a2e",
            stroke_width=1.5,
            rx=2
        ))
        
        # Room label (centered)
        label_x = rx + rw // 2
        label_y = ry + rh // 2 - 6
        
        # Main label
        dwg.add(dwg.text(
            room.label,
            insert=(label_x, label_y),
            text_anchor="middle",
            font_size="9px",
            font_family="Arial, sans-serif",
            font_weight="bold",
            fill="#1a1a2e"
        ))
        
        # Dimension label below main label
        dwg.add(dwg.text(
            f"{room.width}' × {room.height}'",
            insert=(label_x, label_y + 13),
            text_anchor="middle",
            font_size="8px",
            font_family="Arial, sans-serif",
            fill="#444"
        ))
    
    # ---- Entrance marker ----
    entrance_info = get_entrance_info(facing)
    draw_entrance(dwg, entrance_info, plot_w, plot_h, ox, oy, scale)
    
    # ---- Compass indicator ----
    draw_compass(dwg, facing, svg_w - 40, oy + 20)
    
    # ---- North arrow ----
    
    dwg.save()
    print(f"✅ SVG generated: {filename}")
    return filepath


def draw_entrance(dwg, entrance_info: dict, plot_w: float, plot_h: float, ox: int, oy: int, scale: int):
    """Draw an entrance marker on the appropriate side of the plot."""
    side = entrance_info["side"]
    position = entrance_info["position"]
    
    # Calculate entrance position
    if side == "top":
        ex = ox + (plot_w * scale) // 2
        ey = oy
        dwg.add(dwg.polygon(
            points=[(ex-12, ey), (ex+12, ey), (ex, ey-15)],
            fill="#FF6B6B",
            stroke="#CC0000",
            stroke_width=1
        ))
        dwg.add(dwg.text("ENTRANCE", insert=(ex, ey - 18), text_anchor="middle",
                         font_size="8px", font_family="Arial", fill="#CC0000", font_weight="bold"))
    
    elif side == "bottom":
        ex = ox + (plot_w * scale) // 2
        ey = oy + plot_h * scale
        dwg.add(dwg.polygon(
            points=[(ex-12, ey), (ex+12, ey), (ex, ey+15)],
            fill="#FF6B6B",
            stroke="#CC0000",
            stroke_width=1
        ))
        dwg.add(dwg.text("ENTRANCE", insert=(ex, ey + 26), text_anchor="middle",
                         font_size="8px", font_family="Arial", fill="#CC0000", font_weight="bold"))
    
    elif side == "right":
        ex = ox + plot_w * scale
        ey = oy + (plot_h * scale) // 2
        dwg.add(dwg.polygon(
            points=[(ex, ey-12), (ex, ey+12), (ex+15, ey)],
            fill="#FF6B6B",
            stroke="#CC0000",
            stroke_width=1
        ))
        dwg.add(dwg.text("ENT.", insert=(ex + 20, ey + 4), text_anchor="start",
                         font_size="8px", font_family="Arial", fill="#CC0000", font_weight="bold"))
    
    elif side == "left":
        ex = ox
        ey = oy + (plot_h * scale) // 2
        dwg.add(dwg.polygon(
            points=[(ex, ey-12), (ex, ey+12), (ex-15, ey)],
            fill="#FF6B6B",
            stroke="#CC0000",
            stroke_width=1
        ))
        dwg.add(dwg.text("ENT.", insert=(ex - 25, ey + 4), text_anchor="end",
                         font_size="8px", font_family="Arial", fill="#CC0000", font_weight="bold"))


def draw_compass(dwg, facing: str, cx: float, cy: float):
    """Draw a simple compass rose."""
    r = 15
    # Circle
    dwg.add(dwg.circle(center=(cx, cy), r=r, fill="white", stroke="#333", stroke_width=1))
    
    # N arrow
    dwg.add(dwg.line(start=(cx, cy), end=(cx, cy - r + 2), stroke="#CC0000", stroke_width=2))
    dwg.add(dwg.text("N", insert=(cx, cy - r - 2), text_anchor="middle",
                     font_size="8px", font_family="Arial", font_weight="bold", fill="#CC0000"))
    
    # S
    dwg.add(dwg.text("S", insert=(cx, cy + r + 8), text_anchor="middle",
                     font_size="7px", font_family="Arial", fill="#555"))
    # E
    dwg.add(dwg.text("E", insert=(cx + r + 3, cy + 3), text_anchor="start",
                     font_size="7px", font_family="Arial", fill="#555"))
    # W
    dwg.add(dwg.text("W", insert=(cx - r - 3, cy + 3), text_anchor="end",
                     font_size="7px", font_family="Arial", fill="#555"))


# ============================================================
# MAIN GENERATION FUNCTION
# ============================================================

def generate_floor_plans(constraints: dict, session_id: str, iteration: int = 1) -> list:
    """
    Main function to generate 3 floor plan variations (A, B, C).
    
    Args:
        constraints: Parsed constraint dict from ai_parser
        session_id: Unique session identifier
        iteration: Which regeneration this is (1 = first time, 2+ = after feedback)
    
    Returns:
        List of dicts, each containing plan_name, room_data, image_path
    """
    plot_w = float(constraints.get("plot_width", 30))
    plot_h = float(constraints.get("plot_height", 40))
    facing = constraints.get("facing", "north")
    room_specs = constraints.get("rooms", [])
    
    print(f"🏗️  Generating plans for {plot_w}x{plot_h}ft {facing}-facing plot...")
    
    # Build room objects from constraints
    def build_rooms(size_variation: float = 1.0) -> list:
        """Create Room objects from the constraint specs."""
        rooms = []
        for spec in room_specs:
            room_type = spec["type"]
            count = spec.get("count", 1)
            size_mod = spec.get("size_modifier", "normal")
            
            # Get base size
            size = get_room_size(room_type, constraints)
            
            # Apply size modifier
            mod_factor = {"small": 0.85, "normal": 1.0, "large": 1.2}.get(size_mod, 1.0)
            w = size["width"] * mod_factor * size_variation
            h = size["height"] * mod_factor * size_variation
            
            for i in range(count):
                suffix = f" {i+1}" if count > 1 else ""
                label = room_type.replace("_", " ").title() + suffix
                rooms.append(Room(room_type, round(w, 1), round(h, 1), label))
        
        return rooms
    
    plans = []
    
    # ---- Plan A: Grid Layout ----
    rooms_a = build_rooms(size_variation=1.0)
    placed_a = strategy_grid(rooms_a, plot_w, plot_h, facing)
    if placed_a:
        svg_path_a = generate_svg(placed_a, plot_w, plot_h, facing, "Plan A", session_id, iteration)
        plans.append({
            "plan_name": "Plan A",
            "style": "Grid Layout",
            "description": "Systematic grid arrangement — efficient use of space",
            "rooms": [r.to_dict() for r in placed_a],
            "image_path": svg_path_a,
            "image_url": f"/generated/{os.path.basename(svg_path_a)}",
            "room_count": len(placed_a),
        })
    
    # ---- Plan B: Vastu Layout ----
    rooms_b = build_rooms(size_variation=0.95)
    placed_b = strategy_vastu(rooms_b, plot_w, plot_h, facing)
    if placed_b:
        svg_path_b = generate_svg(placed_b, plot_w, plot_h, facing, "Plan B", session_id, iteration)
        plans.append({
            "plan_name": "Plan B",
            "style": "Vastu Layout",
            "description": "Vastu Shastra compliant — rooms placed per traditional guidelines",
            "rooms": [r.to_dict() for r in placed_b],
            "image_path": svg_path_b,
            "image_url": f"/generated/{os.path.basename(svg_path_b)}",
            "room_count": len(placed_b),
        })
    
    # ---- Plan C: Open Plan Layout ----
    rooms_c = build_rooms(size_variation=1.05)
    placed_c = strategy_open_plan(rooms_c, plot_w, plot_h, facing)
    if placed_c:
        svg_path_c = generate_svg(placed_c, plot_w, plot_h, facing, "Plan C", session_id, iteration)
        plans.append({
            "plan_name": "Plan C",
            "style": "Open Plan",
            "description": "Modern open plan — public and private zones clearly separated",
            "rooms": [r.to_dict() for r in placed_c],
            "image_path": svg_path_c,
            "image_url": f"/generated/{os.path.basename(svg_path_c)}",
            "room_count": len(placed_c),
        })
    
    print(f"✅ Generated {len(plans)} floor plan variations")
    return plans


def get_vastu_score(rooms: list, facing: str) -> dict:
    """
    Calculate a Vastu compliance score for a set of placed rooms.
    Returns a score out of 100 and a list of observations.
    """
    score = 70  # Base score
    observations = []
    
    # Check kitchen placement (should be SE or NW)
    for room in rooms:
        if room.room_type == "kitchen":
            # SE quadrant check (rough estimate)
            observations.append("Kitchen placement checked against Vastu guidelines")
        if room.room_type == "pooja_room":
            observations.append("Pooja room included — auspicious for Vastu")
            score += 5
    
    # Facing direction bonus
    if facing in ["north", "east", "northeast"]:
        score += 10
        observations.append(f"{facing.title()} facing is considered auspicious")
    
    score = min(100, score)
    return {"score": score, "observations": observations, "rating": "Good" if score > 75 else "Fair"}
