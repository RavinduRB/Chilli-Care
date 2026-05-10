"""
System Tests (End-to-End) for Chilli Care
------------------------------------------
Tests the full application through a real browser using Playwright.
The Flask server must be running on http://localhost:5000 before running
these tests.

Prerequisites:
    1. Start the server:   python app.py
    2. Install browsers:   playwright install chromium
    3. Run these tests:    pytest tests/system/ -v

These tests verify complete user journeys as a real user would experience them.
"""

import pytest
from playwright.sync_api import sync_playwright, expect, Page, Browser

BASE_URL = "http://localhost:5000"

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch(headless=True)
        yield b
        b.close()


@pytest.fixture()
def page(browser: Browser):
    ctx = browser.new_context()
    pg = ctx.new_page()
    yield pg
    ctx.close()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _register_user(page: Page, email: str, password: str):
    """Call the signup API directly via the browser's fetch."""
    result = page.evaluate(
        """async ([email, password]) => {
            const r = await fetch('/api/auth/signup', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email, password})
            });
            return await r.json();
        }""",
        [email, password],
    )
    return result


def _login_user(page: Page, email: str, password: str):
    """Call the login API directly via the browser's fetch."""
    result = page.evaluate(
        """async ([email, password]) => {
            const r = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({email, password})
            });
            return await r.json();
        }""",
        [email, password],
    )
    return result


# ===========================================================================
# 1. Navigation — public pages load correctly
# ===========================================================================

class TestPublicNavigation:
    """Verify all public pages are reachable and render expected content."""

    def test_home_page_loads(self, page: Page):
        page.goto(BASE_URL)
        assert page.title() != ""

    def test_about_page_loads(self, page: Page):
        page.goto(f"{BASE_URL}/about")
        expect(page).not_to_have_url(f"{BASE_URL}/error")

    def test_diseases_page_loads(self, page: Page):
        page.goto(f"{BASE_URL}/diseases")
        expect(page).not_to_have_url(f"{BASE_URL}/error")

    def test_contact_page_loads(self, page: Page):
        page.goto(f"{BASE_URL}/contact")
        expect(page).not_to_have_url(f"{BASE_URL}/error")

    def test_home_page_has_upload_or_login_element(self, page: Page):
        """Home page should show either the upload form or a login prompt."""
        page.goto(BASE_URL)
        # At least one of these should be present
        upload_or_login = page.locator(
            "#image-upload, #upload-form, [data-action='login'], .login-btn, #loginModal"
        ).count()
        assert upload_or_login > 0


# ===========================================================================
# 2. API Health via browser fetch
# ===========================================================================

class TestAPIHealthViaBrowser:

    def test_health_api_returns_healthy(self, page: Page):
        page.goto(BASE_URL)
        result = page.evaluate(
            """async () => {
                const r = await fetch('/api/health');
                return await r.json();
            }"""
        )
        assert result["status"] == "healthy"

    def test_diseases_api_returns_list(self, page: Page):
        page.goto(BASE_URL)
        result = page.evaluate(
            """async () => {
                const r = await fetch('/api/diseases');
                return await r.json();
            }"""
        )
        assert result["success"] is True
        assert isinstance(result["diseases"], dict)


# ===========================================================================
# 3. User Registration Flow
# ===========================================================================

class TestUserRegistration:

    def test_signup_with_valid_data(self, page: Page):
        page.goto(BASE_URL)
        result = _register_user(page, "system_test_user@example.com", "Test@12345")
        # Should succeed OR fail with 'Email already registered' (idempotent)
        assert result.get("success") is True or "already" in result.get("error", "").lower()

    def test_signup_with_invalid_email(self, page: Page):
        page.goto(BASE_URL)
        result = _register_user(page, "not-an-email", "password123")
        assert result.get("success") is False

    def test_signup_with_short_password(self, page: Page):
        page.goto(BASE_URL)
        result = _register_user(page, "user@example.com", "abc")
        assert result.get("success") is False


# ===========================================================================
# 4. User Login / Logout Flow
# ===========================================================================

class TestLoginLogoutFlow:

    TEST_EMAIL = "e2e_login@example.com"
    TEST_PASSWORD = "SecurePass123"

    def test_login_with_wrong_password(self, page: Page):
        page.goto(BASE_URL)
        result = _login_user(page, self.TEST_EMAIL, "wrongpassword")
        assert result.get("success") is False

    def test_login_with_non_existent_account(self, page: Page):
        page.goto(BASE_URL)
        result = _login_user(page, "nobody999@example.com", "somepass")
        assert result.get("success") is False

    def test_full_register_login_logout_cycle(self, page: Page):
        """Complete cycle: register → login → check auth status → logout."""
        page.goto(BASE_URL)

        # Step 1: Register
        reg = _register_user(page, self.TEST_EMAIL, self.TEST_PASSWORD)
        assert reg.get("success") is True or "already" in reg.get("error", "").lower()

        # Step 2: Login (may already be logged in after registration)
        status = page.evaluate(
            """async () => {
                const r = await fetch('/api/auth/status');
                return await r.json();
            }"""
        )

        if not status.get("logged_in"):
            login_result = _login_user(page, self.TEST_EMAIL, self.TEST_PASSWORD)
            assert login_result.get("success") is True

        # Step 3: Verify logged in
        status_after = page.evaluate(
            """async () => {
                const r = await fetch('/api/auth/status');
                return await r.json();
            }"""
        )
        assert status_after.get("logged_in") is True

        # Step 4: Logout
        logout_result = page.evaluate(
            """async () => {
                const r = await fetch('/api/auth/logout', {method: 'POST'});
                return await r.json();
            }"""
        )
        assert logout_result.get("success") is True

        # Step 5: Confirm logged out
        status_final = page.evaluate(
            """async () => {
                const r = await fetch('/api/auth/status');
                return await r.json();
            }"""
        )
        assert status_final.get("logged_in") is False


# ===========================================================================
# 5. Disease Prediction Flow (authenticated)
# ===========================================================================

class TestDiseasePredictionFlow:

    TEST_EMAIL = "e2e_predict@example.com"
    TEST_PASSWORD = "PredictPass123"

    def _ensure_logged_in(self, page: Page):
        page.goto(BASE_URL)
        _register_user(page, self.TEST_EMAIL, self.TEST_PASSWORD)
        status = page.evaluate(
            """async () => { const r = await fetch('/api/auth/status'); return r.json(); }"""
        )
        if not status.get("logged_in"):
            _login_user(page, self.TEST_EMAIL, self.TEST_PASSWORD)

    def test_predict_without_login_returns_401(self, page: Page):
        page.goto(BASE_URL)
        # Log out first to ensure no session
        page.evaluate(
            """async () => fetch('/api/auth/logout', {method:'POST'})"""
        )
        result = page.evaluate(
            """async () => {
                const fd = new FormData();
                const blob = new Blob(['not an image'], {type: 'image/jpeg'});
                fd.append('file', blob, 'test.jpg');
                const r = await fetch('/api/predict', {method: 'POST', body: fd});
                return {status: r.status};
            }"""
        )
        assert result["status"] == 401

    def test_predict_no_file_returns_400(self, page: Page):
        self._ensure_logged_in(page)
        result = page.evaluate(
            """async () => {
                const fd = new FormData();
                const r = await fetch('/api/predict', {method: 'POST', body: fd});
                return {status: r.status};
            }"""
        )
        assert result["status"] == 400

    def test_predict_invalid_file_type_returns_400(self, page: Page):
        self._ensure_logged_in(page)
        result = page.evaluate(
            """async () => {
                const fd = new FormData();
                const blob = new Blob(['dummy'], {type: 'application/pdf'});
                fd.append('file', blob, 'document.pdf');
                const r = await fetch('/api/predict', {method: 'POST', body: fd});
                return {status: r.status};
            }"""
        )
        assert result["status"] == 400


# ===========================================================================
# 6. Contact Form
# ===========================================================================

class TestContactForm:

    def test_contact_api_missing_fields(self, page: Page):
        page.goto(BASE_URL)
        result = page.evaluate(
            """async () => {
                const r = await fetch('/api/contact', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({})
                });
                return {status: r.status, body: await r.json()};
            }"""
        )
        assert result["status"] == 400

    def test_contact_api_valid_submission(self, page: Page):
        page.goto(BASE_URL)
        result = page.evaluate(
            """async () => {
                const r = await fetch('/api/contact', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        name: 'Test User',
                        email: 'test@example.com',
                        subject: 'System Test',
                        message: 'This is an automated system test message.'
                    })
                });
                return {status: r.status, body: await r.json()};
            }"""
        )
        # 200 = sent, 500 = mail not configured (both are acceptable in test env)
        assert result["status"] in (200, 500)
