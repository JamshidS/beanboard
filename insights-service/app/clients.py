import httpx

from app import config
from app.schemas import Bean, BeanStats, Review


class NotFoundError(Exception):
    """The upstream service answered 404."""


class UpstreamError(Exception):
    """The upstream service is unreachable or answered with an error."""


class _BaseClient:
    def __init__(self, base_url: str, timeout: float = config.REQUEST_TIMEOUT):
        self._http = httpx.Client(base_url=base_url, timeout=timeout)

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
        return response.json()


class CatalogClient(_BaseClient):
    def __init__(self, base_url: str | None = None):
        super().__init__(base_url or config.CATALOG_SERVICE_URL)

    def list_beans(self) -> list[Bean]:
        return [Bean(**item) for item in self._get("/api/catalog/beans")]

    def get_bean(self, bean_id: int) -> Bean:
        return Bean(**self._get(f"/api/catalog/beans/{bean_id}"))


class ReviewsClient(_BaseClient):
    def __init__(self, base_url: str | None = None):
        super().__init__(base_url or config.REVIEWS_SERVICE_URL)

    def list_reviews(self, bean_id: int) -> list[Review]:
        return [Review(**item) for item in self._get(f"/api/reviews/beans/{bean_id}")]

    def stats(self) -> list[BeanStats]:
        return [BeanStats(**item) for item in self._get("/api/reviews/stats")]


_catalog_client = CatalogClient()
_reviews_client = ReviewsClient()


def get_catalog_client() -> CatalogClient:
    return _catalog_client


def get_reviews_client() -> ReviewsClient:
    return _reviews_client
