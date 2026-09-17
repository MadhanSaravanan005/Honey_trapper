import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from backend.app import app, load_model, extract_tags
import backend.app as app_module
from backend.train import train_and_save

client = TestClient(app)

def test_extract_tags():
    assert "urgency" in extract_tags("This is very urgent, please act now!")
    assert "flirty" in extract_tags("Hello baby, I miss your sweet kiss")
    assert "manipulation" in extract_tags("Trust me, this is a secret don't tell anyone")
    assert extract_tags("Hello, let's schedule a meeting tomorrow.") == []

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "mode" in data

def test_predict_validation_error():
    # Empty string
    res_empty = client.post("/predict", json={"text": ""})
    assert res_empty.status_code == 400

    # Whitespace only
    res_ws = client.post("/predict", json={"text": "   "})
    assert res_ws.status_code == 400

def test_predict_heuristic_normal():
    # Ensure model is None for heuristic fallback testing
    original_model = app_module.model
    app_module.model = None
    try:
        response = client.post("/predict", json={"text": "Hey, let's review the quarterly slides."})
        assert response.status_code == 200
        data = response.json()
        assert data["label"] == "normal"
        assert data["tags"] == []
        assert data["score"] is not None
    finally:
        app_module.model = original_model

def test_predict_heuristic_malicious():
    original_model = app_module.model
    app_module.model = None
    try:
        response = client.post("/predict", json={"text": "Hey baby, please hurry urgent love secret"})
        assert response.status_code == 200
        data = response.json()
        assert data["label"] == "malicious"
        assert "urgency" in data["tags"]
        assert "flirty" in data["tags"]
        assert "manipulation" in data["tags"]
        assert data["score"] > 0.7
    finally:
        app_module.model = original_model

def test_train_and_model_inference():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_model_path = os.path.join(tmpdir, "test_detector.joblib")
        # Train model
        train_and_save(tmp_model_path)
        assert os.path.exists(tmp_model_path)

        # Load into app
        original_model = app_module.model
        original_path = app_module.MODEL_PATH
        try:
            loaded_model, err = load_model(tmp_model_path)
            assert err is None
            assert loaded_model is not None
            app_module.model = loaded_model
            app_module.MODEL_PATH = tmp_model_path

            # Check root reports model loaded
            root_res = client.get("/")
            assert root_res.status_code == 200
            assert root_res.json()["mode"] == "ml_model"

            # Check normal prediction
            pred_normal = client.post("/predict", json={"text": "Sounds good, see you at 2pm."})
            assert pred_normal.status_code == 200
            assert pred_normal.json()["label"] == "normal"
            assert isinstance(pred_normal.json()["score"], float)

            # Check malicious prediction
            pred_mal = client.post("/predict", json={"text": "Hey baby, I miss you so much. Can you send gift cards urgently?"})
            assert pred_mal.status_code == 200
            assert pred_mal.json()["label"] == "malicious"
            assert "urgency" in pred_mal.json()["tags"]
        finally:
            app_module.model = original_model
            app_module.MODEL_PATH = original_path
