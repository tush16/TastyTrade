import asyncio
import asyncpg
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from config.logging import logger
from config.settings import settings

DATABASE_URL = settings.DATABASE_URL
pool: asyncpg.Pool | None = None

async def connect_to_db():
    """Initialize the database connection pool"""
    global pool
    logger.info("Connecting to PostgreSQL database...")
    try:
        pool = await asyncpg.create_pool(
            DATABASE_URL, 
            min_size=1, 
            max_size=10,  
            timeout=30,
            command_timeout=60,
            max_inactive_connection_lifetime=300  
        )
        logger.info("Database connection pool created successfully.")
    except Exception as e:
        logger.error(f"Failed to create database pool: {e}")
        raise

async def close_db_connection():
    """Close the database connection pool with proper cleanup"""
    global pool
    if pool:
        logger.info("Closing database connection pool...")
        try:
            await asyncio.wait_for(pool.close(), timeout=10.0)
            logger.info("Database connection pool closed successfully.")
        except asyncio.TimeoutError:
            logger.warning("Pool.close() timed out, forcing termination...")
            try:
                pool.terminate()
                logger.info("Database pool terminated (emergency).")
            except Exception as e:
                logger.error(f"Emergency termination failed: {e}")
        except Exception as e:
            logger.error(f"Error closing database pool: {e}")
        finally:
            pool = None

@asynccontextmanager
async def get_db_connection():
    """Context manager for database connections (manual usage)"""
    global pool
    if pool is None:
        raise RuntimeError("Database connection pool is not initialized.")
    
    connection = await pool.acquire()
    try:
        yield connection
    finally:
        await pool.release(connection)

async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    """FastAPI dependency for database connections (recommended)"""
    global pool
    if pool is None:
        raise RuntimeError("Database connection pool is not initialized.")
    
    connection = await pool.acquire()
    try:
        yield connection
    finally:
        await pool.release(connection)

# Utility functions for connection management
async def check_database_health():
    """Check if database connection is healthy"""
    global pool
    if pool:
        try:
            async with get_db_connection() as conn:
                result = await conn.fetchval("SELECT 1")
                return result == 1
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    return False

def get_pool_stats():
    """Get connection pool statistics"""
    global pool
    if pool:
        try:
            return pool.get_stats()
        except Exception as e:
            logger.error(f"Failed to get pool stats: {e}")
    return None