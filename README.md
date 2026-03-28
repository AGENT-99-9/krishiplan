# 🌾 KrishiSaarthi — Empowering Modern Indian Farmers

**KrishiSaarthi** is an enterprise-grade agricultural platform designed to empower farmers with machine learning insights, a highly professional supply-chain marketplace, and an interactive community portal.

![KrishiSaarthi Dashboard](https://img.shields.io/badge/Status-Production%20Ready-success)
![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-blue)
![Django](https://img.shields.io/badge/Backend-Django%20REST-green)
![MongoDB](https://img.shields.io/badge/Database-MongoDB-47A248)
![AI](https://img.shields.io/badge/AI_Engine-RAG%20%2B%20Gemini-orange)

---

## 🚀 Key Features
1. **🤖 Krishi Intelligence (RAG AI Assistant)**
   Integrated Gemini 2.0 with a local ChromaDB vector store. Capable of advising farmers on crop diseases, optimal planting times, and answering complex agricultural inquiries.
2. **🧪 ML-Powered Soil Lab & Fertilizer Recommendation**
   Upload soil test reports for automated OCR parsing. A trained model calculates exact precise N-P-K fertilizer dosages avoiding harmful over-fertilization.
3. **🏪 Enterprise Vendor Marketplace**
   A seamless B2B & B2C marketplace allowing vendors to sell equipment, seeds, and fertilizers with integrated order fulfillment, tracking logs, and deep inventory analytics.
4. **💬 Community Forum**
   A dedicated space for farmers and agronomists to discuss pest outbreaks, share success stories, and build a local knowledge network.

---

## 🏗️ Tech Stack

### Frontend
* **React 19** + **Vite 7**
* Tailwind CSS v4 (Vanilla + Dynamic styling)
* React Router DOM for routing

### Backend
* **Python 3.10+ / Django 4.2+** 
* Django REST Framework
* **Machine Learning:** Scikit-Learn (Random Forest), PyTesseract (OCR)
* **LLM Engine:** Google Gemini, Sentence-Transformers, ChromaDB vector store
* **Database:** MongoDB (via PyMongo)
* JWT Authentication with strict role-based access logic

---

## 🏁 How to Run Locally

If you clone this repository, strictly follow these instructions to get the platform running beautifully without crash errors.

### 1. Prerequisites
- [Node.js](https://nodejs.org/) (v18 or higher)
- [Python](https://www.python.org/downloads/) (3.10 or higher)
- A **MongoDB Atlas** cluster URI (Free tier works perfectly)
- A **Google Gemini API Key** (Free tier)

### 2. Backend Setup & Seeding
The backend contains complex ML tools and must be initialized first.
```bash
cd backend

# Create Virtual Environment
python -m venv venv

# Activate Environment
# --> Windows: venv\Scripts\activate
# --> Mac/Linux: source venv/bin/activate

# Install ALL dependencies (includes heavy ML libraries)
pip install -r requirements.txt
```

**Setup Environment File:**
Copy the `.env.example` to `.env`:
```bash
cp .env.example .env
```
Inside `.env`, you **MUST** configure:
1. `MONGODB_URL`: Your MongoDB connection string.
2. `DATABASE_NAME`: E.g., `krishisarthi`.
3. `GEMINI_API_KEYS`: Your Gemini API Key (for the Chatbot to work).

**Seed the Database:**
To avoid an empty platform, run our powerful seeder script. It will create **5 Users**, **27 Products**, **12 Orders**, and **Community Posts**!
```bash
python seed_platform.py
```
*(Login details are printed upon success!)*

**Run the Server:**
```bash
python manage.py runserver 
# Server runs on http://127.0.0.1:8000
```

### 3. Frontend Setup
Open a **new terminal tab**.
```bash
cd frontend

# Install Node dependencies
npm install

# Start the Vite dev server
npm run dev
# App runs on http://localhost:5173
```

---

## 👤 Test Accounts Provided by Seed Script
The seed script will create the following test accounts with the password `Test@1234`:
- **Farmer 1:** `farmer@krishi.com`
- **Farmer 2:** `ravi@krishi.com`
- **Vendor (Seller):** `vendor@krishi.com`
- **Administrator:** `admin@krishi.com`

Log into `vendor@krishi.com` to explore the beautiful Vendor Dashboard (Analytics, Fulfillment, Inventory management)!

---

## 🛡️ License
Distributed under the MIT License. See `LICENSE` for more information.
