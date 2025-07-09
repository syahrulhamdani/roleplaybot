import os
from typing import Any, Dict, List, Optional, Union

import httpx
from fastapi import HTTPException
from loguru import logger

from common import PromptListResponse, PromptResponse, PromptType
from common.config import ENV, PROMPT_NAME, USE_CASE
from core.exceptions import PromptNotFoundException


class PromptService:
    """
    Service for retrieving prompts from the Prompt Management API.
    """

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the PromptService.

        Args:
            base_url: Base URL of the Prompt Management API
        """
        self.base_url = base_url or os.getenv(
            "PROMPT_API_BASE_URL", "http://localhost:8000"
        )
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Content-Type": "application/json"},
            timeout=30.0,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def _handle_status_code(
        self, status_code: int, response_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Check the status code and raise appropriate HTTPException if needed.

        Args:
            status_code: HTTP status code
            response_data: Optional response data for error details

        Raises:
            HTTPException: If status code indicates an error
        """
        if 200 <= status_code < 300:
            return

        detail = "An error occurred"
        if response_data and isinstance(response_data, dict):
            detail = response_data.get("detail", str(response_data))

        if status_code == 400:
            raise HTTPException(status_code=400, detail="Bad Request")
        elif status_code == 401:
            raise HTTPException(status_code=401, detail="Unauthorized")
        elif status_code == 403:
            raise HTTPException(status_code=403, detail="Forbidden")
        elif status_code == 404:
            raise HTTPException(status_code=404, detail="Not Found")
        elif status_code == 422:
            raise HTTPException(status_code=422, detail="Validation Error")
        elif status_code >= 500:
            raise HTTPException(status_code=500, detail="Internal Server Error")
        else:
            raise HTTPException(status_code=status_code, detail=detail)

    async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Handle API response and raise appropriate exceptions.

        Args:
            response: The HTTP response to handle

        Returns:
            Parsed JSON response as a dictionary

        Raises:
            HTTPException: If the response indicates an error
        """
        try:
            response_data = response.json() if response.content else {}
            self._handle_status_code(response.status_code, response_data)
            return response_data
        except ValueError:  # JSON decode error
            # If we can't parse JSON, just check the status code
            self._handle_status_code(response.status_code)
            return {}

    async def get_prompt(
        self, prompt_id: str, use_case: str, env: str = "prod", is_active: bool = True
    ) -> Optional[PromptResponse]:
        """
        Get a prompt by ID with environment and use case validation.

        Args:
            prompt_id: ID of the prompt to retrieve
            env: Expected environment (e.g., dev, staging, prod)
            use_case: Expected use case
            is_active: Whether to check if the prompt is active

        Returns:
            The requested prompt if found and matches criteria, None otherwise
        """
        try:
            response = await self.client.get(f"/api/v1/prompts/{prompt_id}")
            data = await self._handle_response(response)
            prompt = PromptResponse(**data)

            # Validate environment and use case
            if (
                prompt.env != env
                or prompt.use_case != use_case
                or (is_active and not prompt.is_active)
            ):
                return None

            return prompt
        except HTTPException as e:
            if e.status_code == 404:
                return None
            raise

    async def list_prompts(
        self,
        use_case: str,
        env: str = "prod",
        is_active: bool = True,
        page: int = 1,
        size: int = 10,
        order_by: str = "created_at",
        order_direction: str = "desc",
        prompt_name: Optional[str] = None,
        prompt_type: Optional[PromptType] = None,
        tag: Optional[str] = None,
    ) -> PromptListResponse:
        """
        List prompts with filtering and pagination.

        Args:
            page: Page number (1-based)
            size: Number of items per page
            order_by: Field to order by
            order_direction: Order direction (asc/desc)
            prompt_name: Filter by prompt name
            is_active: Filter by active status
            prompt_type: Filter by prompt type
            use_case: Filter by use case
            tag: Filter by tag
            env: Filter by environment

        Returns:
            Paginated list of prompts
        """
        params = {
            "page": page,
            "size": size,
            "order_by": order_by,
            "order_direction": order_direction,
            "is_active": str(is_active).lower(),
            "use_case": use_case,
            "env": env,
        }

        if prompt_name:
            params["prompt_name"] = prompt_name
        if prompt_type:
            params["prompt_type"] = prompt_type.value
        if tag:
            params["tag"] = tag

        response = await self.client.get("/api/v1/prompts", params=params)
        data = await self._handle_response(response)
        return PromptListResponse(**data)

    async def get_prompt_by_name(
        self, name: str, use_case: str, env: str = "prod", is_active: bool = True
    ) -> Optional[PromptResponse]:
        """
        Get a prompt by name with environment and use case validation.

        Args:
            name: Name of the prompt to retrieve
            use_case: Expected use case
            env: Expected environment (e.g., dev, staging, prod)
            is_active: Whether to check if the prompt is active

        Returns:
            The requested prompt if found and matches criteria, None otherwise
        """
        try:
            result = await self.list_prompts(
                env=env,
                use_case=use_case,
                is_active=is_active,
                prompt_name=name,
                size=1,
            )
            return result.items[0] if result.items else None
        except HTTPException as e:
            if e.status_code == 404:
                return None
            raise


async def get_latest_prompt(
    service: PromptService, prompt_name: str, use_case: str = USE_CASE, env: str = ENV
) -> Optional[PromptResponse]:
    """Fetch the latest prompt from PromptService.

    Args:
        use_case: The use case for the prompt
        env: Environment (e.g., dev, staging, prod)

    Returns:
        The latest prompt content if found, None otherwise
    """
    try:
        prompts = await service.get_prompt_by_name(
            name=prompt_name,
            use_case=use_case,
            env=env,
            is_active=True,
        )
        return prompts
    except Exception as e:
        logger.exception(f"Error fetching prompt: {e}")
        raise PromptNotFoundException(
            f"Prompt not found for {prompt_name} of {use_case} in {env}: {e}"
        )
