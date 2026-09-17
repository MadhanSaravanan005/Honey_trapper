# Honey Trapper

## Overview
Honey Trapper is a client-server security tool composed of a Manifest V3 Chrome browser extension and a FastAPI backend service. It monitors and inspects WhatsApp Web chat text to identify indicators of social engineering attacks, urgency-driven deception, and honeytrap manipulation patterns.

## Problem
Instant messaging platforms such as WhatsApp are frequently used by bad actors to conduct social engineering, romance scams, financial manipulation, and honeytraps. Users often miss conversational cues indicating artificial urgency, emotional manipulation, or deceptive secrecy before engaging with harmful requests or fraudulent links.

## Solution
Honey Trapper provides proactive message scanning through two operational layers:
1. A **Chrome Extension** that observes incoming messages on WhatsApp Web or allows users to manually submit suspicious messages for verification.
2. A **FastAPI Backend** that classifies message text using a trained machine learning model (`honeytrap_detector.joblib`) or an automated heuristic keyword detection fallback if no custom model has been supplied.

## Features
- **Real-Time DOM Inspection**: Checks incoming messages on WhatsApp Web at configurable intervals.
- **Manual Scanning Popup**: Quick-scan text area in the extension toolbar to evaluate arbitrary snippets on demand.
- **Visual Alert Highlighting**: Emphasizes flagged malicious messages with a distinct red boundary and category tag.
- **Contextual Threat Tagging**: Categorizes signals into `urgency`, `flirty`, and `manipulation`.
- **Dual Inference Modes**:
  - **ML Mode**: Uses a scikit-learn classification pipeline (`honeytrap_detector.joblib`) with class probability scores.
  - **Heuristic Fallback Mode**: Rule-based detection ensures the backend works immediately upon cloning without requiring a pre-existing binary model file.
- **Model Training Utility**: Includes `backend/train.py` to train and export a baseline TF-IDF Logistic Regression model.

## How It Works
1. **Message Ingestion**: The extension content script periodically captures incoming text from WhatsApp Web message containers (`.message-in`), or the user inputs text into the extension popup.
2. **Background Dispatch**: The extension service worker dispatches a JSON POST payload to the FastAPI `/predict` endpoint.
3. **Classification**:
   - The backend runs tag extraction for urgency, flirtation, and secrecy keywords.
   - If a custom model is loaded from disk, `model.predict` and `model.predict_proba` determine the label and confidence score.
   - If no model is present, the heuristic engine classifies the message based on detected threat patterns.
4. **Visual Feedback**: The result (`label`, `score`, `tags`) is returned to the extension, updating the UI badge or highlighting the message element directly in the chat.

## Project Structure
```text
Honey_trapper/
├── backend/
│   ├── app.py               # FastAPI application with REST endpoints and fallback logic
│   ├── requirements.txt     # Python package requirements for backend
│   └── train.py             # Script to train and save baseline ML model
├── extension/
│   ├── background.js        # Extension service worker handling API requests
│   ├── content.js           # Content script monitoring WhatsApp Web DOM
│   ├── manifest.json        # Chrome Extension Manifest V3 configuration
│   ├── popup.html           # Manual scanner popup interface
│   └── popup.js             # Logic for popup manual scanning
├── tests/
│   └── test_app.py          # Pytest suite verifying endpoints and classification
├── .gitignore               # Git exclusion rules
├── README.md                # Project documentation
└── requirements.txt         # Root Python requirements file for easy setup
```

## Requirements
- Python 3.10 or higher
- Google Chrome or Chromium-based browser supporting Manifest V3
- Active internet connection (for initial pip package installation)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/MadhanSaravanan005/Honey_trapper.git
   cd Honey_trapper
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Project

### 1. Start the Backend API
Run the FastAPI application from the project root:
```bash
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```
Or from within the `backend/` directory:
```bash
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```
Verify the server is running by visiting `http://localhost:8000/`.

### 2. (Optional) Train the Baseline ML Model
If you wish to use machine learning classification rather than heuristic fallback:
```bash
python backend/train.py
```
This generates `backend/honeytrap_detector.joblib`. Restart the server to load the trained model.

### 3. Load the Chrome Extension
1. Open Google Chrome and navigate to `chrome://extensions/`.
2. Toggle **Developer mode** in the top-right corner.
3. Click **Load unpacked**.
4. Select the `extension/` directory inside this repository.
5. (Optional) Pin the **WhatsApp Message Watcher** icon to the browser toolbar.

## Testing
Run the automated test suite with pytest from the project root:
```bash
pytest -v
```

## Example Usage

### Health Check Request
```bash
curl http://localhost:8000/
```
Response:
```json
{
  "status": "ready (heuristic fallback)",
  "mode": "heuristic",
  "message": "No trained model file found. Running in rule-based heuristic mode. Place 'honeytrap_detector.joblib' in the backend directory to enable ML inference."
}
```

### Prediction Request
```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Hey baby, please hurry urgent love secret\"}"
```
Response:
```json
{
  "label": "malicious",
  "score": 0.95,
  "tags": [
    "urgency",
    "flirty",
    "manipulation"
  ]
}
```

## Limitations
- **WhatsApp Web DOM Sensitivity**: The content script relies on specific DOM class selectors (`.message-in`) which can change when WhatsApp updates its web client layout.
- **Rule and Baseline Heuristics**: The built-in heuristics and small baseline training corpus are intended as demonstration baselines and do not replace comprehensive commercial anti-fraud systems.
- **Plaintext Analysis Only**: Analysis is limited to text payloads; media files, images, voice notes, and file attachments are not evaluated.
- **Local Connectivity**: The extension requires active connectivity to the local or hosted backend endpoint to classify text.

## Future Improvements
- Implement a `MutationObserver` in `content.js` instead of a polling interval for reduced CPU overhead and faster event-driven reaction.
- Expand training corpus with diverse multi-language dataset covering contemporary social engineering techniques.
- Add real-time link reputation and phishing domain checking.
- Enable user-configurable keyword lists and sensitivity thresholds via the extension settings.

