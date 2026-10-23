from typing import Literal

from fastapi import APIRouter, Query

from app.services.image_service import find_image

router = APIRouter(prefix="/images", tags=["images"])


@router.get("")
def image(
    q: str = Query(..., min_length=2, max_length=120, description="Place / hotel name"),
    kind: Literal["place", "city", "hotel"] = "place",
    exclude: str = Query("", max_length=120, description="Words to ignore when matching, e.g. the city name"),
    city: str = Query("", max_length=120),
):
    """Returns {url, source, credit, generic}; url is null when no matching photo exists."""
    return find_image(q, kind, exclude, city)
