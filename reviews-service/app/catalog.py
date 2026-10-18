import logging

import httpx

from app import config

logger = logging.getLogger("app.catalog")

# Returned to API clients on 502; the real cause is logged, never exposed.
CATALOG_UNAVAILABLE_DETAIL = "Catalog service unavailable, please try again later"


class UpstreamError(Exception):
    """catalog-service is unreachable or answered with an unexpected error."""


class CatalogClient:
    def __init__(
        self,
        base_url: str | None = None,
        timeout: float | None = None,
        transport: httpx.BaseTransport | None = None,
    ):
        self._base_url = (base_url or config.CATALOG_SERVICE_URL).rstrip("/")
        self._timeout = config.REQUEST_TIMEOUT if timeout is None else timeout
        self._transport = transport

    def bean_exists(self, bean_id: int) -> bool:
        """True on 200, False on 404; UpstreamError on anything else."""
        url = f"{self._base_url}/api/catalog/beans/{bean_id}"
        try:
            with httpx.Client(timeout=self._timeout, transport=self._transport) as http:
                response = http.get(url)
        except httpx.HTTPError as exc:
            logger.warning("catalog-service unreachable at %s: %s", url, exc)
            raise UpstreamError(f"catalog-service unreachable: {exc}") from exc
        if response.status_code == 404:
            return False
        if response.status_code >= 400:
            logger.warning(
                "catalog-service returned %s for %s", response.status_code, url
            )
            raise UpstreamError(f"catalog-service returned {response.status_code}")
        return True


def get_catalog_client() -> CatalogClient:
    return CatalogClient()
