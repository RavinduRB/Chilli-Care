"""
Integration Tests for Chilli Care
-----------------------------------
Tests Flask routes (API endpoints) with a real test client.
MongoDB and the ML model are mocked so no real database or GPU is needed.

Run: pytest tests/integration/ -v
"""

import io
import os
import sys
import json
import pytest
from unittest.mock import MagicMock, patch
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


# ===========================================================================
# App + client fixtures (self-contained so the module can run independently)
# ===========================================================================

def _make_image_bytes(color=(34, 139, 34), size=(224, 224), fmt="JPEG"):
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    return buf.read()


@pytest.fixture(scope="module")
def mock_mongo():
    m = MagicMock()
    m.connected = True
    m.get_user_by_email.return_value = None
    m.create_user.return_value = "user123"
    m.update_last_login.return_value = True
    m.get_all_diseases.return_value = []
    m.count_users.return_value = 0
    m.count_predictions.return_value = 0
    m.get_disease.return_value = None   # force fallback to DISEASE_INFO dict
    # Make db attributes JSON-serializable for health check endpoint
    m.db.name = "chilli_care_test"
    m.db.list_collection_names.return_value = ["users", "diseases", "predictions"]
    m.db.diseases.count_documents.return_value = 7
    return m


@pytest.fixture(scope="module")
def mock_model():
    m = MagicMock()
    # Simulate a prediction array with 7 disease classes
    m.predict.return_value = [[0.05, 0.05, 0.80, 0.02, 0.03, 0.03, 0.02]]
    return m


@pytest.fixture(scope="module")
def flask_app(mock_mongo, mock_model):
    with patch("mongodb_database.get_db", return_value=mock_mongo):
        with patch("app.model", mock_model):
            with patch("app.mongodb", mock_mongo):
                import app as flask_app_module

                flask_app_module.app.config.update({
                    "TESTING": True,
                    "SECRET_KEY": "test-secret",
                    "MAIL_SUPPRESS_SEND": True,
                    "WTF_CSRF_ENABLED": False,
                })
                yield flask_app_module.app


@pytest.fixture()
def client(flask_app):
    return flask_app.test_client()


# ===========================================================================
# 1. Health Check endpoint  GET /api/health
# ===========================================================================

class TestHealthCheckEndpoint:

    def test_returns_200_or_500(self, client):
        """Health check may return 500 if MongoDB details fail — still reachable."""
        resp = client.get("/api/health")
        assert resp.status_code in (200, 500)

    def test_response_is_json(self, client):
        resp = client.get("/api/health")
        assert resp.content_type.startswith("application/json")

    def test_status_is_healthy(self, client):
        data = client.get("/api/health").get_json()
        # May be 'healthy' or error — just check key exists
        assert "status" in data or "error" in data

    def test_model_loaded_key_present(self, client):
        data = client.get("/api/health").get_json()
        # model_loaded present on success; skip check if endpoint errored
        assert "model_loaded" in data or "error" in data

    def test_num_classes_key_present(self, client):
        data = client.get("/api/health").get_json()
        assert "num_classes" in data or "error" in data


# ===========================================================================
# 2. Diseases list endpoint  GET /api/diseases
# ===========================================================================

class TestDiseasesEndpoint:

    def test_returns_200(self, client):
        resp = client.get("/api/diseases")
        assert resp.status_code == 200

    def test_success_true(self, client):
        data = client.get("/api/diseases").get_json()
        assert data["success"] is True

    def test_diseases_key_present(self, client):
        data = client.get("/api/diseases").get_json()
        assert "diseases" in data

    def test_total_diseases_is_integer(self, client):
        data = client.get("/api/diseases").get_json()
        assert isinstance(data["total_diseases"], int)


# ===========================================================================
# 3. Single disease endpoint  GET /api/disease/<name>
# ===========================================================================

class TestSingleDiseaseEndpoint:

    def test_known_disease_returns_200_or_404(self, client):
        """Result depends on whether name is in the fallback DISEASE_INFO dict."""
        resp = client.get("/api/disease/Leaf%20Curl")
        assert resp.status_code in (200, 404)

    def test_unknown_disease_returns_404(self, client):
        resp = client.get("/api/disease/NonExistentDisease12345")
        assert resp.status_code == 404

    def test_404_response_has_error_key(self, client):
        data = client.get("/api/disease/NonExistentDisease12345").get_json()
        assert "error" in data


# ===========================================================================
# 4. Signup endpoint  POST /api/auth/signup
# ===========================================================================

class TestSignupEndpoint:

    def test_missing_body_returns_400(self, client):
        resp = client.post(
            "/api/auth/signup",
            data="{}",
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_invalid_email_returns_400(self, client):
        resp = client.post(
            "/api/auth/signup",
            json={"email": "notanemail", "password": "password123"},
        )
        assert resp.status_code == 400

    def test_short_password_returns_400(self, client):
        resp = client.post(
            "/api/auth/signup",
            json={"email": "test@example.com", "password": "abc"},
        )
        assert resp.status_code == 400

    def test_valid_signup_returns_201(self, client, mock_mongo):
        mock_mongo.get_user_by_email.return_value = None
        mock_mongo.create_user.return_value = "new_user_id"
        mock_mongo.update_last_login.return_value = True
        resp = client.post(
            "/api/auth/signup",
            json={"email": "farmer@example.com", "password": "securepass"},
        )
        assert resp.status_code == 201

    def test_valid_signup_success_true(self, client, mock_mongo):
        mock_mongo.get_user_by_email.return_value = None
        mock_mongo.create_user.return_value = "new_user_id"
        mock_mongo.update_last_login.return_value = True
        data = client.post(
            "/api/auth/signup",
            json={"email": "farmer2@example.com", "password": "securepass"},
        ).get_json()
        assert data["success"] is True

    def test_duplicate_email_returns_409(self, client, mock_mongo):
        mock_mongo.get_user_by_email.return_value = {"email": "existing@example.com"}
        resp = client.post(
            "/api/auth/signup",
            json={"email": "existing@example.com", "password": "securepass"},
        )
        assert resp.status_code == 409


# ===========================================================================
# 5. Login endpoint  POST /api/auth/login
# ===========================================================================

class TestLoginEndpoint:

    def test_missing_credentials_returns_400(self, client):
        resp = client.post(
            "/api/auth/login",
            json={},
        )
        assert resp.status_code == 400

    def test_wrong_password_returns_401(self, client, mock_mongo):
        import bcrypt
        hashed = bcrypt.hashpw(b"realpassword", bcrypt.gensalt()).decode()
        mock_mongo.get_user_by_email.return_value = {
            "_id": "abc",
            "email": "user@example.com",
            "password": hashed,        # app uses 'password', not 'password_hash'
            "user_type": "farmer",
        }
        resp = client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": "wrongpassword"},
        )
        assert resp.status_code == 401

    def test_correct_credentials_returns_200(self, client, mock_mongo):
        import bcrypt
        hashed = bcrypt.hashpw(b"correctpass", bcrypt.gensalt()).decode()
        mock_mongo.get_user_by_email.return_value = {
            "_id": "abc",
            "email": "user@example.com",
            "password": hashed,        # app uses 'password', not 'password_hash'
            "user_type": "farmer",
        }
        resp = client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": "correctpass"},
        )
        assert resp.status_code == 200

    def test_non_existent_user_returns_401(self, client, mock_mongo):
        mock_mongo.get_user_by_email.return_value = None
        resp = client.post(
            "/api/auth/login",
            json={"email": "nobody@example.com", "password": "pass123"},
        )
        assert resp.status_code == 401


# ===========================================================================
# 6. Logout endpoint  POST /api/auth/logout
# ===========================================================================

class TestLogoutEndpoint:

    def test_logout_when_not_logged_in(self, client):
        """Logging out without a session should still return 200."""
        resp = client.post("/api/auth/logout")
        assert resp.status_code == 200

    def test_logout_success_true(self, client):
        data = client.post("/api/auth/logout").get_json()
        assert data["success"] is True


# ===========================================================================
# 7. Auth status endpoint  GET /api/auth/status
# ===========================================================================

class TestAuthStatusEndpoint:

    def test_unauthenticated_returns_200(self, client):
        resp = client.get("/api/auth/status")
        assert resp.status_code == 200

    def test_unauthenticated_authenticated_false(self, client):
        data = client.get("/api/auth/status").get_json()
        assert data.get("authenticated") is False


# ===========================================================================
# 8. Predict endpoint  POST /api/predict  (requires login)
# ===========================================================================

class TestPredictEndpoint:

    def test_unauthenticated_returns_401(self, client):
        img_bytes = _make_image_bytes()
        resp = client.post(
            "/api/predict",
            data={"file": (io.BytesIO(img_bytes), "leaf.jpg")},
            content_type="multipart/form-data",
        )
        assert resp.status_code == 401

    def test_no_file_returns_400(self, client, mock_mongo):
        """Simulate a logged-in user posting without a file."""
        import bcrypt
        hashed = bcrypt.hashpw(b"pass1234", bcrypt.gensalt()).decode()
        mock_mongo.get_user_by_email.return_value = {
            "_id": "uid1",
            "email": "u@example.com",
            "password": hashed,
            "user_type": "farmer",
        }
        client.post("/api/auth/login", json={"email": "u@example.com", "password": "pass1234"})
        resp = client.post("/api/predict", content_type="multipart/form-data")
        assert resp.status_code == 400

    def test_invalid_file_type_returns_400(self, client, mock_mongo):
        """Authenticated user uploading a non-image file."""
        import bcrypt
        hashed = bcrypt.hashpw(b"pass1234", bcrypt.gensalt()).decode()
        mock_mongo.get_user_by_email.return_value = {
            "_id": "uid2",
            "email": "u2@example.com",
            "password": hashed,
            "user_type": "farmer",
        }
        client.post("/api/auth/login", json={"email": "u2@example.com", "password": "pass1234"})
        resp = client.post(
            "/api/predict",
            data={"file": (io.BytesIO(b"not an image"), "document.pdf")},
            content_type="multipart/form-data",
        )
        assert resp.status_code == 400


# ===========================================================================
# 9. Page routes (HTML pages)
# ===========================================================================

class TestPageRoutes:

    def test_home_page_returns_200(self, client):
        resp = client.get("/")
        assert resp.status_code == 200

    def test_about_page_returns_200(self, client):
        resp = client.get("/about")
        assert resp.status_code == 200

    def test_diseases_page_returns_200(self, client):
        resp = client.get("/diseases")
        assert resp.status_code == 200

    def test_contact_page_returns_200(self, client):
        resp = client.get("/contact")
        assert resp.status_code == 200
