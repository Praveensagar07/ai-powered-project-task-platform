"""AI Integration Service with LLM provider support and resilient fallback heuristics."""

import json
import logging
from typing import Any, Dict, List, Optional
import httpx

from app.core.config import get_settings
from app.schemas.ai import (
    AIProductivityResponse,
    AIProjectDescriptionRequest,
    AIProjectDescriptionResponse,
    AISummarizeRequest,
    AISummarizeResponse,
    AITaskGenerationRequest,
    AITaskGenerationResponse,
    AITaskItem,
)

logger = logging.getLogger("uvicorn.error")
settings = get_settings()


class AIService:
    """Manages AI integrations for task generation, summarization, and productivity insights."""

    @classmethod
    async def generate_tasks(
        cls, request: AITaskGenerationRequest
    ) -> AITaskGenerationResponse:
        """Generate structured, actionable tasks tailored to project goals."""
        # Attempt LLM call if API key is provided
        if settings.ai_api_key.strip():
            try:
                tasks_data = await cls._call_llm_for_tasks(request)
                if tasks_data and "tasks" in tasks_data:
                    validated_tasks = [AITaskItem(**t) for t in tasks_data["tasks"]]
                    return AITaskGenerationResponse(
                        project_id=request.project_id,
                        suggested_approach=tasks_data.get(
                            "suggested_approach",
                            "Iterative agile delivery broken into core milestones.",
                        ),
                        tasks=validated_tasks,
                        provider_mode="live",
                    )
            except Exception as e:
                logger.warning(f"AI Provider error during task generation: {e}. Switching to heuristic generator.")

        # Resilient Fallback Heuristic Generator
        return cls._fallback_task_generation(request)

    @classmethod
    async def summarize_task(cls, request: AISummarizeRequest) -> AISummarizeResponse:
        """Generate concise summary and action items for a task."""
        if settings.ai_api_key.strip():
            try:
                llm_res = await cls._call_llm_for_summary(request)
                if llm_res:
                    return AISummarizeResponse(
                        summary=llm_res["summary"],
                        key_deliverables=llm_res.get("key_deliverables", []),
                        suggested_action=llm_res.get("suggested_action", "Proceed with implementation."),
                        provider_mode="live",
                    )
            except Exception as e:
                logger.warning(f"AI Provider error during task summary: {e}. Switching to heuristic summary.")

        # Fallback Heuristic Summarizer
        desc = request.description or "No detailed description provided."
        first_sentence = desc.split(".")[0].strip() if "." in desc else desc[:100]
        return AISummarizeResponse(
            summary=f"Objective: {request.title}. {first_sentence}.",
            key_deliverables=[
                f"Verify requirements for {request.title}",
                "Implement and run automated test suite",
                "Perform code review and merge",
            ],
            suggested_action=f"Begin active development on {request.title} and verify against acceptance criteria.",
            provider_mode="fallback-heuristic",
        )

    @classmethod
    async def generate_project_description(
        cls, request: AIProjectDescriptionRequest
    ) -> AIProjectDescriptionResponse:
        """Generate a well-structured project description and deliverables."""
        if settings.ai_api_key.strip():
            try:
                llm_res = await cls._call_llm_for_project_desc(request)
                if llm_res:
                    return AIProjectDescriptionResponse(
                        description=llm_res["description"],
                        key_outcomes=llm_res.get("key_outcomes", []),
                        provider_mode="live",
                    )
            except Exception as e:
                logger.warning(f"AI Provider error during project description: {e}. Using heuristic generator.")

        # Fallback Generator
        desc = (
            f"An end-to-end {request.category.lower()} initiative to {request.goals.strip().lower()}. "
            f"Designed to enhance system reliability, improve developer productivity, "
            f"and deliver seamless user experiences."
        )
        return AIProjectDescriptionResponse(
            description=desc,
            key_outcomes=[
                f"Deliver complete baseline implementation for {request.title}",
                "Ensure resilient data persistence and schema integrity",
                "Integrate responsive frontend controls and telemetry",
            ],
            provider_mode="fallback-heuristic",
        )

    # --------------------------------------------------------------------------
    # Private LLM API Callers
    # --------------------------------------------------------------------------

    @classmethod
    async def _call_llm_for_tasks(cls, request: AITaskGenerationRequest) -> Optional[Dict[str, Any]]:
        system_prompt = (
            "You are an expert technical lead and agile project manager. "
            "Generate 3 to 5 clear, high-impact tasks for a project. "
            "You MUST respond ONLY with valid JSON conforming to this schema:\n"
            "{\n"
            '  "suggested_approach": "concise strategy summary",\n'
            '  "tasks": [\n'
            '    {"title": "string", "description": "string", "priority": "low|medium|high|critical", "estimated_hours": float, "tags": "string"}\n'
            "  ]\n"
            "}"
        )

        user_content = (
            f"Project: {request.project_name}\n"
            f"Context: {request.project_description or 'General development'}\n"
            f"Goals: {request.goals}\n"
            f"Target Date: {request.target_date or 'Next milestone'}\n"
        )

        url = f"{settings.ai_api_base.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.ai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.ai_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.4,
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)

    @classmethod
    async def _call_llm_for_summary(cls, request: AISummarizeRequest) -> Optional[Dict[str, Any]]:
        system_prompt = (
            "You are an AI engineering assistant. Summarize the task concisely. "
            "Return JSON matching: "
            '{"summary": "string", "key_deliverables": ["string"], "suggested_action": "string"}'
        )
        user_content = f"Title: {request.title}\nDescription: {request.description}\nPriority: {request.priority}"

        url = f"{settings.ai_api_base.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.ai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.ai_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.3,
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)

    @classmethod
    async def _call_llm_for_project_desc(cls, request: AIProjectDescriptionRequest) -> Optional[Dict[str, Any]]:
        system_prompt = (
            "You are a technical product manager. Generate a project description. "
            "Return JSON matching: "
            '{"description": "string", "key_outcomes": ["string"]}'
        )
        user_content = f"Title: {request.title}\nCategory: {request.category}\nGoals: {request.goals}"

        url = f"{settings.ai_api_base.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.ai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.ai_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.4,
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            return json.loads(content)

    # --------------------------------------------------------------------------
    # Deterministic Heuristic Fallback
    # --------------------------------------------------------------------------

    @classmethod
    def _fallback_task_generation(
        cls, request: AITaskGenerationRequest
    ) -> AITaskGenerationResponse:
        """Domain-aware heuristic task generation tailored to user input."""
        name = request.project_name.strip()
        goals = request.goals.strip()

        tasks = [
            AITaskItem(
                title=f"Architecture Specification for {name}",
                description=f"Define technical requirements, system boundaries, and API schemas to accomplish: '{goals}'.",
                priority="high",
                estimated_hours=4.0,
                tags="planning,architecture",
            ),
            AITaskItem(
                title=f"Core Data Models & Service Layer",
                description="Implement relational database tables, migrations, CRUD repositories, and service business logic.",
                priority="high",
                estimated_hours=6.0,
                tags="backend,database",
            ),
            AITaskItem(
                title=f"Interactive UI Views & Form Validation",
                description="Build responsive user interfaces, modals, and client-side validation connecting to backend endpoints.",
                priority="medium",
                estimated_hours=6.5,
                tags="frontend,ui",
            ),
            AITaskItem(
                title="Automated Test Suite & Quality Verification",
                description="Author unit tests, integration tests for error boundaries, and verify end-to-end user workflows.",
                priority="medium",
                estimated_hours=4.5,
                tags="testing,qa",
            ),
            AITaskItem(
                title="Production Deployment & Documentation",
                description="Configure production environment variables, Docker / cloud settings, and complete API user guides.",
                priority="low",
                estimated_hours=3.0,
                tags="devops,docs",
            ),
        ]

        return AITaskGenerationResponse(
            project_id=request.project_id,
            suggested_approach="Structured multi-phase development: specifications, core persistence, frontend integration, testing, and deployment.",
            tasks=tasks,
            provider_mode="fallback-heuristic",
        )
