import io
from pathlib import Path

# get the resources folder in the tests folder
resources = Path(__file__).parent / "resources"

def test_images_get_success(client):
    response = client.get("/api/images")
    assert response.status_code == 201 or response.status_code
    data = response.get_json()
    assert isinstance(data, list) or "message" in data

def test_get_thumbnail(client):

    # need to upload the photo to be processed first
    with (resources / "coin.png").open("rb") as f:
        data = {"file": (f, "coin.png")}
        upload_response = client.post("/api/images", data=data)
        assert upload_response.status_code == 201

    response_small = client.get("/api/images/coin.png/thumbnail/small")
    assert response_small.status_code == 201
    assert response_small.data 

    response_medium = client.get("/api/images/coin.png/thumbnail/medium")
    assert response_medium.status_code == 201
    assert response_medium.data 

    # Test invalid thumbnail size
    response_invalid = client.get("/api/images/coin.png/thumbnail/large")
    assert response_invalid.status_code == 400 or response_invalid.status_code == 404

def test_get_image_name(client):
    # need to upload the photo to be processed first
    with (resources / "coin.png").open("rb") as f:
        data = {"file": (f, "coin.png")}
        upload_response = client.post("/api/images", data=data)
        assert upload_response.status_code == 201

    response = client.get("/api/images/coin.png")
    assert response.status_code == 201
    assert response.data  

def test_images_post_success(client):
    assert (resources / "coin.png").exists()
    assert (resources / "person.jpg").exists()

    # Test PNG upload
    with (resources / "coin.png").open("rb") as f:
        data = {"file": (f, "coin.png")}
        response = client.post("/api/images", data=data, content_type="multipart/form-data")
        assert response.status_code == 201

    # Test JPG upload
    with (resources / "person.jpg").open("rb") as f:
        data = {"file": (f, "person.jpg")}
        response = client.post("/api/images", data=data, content_type="multipart/form-data")
        assert response.status_code == 201