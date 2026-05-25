/**
 * PlanCard.jsx - Displays a single generated floor plan.
 * Shows the SVG image, room table, and plan metadata.
 */

import React, { useState } from "react";
import { getImageUrl } from "../api";

// Room colors for the legend (must match backend constraints.py)
const ROOM_COLORS = {
  master_bedroom: "#FFB3BA",
  bedroom:        "#FFDFBA",
  bathroom:       "#B3ECFF",
  kitchen:        "#BAFFC9",
  hall:           "#FFFFBA",
  dining:         "#E8BAFF",
  parking:        "#D3D3D3",
  staircase:      "#C4A882",
  balcony:        "#B3FFD9",
  corridor:       "#F0F0F0",
  pooja_room:     "#FFD700",
  study:          "#DEB887",
  store:          "#BC8F8F",
  garage:         "#A9A9A9",
};

/**
 * Individual plan card component.
 *
 * @param {Object} plan - The plan data including rooms and image_url
 * @param {number} index - 0-based index (for animation delay)
 */
export default function PlanCard({ plan, index }) {
  const [showTable, setShowTable] = useState(false);
  const [imgError, setImgError] = useState(false);

  const imageUrl = getImageUrl(plan.image_url);

  // Calculate total covered area
  const totalArea = plan.rooms
    ? plan.rooms.reduce((sum, r) => sum + (r.width || 0) * (r.height || 0), 0)
    : 0;

  // Color badge for each plan
  const planColors = {
    "Plan A": "#2a4a6b",
    "Plan B": "#4caf82",
    "Plan C": "#c4853a",
  };
  const planColor = planColors[plan.plan_name] || "#1a1a2e";

  return (
    <div
      className={`plan-card fade-in-up fade-in-up-delay-${index + 1}`}
      style={{ borderTop: `4px solid ${planColor}` }}
    >
      {/* Card Header */}
      <div className="plan-card-header">
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <div
            className="plan-badge"
            style={{ background: planColor }}
          >
            {plan.plan_name}
          </div>
          <div className="plan-style-badge">{plan.style}</div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
          <span style={{ fontSize: "12px", color: "var(--text-muted)" }}>
            {plan.room_count} rooms · {totalArea.toFixed(0)} sq.ft
          </span>
        </div>
      </div>

      {/* Description */}
      <p className="plan-description">{plan.description}</p>

      {/* Floor Plan Image */}
      <div className="plan-image-container">
        {!imgError ? (
          <img
            src={imageUrl}
            alt={`${plan.plan_name} floor plan`}
            onError={() => setImgError(true)}
            style={{
              width: "100%",
              height: "auto",
              maxHeight: "450px",
              objectFit: "contain",
              borderRadius: "6px",
              border: "1px solid var(--border)",
              background: "white",
            }}
          />
        ) : (
          <div
            style={{
              padding: "30px",
              textAlign: "center",
              color: "var(--text-muted)",
              background: "var(--cream)",
              borderRadius: "6px",
            }}
          >
            <div style={{ fontSize: "36px", marginBottom: "8px" }}>🏠</div>
            <p style={{ fontSize: "14px" }}>
              Floor plan image loading...
              <br />
              <a
                href={imageUrl}
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: "var(--navy-light)", fontSize: "12px" }}
              >
                Open image directly →
              </a>
            </p>
          </div>
        )}
      </div>

      {/* Room Details Toggle */}
      <div style={{ padding: "10px 20px", borderBottom: "1px solid var(--border)" }}>
        <button
          className="btn btn-outline btn-sm"
          type="button"
          onClick={() => setShowTable(!showTable)}
          style={{ width: "auto" }}
        >
          {showTable ? "▲ Hide Room Details" : "▼ Show Room Details"}
        </button>
      </div>

      {/* Room Details Table */}
      {showTable && plan.rooms && (
        <div className="room-table-wrapper">
          <table className="room-table">
            <thead>
              <tr>
                <th>Room</th>
                <th>Width (ft)</th>
                <th>Depth (ft)</th>
                <th>Area (sq.ft)</th>
              </tr>
            </thead>
            <tbody>
              {plan.rooms.map((room, i) => {
                const area = (room.width || 0) * (room.height || 0);
                const color = ROOM_COLORS[room.type] || "#e0e0e0";
                return (
                  <tr key={i}>
                    <td>
                      <span
                        className="room-color-dot"
                        style={{ backgroundColor: color }}
                      />
                      {room.label || room.type.replace(/_/g, " ")}
                    </td>
                    <td style={{ textAlign: "center" }}>{room.width?.toFixed(1)}</td>
                    <td style={{ textAlign: "center" }}>{room.height?.toFixed(1)}</td>
                    <td style={{ textAlign: "center" }}>{area.toFixed(1)}</td>
                  </tr>
                );
              })}
              <tr style={{ fontWeight: "700", background: "var(--cream-dark)" }}>
                <td colSpan={3}>Total Covered Area</td>
                <td style={{ textAlign: "center" }}>{totalArea.toFixed(1)}</td>
              </tr>
            </tbody>
          </table>
        </div>
      )}

      {/* Quick meta row */}
      <div className="plan-meta">
        <div className="meta-item">
          <span>🏠</span>
          <span>
            <strong>{plan.room_count}</strong> rooms
          </span>
        </div>
        <div className="meta-item">
          <span>📐</span>
          <span>
            <strong>{totalArea.toFixed(0)}</strong> sq.ft covered
          </span>
        </div>
        <div className="meta-item">
          <span>✨</span>
          <span>{plan.style}</span>
        </div>
      </div>
    </div>
  );
}
