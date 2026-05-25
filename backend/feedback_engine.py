"""
feedback_engine.py - Handles the feedback-based regeneration loop.

When users give feedback like "make kitchen bigger" or "add balcony",
this module updates the constraints and triggers regeneration.
"""

from ai_parser import parse_feedback
from database import get_session, add_feedback, update_session_constraints
from generator import generate_floor_plans


def process_feedback(session_id: str, feedback_text: str, iteration: int) -> dict:
    """
    Full feedback processing pipeline:
    1. Load current session
    2. Parse feedback with AI
    3. Update constraints
    4. Regenerate plans
    
    Args:
        session_id: The user's session ID
        feedback_text: Natural language feedback from user
        iteration: Which iteration this is (for file naming)
    
    Returns:
        Dict with updated plans and feedback summary
    """
    # Step 1: Load current session
    session = get_session(session_id)
    if not session:
        return {"error": "Session not found. Please start a new planning session."}
    
    current_constraints = session.get("constraints", {})
    
    print(f"📝 Processing feedback for session {session_id}: '{feedback_text}'")
    
    # Step 2: Parse feedback to get updated constraints
    feedback_result = parse_feedback(feedback_text, current_constraints)
    updated_constraints = feedback_result.get("constraints", current_constraints)
    summary = feedback_result.get("summary", "Layout updated based on your feedback")
    
    # Step 3: Save feedback to database
    add_feedback(session_id, feedback_text)
    update_session_constraints(session_id, updated_constraints)
    
    # Step 4: Regenerate floor plans with updated constraints
    plans = generate_floor_plans(updated_constraints, session_id, iteration)
    
    return {
        "success": True,
        "summary": summary,
        "plans": plans,
        "updated_constraints": updated_constraints,
        "iteration": iteration,
    }
