/**
 * api.js - All API calls to the Flask backend.
 * Uses axios for HTTP requests.
 */

import axios from "axios";

// Backend base URL
// In development, React proxy (set in package.json) forwards /api/* to port 5000
const BASE_URL = process.env.REACT_APP_API_URL || "";

/**
 * Check if the backend is running and configured correctly.
 */
export const checkHealth = async () => {
  const response = await axios.get(`${BASE_URL}/api/health`);
  return response.data;
};

/**
 * Generate floor plans from user inputs.
 *
 * @param {Object} inputs - Form inputs including plot size, rooms, natural text
 * @returns {Promise<Object>} - Contains session_id, plans, constraints, bhk, vastu_score
 */
export const generatePlans = async (inputs) => {
  const response = await axios.post(`${BASE_URL}/api/generate`, inputs, {
    timeout: 60000, // 60 second timeout (AI parsing can take time)
  });
  return response.data;
};

/**
 * Submit feedback to improve the current floor plans.
 *
 * @param {string} sessionId - The current session ID
 * @param {string} feedbackText - Natural language feedback
 * @param {number} iteration - Which regeneration this is
 * @returns {Promise<Object>} - Updated plans and summary
 */
export const submitFeedback = async (sessionId, feedbackText, iteration) => {
  const response = await axios.post(
    `${BASE_URL}/api/feedback`,
    {
      session_id: sessionId,
      feedback: feedbackText,
      iteration: iteration,
    },
    { timeout: 60000 }
  );
  return response.data;
};

/**
 * Get full session data by session ID.
 *
 * @param {string} sessionId - Session ID to retrieve
 * @returns {Promise<Object>} - Session data including history
 */
export const getSession = async (sessionId) => {
  const response = await axios.get(`${BASE_URL}/api/session/${sessionId}`);
  return response.data;
};

/**
 * Request PDF download and trigger browser download.
 *
 * @param {string} sessionId - The current session ID
 * @param {Array} plans - Current plans data
 * @param {Object} constraints - Current constraints
 */
export const downloadPdf = async (sessionId, plans, constraints) => {
  const response = await axios.post(
    `${BASE_URL}/api/download-pdf`,
    {
      session_id: sessionId,
      plans: plans,
      constraints: constraints,
    },
    {
      responseType: "blob", // Important: receive as binary blob
      timeout: 60000,
    }
  );

  // Create download link and click it
  const blob = new Blob([response.data], { type: "application/pdf" });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `house_plans_${sessionId.slice(0, 8)}.pdf`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

/**
 * Get the full URL for a generated image.
 * The image_url from backend is like "/generated/filename.svg"
 *
 * @param {string} imageUrl - Relative image URL from backend
 * @returns {string} - Full URL
 */
export const getImageUrl = (imageUrl) => {
  if (!imageUrl) return "";
  if (imageUrl.startsWith("http")) return imageUrl;
  return `${BASE_URL || "http://localhost:5000"}${imageUrl}`;
};
