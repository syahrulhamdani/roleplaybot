import os
from typing import Optional, Dict, Any, AsyncContextManager

import httpx
from fastapi import HTTPException
from contextlib import asynccontextmanager

from common.config_models import ConfigListResponse


class ConfigService:
    """
    Service for retrieving configurations from the Config Management API.
    """

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the ConfigService.

        Args:
            base_url: Base URL of the Config Management API
        """
        self.base_url = base_url or os.getenv(
            "CONFIG_API_BASE_URL", "http://localhost:8000"
        )
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Content-Type": "application/json"},
            timeout=30.0,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - ensure client is closed."""
        if self.client:
            await self.client.aclose()
            self.client = None

    async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle API response and raise appropriate exceptions."""
        try:
            response.raise_for_status()
            return response.json() if response.content else {}
        except httpx.HTTPStatusError as e:
            try:
                error_data = e.response.json()
                detail = error_data.get("detail", str(e))
            except:
                detail = str(e)
            raise HTTPException(status_code=e.response.status_code, detail=detail)

    async def list_configs(
        self,
        env: str,
        useCase: str,
        page: int = 1,
        size: int = 10,
        order_by: str = "createdon",
        order_direction: str = "desc",
    ) -> ConfigListResponse:
        """
        List configurations with filtering and pagination.

        Args:
            env: Environment (e.g., dev, staging, prod)
            use_case: Use case for the configuration
            page: Page number (1-based)
            size: Number of items per page
            order_by: Field to order by
            order_direction: Order direction (asc/desc)

        Returns:
            Paginated list of configurations
        """
        params = {
            "env": env,
            "useCase": useCase,
            "page": page,
            "size": size,
            "order_by": order_by,
            "order_direction": order_direction,
        }

        if not self.client:
            raise RuntimeError(
                "ConfigService client not initialized. Use 'async with ConfigService()'"
            )

        response = await self.client.get("/api/v1/configs", params=params)
        data = await self._handle_response(response)
        return ConfigListResponse(**data)
