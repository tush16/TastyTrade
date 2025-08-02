from fastapi import FastAPI, Depends
from tastytrade import Session
from dotenv import load_dotenv
from fastapi.security import HTTPBearer
from controllers import (
    authController,
    equitiesController,
    optionController,
    optionChainController,
    futuresController,
)
from config.settings import settings
from config.logging import logger

load_dotenv()

app = FastAPI(
    title="OptionsAnalytics APIs",
    description="This API requires authentication using Session Token",
    version="0.1.0",
)


@app.on_event("startup")
async def startup_event():
    logger.info("Logging in to Tastytrade sandbox...")
    LOGIN = settings.LOGIN
    PASSWORD = settings.PASSWORD
    session = Session(LOGIN, PASSWORD, is_test=True)
    app.state.session = session
    logger.info("Startup complete.")


security = HTTPBearer()

app.include_router(authController.router)
app.include_router(equitiesController.router, dependencies=[Depends(security)])
app.include_router(optionController.router)
app.include_router(optionChainController.router)
app.include_router(futuresController.router, dependencies=[Depends(security)])
