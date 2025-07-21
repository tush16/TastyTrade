from fastapi import FastAPI
from dotenv import load_dotenv
from webapp.middleware.controllers import authController

load_dotenv()

app = FastAPI(
    title="TastyTrade APIs",
    description="This API requires authentication using Bearer Token",
    version="0.1.0",
)

app.include_router(authController.router)
