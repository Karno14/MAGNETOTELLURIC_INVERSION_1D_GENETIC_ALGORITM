"""
Database connection module for PostgreSQL analytic database.
Follows the pattern from svc-time-table-report.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional
import psycopg2
from config.settings import CONFIG

logger = logging.getLogger(__name__)


def get_connection(config: Optional[Dict[str, Any]] = None):
    """
    Create and return a new PostgreSQL connection to datamart_analytic.

    Args:
        config (dict, optional): Configuration dictionary containing DB credentials.
                                 If None, falls back to global CONFIG.

    Returns:
        psycopg2 connection object.
    """
    cfg = config if config is not None else (CONFIG or {})

    host = cfg.get("DB_HOST", "127.0.0.1")
    port = int(cfg.get("DB_PORT", 1244))
    db_name = cfg.get("DB_NAME", "datamart_analytic")
    db_user = cfg.get("DB_USER", "auser")
    db_password = cfg.get("DB_PASSWORD", "***********")

    logger.info(
        f"Connecting to PostgreSQL database: {db_name} at {host}:{port} as user '{db_user}'"
    )

    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=db_name,
            user=db_user,
            password=db_password,
            connect_timeout=10,
        )
        logger.info("Successfully connected to PostgreSQL analytic database.")
        return conn
    except Exception as exc:
        logger.error(
            f"Failed to connect to PostgreSQL ({host}:{port}/{db_name}): {exc}. "
            "Please check if your SSH tunnel / database service is active on port 1244, "
            "or set DATA_SOURCE = 'txt' in param_input.py to use local data."
        )
        raise

