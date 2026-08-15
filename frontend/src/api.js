import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const client = axios.create({ baseURL: API_BASE_URL });

function authHeader(token) {
  return { headers: { Authorization: `Bearer ${token}` } };
}

export async function signupParent(email, password) {
  const { data } = await client.post("/parents/signup", { email, password });
  return data;
}

export async function loginParent(email, password) {
  const { data } = await client.post("/parents/login", { email, password });
  return data;
}

export async function forgotPassword(email) {
  const { data } = await client.post("/parents/forgot-password", { email });
  return data;
}

export async function resetPassword(token, newPassword) {
  const { data } = await client.post("/parents/reset-password", {
    token,
    new_password: newPassword,
  });
  return data;
}

export async function addChild(parentToken, { name, pin, grade }) {
  const { data } = await client.post(
    "/parents/children",
    { name, pin, grade },
    authHeader(parentToken)
  );
  return data;
}

export async function listChildren(parentToken) {
  const { data } = await client.get("/parents/children", authHeader(parentToken));
  return data;
}

export async function verifyChildPin(childId, pin) {
  const { data } = await client.post(`/children/${childId}/verify-pin`, { pin });
  return data;
}

export async function getChildProgress(childToken, childId) {
  const { data } = await client.get(
    `/children/${childId}/progress`,
    authHeader(childToken)
  );
  return data;
}

export async function recordAttempt(
  childToken,
  childId,
  { topic, track, question_id, selected_answer, is_correct }
) {
  const { data } = await client.post(
    `/children/${childId}/attempts`,
    { topic, track, question_id, selected_answer, is_correct },
    authHeader(childToken)
  );
  return data;
}

export async function getQuestions({ topic, track, difficulty, limit }) {
  const params = { topic, track };
  if (difficulty) params.difficulty = difficulty;
  if (limit) params.limit = limit;
  const { data } = await client.get("/questions", { params });
  return data.questions;
}

export async function generateQuestions({ topic, track, difficulty = "easy", n = 5 }) {
  const { data } = await client.post("/generate-questions", {
    topic,
    track,
    difficulty,
    n,
  });
  return data.questions;
}

export async function getSolution({ question_text, correct_answer, explanation_hint }) {
  const { data } = await client.post("/get-solution", {
    question_text,
    correct_answer,
    explanation_hint,
  });
  return data;
}

export function apiErrorMessage(err, fallback) {
  return err?.response?.data?.detail || fallback;
}
