"""
ai_parser.py - Handles AI integration using Gemini or OpenAI.

This module converts natural language input into structured constraints
that the layout generator can use to create floor plans.
"""

import os
import json
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Determine which AI provider to use
AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ============================================================
# SYSTEM PROMPT - Tells the AI exactly what to output
# ============================================================

SYSTEM_PROMPT = """You are an expert house architect AI assistant. 
Your job is to parse user requirements for a house floor plan and return a structured JSON object.

ALWAYS respond with ONLY a valid JSON object — no markdown, no explanation, no extra text.

The JSON must follow this exact structure:
{
  "plot_width": <number in feet>,
  "plot_height": <number in feet>,
  "facing": "<north|south|east|west|northeast|northwest|southeast|southwest>",
  "rooms": [
    {"type": "<room_type>", "count": <number>, "size_modifier": "<small|normal|large>"}
  ],
  "special_instructions": ["<instruction1>", "<instruction2>"],
  "style": "<modern|traditional|contemporary|minimalist>",
  "vastu_compliant": <true|false>,
  "parking": <true|false>,
  "floors": <1|2>
}

Valid room types: master_bedroom, bedroom, bathroom, kitchen, hall, dining, parking, staircase, balcony, corridor, pooja_room, study, store, garage

Rules:
- plot_width and plot_height should be in feet
- If user says "30x40", width=30, height=40
- If user says "2BHK", add master_bedroom(count:1) + bedroom(count:1) + bathroom(count:2) + kitchen(count:1) + hall(count:1)
- If user says "3BHK", add master_bedroom(count:1) + bedroom(count:2) + bathroom(count:2) + kitchen(count:1) + hall(count:1)
- Always include at least: hall, kitchen, bathroom
- "east-facing" means facing: "east"
- If floor count > 1, add staircase room
"""

FEEDBACK_SYSTEM_PROMPT = """You are an expert house architect AI assistant.
The user has provided feedback on their existing floor plan. 
Parse their feedback and return ONLY a JSON object with constraint updates.

ALWAYS respond with ONLY a valid JSON object — no markdown, no explanation.

Return this structure:
{
  "updates": {
    "room_size_changes": {"<room_type>": "<larger|smaller|normal>"},
    "add_rooms": [{"type": "<room_type>", "count": <number>}],
    "remove_rooms": ["<room_type>"],
    "move_rooms": {"<room_type>": "<preferred_zone>"},
    "special_instructions": ["<new instruction>"]
  },
  "summary": "<one sentence summary of what changed>"
}
"""


# ============================================================
# GEMINI INTEGRATION
# ============================================================

def parse_with_gemini(prompt: str, system_prompt: str) -> str:
    """Send a prompt to Gemini API and return the response text."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Use gemini-1.5-flash for speed and cost efficiency
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_prompt
        )
        
        response = model.generate_content(prompt)
        return response.text.strip()
    
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        raise e


# ============================================================
# OPENAI INTEGRATION
# ============================================================

def parse_with_openai(prompt: str, system_prompt: str) -> str:
    """Send a prompt to OpenAI API and return the response text."""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use GPT-3.5 for cost efficiency
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3  # Low temperature for more structured output
        )
        return response.choices[0].message.content.strip()
    
    except Exception as e:
        print(f"❌ OpenAI API error: {e}")
        raise e


# ============================================================
# RULE-BASED FALLBACK PARSER
# Used when AI API is not available or fails
# ============================================================

def parse_with_rules(user_inputs: dict) -> dict:
    """
    Fallback rule-based parser that doesn't need any AI API.
    Parses structured form inputs to create constraints.
    """
    print("⚠️  Using rule-based fallback parser (no AI API)")
    
    # Extract inputs
    plot_width = float(user_inputs.get("plot_width", 30))
    plot_height = float(user_inputs.get("plot_height", 40))
    facing = user_inputs.get("facing", "north").lower()
    bedrooms = int(user_inputs.get("bedrooms", 2))
    bathrooms = int(user_inputs.get("bathrooms", 2))
    has_parking = user_inputs.get("parking", True)
    has_stairs = user_inputs.get("stairs", False)
    natural_text = user_inputs.get("natural_text", "").lower()
    
    # Build rooms list
    rooms = []
    
    # Add bedrooms
    if bedrooms >= 1:
        rooms.append({"type": "master_bedroom", "count": 1, "size_modifier": "normal"})
    if bedrooms >= 2:
        rooms.append({"type": "bedroom", "count": bedrooms - 1, "size_modifier": "normal"})
    
    # Always add basic rooms
    rooms.append({"type": "hall", "count": 1, "size_modifier": "normal"})
    rooms.append({"type": "kitchen", "count": 1, "size_modifier": "normal"})
    rooms.append({"type": "bathroom", "count": bathrooms, "size_modifier": "normal"})
    
    # Optional rooms
    if has_parking:
        rooms.append({"type": "parking", "count": 1, "size_modifier": "normal"})
    
    if has_stairs or bedrooms > 2:
        rooms.append({"type": "staircase", "count": 1, "size_modifier": "normal"})
    
    # Parse natural text for additional rooms
    if "dining" in natural_text or "dining room" in natural_text:
        rooms.append({"type": "dining", "count": 1, "size_modifier": "normal"})
    
    if "balcony" in natural_text:
        rooms.append({"type": "balcony", "count": 1, "size_modifier": "normal"})
    
    if "pooja" in natural_text or "puja" in natural_text or "prayer" in natural_text:
        rooms.append({"type": "pooja_room", "count": 1, "size_modifier": "small"})
    
    if "study" in natural_text or "office" in natural_text:
        rooms.append({"type": "study", "count": 1, "size_modifier": "normal"})
    
    # Parse style from natural text
    style = "modern"
    if "traditional" in natural_text:
        style = "traditional"
    elif "contemporary" in natural_text:
        style = "contemporary"
    elif "minimalist" in natural_text:
        style = "minimalist"
    
    # Parse vastu preference
    vastu = "vastu" in natural_text
    
    return {
        "plot_width": plot_width,
        "plot_height": plot_height,
        "facing": facing,
        "rooms": rooms,
        "special_instructions": [],
        "style": style,
        "vastu_compliant": vastu,
        "parking": has_parking,
        "floors": 1
    }


# ============================================================
# MAIN PARSING FUNCTION
# ============================================================

def clean_json_response(text: str) -> str:
    """Remove markdown code blocks from AI response if present."""
    # Remove ```json ... ``` wrapper
    text = re.sub(r'^```(?:json)?\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\s*```$', '', text, flags=re.MULTILINE)
    return text.strip()


def parse_user_requirements(user_inputs: dict) -> dict:
    """
    Main function to parse user inputs into structured constraints.
    
    Tries AI parsing first, falls back to rule-based parsing if AI fails.
    
    Args:
        user_inputs: Dict containing form inputs and natural language text
    
    Returns:
        Dict containing structured constraints for the layout generator
    """
    # Build a comprehensive prompt from user inputs
    natural_text = user_inputs.get("natural_text", "")
    
    prompt = f"""
Parse the following house plan requirements:

Plot Size: {user_inputs.get('plot_width', 30)} x {user_inputs.get('plot_height', 40)} feet
Facing Direction: {user_inputs.get('facing', 'north')}
Bedrooms: {user_inputs.get('bedrooms', 2)}
Bathrooms: {user_inputs.get('bathrooms', 2)}
Kitchen: {user_inputs.get('kitchen', True)}
Hall/Living Room: {user_inputs.get('hall', True)}
Parking: {user_inputs.get('parking', True)}
Stairs: {user_inputs.get('stairs', False)}

Additional Instructions: {natural_text if natural_text else 'None'}

Generate the structured JSON for this house plan.
"""
    
    # Try AI parsing
    try:
        if AI_PROVIDER == "gemini" and GEMINI_API_KEY:
            raw_response = parse_with_gemini(prompt, SYSTEM_PROMPT)
        elif AI_PROVIDER == "openai" and OPENAI_API_KEY:
            raw_response = parse_with_openai(prompt, SYSTEM_PROMPT)
        else:
            # No API key configured, use rule-based fallback
            return parse_with_rules(user_inputs)
        
        # Clean and parse the JSON response
        clean_response = clean_json_response(raw_response)
        constraints = json.loads(clean_response)
        print(f"✅ AI parsing successful: {constraints.get('facing')} facing, {len(constraints.get('rooms', []))} room types")
        return constraints
    
    except json.JSONDecodeError as e:
        print(f"⚠️  JSON parsing failed: {e}. Using rule-based fallback.")
        return parse_with_rules(user_inputs)
    
    except Exception as e:
        print(f"⚠️  AI parsing failed: {e}. Using rule-based fallback.")
        return parse_with_rules(user_inputs)


def parse_feedback(feedback_text: str, current_constraints: dict) -> dict:
    """
    Parse user feedback to update existing constraints.
    
    Args:
        feedback_text: Natural language feedback from user
        current_constraints: The current constraint set to update
    
    Returns:
        Dict with 'updates' and updated 'constraints'
    """
    prompt = f"""
The user has given feedback on their floor plan.

Current constraints summary:
- Plot: {current_constraints.get('plot_width')}x{current_constraints.get('plot_height')} feet
- Facing: {current_constraints.get('facing')}
- Rooms: {[r['type'] for r in current_constraints.get('rooms', [])]}

User Feedback: "{feedback_text}"

Parse this feedback and return the JSON update object.
"""
    
    try:
        if AI_PROVIDER == "gemini" and GEMINI_API_KEY:
            raw_response = parse_with_gemini(prompt, FEEDBACK_SYSTEM_PROMPT)
        elif AI_PROVIDER == "openai" and OPENAI_API_KEY:
            raw_response = parse_with_openai(prompt, FEEDBACK_SYSTEM_PROMPT)
        else:
            return parse_feedback_with_rules(feedback_text, current_constraints)
        
        clean_response = clean_json_response(raw_response)
        feedback_data = json.loads(clean_response)
        
        # Apply updates to current constraints
        updated_constraints = apply_feedback_updates(current_constraints, feedback_data.get("updates", {}))
        
        return {
            "updates": feedback_data.get("updates", {}),
            "summary": feedback_data.get("summary", "Layout updated based on feedback"),
            "constraints": updated_constraints
        }
    
    except Exception as e:
        print(f"⚠️  Feedback parsing failed: {e}. Using rule-based fallback.")
        return parse_feedback_with_rules(feedback_text, current_constraints)


def parse_feedback_with_rules(feedback: str, constraints: dict) -> dict:
    """Rule-based feedback parser fallback."""
    feedback_lower = feedback.lower()
    updates = {"room_size_changes": {}, "add_rooms": [], "remove_rooms": [], "special_instructions": []}
    
    # Detect size increase keywords
    increase_words = ["increase", "larger", "bigger", "more space", "expand"]
    decrease_words = ["decrease", "smaller", "reduce", "less space", "shrink"]
    
    # Check each room type
    room_keywords = {
        "kitchen": ["kitchen"],
        "master_bedroom": ["master bedroom", "master"],
        "bedroom": ["bedroom", "room"],
        "bathroom": ["bathroom", "toilet", "washroom"],
        "hall": ["hall", "living room", "living"],
        "parking": ["parking", "car"],
        "staircase": ["stairs", "staircase"],
        "balcony": ["balcony"],
        "dining": ["dining"],
    }
    
    for room_type, keywords in room_keywords.items():
        for keyword in keywords:
            if keyword in feedback_lower:
                for word in increase_words:
                    if word in feedback_lower:
                        updates["room_size_changes"][room_type] = "larger"
                for word in decrease_words:
                    if word in feedback_lower:
                        updates["room_size_changes"][room_type] = "smaller"
    
    # Detect "add" keywords
    if "add parking" in feedback_lower:
        updates["add_rooms"].append({"type": "parking", "count": 1})
    if "add balcony" in feedback_lower:
        updates["add_rooms"].append({"type": "balcony", "count": 1})
    if "add dining" in feedback_lower or "add dining room" in feedback_lower:
        updates["add_rooms"].append({"type": "dining", "count": 1})
    if "add study" in feedback_lower or "add office" in feedback_lower:
        updates["add_rooms"].append({"type": "study", "count": 1})
    
    # Apply updates
    updated_constraints = apply_feedback_updates(constraints, updates)
    
    return {
        "updates": updates,
        "summary": "Layout updated based on your feedback",
        "constraints": updated_constraints
    }


def apply_feedback_updates(constraints: dict, updates: dict) -> dict:
    """Apply parsed feedback updates to the existing constraint set."""
    import copy
    updated = copy.deepcopy(constraints)
    
    # Ensure room_sizes dict exists in constraints
    if "room_sizes" not in updated:
        updated["room_sizes"] = {}
    
    # Apply room size changes
    size_changes = updates.get("room_size_changes", {})
    for room_type, size in size_changes.items():
        from constraints import DEFAULT_ROOM_SIZES
        if room_type in DEFAULT_ROOM_SIZES:
            base_size = DEFAULT_ROOM_SIZES[room_type].copy()
            if size == "larger":
                base_size["width"] = int(base_size["width"] * 1.25)
                base_size["height"] = int(base_size["height"] * 1.25)
            elif size == "smaller":
                base_size["width"] = int(base_size["width"] * 0.8)
                base_size["height"] = int(base_size["height"] * 0.8)
            updated["room_sizes"][room_type] = base_size
    
    # Add new rooms
    for new_room in updates.get("add_rooms", []):
        # Check if room type already exists
        existing_types = [r["type"] for r in updated.get("rooms", [])]
        if new_room["type"] not in existing_types:
            updated.setdefault("rooms", []).append({
                "type": new_room["type"],
                "count": new_room.get("count", 1),
                "size_modifier": "normal"
            })
    
    # Remove rooms
    for remove_type in updates.get("remove_rooms", []):
        updated["rooms"] = [r for r in updated.get("rooms", []) if r["type"] != remove_type]
    
    # Add special instructions
    existing_instructions = updated.get("special_instructions", [])
    new_instructions = updates.get("special_instructions", [])
    updated["special_instructions"] = existing_instructions + new_instructions
    
    return updated
