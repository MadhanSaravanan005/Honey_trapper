# WhatsApp Malicious Message Detector

A Chrome extension and FastAPI backend system that detects potentially malicious messages on WhatsApp Web using machine learning.

## 🚀 Features

- **Real-time Detection**: Automatically scans incoming WhatsApp messages
- **Manual Scanning**: Extension popup for manually checking suspicious text
- **Visual Alerts**: Highlights malicious messages with red borders and warning tags
- **AI-Powered**: Uses machine learning model for accurate detection
- **Tag System**: Categorizes threats (urgency, manipulation, flirty content)

## 📁 Project Structure

```
├── backend/
│   ├── app.py                    # FastAPI server
│   ├── requirements.txt          # Python dependencies
│   └── honeytrap_detector.joblib # ML model (not included)
├── extension/
│   ├── manifest.json            # Chrome extension manifest
│   ├── background.js            # Service worker
│   ├── content.js               # WhatsApp page content script
│   ├── popup.html               # Extension popup UI
│   └── popup.js                 # Popup functionality
└── README.md
```

## 🛠 Setup Instructions

### Backend Setup

1. **Navigate to backend folder**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Add your ML model**:
   - Place your trained model file as `honeytrap_detector.joblib` in the backend folder
   - The model should be trained with scikit-learn and saved using joblib

5. **Run the server**:
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

### Chrome Extension Setup

1. **Open Chrome and go to**: `chrome://extensions/`

2. **Enable Developer Mode** (toggle in top right)

3. **Click "Load unpacked"** and select the `extension` folder

4. **Pin the extension** to your toolbar for easy access

## 📋 Usage

### Automatic Detection
1. Open WhatsApp Web in Chrome
2. The extension automatically monitors incoming messages
3. Malicious messages are highlighted with red borders and warning tags

### Manual Scanning
1. Click the extension icon in your toolbar
2. Paste suspicious text into the textarea
3. Click "Scan" to check the message
4. Results show as "MALICIOUS" (red) or "NORMAL" (green)

## 🔧 Configuration

### API Endpoint
- Default: `http://localhost:8000/predict`
- Can be changed in the extension popup
- Settings are automatically saved

### CORS Settings
- Currently set to allow all origins (`*`) for development
- **⚠️ For production**: Update CORS settings in `backend/app.py` to restrict origins

## 📊 API Endpoints

### `GET /`
Health check endpoint
- Returns model loading status

### `POST /predict`
Predict if text is malicious
- **Request**: `{"text": "message content"}`
- **Response**: 
  ```json
  {
    "label": "malicious|normal",
    "score": 0.85,
    "tags": ["urgency", "manipulation"]
  }
  ```

## 🏷 Detection Tags

- **urgency**: Contains urgent/time-pressure language
- **flirty**: Contains romantic/flirtatious content
- **manipulation**: Contains trust/secrecy manipulation tactics

## ⚠️ Important Notes

1. **ML Model Required**: You need to provide your own `honeytrap_detector.joblib` file
2. **Development Mode**: CORS is currently open for all origins
3. **Privacy**: No data is stored or transmitted outside your local setup
4. **WhatsApp TOS**: Ensure compliance with WhatsApp's Terms of Service
