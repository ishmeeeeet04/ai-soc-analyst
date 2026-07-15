# 🛡️ AI-Powered Autonomous SOC Analyst

An end-to-end AI system that ingests security logs, detects threats using rule-based
detection and machine learning, explains its decisions with SHAP (Explainable AI),
maps findings to the MITRE ATT&CK framework, and generates human-readable incident
reports using a RAG-grounded LLM pipeline.

## 🔗 Live Demo
- **Dashboard:** https://ai-soc-analyst-sigma.vercel.app/
- **API:** https://ai-soc-analyst-8dx9.onrender.com/health

> Note: hosted on free-tier infrastructure — first request may take 30-60s to wake up.

## 🏗️ Architecture
- **Detection Engine:** Rule-based (Brute Force, Impossible Travel) + Random Forest ML model
- **Explainability:** SHAP feature attribution for every ML prediction
- **Threat Intelligence:** MITRE ATT&CK technique mapping (T1110, T1078)
- **AI Reporting:** RAG-grounded incident summaries via Gemini API + ChromaDB
- **Backend:** Flask REST API, deployed on Render
- **Frontend:** React (Vite), deployed on Vercel

## 🧰 Tech Stack
Python, Flask, scikit-learn, SHAP, ChromaDB, Google Gemini API, React, Vite, pandas

## 📊 Key Results
- 89% precision / 89% recall on synthetic attack detection (Random Forest)
- Real-time IP geolocation-based impossible travel detection
- Fully explainable predictions via SHAP

## 🚀 Running Locally
See `/docs` for setup instructions.