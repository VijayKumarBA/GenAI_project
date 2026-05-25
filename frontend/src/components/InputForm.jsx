/**
 * InputForm.jsx - The main user input form.
 * Collects plot details, room requirements, and natural language instructions.
 */

import React, { useState } from "react";

// Facing direction options
const FACING_OPTIONS = [
  { value: "north", label: "⬆ North" },
  { value: "south", label: "⬇ South" },
  { value: "east",  label: "➡ East" },
  { value: "west",  label: "⬅ West" },
  { value: "northeast", label: "↗ North East" },
  { value: "northwest", label: "↖ North West" },
  { value: "southeast", label: "↘ South East" },
  { value: "southwest", label: "↙ South West" },
];

// Example natural language prompts to inspire users
const EXAMPLE_PROMPTS = [
  "Modern 2BHK east-facing house with parking and balcony",
  "Traditional north-facing house with vastu compliance and pooja room",
  "3BHK contemporary design with open kitchen and large living area",
  "Compact 1BHK studio apartment for a single professional",
  "4BHK luxury villa with separate garage and study room",
];

/**
 * Main input form component.
 *
 * @param {Function} onGenerate - Callback when user submits form
 * @param {boolean} isLoading - Whether a generation is in progress
 */
export default function InputForm({ onGenerate, isLoading }) {
  // Form state
  const [plotWidth, setPlotWidth] = useState(30);
  const [plotHeight, setPlotHeight] = useState(40);
  const [facing, setFacing] = useState("north");
  const [bedrooms, setBedrooms] = useState(2);
  const [bathrooms, setBathrooms] = useState(2);
  const [features, setFeatures] = useState({
    kitchen: true,
    hall: true,
    parking: true,
    stairs: false,
    dining: false,
    balcony: false,
    pooja_room: false,
    study: false,
  });
  const [naturalText, setNaturalText] = useState("");
  const [promptExample, setPromptExample] = useState("");

  // Toggle a feature checkbox
  const toggleFeature = (key) => {
    setFeatures((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  // Handle example prompt selection
  const applyExample = (example) => {
    setNaturalText(example);
    setPromptExample(example);
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Build inputs object
    const inputs = {
      plot_width: parseFloat(plotWidth) || 30,
      plot_height: parseFloat(plotHeight) || 40,
      facing,
      bedrooms: parseInt(bedrooms) || 2,
      bathrooms: parseInt(bathrooms) || 2,
      kitchen: features.kitchen,
      hall: features.hall,
      parking: features.parking,
      stairs: features.stairs,
      dining: features.dining,
      balcony: features.balcony,
      pooja_room: features.pooja_room,
      study: features.study,
      natural_text: naturalText.trim(),
    };
    
    onGenerate(inputs);
  };

  // Calculate plot area
  const plotArea = (parseFloat(plotWidth) || 0) * (parseFloat(plotHeight) || 0);

  return (
    <form onSubmit={handleSubmit} className="panel" style={{ height: "fit-content" }}>
      
      {/* Panel Header */}
      <div className="panel-header">
        <span className="panel-icon">📐</span>
        <h2>House Requirements</h2>
      </div>

      <div className="panel-body">

        {/* ---- Plot Dimensions ---- */}
        <div className="form-section">
          <div className="form-section-title">
            <span>📏</span> Plot Dimensions
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Width (feet)</label>
              <input
                type="number"
                value={plotWidth}
                onChange={(e) => setPlotWidth(e.target.value)}
                min={15}
                max={200}
                step={1}
                required
              />
            </div>
            <div className="form-group">
              <label>Depth (feet)</label>
              <input
                type="number"
                value={plotHeight}
                onChange={(e) => setPlotHeight(e.target.value)}
                min={20}
                max={200}
                step={1}
                required
              />
            </div>
          </div>
          {plotArea > 0 && (
            <p style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "-4px" }}>
              📐 Plot area: <strong>{plotArea} sq.ft</strong> ({(plotArea / 9).toFixed(1)} sq.yards)
            </p>
          )}
        </div>

        {/* ---- Facing Direction ---- */}
        <div className="form-section">
          <div className="form-section-title">
            <span>🧭</span> Facing Direction
          </div>
          <div className="form-group">
            <label>House Faces Towards</label>
            <select value={facing} onChange={(e) => setFacing(e.target.value)}>
              {FACING_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* ---- Bedrooms & Bathrooms ---- */}
        <div className="form-section">
          <div className="form-section-title">
            <span>🛏️</span> Bedrooms & Bathrooms
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Bedrooms</label>
              <input
                type="number"
                value={bedrooms}
                onChange={(e) => setBedrooms(e.target.value)}
                min={0}
                max={6}
              />
            </div>
            <div className="form-group">
              <label>Bathrooms</label>
              <input
                type="number"
                value={bathrooms}
                onChange={(e) => setBathrooms(e.target.value)}
                min={1}
                max={6}
              />
            </div>
          </div>
        </div>

        {/* ---- Additional Features ---- */}
        <div className="form-section">
          <div className="form-section-title">
            <span>🏗️</span> Additional Spaces
          </div>
          <div className="checkbox-grid">
            {Object.entries({
              kitchen:    "🍳 Kitchen",
              hall:       "🛋️ Living Hall",
              parking:    "🚗 Parking",
              stairs:     "🪜 Staircase",
              dining:     "🍽️ Dining Room",
              balcony:    "🌿 Balcony",
              pooja_room: "🪔 Pooja Room",
              study:      "📚 Study Room",
            }).map(([key, label]) => (
              <label
                key={key}
                className={`checkbox-item ${features[key] ? "checked" : ""}`}
                onClick={() => toggleFeature(key)}
              >
                <input
                  type="checkbox"
                  checked={features[key]}
                  onChange={() => toggleFeature(key)}
                  onClick={(e) => e.stopPropagation()}
                />
                <span className="item-label">{label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* ---- Natural Language Input ---- */}
        <div className="form-section">
          <div className="form-section-title">
            <span>💬</span> Natural Language Instructions
          </div>
          
          {/* Example prompts */}
          <p style={{ fontSize: "12px", color: "var(--text-muted)", marginBottom: "8px" }}>
            Click an example or type your own:
          </p>
          <div className="feedback-suggestions" style={{ marginBottom: "10px" }}>
            {EXAMPLE_PROMPTS.map((ex, i) => (
              <button
                key={i}
                type="button"
                className="suggestion-chip"
                onClick={() => applyExample(ex)}
              >
                {ex.slice(0, 30)}{ex.length > 30 ? "…" : ""}
              </button>
            ))}
          </div>
          
          <div className="form-group">
            <label>Describe your dream home</label>
            <textarea
              value={naturalText}
              onChange={(e) => setNaturalText(e.target.value)}
              placeholder="e.g. I want a modern 2BHK east-facing house with parking, vastu compliance, and a large kitchen..."
              rows={3}
            />
          </div>
        </div>

        {/* ---- Submit Button ---- */}
        <button
          type="submit"
          className="btn btn-primary"
          disabled={isLoading}
          style={{ fontSize: "16px", padding: "14px" }}
        >
          {isLoading ? (
            <>
              <span style={{ fontSize: "16px" }}>⏳</span>
              Generating Plans...
            </>
          ) : (
            <>
              <span style={{ fontSize: "16px" }}>🏠</span>
              Generate Floor Plans
            </>
          )}
        </button>

        {/* Info note */}
        <p style={{
          fontSize: "11px",
          color: "var(--text-muted)",
          textAlign: "center",
          marginTop: "8px"
        }}>
          Generates 3 unique layout variations (A, B, C)
        </p>

      </div>
    </form>
  );
}
