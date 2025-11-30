# Nova Banking AI 🏦 🤖

> **Status**: 🚧 Under Development (Alpha)

**Nova** is a next-generation, voice-first banking assistant designed to revolutionize customer service. Unlike traditional chatbots that only escalate issues, Nova is an **autonomous agent** capable of solving complex banking problems, analyzing financial data, and executing transactions in real-time.

---

## 🌟 Vision

Our goal is to build a **Complete Customer Service Agent** that:
1.  **Understands** natural language (voice & text) with human-level nuance.
2.  **Solves** issues autonomously (e.g., "Why was I charged this?", "Fix my transaction").
3.  **Escalates** intelligently only when human intervention is strictly necessary.
4.  **Proactively** monitors financial health (Fraud detection, Cashflow alerts).

---

## 🚀 Key Features Achieved

### 1. 🗣️ Real-Time Voice Interface
*   **Hands-Free Interaction**: Full-duplex voice chat with "Barge-in" capability (interrupt the AI naturally).
*   **Low Latency**: Streaming architecture for near-instant responses.
*   **Visual Feedback**: "Circular Wave" visualizer that reacts to audio frequency in real-time.
*   **Text-to-Speech (TTS)**: High-quality, natural-sounding voice synthesis (Google Cloud TTS).

### 2. 🧠 Advanced AI Brain (Vertex AI)
*   **Model**: Powered by **Gemini 2.0 Flash** for speed and reasoning.
*   **Persona**: "Nova" - A professional, warm, and concise banking expert.
*   **Context Awareness**: Remembers conversation history and user context.

### 3. 🧪 Gen AI Techniques & Tuning
We employed advanced techniques to ensure production-grade performance:
*   **Few-Shot Prompting**: The system prompt includes curated examples of "Voice-First" banking interactions to guide the model's style and conciseness.
*   **System Prompt Engineering**: A robust persona definition ("Nova") enforces strict constraints on response length and tone, optimized for audio output.
*   **Tool Use (Function Calling)**: The model is fine-tuned to detect when to call external tools (MCP) vs. when to answer directly.
*   **Streaming Architecture**: We implemented a custom streaming pipeline that tokenizes text and synthesizes audio in real-time chunks to minimize latency.

### 4. 🔌 Model Context Protocol (MCP) Integration
*   **Standardized Tooling**: Uses the open standard **MCP** to discover and execute tools.
*   **Dynamic Extensibility**: New tools added to the MCP server are instantly available to the agent.
*   **Tools Implemented**:
    *   `get_account_balance`: Real-time balance checks.
    *   `get_recent_transactions`: Transaction history with filtering.
    *   `get_spending_analysis`: Category-based spending breakdown.
    *   `detect_anomalies`: Statistical fraud/anomaly detection.
    *   `predict_cashflow`: Future balance forecasting.
    *   `transfer_funds`: Secure fund transfers (with PIN verification).
    *   `pay_bill`: Bill payment execution.

### 4. 📊 Data Lake Architecture
*   **BigQuery**: Centralized data warehouse for all banking data (Users, Transactions, Offers).
*   **Real-time Analytics**: SQL-based insights generated on the fly.

---

## 🛠️ Technology Stack

*   **Frontend**: React, Vite, TailwindCSS, Web Audio API.
*   **Backend**: Python, FastAPI, WebSockets.
*   **AI & ML**: Google Vertex AI (Gemini), Google Cloud Speech-to-Text, Google Cloud Text-to-Speech.
*   **Data**: Google BigQuery.
*   **Protocol**: Model Context Protocol (MCP).

---

## 🔮 Roadmap

- [ ] **Autonomous Issue Resolution**: Agents that can investigate disputes and issue refunds.
- [ ] **Multi-Agent Orchestration**: Specialized agents for Loans, Mortgages, and Investments.
- [ ] **Biometric Authentication**: Voice ID for secure transactions.
- [ ] **Mobile App Integration**: Native iOS/Android support.

---

## 🏃‍♂️ Getting Started

### Prerequisites
*   Node.js & npm
*   Python 3.10+
*   Google Cloud Platform Account (Vertex AI, BigQuery enabled)

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/your-org/nova-banking-ai.git
    cd nova-banking-ai
    ```

2.  **Backend Setup**
    ```bash
    cd backend
    pip install -r requirements.txt
    export GCP_PROJECT_ID=your-project-id
    python -m backend.main
    ```

3.  **Frontend Setup**
    ```bash
    cd frontend
    npm install
    npm run dev
    ```


