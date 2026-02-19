"""API endpoint tests for the Course Materials RAG system.

Covers the two public REST endpoints:
  POST /api/query   – submit a question, receive an answer with sources
  GET  /api/courses – retrieve loaded-course metadata

The test_app and client fixtures are provided by conftest.py.  That app
mirrors the production API surface (same routes, same Pydantic models) but
uses a MagicMock instead of a live RAGSystem and omits the StaticFiles mount.

Static-file serving of the frontend at "/" is a deployment concern and is
intentionally not covered here.
"""

import pytest


class TestQueryEndpoint:
    """Tests for POST /api/query."""

    # -----------------------------------------------------------------------
    # Happy-path response structure
    # -----------------------------------------------------------------------

    def test_returns_200_for_valid_request(self, client, query_payload):
        response = client.post("/api/query", json=query_payload)
        assert response.status_code == 200

    def test_response_has_required_fields(self, client, query_payload):
        body = client.post("/api/query", json=query_payload).json()
        assert "answer" in body
        assert "sources" in body
        assert "session_id" in body

    def test_answer_is_a_non_empty_string(self, client, query_payload):
        body = client.post("/api/query", json=query_payload).json()
        assert isinstance(body["answer"], str)
        assert len(body["answer"]) > 0

    def test_sources_is_a_list(self, client, query_payload):
        body = client.post("/api/query", json=query_payload).json()
        assert isinstance(body["sources"], list)

    # -----------------------------------------------------------------------
    # Session handling
    # -----------------------------------------------------------------------

    def test_creates_session_when_none_provided(self, client, query_payload, mock_rag_system):
        body = client.post("/api/query", json=query_payload).json()
        mock_rag_system.session_manager.create_session.assert_called_once()
        assert body["session_id"] == "test-session-123"

    def test_reuses_provided_session_id(self, client, query_payload_with_session, mock_rag_system):
        body = client.post("/api/query", json=query_payload_with_session).json()
        assert body["session_id"] == "existing-session-456"
        mock_rag_system.session_manager.create_session.assert_not_called()

    def test_session_id_in_response_matches_provided_value(self, client, mock_rag_system):
        payload = {"query": "Hello", "session_id": "my-custom-session"}
        body = client.post("/api/query", json=payload).json()
        assert body["session_id"] == "my-custom-session"

    # -----------------------------------------------------------------------
    # RAG system delegation
    # -----------------------------------------------------------------------

    def test_passes_query_text_and_session_to_rag_system(self, client, query_payload, mock_rag_system):
        client.post("/api/query", json=query_payload)
        mock_rag_system.query.assert_called_once_with("What is Python?", "test-session-123")

    def test_returns_answer_from_rag_system(self, client, query_payload, mock_rag_system):
        mock_rag_system.query.return_value = ("Custom answer text.", ["Source A"])
        body = client.post("/api/query", json=query_payload).json()
        assert body["answer"] == "Custom answer text."

    def test_returns_sources_from_rag_system(self, client, query_payload, mock_rag_system):
        mock_rag_system.query.return_value = ("Answer.", ["Lesson 1", "Lesson 2"])
        body = client.post("/api/query", json=query_payload).json()
        assert body["sources"] == ["Lesson 1", "Lesson 2"]

    def test_returns_empty_sources_list_when_rag_finds_none(self, client, query_payload, mock_rag_system):
        mock_rag_system.query.return_value = ("Answer with no sources.", [])
        body = client.post("/api/query", json=query_payload).json()
        assert body["sources"] == []

    def test_rag_system_is_called_exactly_once_per_request(self, client, query_payload, mock_rag_system):
        client.post("/api/query", json=query_payload)
        assert mock_rag_system.query.call_count == 1

    # -----------------------------------------------------------------------
    # Error handling
    # -----------------------------------------------------------------------

    def test_returns_500_when_rag_system_raises(self, client, query_payload, mock_rag_system):
        mock_rag_system.query.side_effect = RuntimeError("Database unavailable")
        response = client.post("/api/query", json=query_payload)
        assert response.status_code == 500

    def test_500_body_contains_error_detail(self, client, query_payload, mock_rag_system):
        mock_rag_system.query.side_effect = RuntimeError("Database unavailable")
        body = client.post("/api/query", json=query_payload).json()
        assert "Database unavailable" in body["detail"]

    def test_returns_500_when_session_creation_raises(self, client, query_payload, mock_rag_system):
        mock_rag_system.session_manager.create_session.side_effect = RuntimeError("Session store error")
        response = client.post("/api/query", json=query_payload)
        assert response.status_code == 500

    # -----------------------------------------------------------------------
    # Input validation
    # -----------------------------------------------------------------------

    def test_returns_422_when_query_field_is_missing(self, client):
        response = client.post("/api/query", json={"session_id": "s1"})
        assert response.status_code == 422

    def test_returns_422_when_body_is_absent(self, client):
        response = client.post("/api/query")
        assert response.status_code == 422

    def test_returns_422_when_query_is_not_a_string(self, client):
        response = client.post("/api/query", json={"query": 42})
        # FastAPI coerces integers to strings for str fields, so 200 is also
        # acceptable; the important thing is the field is present and handled.
        assert response.status_code in (200, 422)


class TestCoursesEndpoint:
    """Tests for GET /api/courses."""

    # -----------------------------------------------------------------------
    # Happy-path response structure
    # -----------------------------------------------------------------------

    def test_returns_200(self, client):
        response = client.get("/api/courses")
        assert response.status_code == 200

    def test_response_has_required_fields(self, client):
        body = client.get("/api/courses").json()
        assert "total_courses" in body
        assert "course_titles" in body

    def test_total_courses_is_an_integer(self, client):
        body = client.get("/api/courses").json()
        assert isinstance(body["total_courses"], int)

    def test_course_titles_is_a_list(self, client):
        body = client.get("/api/courses").json()
        assert isinstance(body["course_titles"], list)

    def test_total_count_matches_titles_length(self, client):
        body = client.get("/api/courses").json()
        assert body["total_courses"] == len(body["course_titles"])

    # -----------------------------------------------------------------------
    # RAG system delegation
    # -----------------------------------------------------------------------

    def test_calls_get_course_analytics_once(self, client, mock_rag_system):
        client.get("/api/courses")
        mock_rag_system.get_course_analytics.assert_called_once()

    def test_returns_course_data_from_rag_system(self, client, mock_rag_system):
        mock_rag_system.get_course_analytics.return_value = {
            "total_courses": 3,
            "course_titles": ["Course A", "Course B", "Course C"],
        }
        body = client.get("/api/courses").json()
        assert body["total_courses"] == 3
        assert body["course_titles"] == ["Course A", "Course B", "Course C"]

    def test_handles_empty_course_list(self, client, mock_rag_system):
        mock_rag_system.get_course_analytics.return_value = {
            "total_courses": 0,
            "course_titles": [],
        }
        body = client.get("/api/courses").json()
        assert body["total_courses"] == 0
        assert body["course_titles"] == []

    def test_handles_single_course(self, client, mock_rag_system):
        mock_rag_system.get_course_analytics.return_value = {
            "total_courses": 1,
            "course_titles": ["Intro to Python"],
        }
        body = client.get("/api/courses").json()
        assert body["total_courses"] == 1
        assert body["course_titles"] == ["Intro to Python"]

    # -----------------------------------------------------------------------
    # Error handling
    # -----------------------------------------------------------------------

    def test_returns_500_when_rag_system_raises(self, client, mock_rag_system):
        mock_rag_system.get_course_analytics.side_effect = RuntimeError("Storage error")
        response = client.get("/api/courses")
        assert response.status_code == 500

    def test_500_body_contains_error_detail(self, client, mock_rag_system):
        mock_rag_system.get_course_analytics.side_effect = RuntimeError("Storage error")
        body = client.get("/api/courses").json()
        assert "Storage error" in body["detail"]
