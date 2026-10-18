from fastapi import APIRouter, Depends, HTTPException, Query

from app.clients import (
    CatalogClient,
    NotFoundError,
    ReviewsClient,
    UpstreamError,
    get_catalog_client,
    get_reviews_client,
)
from app.schemas import BeanScore, BeanSummary

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.get("/leaderboard", response_model=list[BeanScore])
def leaderboard(
    limit: int = Query(5, ge=1, le=20),
    catalog: CatalogClient = Depends(get_catalog_client),
    reviews: ReviewsClient = Depends(get_reviews_client),
):
    try:
        beans = catalog.list_beans()
        stats = {s.bean_id: s for s in reviews.stats()}
    except NotFoundError as exc:
        raise HTTPException(
            status_code=502, detail=f"Upstream resource not found: {exc}"
        ) from exc
    except UpstreamError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    scores = [
        BeanScore(
            bean_id=bean.id,
            name=bean.name,
            roaster=bean.roaster,
            roast=bean.roast,
            average_rating=stats[bean.id].average_rating if bean.id in stats else None,
            review_count=stats[bean.id].review_count if bean.id in stats else 0,
        )
        for bean in beans
    ]
    scores.sort(
        key=lambda s: (
            s.average_rating is None,
            -(s.average_rating or 0),
            -s.review_count,
        )
    )
    return scores[:limit]


@router.get("/beans/{bean_id}", response_model=BeanSummary)
def bean_summary(
    bean_id: int,
    catalog: CatalogClient = Depends(get_catalog_client),
    reviews: ReviewsClient = Depends(get_reviews_client),
):
    try:
        bean = catalog.get_bean(bean_id)
        bean_reviews = reviews.list_reviews(bean_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail="Bean not found") from exc
    except UpstreamError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    count = len(bean_reviews)
    average = round(sum(r.rating for r in bean_reviews) / count, 2) if count else None
    return BeanSummary(
        bean=bean,
        average_rating=average,
        review_count=count,
        latest_reviews=bean_reviews[:3],
    )
