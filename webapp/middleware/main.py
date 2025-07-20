from fastapi import FastAPI, Depends
from fastapi.security import HTTPBearer
from dotenv import load_dotenv
from controllers import (
    fetchController,
)

load_dotenv()

app = FastAPI(
    title="TastyTrade APIs",
    description="This API requires authentication using Bearer Token",
    version="0.1.0",
)

app.include_router(dim_controller.router)