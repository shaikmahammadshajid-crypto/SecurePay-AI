from app import app


def test_health_endpoint_reports_status():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code in (200, 503)
    assert "status" in response.get_json()


def test_login_page_renders_without_streamlit():
    client = app.test_client()

    response = client.get("/login")

    assert response.status_code == 200
    assert b"SecurePay AI" in response.data
    assert b"Streamlit" not in response.data


def test_dashboard_requires_login():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
