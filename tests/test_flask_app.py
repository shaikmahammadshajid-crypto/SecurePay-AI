from app import app


def test_health_endpoint_reports_status():
    client = app.test_client()

    response = client.get("/health")

    assert response.status_code in (200, 503)
    assert "status" in response.get_json()


def test_login_page_renders_without_streamlit_or_banking_scope():
    client = app.test_client()

    response = client.get("/login")

    assert response.status_code == 200
    assert b"SecurePay AI" in response.data
    assert b"Streamlit" not in response.data
    assert b"Banking Staff" not in response.data


def test_dashboard_requires_login():
    client = app.test_client()

    response = client.get("/")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_required_pages_are_protected():
    client = app.test_client()

    for route in ["/predict", "/batch", "/analytics", "/history", "/reports", "/profile"]:
        response = client.get(route)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]


def test_admin_requires_admin_role():
    client = app.test_client()
    with client.session_transaction() as test_session:
        test_session["logged_in"] = True
        test_session["username"] = "alice"
        test_session["role"] = "user"

    response = client.get("/admin")

    assert response.status_code == 302
    assert "/" in response.headers["Location"]


def test_removed_out_of_scope_routes_are_404():
    client = app.test_client()

    assert client.get("/banking").status_code == 404
    assert client.get("/assistant").status_code == 404
    assert client.get("/reviewer-guide").status_code == 404
    assert client.get("/presentation-download").status_code == 404


def test_sample_batch_csv_downloads_required_columns():
    client = app.test_client()

    response = client.get("/sample-batch.csv")

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("text/csv")
    assert b"Time,V1,V2" in response.data
    assert b"Amount" in response.data
