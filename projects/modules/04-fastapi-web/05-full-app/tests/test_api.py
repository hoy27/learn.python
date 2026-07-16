# ============================================================================
# tests/test_api.py — Integration tests for the full todo API
# ============================================================================
# Shared setup — the in-memory test database, the get_db dependency override,
# and the `client` / `auth_headers` fixtures — lives in conftest.py so it is
# defined ONCE and shared with test_project.py (no cross-file pollution).
#
# These tests use FastAPI's TestClient (in-process, no real server) and cover
# both success cases and error cases (401, 404, 400).
#
# Run: pytest tests/ -v
# ============================================================================


def test_register_user(client):
    """Test that a new user can register successfully."""
    response = client.post(
        "/register",
        json={"username": "newuser", "password": "password123"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert "id" in data
    # The password should never appear in the response.
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_user(client):
    """Test that registering with an existing username returns 400."""
    # Register the first time.
    client.post("/register", json={"username": "duplicate", "password": "pass1"})

    # Try to register again with the same username.
    response = client.post("/register", json={"username": "duplicate", "password": "pass2"})

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login(client):
    """Test that a registered user can log in and receive a token."""
    # Register first.
    client.post("/register", json={"username": "loginuser", "password": "secret"})

    # Log in.
    response = client.post("/login", json={"username": "loginuser", "password": "secret"})

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    """Test that wrong password returns 401 Unauthorized."""
    client.post("/register", json={"username": "wrongpass", "password": "correct"})

    response = client.post("/login", json={"username": "wrongpass", "password": "incorrect"})

    assert response.status_code == 401


def test_create_todo(client, auth_headers):
    """Test creating a new todo with authentication."""
    response = client.post(
        "/todos",
        json={"title": "Write tests"},
        headers=auth_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Write tests"
    assert data["completed"] is False
    assert "id" in data
    assert "created_at" in data


def test_list_todos(client, auth_headers):
    """Test listing todos returns only the authenticated user's todos."""
    # Create two todos.
    client.post("/todos", json={"title": "Todo 1"}, headers=auth_headers)
    client.post("/todos", json={"title": "Todo 2"}, headers=auth_headers)

    # List todos.
    response = client.get("/todos", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Todo 1"
    assert data[1]["title"] == "Todo 2"


def test_update_todo(client, auth_headers):
    """Test updating a todo's title and completion status."""
    # Create a todo.
    create_response = client.post(
        "/todos",
        json={"title": "Original title"},
        headers=auth_headers,
    )
    todo_id = create_response.json()["id"]

    # Update it.
    response = client.put(
        f"/todos/{todo_id}",
        json={"title": "Updated title", "completed": True},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated title"
    assert data["completed"] is True


def test_delete_todo(client, auth_headers):
    """Test deleting a todo."""
    # Create a todo.
    create_response = client.post(
        "/todos",
        json={"title": "To be deleted"},
        headers=auth_headers,
    )
    todo_id = create_response.json()["id"]

    # Delete it.
    response = client.delete(f"/todos/{todo_id}", headers=auth_headers)
    assert response.status_code == 204

    # Verify it is gone.
    get_response = client.get(f"/todos/{todo_id}", headers=auth_headers)
    assert get_response.status_code == 404


def test_unauthorized_access(client):
    """Test that accessing protected endpoints without a token returns 401.

    Modern FastAPI's HTTPBearer returns 401 Unauthorized when no credentials
    are provided (older versions returned 403). 401 is the semantically
    correct status for "not authenticated" — see auth vs authz.
    """
    # Try to list todos without authentication.
    response = client.get("/todos")
    assert response.status_code == 401

def test_todo_stats(client, auth_headers):
    """stats가 현재 유저의 total/completed/pending을 정확하게 세는지?"""
    # Create a todo.
    create_response1 = client.post(
        "/todos",
        json={"title": "test todo stats 1"},
        headers=auth_headers,
    )
    create_response2 = client.post(
        "/todos",
        json={"title": "test todo stats 2"},
        headers=auth_headers,
    )
    create_response3 = client.post(
        "/todos",
        json={"title": "test todo stats 3"},
        headers=auth_headers,
    )
    todo_id1 = create_response1.json()["id"]
    todo_id2 = create_response2.json()["id"]

    # Update it.
    client.put(
        f"/todos/{todo_id1}",
        json={"title": "updated title", "completed": True},
        headers=auth_headers,
    )

    client.put(
        f"/todos/{todo_id2}",
        json={"title": "updated title", "completed": True},
        headers=auth_headers,
    )
    
    response = client.get("/todos/stats", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["total"] == 3
    assert data["completed"] == 2
    assert data["pending"] == 1