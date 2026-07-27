"""
Throwaway script to pressure-test the full flow: two users independently
forming the same connection, and confirming idempotency.

Run your FastAPI server first (uvicorn app.main:app --reload), then:
    python test_flow.py

Not a real test suite — no assertions library, no fixtures, no cleanup.
Just enough to see the actual behavior and catch anything obviously wrong.
"""

import requests

BASE_URL = "http://localhost:8000"


def signup_and_login(username: str, password: str) -> str:
    """Returns an access token for the given user, creating them if needed."""
    signup_resp = requests.post(
        f"{BASE_URL}/auth/signup",
        json={"username": username, "password": password},
    )
    # 409 just means this user already exists from a previous run — fine.
    print(f"signup({username}): {signup_resp.status_code}")

    login_resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password},
    )
    print(f"login({username}): {login_resp.status_code}")
    login_resp.raise_for_status()
    return login_resp.json()["access_token"]


def save_song(token: str, mb_id: str, title: str, artist: str) -> int:
    resp = requests.post(
        f"{BASE_URL}/songs",
        json={"mb_id": mb_id, "title": title, "artist": artist},
    )
    print(f"save_song({title}): {resp.status_code} -> {resp.json()}")
    resp.raise_for_status()
    return resp.json()["id"]


def create_connection(token: str, song_1_id: int, song_2_id: int) -> dict:
    resp = requests.post(
        f"{BASE_URL}/connections",
        json={"song_1_id": song_1_id, "song_2_id": song_2_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    print(f"create_connection: {resp.status_code} -> {resp.json()}")
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    print("--- setting up two users ---")
    token_alice = signup_and_login("alice", "password123")
    token_bob = signup_and_login("bob", "password123")

    print("\n--- saving two songs (using a real-looking fake MBID) ---")
    song_1_id = save_song(
        token_alice, "b1a9c0e9-d987-4042-ae91-78d6a3267d69", "Song One", "Artist A"
    )
    song_2_id = save_song(
        token_alice, "c2b8d1f0-e098-5153-bf02-89e7b4378e70", "Song Two", "Artist B"
    )

    print("\n--- alice forms the connection ---")
    result_1 = create_connection(token_alice, song_1_id, song_2_id)

    print("\n--- alice forms it again (should be a no-op, same connection id) ---")
    result_2 = create_connection(token_alice, song_1_id, song_2_id)
    assert result_1["id"] == result_2["id"], "Expected the same connection, got a new one!"

    print("\n--- bob independently forms the same connection ---")
    result_3 = create_connection(token_bob, song_1_id, song_2_id)
    assert result_3["id"] == result_1["id"], "Expected bob to reuse alice's connection!"

    print("\n--- all checks passed ---")