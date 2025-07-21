from fastapi import FastAPI, Depends
from dotenv import load_dotenv
from fastapi.security import HTTPBearer
from controllers import authController, stockController

load_dotenv()

app = FastAPI(
    title="TastyTrade APIs",
    description="This API requires authentication using Session Token",
    version="0.1.0",
)

security = HTTPBearer()

app.include_router(authController.router)
app.include_router(stockController.router, dependencies=[Depends(security)])
