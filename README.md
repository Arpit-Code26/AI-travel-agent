# AI Travel Agent

An autonomous travel planning assistant built with LangGraph, Google Gemini, SerpAPI, and SendGrid, packaged in a Streamlit web interface.

The system gathers flight and accommodation details from live search, formats an itinerary, pauses for user review via a human-in-the-loop checkpoint, and sends the final plan to the traveler's inbox.

---

## Architecture Overview

```text
User Input 
    │
    ▼
[Chatbot Node (Gemini)]
    │
    ├─► [Search Node (SerpAPI)] ──► Gathers live flights & hotels
    │
    ▼
[Human-in-the-Loop Interruption] ──► Awaits approval in Streamlit
    │
    ▼
[Email Node (SendGrid)] ──► Dispatches HTML itinerary to inbox
```

---

## Core Features

* **Autonomous Tool Routing:** LangGraph manages execution flow between reasoning and external tools.
* **Live Search Integration:** SerpAPI queries current flight schedules and lodging rates.
* **Human Authorization:** LangGraph interrupts execution before running the email tool, allowing users to review the itinerary on screen prior to delivery.
* **Formatted Email Delivery:** SendGrid converts Markdown itineraries into responsive HTML emails.

---

## Project Structure

```text
ai-travel-agent/
│
├── agent.py          # LangGraph state machine, nodes, and tool routing
├── app.py            # Streamlit chat interface and human-in-the-loop controls
├── tools.py          # SerpAPI flight/hotel search and SendGrid email functions
├── requirements.txt  # Project dependencies
├── .env.example      # Template for environment variables
└── README.md
```

---

## Setup & Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/Arpit-Code26/AI-travel-agent.git](https://github.com/Arpit-Code26/AI-travel-agent.git)
cd AI-travel-agent/ai-travel-agent
```

### 2. Create and Activate a Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```env
GOOGLE_API_KEY=your_gemini_api_key
SERPAPI_API_KEY=your_serpapi_api_key
SENDGRID_API_KEY=your_sendgrid_api_key
```

### 5. Verify SendGrid Sender
Register your sending address under **Settings > Sender Authentication > Single Sender Verification** in the SendGrid dashboard, and set that address as `from_email` inside `tools.py`.

---

## Usage

Start the Streamlit application:
```bash
python -m streamlit run app.py
```

### Example Prompt
```text
Find round-trip flights and hotel options for a 5-day trip from Jaipur to Bali, and email the final itinerary to your_email@example.com.
```

Review the itinerary in the chat window, then click **Approve Email Dispatch** to trigger the email.
