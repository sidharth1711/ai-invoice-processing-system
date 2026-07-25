# 🧾 AI Invoice Processing & Validation System

An AI-powered invoice processing application that extracts structured information from PDF and image invoices, validates business-critical fields, enables human review, and exports approved invoice data for downstream automation.

## 🚀 Live Demo

**Live Application:** Add your Streamlit deployment URL here

> This application is a portfolio demonstration. Please do not upload confidential, sensitive, or production financial documents.

## 📌 Business Problem

Manual invoice processing often requires finance teams to:

* Open PDF or image invoices
* Manually identify invoice details
* Copy information into Excel or ERP systems
* Validate invoice totals and tax information
* Check mandatory fields
* Review exceptions
* Prepare structured data for downstream processing

This application demonstrates how multimodal AI and deterministic Python validation can automate a significant portion of this workflow while keeping a human in the loop for review and approval.

## ✨ Features

* 📄 Supports PDF invoices
* 🖼️ Supports JPG, JPEG and PNG invoices
* 🤖 AI-powered invoice data extraction
* 🧩 Pydantic-based structured output
* 🧾 Invoice header extraction
* 📋 Line-item extraction
* ✏️ Human-in-the-loop editing and review
* ✅ Business-rule validation
* 🇮🇳 GSTIN format validation
* 🧮 Invoice total validation
* ⚠️ PASS / REVIEW / FAILED status
* 👍 Approve / Reject workflow
* 📥 CSV export
* 🔐 Secure API-key handling

## 🧠 How It Works

```text
PDF / JPG / PNG Invoice
          │
          ▼
   Streamlit Interface
          │
          ▼
 OpenAI Multimodal Model
          │
          ▼
  Pydantic Data Model
          │
          ▼
 Structured Invoice Data
          │
     ┌────┴────┐
     ▼         ▼
Human Review  Python Validation
     │         │
     └────┬────┘
          ▼
 PASS / REVIEW / FAILED
          │
          ▼
   Approve / Reject
          │
          ▼
      CSV Export
```

## 🔍 Extracted Information

The application can extract information including:

### Invoice Header

* Invoice Number
* Invoice Date
* Vendor Name
* Vendor GSTIN
* Customer Name
* Customer GSTIN
* Purchase Order Number
* Subtotal
* Tax
* Total Amount
* Currency

### Line Items

* Description
* Quantity
* Unit Price
* Tax
* Amount

## ✅ Validation Engine

AI is used for document understanding and extraction, while deterministic Python rules are used for business validation.

Current validations include:

* Invoice number availability
* Invoice date availability
* Vendor identification
* GSTIN format
* Purchase order availability
* Subtotal + Tax = Total validation

The application categorizes invoices as:

**PASS** — Validation checks passed.

**REVIEW** — Human verification is required.

**FAILED** — One or more critical validation checks failed.

## 🛠️ Technology Stack

* **Python** — Application and business logic
* **Streamlit** — Web interface
* **OpenAI API** — Multimodal invoice understanding
* **Pydantic** — Structured AI output
* **Pandas** — Data manipulation and CSV generation
* **python-dotenv** — Local environment configuration

## 📁 Project Structure

```text
ai-invoice-processing-system/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
└── src/
    ├── __init__.py
    ├── models.py
    ├── extractor.py
    └── validator.py
```

## 💻 Running Locally

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd ai-invoice-processing-system
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure the OpenAI API key

Create a `.env` file:

```text
OPENAI_API_KEY=your_openai_api_key
```

Never commit your `.env` file or API key to GitHub.

### 4. Start the application

```bash
python -m streamlit run app.py
```

The application will normally be available at:

```text
http://localhost:8501
```

## 🔐 Security

API credentials are not stored in the source code.

For local development, credentials are loaded through environment variables.

For cloud deployment, secrets should be configured using the deployment platform's secret-management functionality.

The public version of this project is intended for demonstration purposes and should not be used to process confidential production invoices.

## 🗺️ Future Roadmap

Planned enhancements include:

* Multi-invoice batch processing
* Processing history dashboard
* Database integration
* Duplicate invoice detection
* Vendor master validation
* Purchase-order matching
* Three-way matching
* Configurable tolerance rules
* Role-based approval workflow
* Authentication
* REST API using FastAPI
* PostgreSQL integration
* SAP/ERP integration
* Agentic exception handling using LangGraph

## 💡 Potential Enterprise Workflow

```text
Invoice
   │
   ▼
AI Extraction
   │
   ▼
Business Validation
   │
   ├──── Vendor Master Check
   │
   ├──── Purchase Order Match
   │
   ├──── Duplicate Detection
   │
   └──── Amount/Tolerance Check
   │
   ▼
Decision
   │
   ├──── Valid ─────► Approval / ERP
   │
   └──── Exception ─► Human Review
```

## 🎯 Project Objective

This project demonstrates how Generative AI can be combined with traditional automation and deterministic business rules to build practical finance-process automation.

The goal is not simply to extract text from an invoice, but to convert unstructured financial documents into validated, reviewable, structured information that can eventually integrate with enterprise systems.

## ⚠️ Disclaimer

This project is intended for educational, portfolio, and demonstration purposes. AI-generated extraction may contain errors. Human verification is recommended before using extracted information for financial or business decisions.
