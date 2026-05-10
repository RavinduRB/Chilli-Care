"""
Shared fixtures for all tests (unit, integration, system).
"""

import io
import os
import sys
import pytest
from unittest.mock import MagicMock, patch
from PIL import Image

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


# ---------------------------------------------------------------------------
# Flask app fixture (mocks heavy dependencies so no GPU / DB needed)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def app():
    """Create Flask test application with mocked external services."""

    # --- Mock TensorFlow model before importing app ---
    mock_model = MagicMock()
    mock_model.predict.return_value = [[0.1, 0.05, 0.8, 0.02, 0.01, 0.01, 0.01]]

    # --- Mock MongoDB ---
    mock_mongo = MagicMock()
    mock_mongo.connected = True
    mock_mongo.get_user_by_email.return_value = None
    mock_mongo.create_user.return_value = "mock_user_id_123"
    mock_mongo.update_last_login.return_value = True

    with patch.dict("sys.modules", {
        "tensorflow": MagicMock(),
        "tensorflow.keras": MagicMock(),
    }):
        with patch("mongodb_database.get_db", return_value=mock_mongo):
            with patch("app.model", mock_model):
                with patch("app.mongodb", mock_mongo):
                    import app as flask_app

                    flask_app.app.config.update({
                        "TESTING": True,
                        "WTF_CSRF_ENABLED": False,
                        "SECRET_KEY": "test-secret-key",
                        "MAIL_SUPPRESS_SEND": True,
                    })

                    yield flask_app.app


@pytest.fixture()
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture()
def runner(app):
    """Flask CLI test runner."""
    return app.test_cli_runner()


# ---------------------------------------------------------------------------
# Image helpers
# ---------------------------------------------------------------------------

def make_green_image_bytes(width=224, height=224, fmt="JPEG"):
    """Return bytes of a solid green RGB image (looks like a leaf)."""
    img = Image.new("RGB", (width, height), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    return buf


def make_tiny_image_bytes(width=5, height=5, fmt="JPEG"):
    """Return bytes of a very small image."""
    img = Image.new("RGB", (width, height), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    return buf


@pytest.fixture()
def green_image():
    """A valid green JPEG image BytesIO."""
    return make_green_image_bytes()
