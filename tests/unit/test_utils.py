"""
Unit Tests for Chilli Care
--------------------------
Tests individual functions in isolation — no database, no real model,
no network calls required.

Run: pytest tests/unit/ -v
"""

import io
import sys
import os
import pytest
import numpy as np
from unittest.mock import MagicMock, patch
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


# ===========================================================================
# Helpers
# ===========================================================================

def _make_image_bytes(color=(34, 139, 34), size=(224, 224), fmt="JPEG"):
    img = Image.new("RGB", size, color=color)
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    buf.seek(0)
    return buf.read()


# ===========================================================================
# 1. Input Validation — allowed file extensions
# ===========================================================================

class TestAllowedExtensions:
    """Unit tests for file-extension validation logic (extracted from api_predict)."""

    ALLOWED = {"png", "jpg", "jpeg"}

    def _is_allowed(self, filename):
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in self.ALLOWED
        )

    def test_jpg_allowed(self):
        assert self._is_allowed("leaf.jpg") is True

    def test_jpeg_allowed(self):
        assert self._is_allowed("leaf.jpeg") is True

    def test_png_allowed(self):
        assert self._is_allowed("leaf.PNG") is True   # case-insensitive

    def test_gif_not_allowed(self):
        assert self._is_allowed("leaf.gif") is False

    def test_pdf_not_allowed(self):
        assert self._is_allowed("document.pdf") is False

    def test_no_extension_not_allowed(self):
        assert self._is_allowed("noextension") is False

    def test_empty_filename_not_allowed(self):
        assert self._is_allowed("") is False

    def test_dotfile_no_extension(self):
        # ".jpg" has no name before the dot — rsplit gives ["", "jpg"]
        assert self._is_allowed(".jpg") is True


# ===========================================================================
# 2. Email validation (same logic used in signup route)
# ===========================================================================

class TestEmailValidation:
    """Unit tests for basic email format validation."""

    def _is_valid_email(self, email: str) -> bool:
        return "@" in email and "." in email

    def test_valid_email(self):
        assert self._is_valid_email("farmer@example.com") is True

    def test_valid_email_subdomain(self):
        assert self._is_valid_email("user@mail.server.org") is True

    def test_missing_at_sign(self):
        assert self._is_valid_email("farmergmail.com") is False

    def test_missing_dot(self):
        assert self._is_valid_email("farmer@gmailcom") is False

    def test_empty_string(self):
        assert self._is_valid_email("") is False

    def test_only_at_sign(self):
        assert self._is_valid_email("@") is False


# ===========================================================================
# 3. Password validation (same logic used in signup route)
# ===========================================================================

class TestPasswordValidation:
    """Unit tests for password length validation."""

    MIN_LENGTH = 6

    def _is_valid_password(self, password: str) -> bool:
        return len(password) >= self.MIN_LENGTH

    def test_valid_password(self):
        assert self._is_valid_password("securePass1") is True

    def test_exactly_six_chars(self):
        assert self._is_valid_password("abc123") is True

    def test_five_chars_invalid(self):
        assert self._is_valid_password("abc12") is False

    def test_empty_password(self):
        assert self._is_valid_password("") is False


# ===========================================================================
# 4. get_location_from_ip — pure function (no real HTTP calls)
# ===========================================================================

class TestGetLocationFromIP:
    """Unit tests for IP geolocation helper function."""

    @pytest.fixture(autouse=True)
    def _import_fn(self):
        """Import app without triggering the model/DB load."""
        with patch("mongodb_database.get_db", return_value=MagicMock(connected=False)):
            with patch("app.model", MagicMock()):
                import app as flask_app
                self.get_location_from_ip = flask_app.get_location_from_ip

    def test_localhost_returns_local(self):
        result = self.get_location_from_ip("127.0.0.1")
        assert result["city"] == "Local"

    def test_loopback_ipv6(self):
        result = self.get_location_from_ip("::1")
        assert result["city"] == "Local"

    def test_none_returns_local(self):
        result = self.get_location_from_ip(None)
        assert result["city"] == "Local"

    def test_private_192_168(self):
        result = self.get_location_from_ip("192.168.1.100")
        assert result["city"] == "Private Network"

    def test_private_10_x(self):
        result = self.get_location_from_ip("10.0.0.5")
        assert result["city"] == "Private Network"

    def test_public_ip_calls_api(self):
        """Public IPs should trigger an HTTP call (mocked here)."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "success",
            "country": "Philippines",
            "regionName": "Central Visayas",
            "city": "Cebu City",
            "lat": 10.3157,
            "lon": 123.8854,
        }

        with patch("app.requests.get", return_value=mock_response):
            result = self.get_location_from_ip("203.0.113.10")  # TEST-NET address

        assert result["country"] == "Philippines"
        assert result["city"] == "Cebu City"

    def test_api_failure_returns_unknown_fallback(self):
        """When HTTP call fails, function should return a fallback dict with 'Unknown' values."""
        import app as flask_app
        # Use an uncached IP so the cache doesn't interfere
        uncached_ip = "198.51.100.42"  # TEST-NET-3 (RFC 5737)
        flask_app.location_cache.pop(uncached_ip, None)
        with patch("app.requests.get", side_effect=Exception("timeout")):
            result = self.get_location_from_ip(uncached_ip)
        assert isinstance(result, dict)
        assert result.get("city") == "Unknown"
        assert result.get("country") == "Unknown"


# ===========================================================================
# 5. preprocess_image — image preprocessing pipeline
# ===========================================================================

class TestPreprocessImage:
    """Unit tests for the image preprocessing function."""

    @pytest.fixture(autouse=True)
    def _import_fn(self):
        with patch("mongodb_database.get_db", return_value=MagicMock(connected=False)):
            with patch("app.model", MagicMock()):
                import app as flask_app
                self.preprocess_image = flask_app.preprocess_image

    def test_returns_tuple_of_two(self):
        img_bytes = io.BytesIO(_make_image_bytes())
        result = self.preprocess_image(img_bytes)
        assert isinstance(result, tuple) and len(result) == 2

    def test_array_shape(self):
        img_bytes = io.BytesIO(_make_image_bytes())
        img_array, _ = self.preprocess_image(img_bytes)
        # Should be (1, H, W, 3)
        assert img_array.ndim == 4
        assert img_array.shape[0] == 1
        assert img_array.shape[3] == 3

    def test_pixel_values_normalized(self):
        """All pixel values must be in [0, 1] after normalization."""
        img_bytes = io.BytesIO(_make_image_bytes())
        img_array, _ = self.preprocess_image(img_bytes)
        assert img_array.min() >= 0.0
        assert img_array.max() <= 1.0

    def test_second_element_is_pil_image(self):
        img_bytes = io.BytesIO(_make_image_bytes())
        _, pil_img = self.preprocess_image(img_bytes)
        assert isinstance(pil_img, Image.Image)


# ===========================================================================
# 6. validate_with_local_rules — local color-based validation
# ===========================================================================

class TestValidateWithLocalRules:
    """Unit tests for local plant image validation (no external API)."""

    @pytest.fixture(autouse=True)
    def _import_fn(self):
        with patch("mongodb_database.get_db", return_value=MagicMock(connected=False)):
            with patch("app.model", MagicMock()):
                import app as flask_app
                self.validate = flask_app.validate_with_local_rules

    def test_green_image_passes(self):
        """A predominantly green image should pass as a potential chilli leaf."""
        image_bytes = _make_image_bytes(color=(34, 139, 34))  # forest green
        is_valid, _ = self.validate(image_bytes)
        assert is_valid is True

    def test_pure_white_image_fails(self):
        """A pure white image is not a plant."""
        image_bytes = _make_image_bytes(color=(255, 255, 255))
        is_valid, _ = self.validate(image_bytes)
        assert is_valid is False

    def test_pure_black_image_fails(self):
        """A pure black image should not pass validation."""
        image_bytes = _make_image_bytes(color=(0, 0, 0))
        is_valid, _ = self.validate(image_bytes)
        assert is_valid is False

    def test_returns_tuple(self):
        image_bytes = _make_image_bytes(color=(34, 139, 34))
        result = self.validate(image_bytes)
        assert isinstance(result, tuple) and len(result) == 2

    def test_message_is_string(self):
        image_bytes = _make_image_bytes(color=(34, 139, 34))
        _, message = self.validate(image_bytes)
        assert isinstance(message, str)
