import aioodbc
from utils.repository import RepositoryResponse, RepositoryUtilsAsync


class FetchRepository:
    """Handles async database operations related to Fetch."""

    def __init__(self, pool: aioodbc.pool.Pool):
        self.pool = pool

    async def fetch_data(self) -> RepositoryResponse:
        """Asynchronously fetch data using aioodbc."""
        query = """
            SELECT 1
        """
        return await RepositoryUtils.fetch_all(self.pool, query)
