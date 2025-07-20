from fastapi import Depends
from config.database import DBConn
from repositories.fetchRepository import FetchRepository
from services.fetchService import FetchService


class FetchServiceProvider:
    def __init__(self, conn=Depends(DBConn)):
        self.conn = conn

    async def get_fetch_service(self) -> FetchService:
        repository = FetchRepository(self.conn)
        return FetchService(repository)
