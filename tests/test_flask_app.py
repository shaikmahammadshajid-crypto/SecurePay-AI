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
    assert response.headers["Content-Type"].startswith(("application/pdf", "text/markdown"))


def test_public_demo_renders_actual_project_task():
    client = app.test_client()

    response = client.get("/demo")

    assert response.status_code == 200
    assert b"No-login reviewer demo" in response.data
    assert b"Main task" in response.data


def test_sample_batch_csv_downloads_required_columns():
    client = app.test_client()

    response = client.get("/sample-batch.csv")

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("text/csv")
    assert b"Time,V1,V2" in response.data
    assert b"Amount" in response.data
