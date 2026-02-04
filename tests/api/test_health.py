from fastapi import status


def test_health_ok(client):
    resp = client.get("/api/v1/health")
    assert resp.status_code == status.HTTP_200_OK
    assert resp.json()["status"] == "ok"