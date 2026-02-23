# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Retrieval-Augmented Generation (RAG) system for querying course materials. It uses ChromaDB for vector storage, Anthropic's Claude API for AI generation, and provides a web interface for interaction.

**Stack**: Python 3.13, FastAPI, ChromaDB, sentence-transformers, vanilla HTML/CSS/JS frontend

**Package Manager**: uv (NEVER use pip directly - always use uv for all Python operations)

## Setup and Running

**IMPORTANT**: Always use `uv` for all Python operations. Never use `pip` directly.

Install dependencies:
```bash
uv sync
```

Run the application:
```bash
./run.sh
```

Or manually:
```bash
cd backend && uv run uvicorn app:app --reload --port 8000
```

Run any Python file or script:
```bash
uv run python script.py
uv run python backend/app.py
uv run pytest  # for tests
```

**Never run**: `python script.py`, `pip install`, or `python -m` directly - always prefix with `uv run`

Access at `http://localhost:8000` (web UI) or `http://localhost:8000/docs` (API docs)

**Required**: `.env` file with `ANTHROPIC_API_KEY=your-key-here` (see `.env.example`)

## Architecture

### Core Components (backend/)

The `RAGSystem` class (backend/rag_system.py) orchestrates all components:

1. **DocumentProcessor** (backend/document_processor.py) - Parses course documents (.txt, .pdf, .docx) and extracts structured metadata (title, instructor, lessons). Chunks content into 800-character segments with 100-character overlap.

2. **VectorStore** (backend/vector_store.py) - Manages two ChromaDB collections:
   - `course_catalog`: Course metadata (titles, instructors, lessons) for semantic course name matching
   - `course_content`: Text chunks from course materials with metadata (course_title, lesson_number, chunk_index)

3. **AIGenerator** (backend/ai_generator.py) - Handles Claude API interactions with tool calling support. Uses temperature=0 and max_tokens=800. Includes a system prompt optimized to minimize meta-commentary.

4. **ToolManager & CourseSearchTool** (backend/search_tools.py) - Tool-based architecture for search:
   - CourseSearchTool provides `search_course_content` tool to Claude
   - Supports fuzzy course name matching and lesson filtering
   - ToolManager handles tool registration and execution

5. **SessionManager** (backend/session_manager.py) - Maintains conversation history (configurable MAX_HISTORY in config.py, default 2 exchanges)

### Data Flow

1. Course documents in `docs/` are loaded on startup (app.py:88-98)
2. User queries hit `/api/query` endpoint
3. RAGSystem passes query to AIGenerator with tools
4. Claude decides whether to call `search_course_content` tool
5. Tool searches ChromaDB and returns formatted results
6. Claude synthesizes final response
7. Response returned with sources extracted from tool usage

### Configuration

All settings in `backend/config.py`:
- `ANTHROPIC_MODEL`: Default is "claude-sonnet-4-20250514"
- `EMBEDDING_MODEL`: Default is "all-MiniLM-L6-v2"
- `CHUNK_SIZE`: 800, `CHUNK_OVERLAP`: 100
- `MAX_RESULTS`: 5 (search result limit)
- `MAX_HISTORY`: 2 (conversation exchanges to remember)
- `CHROMA_PATH`: "./chroma_db"

### Data Models (backend/models.py)

Three Pydantic models represent the domain:
- `Lesson`: lesson_number, title, lesson_link
- `Course`: title (unique ID), course_link, instructor, lessons[]
- `CourseChunk`: content, course_title, lesson_number, chunk_index

## Adding New Course Documents

Place .txt, .pdf, or .docx files in the `docs/` folder. They're automatically processed on app startup. The DocumentProcessor expects a specific format to extract course metadata (see backend/document_processor.py for parsing logic).

## Tool-Based Search Architecture

The system uses Anthropic's tool calling feature. When adding new tools:
1. Create a class that inherits from `Tool` (search_tools.py)
2. Implement `get_tool_definition()` and `execute()`
3. Register with `tool_manager.register_tool(your_tool)`
4. Tools are automatically passed to Claude API calls
