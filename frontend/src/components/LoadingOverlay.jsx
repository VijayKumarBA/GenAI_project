/**
 * LoadingOverlay.jsx - Full-screen loading indicator.
 * Shown while the backend is generating floor plans.
 */

import React from "react";

const LOADING_MESSAGES = [
  "Analyzing your requirements...",
  "Consulting the AI architect...",
  "Calculating room placements...",
  "Applying Vastu guidelines...",
  "Drawing floor plan variations...",
  "Almost ready...",
];

export default function LoadingOverlay({ message = null }) {
  // Cycle through messages
  const [msgIndex, setMsgIndex] = React.useState(0);

  React.useEffect(() => {
    const interval = setInterval(() => {
      setMsgIndex((i) => (i + 1) % LOADING_MESSAGES.length);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const displayMessage = message || LOADING_MESSAGES[msgIndex];

  return (
    <div className="loading-overlay">
      <div className="loading-card">
        {/* Animated house icon */}
        <div
          style={{
            fontSize: "42px",
            marginBottom: "12px",
            animation: "float 2s ease-in-out infinite",
          }}
        >
          🏗️
        </div>
        
        <div className="loading-spinner" />
        
        <div className="loading-title">Generating Floor Plans</div>
        <div className="loading-message">{displayMessage}</div>

        <p
          style={{
            fontSize: "11px",
            color: "#aaa",
            marginTop: "12px",
          }}
        >
          This may take 10–30 seconds
        </p>
      </div>

      {/* Float animation */}
      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-8px); }
        }
      `}</style>
    </div>
  );
}
