"""
app.py - Main Flask backend for the AI House Plan Generator.

REST API endpoints:
  POST /api/generate      - Generate floor plans from user inputs
  POST /api/feedback      - Process feedback and regenerate
  GET  /api/session/:id   - Get session data
  GET  /api/download/:id  - Download PDF
  GET  /generated/:file   - Serve generated SVG/PNG files

Run: python app.py
"""

import os
import json
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Internal modules
from database import init_db, save_session, save_plan, get_session
from ai_parser import parse_user_requirements
from generator import generate_floor_plans, get_vastu_score
from pdf_generator import generate_pdf
from feedback_engine import process_feedback
from utils import generate_session_id, validate_plot_size, get_bhk_description, estimate_construction_cost

# ============================================================
# FLASK APP SETUP
# ============================================================

app = Flask(__name__)

# Allow requests from React frontend (port 3000)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

# Path to generated files
GENERATED_DIR = os.path.join(os.path.dirname(__file__), "generated")
os.makedirs(GENERATED_DIR, exist_ok=True)

# Initialize database on startup
init_db()

print("🏠 AI House Plan Generator Backend Started")
print(f"   AI Provider: {os.getenv('AI_PROVIDER', 'gemini').upper()}")
print(f"   Gemini Key: {'✅ Set' if os.getenv('GEMINI_API_KEY') else '❌ Not set (using rule-based fallback)'}")
print(f"   OpenAI Key: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not set'}")


# ============================================================
# HEALTH CHECK
# ============================================================

@app.route("/api/health", methods=["GET"])
def health_check():
    """Simple health check endpoint."""
    return jsonify({
        "status": "ok",
        "message": "AI House Plan Generator is running!",
        "ai_provider": os.getenv("AI_PROVIDER", "gemini"),
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
    })


# ============================================================
# GENERATE FLOOR PLANS
# ============================================================

@app.route("/api/generate", methods=["POST"])
def generate():
    """
    Generate floor plans from user inputs.
    
    Request body (JSON):
    {
        "plot_width": 30,
        "plot_height": 40,
        "facing": "north",
        "bedrooms": 2,
        "bathrooms": 2,
        "kitchen": true,
        "hall": true,
        "parking": true,
        "stairs": false,
        "natural_text": "I want a modern house with vastu compliance"
    }
    
    Response:
    {
        "session_id": "abc123...",
        "plans": [...],
        "constraints": {...},
        "bhk": "2BHK",
        "vastu_score": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No input data provided"}), 400
        
        # Validate required fields
        plot_w = float(data.get("plot_width", 30))
        plot_h = float(data.get("plot_height", 40))
        plot_w, plot_h = validate_plot_size(plot_w, plot_h)
        
        # Normalize inputs
        user_inputs = {
            "plot_width": plot_w,
            "plot_height": plot_h,
            "facing": data.get("facing", "north").lower(),
            "bedrooms": max(0, min(6, int(data.get("bedrooms", 2)))),
            "bathrooms": max(1, min(6, int(data.get("bathrooms", 2)))),
            "kitchen": bool(data.get("kitchen", True)),
            "hall": bool(data.get("hall", True)),
            "parking": bool(data.get("parking", True)),
            "stairs": bool(data.get("stairs", False)),
            "natural_text": str(data.get("natural_text", "")).strip(),
        }
        
        print(f"\n📥 New generation request:")
        print(f"   Plot: {plot_w}x{plot_h}ft | Facing: {user_inputs['facing']}")
        print(f"   Bedrooms: {user_inputs['bedrooms']} | Bathrooms: {user_inputs['bathrooms']}")
        print(f"   Natural text: {user_inputs['natural_text'][:50] if user_inputs['natural_text'] else 'None'}")
        
        # Generate unique session ID
        session_id = generate_session_id()
        
        # Step 1: Parse user requirements with AI
        constraints = parse_user_requirements(user_inputs)
        
        # Step 2: Save session to database
        save_session(session_id, user_inputs, constraints)
        
        # Step 3: Generate floor plans
        plans = generate_floor_plans(constraints, session_id, iteration=1)
        
        if not plans:
            return jsonify({"error": "Failed to generate floor plans. Plot may be too small."}), 422
        
        # Step 4: Save plans to database
        for plan in plans:
            save_plan(session_id, plan["plan_name"], plan, plan.get("image_path", ""), iteration=1)
        
        # Step 5: Calculate BHK and Vastu score for first plan
        bhk = get_bhk_description(constraints.get("rooms", []))
        vastu = get_vastu_score([], constraints.get("facing", "north"))
        
        # Step 6: Cost estimation
        cost = None
        if plans:
            cost = estimate_construction_cost(plans[0].get("rooms", []))
        
        # Return response (don't include full image_path in response, use image_url)
        plans_response = []
        for p in plans:
            plans_response.append({
                "plan_name": p["plan_name"],
                "style": p["style"],
                "description": p["description"],
                "rooms": p["rooms"],
                "image_url": p["image_url"],
                "room_count": p["room_count"],
            })
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "plans": plans_response,
            "constraints": constraints,
            "bhk": bhk,
            "vastu_score": vastu,
            "cost_estimate": cost,
            "iteration": 1,
        })
    
    except ValueError as e:
        return jsonify({"error": f"Invalid input: {str(e)}"}), 400
    except Exception as e:
        print(f"❌ Generation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Generation failed: {str(e)}"}), 500


# ============================================================
# PROCESS FEEDBACK & REGENERATE
# ============================================================

@app.route("/api/feedback", methods=["POST"])
def feedback():
    """
    Process user feedback and regenerate improved plans.
    
    Request body (JSON):
    {
        "session_id": "abc123...",
        "feedback": "Increase kitchen size and add balcony",
        "iteration": 2
    }
    
    Response:
    {
        "success": true,
        "summary": "Kitchen enlarged, balcony added",
        "plans": [...],
        "iteration": 2
    }
    """
    try:
        data = request.get_json()
        
        session_id = data.get("session_id", "")
        feedback_text = data.get("feedback", "").strip()
        iteration = int(data.get("iteration", 2))
        
        if not session_id:
            return jsonify({"error": "session_id is required"}), 400
        
        if not feedback_text:
            return jsonify({"error": "feedback text is required"}), 400
        
        print(f"\n🔄 Feedback received for session {session_id}:")
        print(f"   Feedback: {feedback_text}")
        print(f"   Iteration: {iteration}")
        
        result = process_feedback(session_id, feedback_text, iteration)
        
        if "error" in result:
            return jsonify(result), 404
        
        # Clean response (remove internal file paths)
        plans_response = []
        for p in result.get("plans", []):
            plans_response.append({
                "plan_name": p["plan_name"],
                "style": p["style"],
                "description": p["description"],
                "rooms": p["rooms"],
                "image_url": p["image_url"],
                "room_count": p["room_count"],
            })
        
        return jsonify({
            "success": True,
            "summary": result["summary"],
            "plans": plans_response,
            "updated_constraints": result["updated_constraints"],
            "iteration": iteration,
        })
    
    except Exception as e:
        print(f"❌ Feedback error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Feedback processing failed: {str(e)}"}), 500


# ============================================================
# GET SESSION DATA
# ============================================================

@app.route("/api/session/<session_id>", methods=["GET"])
def get_session_data(session_id):
    """Get stored session data by session ID."""
    session = get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(session)


# ============================================================
# DOWNLOAD PDF
# ============================================================

@app.route("/api/download-pdf", methods=["POST"])
def download_pdf():
    """
    Generate and download a PDF of the floor plans.
    
    Request body (JSON):
    {
        "session_id": "abc123...",
        "plans": [...],  -- current plans data
        "constraints": {...}
    }
    """
    try:
        data = request.get_json()
        session_id = data.get("session_id", "")
        plans = data.get("plans", [])
        constraints = data.get("constraints", {})
        
        if not session_id:
            return jsonify({"error": "session_id required"}), 400
        
        # Get user inputs from session
        session = get_session(session_id)
        user_inputs = session.get("user_inputs", {}) if session else {}
        
        # Add image paths back (plans from frontend don't have them)
        # Reconstruct image paths
        for plan in plans:
            plan_name = plan.get("plan_name", "").replace(" ", "_")
            # Try to find latest image file
            import glob
            pattern = os.path.join(GENERATED_DIR, f"{session_id}_{plan_name}_*.svg")
            files = sorted(glob.glob(pattern))
            if files:
                plan["image_path"] = files[-1]  # Latest file
        
        print(f"📄 Generating PDF for session {session_id}")
        pdf_path = generate_pdf(session_id, constraints, plans, user_inputs)
        
        # Send file as download
        return send_file(
            pdf_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"house_plans_{session_id[:8]}.pdf"
        )
    
    except Exception as e:
        print(f"❌ PDF generation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"PDF generation failed: {str(e)}"}), 500


# ============================================================
# SERVE GENERATED IMAGES
# ============================================================

@app.route("/generated/<filename>")
def serve_generated_file(filename):
    """Serve generated SVG, PNG, or PDF files."""
    try:
        return send_from_directory(GENERATED_DIR, filename)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404


# ============================================================
# RUN THE APP
# ============================================================

if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    
    print(f"\n🚀 Starting Flask server on http://localhost:{port}")
    print("   Press CTRL+C to stop\n")
    
    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug
    )
