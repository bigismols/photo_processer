import pytest
from flaskr import create_app

# fixtures will run before the tests
@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    # other setup can go here

    yield app

    # clean up / reset resources here

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

def test_images_get():
    return

def test_images_post():
    return

def test_images_id():
    return

def test_images_id_thumbnail():
    return

def test_stats():
    return