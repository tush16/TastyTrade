from typing import Any, Optional, Tuple, Union, List, Dict
from pydantic import BaseModel
from fastapi import HTTPException
from contextlib import contextmanager
import pyodbc
from decimal import Decimal
from datetime import datetime, date
from config.logging import logger


class RepositoryResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    status_code: Optional[int] = None
    affected_rows: Optional[int] = None


class RepositoryUtils:
    """Repository utilities for Azure SQL"""

    @staticmethod
    @contextmanager
    def get_cursor(conn):
        """Context manager for proper cursor cleanup"""
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    @staticmethod
    def _serialize_value(value: Any) -> Any:
        """Convert SQL types to JSON-serializable types"""
        if isinstance(value, Decimal):
            return float(value)
        elif isinstance(value, (datetime, date)):
            return value.isoformat()
        elif isinstance(value, bytes):
            return value.decode("utf-8", errors="ignore")
        return value

    @staticmethod
    def _row_to_dict(row, columns: List[str]) -> Dict[str, Any]:
        """Convert row to dictionary with proper serialization"""
        return {
            col: RepositoryUtils._serialize_value(val) for col, val in zip(columns, row)
        }

    @staticmethod
    def fetch_all(
        conn, query: str, params: Optional[Union[Tuple, List]] = None
    ) -> RepositoryResponse:
        """Fetch all rows from query"""
        try:
            with RepositoryUtils.get_cursor(conn) as cursor:
                cursor.execute(query, params or ())
                rows = cursor.fetchall()

                if not rows:
                    return RepositoryResponse(
                        success=False, status_code=404, error="Record not found"
                    )

                columns = [col[0] for col in cursor.description]
                data = [RepositoryUtils._row_to_dict(row, columns) for row in rows]

                return RepositoryResponse(
                    success=True, data=data, affected_rows=len(data)
                )

        except Exception as e:
            logger.error(f"fetch_all error: {e}", exc_info=True)
            return RepositoryUtils._handle_exception(e)

    @staticmethod
    def fetch_one(
        conn, query: str, params: Optional[Union[Tuple, List]] = None
    ) -> RepositoryResponse:
        """Fetch single row from query"""
        try:
            with RepositoryUtils.get_cursor(conn) as cursor:
                cursor.execute(query, params or ())
                row = cursor.fetchone()

                if not row:
                    return RepositoryResponse(
                        success=False, status_code=404, error="Record not found"
                    )

                columns = [col[0] for col in cursor.description]
                data = RepositoryUtils._row_to_dict(row, columns)

                return RepositoryResponse(success=True, data=data, affected_rows=1)

        except Exception as e:
            logger.error(f"fetch_one error: {e}", exc_info=True)
            return RepositoryUtils._handle_exception(e)

    @staticmethod
    def fetch_paginated(
        conn,
        query: str,
        page: int = 1,
        page_size: int = 10,
        params: Optional[Union[Tuple, List]] = None,
    ) -> RepositoryResponse:
        """Fetch paginated results"""
        try:
            offset = (page - 1) * page_size

            # Add pagination to query
            paginated_query = (
                f"{query} ORDER BY (SELECT NULL) OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
            )
            pagination_params = list(params or ()) + [offset, page_size]

            with RepositoryUtils.get_cursor(conn) as cursor:
                cursor.execute(paginated_query, pagination_params)
                rows = cursor.fetchall()

                columns = [col[0] for col in cursor.description]
                data = [RepositoryUtils._row_to_dict(row, columns) for row in rows]

                # Get total count
                count_query = "SELECT COUNT(*) FROM (%s) AS count_query"
                cursor.execute(count_query, (query, *(params or ())))
                total_count = cursor.fetchone()[0]

                return RepositoryResponse(
                    success=True,
                    data={
                        "items": data,
                        "page": page,
                        "page_size": page_size,
                        "total_count": total_count,
                        "total_pages": (total_count + page_size - 1) // page_size,
                    },
                    affected_rows=len(data),
                )

        except Exception as e:
            logger.error(f"fetch_paginated error: {e}", exc_info=True)
            return RepositoryUtils._handle_exception(e)

    @staticmethod
    def execute(
        conn, query: str, params: Optional[Union[Tuple, List]] = None
    ) -> RepositoryResponse:
        """Execute INSERT, UPDATE, DELETE operations"""
        try:
            with RepositoryUtils.get_cursor(conn) as cursor:
                logger.info(f"[SQL EXECUTE] Query: {query.strip()}")
                logger.info(f"[SQL EXECUTE] Params: {params}")
                if isinstance(params, dict):
                    raise ValueError(
                        "Do not pass dict as SQL parameters. Use a tuple or list."
                    )
                cursor.execute(query, params or ())
                rowcount = cursor.rowcount
                conn.commit()

                return RepositoryResponse(
                    success=True,
                    data={"affected_rows": rowcount},
                    affected_rows=rowcount,
                )

        except Exception as e:
            logger.error(f"execute error: {e}", exc_info=True)
            try:
                conn.rollback()
            except Exception as rollback_error:
                logger.warning("Rollback failed: %s", rollback_error)
            return RepositoryUtils._handle_exception(e)

    @staticmethod
    def execute_with_output(
        conn, query: str, params: Optional[Union[Tuple, List]] = None
    ) -> RepositoryResponse:
        """Execute an INSERT with OUTPUT clause and return a single row"""
        try:
            with RepositoryUtils.get_cursor(conn) as cursor:
                logger.info(f"[SQL EXECUTE] Query: {query.strip()}")
                logger.info(f"[SQL EXECUTE] Params: {params}")
                if isinstance(params, dict):
                    raise ValueError(
                        "Do not pass dict as SQL parameters. Use a tuple or list."
                    )
                cursor.execute(query, params or ())
                row = cursor.fetchone()
                conn.commit()
                data = (
                    RepositoryUtils._row_to_dict(
                        row, [col[0] for col in cursor.description]
                    )
                    if row
                    else {}
                )
                return RepositoryResponse(success=True, data=data)

        except Exception as e:
            logger.error("execute_with_output error: %s", e, exc_info=True)
            try:
                conn.rollback()
            except Exception as rollback_error:
                logger.warning("Rollback failed: %s", rollback_error)
            return RepositoryUtils._handle_exception(e)

    @staticmethod
    def execute_many(
        conn, query: str, params_list: List[Union[Tuple, List]]
    ) -> RepositoryResponse:
        """Execute batch operations"""
        try:
            with RepositoryUtils.get_cursor(conn) as cursor:
                cursor.executemany(query, params_list)
                rowcount = cursor.rowcount
                conn.commit()

                return RepositoryResponse(
                    success=True,
                    data={"affected_rows": rowcount, "batch_size": len(params_list)},
                    affected_rows=rowcount,
                )

        except Exception as e:
            logger.error(f"execute_many error: {e}", exc_info=True)
            try:
                conn.rollback()
            except Exception as rollback_error:
                logger.warning("Rollback failed: %s", rollback_error)
            return RepositoryUtils._handle_exception(e)

    @staticmethod
    def call_procedure(
        conn, proc_name: str, params: Optional[Union[Tuple, List]] = None
    ) -> RepositoryResponse:
        """Call stored procedure and return list of dicts or empty list"""

        try:
            with RepositoryUtils.get_cursor(conn) as cursor:
                # Prepare procedure call with parameter placeholders
                param_placeholders = ",".join(["?" for _ in (params or [])])
                call_query = f"EXEC {proc_name} {param_placeholders}"

                cursor.execute(call_query, params or ())

                # Try to fetch rows (if any)
                try:
                    rows = cursor.fetchall()
                    if rows:
                        columns = [col[0] for col in cursor.description]
                        data: List[dict[str, Any]] = [
                            RepositoryUtils._row_to_dict(row, columns) for row in rows
                        ]
                    else:
                        data = []
                except pyodbc.Error:
                    # No result set returned from procedure
                    data = []

                conn.commit()
                return RepositoryResponse(success=True, data=data)

        except Exception as e:
            logger.error(f"call_procedure error: {e}", exc_info=True)
            try:
                conn.rollback()
            except Exception as rollback_error:
                logger.warning("Rollback failed: %s", rollback_error)
            return RepositoryUtils._handle_exception(e)

    @staticmethod
    def _handle_exception(exc: Exception) -> RepositoryResponse:
        """Enhanced error handling for Azure SQL"""
        msg = str(exc).lower()

        # Azure SQL / SQL Server specific error patterns
        if isinstance(exc, pyodbc.IntegrityError):
            if "2627" in msg or "2601" in msg or "duplicate" in msg:
                return RepositoryResponse(
                    success=False, error="Duplicate record exists", status_code=409
                )
            elif "547" in msg or "foreign key" in msg:
                return RepositoryResponse(
                    success=False,
                    error="Foreign key constraint violation",
                    status_code=400,
                )

        elif isinstance(exc, pyodbc.ProgrammingError):
            if "syntax" in msg or "invalid column" in msg:
                return RepositoryResponse(
                    success=False,
                    error="Invalid SQL syntax or column reference",
                    status_code=400,
                )
            elif "conversion failed" in msg:
                return RepositoryResponse(
                    success=False, error="Data type conversion failed", status_code=400
                )

        elif isinstance(exc, pyodbc.DataError):
            return RepositoryResponse(
                success=False, error="Invalid data format or value", status_code=400
            )

        elif isinstance(exc, pyodbc.OperationalError):
            if "timeout" in msg:
                return RepositoryResponse(
                    success=False, error="Database operation timeout", status_code=408
                )
            elif "connection" in msg:
                return RepositoryResponse(
                    success=False, error="Database connection error", status_code=503
                )

        # Generic error
        return RepositoryResponse(
            success=False, error=f"Database error: {str(exc)}", status_code=500
        )

    @staticmethod
    def validate(
        response: RepositoryResponse, not_found_msg: str = "Resource not found"
    ) -> Any:
        """Convert RepositoryResponse to FastAPI HTTPException or return data."""
        if response.success:
            return response.data

        status = response.status_code or 500
        message = response.error or (
            not_found_msg if status == 404 else "Internal server error"
        )
        logger.error(
            "[REPO ERROR] Status: %s | Message: %s | Response: %s",
            status,
            message,
            response,
        )
        raise HTTPException(status_code=status, detail=message)

    @staticmethod
    def validate_or_none(response: RepositoryResponse) -> Optional[Any]:
        """
        Return the data if successful; return None if not found (404);
        Raise HTTPException for other errors.
        """
        if response.success:
            return response.data

        if response.status_code == 404:
            logger.warning("[REPO WARNING] Not found (404): %s", response)
            return None

        status = response.status_code or 500
        message = response.error or "Internal server error"
        logger.error(
            "[REPO ERROR] Status: %s | Message: %s | Response: %s",
            status,
            message,
            response,
        )
        raise HTTPException(status_code=status, detail=message)

    @staticmethod
    def log_dml_result(response: RepositoryResponse) -> None:
        """Logs the result of a DML (insert/update/delete) operation."""
        affected = response.get("affected_rows", 0) if response else 0
        logger.info(f"Rows affected: {affected}")
