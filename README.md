<div align="center">
  <h1>🤖 AztecaBot (UDLAPbot)</h1>
  <p><strong>An intelligent, bilingual AI Chatbot tailored for International Business students at UDLAP.</strong></p>

  [![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](#)
  [![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)](#)
  [![Groq](https://img.shields.io/badge/Groq_API-F55036?style=for-the-badge&logo=groq&logoColor=white)](#)
</div>

---

## 🚀 Overview

**AztecaBot** (also known as UDLAPbot in English) is a web-based AI assistant built with Flask. It is designed to help International Business students at Universidad de las Américas Puebla (UDLAP) find accurate information regarding their academic journey.

The bot dynamically fetches real-time data from UDLAP's official websites (such as the curriculum, calendar, and professor directories) and leverages the power of the **Groq API** (Llama 3.3 models) to provide natural, contextual, and helpful answers.

## ✨ Key Features

- 🧠 **AI-Powered Responses:** Utilizes Llama 3.3 models via Groq API for fast and intelligent conversations.
- 🕸️ **Real-Time Web Scraping:** Uses `BeautifulSoup4` and `requests` to fetch the latest academic plans, events, and contact info directly from UDLAP's websites.
- 🌐 **Bilingual Support:** Instantly switch between Spanish and English interfaces and chatbot personalities.
- 🌓 **Theming:** Includes a Light and Dark (grayscale) theme toggle for better accessibility.
- 🔐 **Mock Login System:** A built-in login portal to access the chat interface.
- ☁️ **Deployment-Ready:** Configured with `gunicorn` and a `Procfile` for easy deployment to platforms like Heroku or Render.

## 🛠️ Tech Stack

- **Backend:** Python, Flask, Gunicorn
- **AI Integration:** Groq API (`llama-3.3-70b-versatile` & `llama-3.3-8b-instruct`)
- **Web Scraping:** BeautifulSoup4, Requests
- **Frontend:** Vanilla HTML, CSS, JavaScript (No external frameworks)

## 💻 Local Installation

To run this project on your local machine, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DiegoBCA/Chatbot1.git
   cd Chatbot1
