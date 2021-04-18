import pytest
from app import app

# see: http://flask.pocoo.org/docs/1.0/testing/
@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    yield client


def test_info(client):
    response = client.get('/')
    result = response.get_json()
    assert result is not None
    assert "message" in result
    assert result["message"] == "It Works"
