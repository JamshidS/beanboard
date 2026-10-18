import httpx
from pydantic import ValidationError

from app import config
from app.schemas import Bean, BeanStats, Review


class NotFoundError(Exception):
    """The upstream service answered 404."""


class UpstreamError(Exception):
    """The upstream service is unreachable or answered with an error."""


class _BaseClient:
    def __init__(
        self,
        base_url: str,
        timeout: float = config.REQUEST_TIMEOUT,
        transport: httpx.BaseTransport | None = None,
    ):
        self._http = httpx.Client(base_url=base_url, timeout=timeout, transport=transport)

    def _get(self, path: str):
        try:
            response = self._http.get(path)
        except httpx.HTTPError as exc:
            raise UpstreamError(f"Could not reach {self._http.base_url}: {exc}") from exc
        if response.status_code == 404:
            raise NotFoundError(path)
        if response.status_code >= 400:
            raise UpstreamError(
                f"{self._http.base_url} answered {response.status_code} for {path}"
            )
        try:
            return response.json()
        except ValueError as exc:
            raise UpstreamError(f"{self._http.base_url} returned invalid JSON for {path}") from exc

    def _parse(self, path: str, parse):
        """GET path and build models via parse(body); bad payloads become UpstreamError."""
        body = self._get(path)
        try:
            return parse(body)
        except (ValidationError, TypeError, ValueError) as exc:
            raise UpstreamError(
                f"{self._http.base_url} returned an unexpected payload for {path}"
            ) from exc


class CatalogClient(_BaseClient):
    def __init__(
        self, base_url: str | None = None, transport: httpx.BaseTransport | None = None
    ):
        super().__init__(base_url or config.CATALOG_SERVICE_URL, transport=transport)

    def list_beans(self) -> list[Bean]:
        return self._parse("/api/catalog/beans", lambda b: [Bean(**i) for i in b])

    def get_bean(self, bean_id: int) -> Bean:
        return self._parse(f"/api/catalog/beans/{bean_id}", lambda b: Bean(**b))


class ReviewsClient(_BaseClient):
    def __init__(
        self, base_url: str | None = None, transport: httpx.BaseTransport | None = None
    ):
        super().__init__(base_url or config.REVIEWS_SERVICE_URL, transport=transport)

    def list_reviews(self, bean_id: int) -> list[Review]:
        return self._parse(
            f"/api/reviews/beans/{bean_id}", lambda b: [Review(**i) for i in b]
        )

    def stats(self) -> list[BeanStats]:
        return self._parse("/api/reviews/stats", lambda b: [BeanStats(**i) for i in b])


_catalog_client = CatalogClient()
_reviews_client = ReviewsClient()


def get_catalog_client() -> CatalogClient:
    return _catalog_client


def get_reviews_client() -> ReviewsClient:
    return _reviews_client
