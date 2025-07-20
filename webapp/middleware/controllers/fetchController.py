from fastapi import APIRouter, Depends
from dependencies.injectors import FetchServiceProvider
from services.fetchService import FetchService
from serializers.fetchSerializer import FetchSerializer

router = APIRouter(tags=["Fetch API"])

@router.get("/fetch", response_model=FetchModel.FetchResponse)
async def get_fetch(
    service: FetchService = Depends(lambda: FetchServiceProvider().get_service())
):
    """Get all fetch details."""
    return await service.get_fetch()
