from pathlib import Path

# get the resources folder in the tests folder
resources = Path(__file__).parent / "resources"

def test_get_stats_success(client):
    
    with (resources / "coin.png").open("rb") as f:
        data = {"file": (f, "coin.png")}
        upload_response = client.post("/api/images", data=data)
        assert upload_response.status_code == 201

    with (resources / "person.jpg").open("rb") as f:
        data = {"file": (f, "coin.png")}
        upload_response = client.post("/api/images", data=data)
        assert upload_response.status_code == 201

    response = client.get("/api/stats")
    assert response.status_code == 201
    assert response.data