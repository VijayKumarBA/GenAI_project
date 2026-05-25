/**
 * App.js - Main React application.
 *
 * Layout:
 * - Left sidebar: Input form
 * - Right main area: Generated plans gallery + feedback
 */

import React, { useState, useEffect } from "react";
import InputForm from "./components/InputForm";
import PlanCard from "./components/PlanCard";
import FeedbackPanel from "./components/FeedbackPanel";
import LoadingOverlay from "./components/LoadingOverlay";
import { generatePlans, submitFeedback, downloadPdf, checkHealth } from "./api";
import "./styles/App.css";

export default function App() {
  // ---- State ----
  const [isLoading, setIsLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState(null);
  const [plans, setPlans] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [constraints, setConstraints] = useState(null);
  const [bhk, setBhk] = useState(null);
  const [vastuScore, setVastuScore] = useState(null);
  const [costEstimate, setCostEstimate] = useState(null);
  const [error, setError] = useState(null);
  const [iteration, setIteration] = useState(1);
  const [feedbackHistory, setFeedbackHistory] = useState([]);
  const [lastFeedbackSummary, setLastFeedbackSummary] = useState("");
  const [backendStatus, setBackendStatus] = useState(null); // "ok" | "error" | null
  const [hasGenerated, setHasGenerated] = useState(false);
  const [isPdfLoading, setIsPdfLoading] = useState(false);

  // ---- Check backend health on mount ----
  useEffect(() => {
    checkHealth()
      .then((data) => {
        setBackendStatus("ok");
        console.log("✅ Backend connected:", data);
      })
      .catch(() => {
        setBackendStatus("error");
        console.error("❌ Backend not reachable");
      });
  }, []);

  // ---- Generate Floor Plans ----
  const handleGenerate = async (inputs) => {
    setIsLoading(true);
    setError(null);
    setPlans([]);
    setHasGenerated(false);
    setFeedbackHistory([]);
    setLastFeedbackSummary("");
    setIteration(1);

    try {
      setLoadingMessage("Sending requirements to AI...");
      const result = await generatePlans(inputs);

      setPlans(result.plans || []);
      setSessionId(result.session_id);
      setConstraints(result.constraints);
      setBhk(result.bhk);
      setVastuScore(result.vastu_score);
      setCostEstimate(result.cost_estimate);
      setHasGenerated(true);

      // Scroll to results
      setTimeout(() => {
        document.getElementById("results-section")?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }, 200);
    } catch (err) {
      const msg =
        err?.response?.data?.error ||
        err.message ||
        "Failed to generate plans. Is the backend running?";
      setError(msg);
    } finally {
      setIsLoading(false);
      setLoadingMessage(null);
    }
  };

  // ---- Process Feedback ----
  const handleFeedback = async (feedbackText) => {
    if (!sessionId) return;

    setIsLoading(true);
    setError(null);
    const nextIteration = iteration + 1;

    try {
      setLoadingMessage("Applying your feedback...");
      const result = await submitFeedback(sessionId, feedbackText, nextIteration);

      setPlans(result.plans || []);
      setConstraints(result.updated_constraints);
      setIteration(nextIteration);
      setLastFeedbackSummary(result.summary);
      setFeedbackHistory((prev) => [...prev, { text: feedbackText }]);

      // Scroll to top of results
      document.getElementById("results-section")?.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    } catch (err) {
      const msg =
        err?.response?.data?.error ||
        err.message ||
        "Failed to process feedback.";
      setError(msg);
    } finally {
      setIsLoading(false);
      setLoadingMessage(null);
    }
  };

  // ---- Download PDF ----
  const handleDownloadPdf = async () => {
    if (!sessionId || !plans.length) return;
    setIsPdfLoading(true);

    try {
      await downloadPdf(sessionId, plans, constraints);
    } catch (err) {
      setError("PDF download failed. Please try again.");
    } finally {
      setIsPdfLoading(false);
    }
  };

  // ---- Render ----
  return (
    <div>
      {/* Loading overlay */}
      {isLoading && <LoadingOverlay message={loadingMessage} />}

      {/* ---- Header ---- */}
      <header className="app-header">
        <div className="header-inner">
          <div className="header-brand">
            <div className="header-icon">🏠</div>
            <div>
              <div className="header-title">
                AI House <span>Plan</span> Generator
              </div>
              <div className="header-subtitle">
                Top-View 2D Floor Plans · AI-Powered
              </div>
            </div>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
            {/* Backend status */}
            {backendStatus === "ok" && (
              <span className="header-badge">● Backend Online</span>
            )}
            {backendStatus === "error" && (
              <span
                className="header-badge"
                style={{
                  borderColor: "var(--red)",
                  color: "var(--red)",
                  background: "rgba(224,82,82,0.1)",
                }}
              >
                ● Backend Offline
              </span>
            )}

            {/* PDF Download button */}
            {hasGenerated && (
              <button
                className="btn btn-amber btn-sm"
                onClick={handleDownloadPdf}
                disabled={isPdfLoading}
                style={{ width: "auto" }}
              >
                {isPdfLoading ? "⏳ Generating..." : "📄 Download PDF"}
              </button>
            )}
          </div>
        </div>
      </header>

      {/* ---- Main Layout ---- */}
      <div className="main-layout" style={{ padding: "24px" }}>

        {/* ---- Left Sidebar: Input Form ---- */}
        <aside>
          {/* Backend offline warning */}
          {backendStatus === "error" && (
            <div className="alert alert-error" style={{ marginBottom: "14px" }}>
              <span>⚠️</span>
              <div>
                <strong>Backend not running!</strong>
                <br />
                Start the Flask backend: <code>cd backend && python app.py</code>
              </div>
            </div>
          )}

          <InputForm onGenerate={handleGenerate} isLoading={isLoading} />
        </aside>

        {/* ---- Right Main: Results ---- */}
        <main id="results-section">
          {/* Error alert */}
          {error && (
            <div className="alert alert-error" style={{ marginBottom: "20px" }}>
              <span>❌</span>
              <div>
                <strong>Error:</strong> {error}
              </div>
            </div>
          )}

          {/* Empty state (before first generation) */}
          {!hasGenerated && !isLoading && !error && (
            <div className="empty-state">
              <div className="empty-icon">📐</div>
              <div className="empty-title">Your floor plans will appear here</div>
              <p className="empty-text">
                Fill in your requirements on the left and click{" "}
                <strong>Generate Floor Plans</strong> to create 3 unique
                top-view layouts.
              </p>
              <div
                style={{
                  display: "flex",
                  gap: "12px",
                  marginTop: "8px",
                  flexWrap: "wrap",
                  justifyContent: "center",
                }}
              >
                {["Plan A: Grid Layout", "Plan B: Vastu", "Plan C: Open Plan"].map((p) => (
                  <span
                    key={p}
                    style={{
                      padding: "6px 14px",
                      background: "var(--navy)",
                      color: "var(--white)",
                      borderRadius: "20px",
                      fontSize: "12px",
                      fontFamily: "Rajdhani, sans-serif",
                      fontWeight: "600",
                    }}
                  >
                    {p}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Results header row */}
          {hasGenerated && plans.length > 0 && (
            <>
              <div className="stats-row" style={{ marginBottom: "20px" }}>
                <div className="stat-chip">🏠 {bhk || "House"}</div>
                <div className="stat-chip amber">
                  🧭 {constraints?.facing?.replace(/\b\w/g, (c) => c.toUpperCase()) || ""}-Facing
                </div>
                <div className="stat-chip">
                  📐 {constraints?.plot_width}×{constraints?.plot_height} ft
                </div>
                {iteration > 1 && (
                  <div className="iteration-badge">
                    🔄 Iteration {iteration}
                  </div>
                )}
                {vastuScore && (
                  <div className="stat-chip green">
                    🕉️ Vastu: {vastuScore.score}/100
                  </div>
                )}
              </div>

              {/* Plans gallery */}
              <div className="plans-gallery">
                {plans.map((plan, i) => (
                  <PlanCard key={`${plan.plan_name}-${iteration}`} plan={plan} index={i} />
                ))}
              </div>

              {/* Cost estimate card */}
              {costEstimate && (
                <div className="cost-card fade-in-up" style={{ marginTop: "24px" }}>
                  <div className="cost-title">
                    <span>💰</span> Rough Construction Estimate
                  </div>
                  <div className="cost-row">
                    <span className="label">Total Covered Area</span>
                    <span className="value">{costEstimate.total_covered_area} sq.ft</span>
                  </div>
                  <div className="cost-row">
                    <span className="label">Rate (Standard)</span>
                    <span className="value">₹{costEstimate.cost_per_sqft_inr}/sq.ft</span>
                  </div>
                  <div className="cost-row">
                    <span className="label">Estimated Cost</span>
                    <span className="value big">₹{costEstimate.estimated_cost_lakhs} Lakhs</span>
                  </div>
                  <p
                    style={{
                      fontSize: "10px",
                      color: "rgba(255,255,255,0.45)",
                      marginTop: "8px",
                    }}
                  >
                    {costEstimate.disclaimer}
                  </p>
                </div>
              )}

              {/* PDF Download CTA */}
              <div
                style={{
                  display: "flex",
                  gap: "12px",
                  marginTop: "20px",
                  flexWrap: "wrap",
                }}
              >
                <button
                  className="btn btn-amber"
                  onClick={handleDownloadPdf}
                  disabled={isPdfLoading}
                  style={{ flex: 1, minWidth: "200px" }}
                >
                  {isPdfLoading ? "⏳ Generating PDF..." : "📄 Download All Plans as PDF"}
                </button>
              </div>

              {/* Feedback panel */}
              <FeedbackPanel
                onFeedback={handleFeedback}
                isLoading={isLoading}
                feedbackHistory={feedbackHistory}
                lastSummary={lastFeedbackSummary}
              />
            </>
          )}
        </main>
      </div>

      {/* ---- Footer ---- */}
      <footer
        style={{
          textAlign: "center",
          padding: "20px",
          background: "var(--navy)",
          color: "rgba(255,255,255,0.4)",
          fontSize: "12px",
          marginTop: "40px",
        }}
      >
        AI-Powered House Plan Generator · Built with React + Flask + Gemini AI
        · For planning purposes only
      </footer>
    </div>
  );
}
