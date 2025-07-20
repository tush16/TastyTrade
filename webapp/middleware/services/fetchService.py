from repositories.fetchRepository import FetchRepository
from serializers.fetchSerializer import FetchSerializer
from utils.repository import RepositoryUtils


class FetchService:
    """Service layer handling business logic for Fetch."""

    def __init__(self, repository: FetchRepository):
        self.repository = repository

    async def get_data_product_details_configuration(
        self
    ) -> FetchModel.FetchResponse:
        """Asynchronously fetch data product configuration details."""
        
        raw_data = await self.repository.fetch_data()
        validated_data = RepositoryUtils.validate(raw_data)
        return FetchSerializer.FetchResponse(**validated_data[0])
