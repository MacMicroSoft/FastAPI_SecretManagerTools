# test_main.py
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_read_main(client):
    response = client.get("/auth")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}


@pytest.fixture(scope="module")
def test_user():
    payload = {
        "username": "testuser1",
        "password": "password1234"
    }
    return payload


@pytest.fixture(scope="module")
def test_user_manager():
    payload = {
        "username": "test_manager",
        "password": "12345"
    }
    return payload


def test_login(client, test_user):
    response = client.post("/auth/login/", data=test_user)
    assert response.status_code == 200

    token = response.json()["access_token"]
    assert token is not None
    return token


def test_user_me(client, test_user):
    token = test_login(client, test_user)
    response = client.get("auth/users/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()

    user_id = data.get('id')
    assert user_id is not None

    return user_id


def test_user_create_note_visitor(client, test_user):
    token = test_login(client, test_user)
    json_content = {"title": "string", "content": "string"}
    response = client.post("/note/create/", json=json_content, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_user_delete_note_visitor(client, test_user):
    token = test_login(client, test_user)
    note_id = 14
    response = client.delete(f"/note/{note_id}/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_user_share_note_visitor(client, test_user):
    token = test_login(client, test_user)
    json_content = {
        "to_user_id": "801aaac1-0e02-4383-944d-e8d1a0510d88",
        "note_id": 13
    }
    response = client.post("/note/share/", json=json_content, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


# test_manager

def test_create_note_manager(client, test_user_manager):
    token = test_login(client, test_user_manager)
    json_content = {"title": "test1234", "content": "test1234"}
    response = client.post("/note/create/", json=json_content, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200


def test_my_list_note(client, test_user_manager):
    token = test_login(client, test_user_manager)
    response = client.get("/note/list/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200

    data = response.json()

    notes = []
    for note in data:
        if note.get("title") == "test1234":
            notes.append(note.get("note_id"))

    return notes[0]


def test_user_put_note_visitor(client, test_user, test_user_manager):
    note_id = test_my_list_note(client, test_user_manager)

    token = test_login(client, test_user)
    response = client.put(f"/note/{note_id}/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_share_note_manager(client, test_user_manager, test_user):
    token = test_login(client, test_user_manager)
    user_visitor_id = test_user_me(client, test_user)
    note_id = test_my_list_note(client, test_user_manager)

    json_content = {
        "to_user_id": user_visitor_id,
        "note_id": note_id,
    }

    response = client.post("/note/share/", json=json_content, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200

    print(user_visitor_id)
    print(note_id)


def test_get_notes_to_others_manager(client, test_user_manager):
    token = test_login(client, test_user_manager)
    response = client.get(f"/note/shared/to/others/", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200


def test_put_note_manager(client, test_user_manager):
    token = test_login(client, test_user_manager)
    note_id = test_my_list_note(client, test_user_manager)

    json_content = {
        "title": "test1234",
        "content": "put_test"
    }

    response = client.put(f"/note/{note_id}/", data=json_content, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200


def test_delete_note_manager(client, test_user_manager):
    token = test_login(client, test_user_manager)
    note_id = test_my_list_note(client, test_user_manager)

    response = client.delete(f"/note/{note_id}/", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 204


def test_get_notes_from_others_delete(client, test_user_manager):
    token = test_login(client, test_user_manager)
    response = client.get(f"/note/shared/from/others/", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404


def test_get_notes_to_others_after_delete(client, test_user_manager):
    token = test_login(client, test_user_manager)
    response = client.get(f"/note/shared/to/others/", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 404
