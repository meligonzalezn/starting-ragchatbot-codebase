"""Shared test fixtures for the Course Materials RAG system.

Design notes
------------
The production app (app.py) has two module-level side-effects that break in a
test environment:

1. ``RAGSystem(config)`` – tries to start ChromaDB, load embedding models, and
   contact the Anthropic API.
2. ``app.mount("/", StaticFiles(directory="../frontend"), ...)`` – requires the
   frontend directory to exist on disk.

Rather than patching those module-level calls, this conftest builds a
*lightweight test_app* that exposes the same REST surface as production but
uses a ``MagicMock`` in place of ``RAGSystem`` and omits the static-files
mount entirely.  The mock is passed directly into the route closures so the
same object is available to both the app internals and the test assertions.
"""

import os
import sys

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient
from pydantic import BaseModel
from typing import List, Optional
from unittest.mock import MagicMock

# Make backend modules importable when pytest is run from the project root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ---------------------------------------------------------------------------
# Pydantic models
# Mirrored from app.py so test_app can validate requests/responses without
# importing the production module (and triggering its side-effects).
# ---------------------------------------------------------------------------

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    session_id: str


class CourseStats(BaseModel):
    total_courses: int
    course_titles: List[str]


# ---------------------------------------------------------------------------
# Core fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_rag_system():
    """MagicMock standing in for a live RAGSystem.

    Provides sensible default return values for the happy path.
    Individual tests override only the parts they care about.
    """
    mock = MagicMock()
    mock.session_manager.create_session.return_value = "test-session-123"
    mock.query.return_value = (
        "Python is a high-level, general-purpose programming language.",
        ["Python Basics - Lesson 1", "Python Basics - Lesson 2"],
    )
    mock.get_course_analytics.return_value = {
        "total_courses": 2,
        "course_titles": ["Python Basics", "Advanced Python"],
    }
    return mock


@pytest.fixture
def test_app(mock_rag_system):
    """Standalone FastAPI app that mirrors the production API surface.

    Differences from the real app (app.py):
    - No StaticFiles mount (no frontend directory in tests).
    - Uses mock_rag_system instead of a live RAGSystem / ChromaDB / Claude.

    The route closures capture mock_rag_system from this fixture's scope.
    Because pytest reuses fixture instances within a single test invocation,
    any test that requests both ``client`` and ``mock_rag_system`` receives
    the *same* mock object — so call-count assertions work correctly.
    """
    app = FastAPI(title="Test Course RAG System")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.post("/api/query", response_model=QueryResponse)
    async def query_documents(request: QueryRequest):
        try:
            session_id = request.session_id
            if not session_id:
                session_id = mock_rag_system.session_manager.create_session()
            answer, sources = mock_rag_system.query(request.query, session_id)
            return QueryResponse(answer=answer, sources=sources, session_id=session_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/courses", response_model=CourseStats)
    async def get_course_stats():
        try:
            analytics = mock_rag_system.get_course_analytics()
            return CourseStats(
                total_courses=analytics["total_courses"],
                course_titles=analytics["course_titles"],
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app


@pytest.fixture
def client(test_app):
    """Synchronous TestClient wrapping test_app."""
    return TestClient(test_app)


# ---------------------------------------------------------------------------
# Request payload fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def query_payload():
    """Standard query body with no session ID (triggers session creation)."""
    return {"query": "What is Python?"}


@pytest.fixture
def query_payload_with_session():
    """Query body that supplies a pre-existing session ID."""
    return {"query": "Tell me more about Python.", "session_id": "existing-session-456"}
