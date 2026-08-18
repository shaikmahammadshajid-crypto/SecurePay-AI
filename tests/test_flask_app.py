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


def test_reviewer_guide_is_public_and_explains_main_task():
    client = app.test_client()

    response = client.get("/reviewer-guide")

    assert response.status_code == 200
    assert b"Main Task of the Project" in response.data
    assert b"credit card transactions" in response.data


def test_presentation_document_downloads():
    client = app.test_client()

    response = client.get("/presentation-download")

    assert response.status_code == 200
    assert response.headers["Content-Disposition"].startswith("attachment;")
    assert b"Final Project Presentation" in response.data
