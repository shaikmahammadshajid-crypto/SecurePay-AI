from utils.ai_assistant import detect_app_intent, get_assistant_answer


def test_detect_app_intent_routes_batch_requests():
    intent = detect_app_intent("open batch prediction")

    assert intent == {"type": "navigate", "page": "batch"}


def test_detect_app_intent_routes_history_summary():
    intent = detect_app_intent("summarize my activity")

    assert intent == {"type": "history_summary"}


def test_detect_app_intent_routes_health_check():
    intent = detect_app_intent("check app health")

    assert intent == {"type": "health_check"}


def test_detect_app_intent_routes_report_generation():
    intent = detect_app_intent("generate my audit report pdf")

    assert intent == {"type": "history_report"}


def test_assistant_explains_safe_agent_limits():
    answer = get_assistant_answer("can the agent do it by itself automatically?")

    assert "user-confirmed" in answer
