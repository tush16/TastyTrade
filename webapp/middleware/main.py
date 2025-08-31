import asyncpg
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
    pnfController,
)
from config.settings import settings
from config.logging import logger
from fastapi.middleware.cors import CORSMiddleware
from config.database import connect_to_db, close_db_connection, get_db
from contextlib import asynccontextmanager

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_db()
    logger.info("Logging in to Tastytrade sandbox...")
    LOGIN = settings.LOGIN
    PASSWORD = settings.PASSWORD
    session = Session(LOGIN, PASSWORD, is_test=True)
    app.state.session = session
    logger.info("Tastytrade session established.")

    yield

    await close_db_connection()

    logger.info("Application shutdown complete.")


app = FastAPI(
    title="OptionsAnalytics APIs",
    description="This API requires authentication using Session Token",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

app.include_router(authController.router)
app.include_router(equitiesController.router, dependencies=[Depends(security)])
app.include_router(optionController.router)
app.include_router(optionChainController.router)
app.include_router(futuresController.router, dependencies=[Depends(security)])
app.include_router(pnfController.router)


@app.get("/test-db")
async def test_db(conn: asyncpg.Connection = Depends(get_db)):
    row = await conn.fetchrow("SELECT NOW() as now")
    return {"db_time": row["now"]}
