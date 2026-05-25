/**
 * FeedbackPanel.jsx - The conversational feedback panel.
 * Allows users to give natural language feedback to improve their floor plans.
 */

import React, { useState, useRef, useEffect } from "react";

// Pre-defined quick feedback suggestions
const FEEDBACK_SUGGESTIONS = [
  "Increase kitchen size",
  "Add balcony",
  "Reduce corridor area",
  "Make master bedroom larger",
  "Add dining room",
  "Move parking to front",
  "Add study room",
  "Increase bathroom size",
  "Add pooja room",
  "Make hall bigger",
  "Add second bathroom",
  "Make bedrooms smaller to save space",
];

/**
 * Feedback panel component.
 *
 * @param {Function} onFeedback - Callback with feedback text
 * @param {boolean} isLoading - Whether feedback is being processed
 * @param {Array} feedbackHistory - Previous feedback messages
 * @param {string} lastSummary - Summary of last update
 */
export default function FeedbackPanel({
  onFeedback,
  isLoading,
  feedbackHistory = [],
  lastSummary = "",
}) {
  const [feedbackText, setFeedbackText] = useState("");
  const textareaRef = useRef(null);

  // Apply a quick suggestion
  const applySuggestion = (suggestion) => {
    setFeedbackText(suggestion);
    textareaRef.current?.focus();
  };

  // Submit feedback
  const handleSubmit = () => {
    if (!feedbackText.trim() || isLoading) return;
    onFeedback(feedbackText.trim());
    setFeedbackText("");
  };

  // Handle Enter key (Shift+Enter = newline, Enter = submit)
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="feedback-panel">
      {/* Panel Header */}
      <div className="panel-header">
        <span className="panel-icon">💬</span>
        <h2>Refine Your Plans</h2>
      </div>

      <div className="panel-body">
        {/* Last update summary */}
        {lastSummary && (
          <div className="alert alert-success" style={{ marginBottom: "14px" }}>
            <span>✅</span>
            <span>{lastSummary}</span>
          </div>
        )}

        {/* Feedback history */}
        {feedbackHistory.length > 0 && (
          <div style={{ marginBottom: "14px" }}>
            <p
              style={{
                fontSize: "11px",
                fontWeight: "700",
                color: "var(--text-muted)",
                textTransform: "uppercase",
                letterSpacing: "0.06em",
                marginBottom: "8px",
              }}
            >
              Previous Feedback
            </p>
            <div className="feedback-history">
              {feedbackHistory.slice(-3).map((item, i) => (
                <div key={i} className="feedback-bubble">
                  <div className="bubble-label">You said</div>
                  {item.text || item}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Quick suggestions */}
        <p
          style={{
            fontSize: "12px",
            color: "var(--text-muted)",
            marginBottom: "8px",
          }}
        >
          Quick suggestions:
        </p>
        <div className="feedback-suggestions">
          {FEEDBACK_SUGGESTIONS.map((s, i) => (
            <button
              key={i}
              type="button"
              className="suggestion-chip"
              onClick={() => applySuggestion(s)}
            >
              {s}
            </button>
          ))}
        </div>

        {/* Feedback text input */}
        <div
          style={{
            marginTop: "12px",
            fontSize: "12px",
            color: "var(--text-muted)",
            marginBottom: "6px",
          }}
        >
          Or describe changes in your own words:
        </div>
        <div className="feedback-input-row">
          <textarea
            ref={textareaRef}
            value={feedbackText}
            onChange={(e) => setFeedbackText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder='e.g. "Make the kitchen larger and add a balcony near the master bedroom"'
            disabled={isLoading}
          />
          <button
            type="button"
            className={`btn ${isLoading ? "btn-outline" : "btn-amber"}`}
            onClick={handleSubmit}
            disabled={isLoading || !feedbackText.trim()}
            style={{ width: "auto", alignSelf: "flex-end" }}
          >
            {isLoading ? "⏳" : "🔄 Update"}
          </button>
        </div>

        <p
          style={{
            fontSize: "11px",
            color: "var(--text-muted)",
            marginTop: "6px",
            textAlign: "right",
          }}
        >
          Press Enter to submit • Shift+Enter for new line
        </p>
      </div>
    </div>
  );
}
