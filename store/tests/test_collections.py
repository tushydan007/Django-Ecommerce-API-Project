from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
import pytest


@pytest.mark.django_db
class TestCreateCollection:
    def test_if_user_is_anonynous_returns_401(self, client):
        response = client.post("/store/collections/", {"title": "a"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_logged_in_user_is_not_an_admin_returns_403(self, client):
        client.force_authenticate(user=User(is_staff=False))
        response = client.post("/store/collections/", {"title": "a"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_logged_in_user_is_an_admin_but_invalid_data_returns_400(self, client):
        client.force_authenticate(user=User(is_staff=True))
        response = client.post("/store/collections/", {"title": ""})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_logged_in_user_is_an_admin_and_valid_data_returns_201(self, client):
        client.force_authenticate(user=User(is_staff=True))
        response = client.post("/store/collections/", {"title": "Home Appliances"})
        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestRetrieveCollection:
    def test_if_user_is_anonymous_returns_200(self, client):
        response = client.get("/store/collections/")
        assert response.status_code == status.HTTP_200_OK
