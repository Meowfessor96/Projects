# 🔍 GitHub Repo Intelligence

**GitHub Repo Intelligence** is an AI-powered Chrome extension designed to accelerate developer onboarding. It injects a smart, context-aware sidebar directly into GitHub repository pages, instantly analyzing codebases, file structures, and documentation to provide actionable architectural insights—saving developers hours of manual exploration.

## ✨ Key Features

- **📝 AI-Powered TL;DR:** Generates a concise, 2-sentence summary of the repository's core purpose and problem statement using advanced LLMs.
- **️ Smart Tagging & OS Support:** Automatically detects repository type (e.g., CLI Tool, UI Library, Monorepo) and supported platforms (Linux, macOS, Windows, Web).
- **🛠️ Tech Stack & Architecture:** Identifies specific frameworks, tools, and architectural patterns (e.g., Microservices, MVC, Serverless) beyond just base programming languages.
- ** Deployment & Entry Points:** Infers deployment targets (Docker, Vercel, AWS) and highlights the exact file paths a developer should read first to understand the codebase.
- **🔗 Similar Projects:** Dynamically searches and recommends highly relevant, popular alternative repositories based on native GitHub topics.

## ⚙️ Tech Stack

- **Frontend:** Vanilla JavaScript, Shadow DOM (for strict CSS isolation), CSS3 (Custom Properties & Animations)
- **Backend:** Python, Flask, Flask-CORS
- **AI & APIs:** Groq API (Llama 3.3), OpenAI API, GitHub REST API
- **Architecture:** Client-Server (Localhost), Asynchronous Data Fetching

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- A free Groq API Key ([console.groq.com](https://console.groq.com/keys)) or OpenAI API Key
- A GitHub Personal Access Token (Optional, but highly recommended to prevent API rate limits)

### 1. Setup the Backend

Navigate to the `backend` directory and install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

### 2.Click on the extension to enter your Groq | GitHub API keys in the popup

#### 2.5 Alternate local way

Create a `.env` file in the backend directory and add your keys /

```bash
OPENAI_API_KEY=gsk_your_groq_key_here
GITHUB_TOKEN=ghp_your_github_token_here
```

### 3.Start the locala Flask Server

```bash
python app.py
```

### 4.Load the Extension

- Open you browser and navigate to `chrome://extensions/`
- Enable Developer mode using the toggle in the top right corner.
- Click Load unpacked and select the root directory of this project.
- Click the extension icon in your browser toolbar and save your API keys in the settings popup.
- Navigate to any GitHub repository to see the sidebar in action!
