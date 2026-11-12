from unittest.mock import patch

from django.test import SimpleTestCase
from rest_framework.test import APIClient


class AuthViewSetTests(SimpleTestCase):
    def test_login_ignores_an_invalid_previously_saved_access_token(self):
        with patch("api.viewsets.auth_viewset.authenticate_user", return_value=None):
            response = APIClient().post(
                "/api/v1/auth/login",
                {"identifier": "client@example.com", "password": "password"},
                format="json",
                HTTP_AUTHORIZATION="Bearer invalid-token",
            )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["error"]["code"], "INVALID_CREDENTIALS")
