"""
pdf_generator.py - Generates professional PDF reports for floor plans.
Uses reportlab — lightweight, no external dependencies.
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import svgwrite

# Output directory
GENERATED_DIR = os.path.join(os.path.dirname(__file__), "generated")


def convert_svg_to_png(svg_path: str) -> str:
    """
    Convert SVG to PNG for embedding in PDF.
    Uses Pillow + cairosvg if available, otherwise skips.
    Returns PNG path or None.
    """
    png_path = svg_path.replace(".svg", ".png")
    
    try:
        # Try cairosvg (best quality)
        import cairosvg
        cairosvg.svg2png(url=svg_path, write_to=png_path, scale=1.5)
        return png_path
    except ImportError:
        pass
    
    try:
        # Try matplotlib to render SVG → PNG
        import matplotlib.pyplot as plt
        import matplotlib.image as mpimg
        from PIL import Image as PILImage
        
        # Fallback: create a simple representation
        return None
    except Exception:
        return None


def generate_floor_plan_as_drawing(plan_data: dict, width: float = 400, height: float = 300) -> str:
    """
    Re-render a plan as a standalone SVG image for PDF embedding.
    Returns path to the SVG file.
    """
    from generator import generate_svg
    return plan_data.get("image_path", "")


def generate_pdf(
    session_id: str,
    constraints: dict,
    plans: list,
    user_inputs: dict
) -> str:
    """
    Generate a professional PDF containing all floor plan details.
    
    Args:
        session_id: Session identifier
        constraints: Parsed constraints dict
        plans: List of generated plan dicts
        user_inputs: Original user form inputs
    
    Returns:
        Path to the generated PDF file
    """
    # Output file path
    pdf_filename = f"{session_id}_floor_plans.pdf"
    pdf_path = os.path.join(GENERATED_DIR, pdf_filename)
    
    # Setup document
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=22,
        textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=6,
        alignment=TA_CENTER
    )
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor("#4a4a8a"),
        spaceAfter=4,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor("#1a1a2e"),
        spaceBefore=12,
        spaceAfter=6,
        borderPad=4
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor("#333333"),
        spaceAfter=4,
        leading=14
    )
    
    # Build content
    story = []
    
    # ---- Header ----
    story.append(Paragraph("🏠 AI-Generated House Floor Plans", title_style))
    
    generated_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    story.append(Paragraph(f"Generated on {generated_time}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a1a2e")))
    story.append(Spacer(1, 0.3 * cm))
    
    # ---- Project Details Section ----
    story.append(Paragraph("📋 Project Details", heading_style))
    
    plot_w = constraints.get("plot_width", "N/A")
    plot_h = constraints.get("plot_height", "N/A")
    facing = constraints.get("facing", "N/A").title()
    style = constraints.get("style", "Modern").title()
    vastu = "Yes" if constraints.get("vastu_compliant", False) else "No"
    
    # Details table
    details_data = [
        ["Plot Size", f"{plot_w} × {plot_h} feet  ({float(plot_w) * float(plot_h) if plot_w != 'N/A' else 'N/A'} sq.ft)"],
        ["Facing Direction", facing],
        ["Architectural Style", style],
        ["Vastu Compliant", vastu],
        ["Number of Plans", str(len(plans))],
        ["Session ID", session_id[:16] + "..."],
    ]
    
    details_table = Table(details_data, colWidths=[4 * cm, 10 * cm])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#eef0f8")),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor("#1a1a2e")),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor("#f8f9fc")]),
    ]))
    
    story.append(details_table)
    story.append(Spacer(1, 0.3 * cm))
    
    # ---- User Requirements ----
    natural_text = user_inputs.get("natural_text", "")
    if natural_text:
        story.append(Paragraph("💬 User Instructions", heading_style))
        story.append(Paragraph(f'"{natural_text}"', body_style))
        story.append(Spacer(1, 0.2 * cm))
    
    # ---- Rooms Summary ----
    story.append(Paragraph("🛏️ Room Requirements", heading_style))
    
    room_specs = constraints.get("rooms", [])
    if room_specs:
        room_data = [["Room Type", "Count", "Size"]]
        for spec in room_specs:
            room_data.append([
                spec["type"].replace("_", " ").title(),
                str(spec.get("count", 1)),
                spec.get("size_modifier", "normal").title()
            ])
        
        room_table = Table(room_data, colWidths=[7 * cm, 3 * cm, 4 * cm])
        room_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (1, 0), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ]))
        
        story.append(room_table)
    
    story.append(Spacer(1, 0.5 * cm))
    
    # ---- Generated Plans ----
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc")))
    story.append(Paragraph("📐 Generated Floor Plans", heading_style))
    
    for i, plan in enumerate(plans):
        plan_name = plan.get("plan_name", f"Plan {i+1}")
        plan_style = plan.get("style", "")
        description = plan.get("description", "")
        rooms = plan.get("rooms", [])
        
        # Plan header
        story.append(Paragraph(f"◉ {plan_name}: {plan_style}", heading_style))
        story.append(Paragraph(description, body_style))
        
        # Try to embed the SVG image (convert to PNG first)
        image_path = plan.get("image_path", "")
        if image_path and os.path.exists(image_path):
            try:
                png_path = convert_svg_to_png(image_path)
                if png_path and os.path.exists(png_path):
                    img = Image(png_path, width=14 * cm, height=10 * cm)
                    story.append(img)
                else:
                    story.append(Paragraph("[Floor plan image — view in web app]", body_style))
            except Exception as e:
                story.append(Paragraph(f"[Floor plan image available in web app]", body_style))
        
        # Room dimensions table
        if rooms:
            story.append(Spacer(1, 0.2 * cm))
            story.append(Paragraph("Room Dimensions:", body_style))
            
            room_dim_data = [["Room", "Width (ft)", "Height (ft)", "Area (sq.ft)"]]
            total_area = 0
            
            for room in rooms:
                w = room.get("width", 0)
                h = room.get("height", 0)
                area = w * h
                total_area += area
                room_dim_data.append([
                    room.get("label", room.get("type", "Room")),
                    f"{w:.1f}",
                    f"{h:.1f}",
                    f"{area:.1f}"
                ])
            
            room_dim_data.append(["TOTAL COVERED AREA", "", "", f"{total_area:.1f}"])
            
            dim_table = Table(room_dim_data, colWidths=[6 * cm, 3 * cm, 3 * cm, 3 * cm])
            dim_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4a4a8a")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#eef0f8")),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
                ('PADDING', (0, 0), (-1, -1), 5),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('ROWBACKGROUNDS', (1, 0), (-2, -1), [colors.white, colors.HexColor("#f5f5f5")]),
            ]))
            
            story.append(dim_table)
        
        story.append(Spacer(1, 0.5 * cm))
        
        # Page break between plans (except last)
        if i < len(plans) - 1:
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#eeeeee")))
    
    # ---- Footer ----
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a1a2e")))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph(
        "Generated by AI-Powered House Plan Generator | For planning purposes only. "
        "Consult a licensed architect before construction.",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, 
                      textColor=colors.grey, alignment=TA_CENTER)
    ))
    
    # Build PDF
    doc.build(story)
    print(f"✅ PDF generated: {pdf_filename}")
    return pdf_path
