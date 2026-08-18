from pathlib import Path


def test_requirements_do_not_include_streamlit_runtime():
    requirements = Path("requirements.txt").read_text(encoding="utf-8").lower()

    assert "streamlit" not in requirements
    assert "flask" in requirements
    assert "gunicorn" in requirements


def test_render_uses_gunicorn_start_command():
    render_config = Path("render.yaml").read_text(encoding="utf-8")

    assert "gunicorn app:app" in render_config
    assert "streamlit run" not in render_config
