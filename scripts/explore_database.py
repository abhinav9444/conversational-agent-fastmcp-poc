"""Read-only PostgreSQL explorer for the Orion POC."""

from __future__ import annotations

import sys
from decimal import Decimal
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection

from config import get_settings


MAX_COLUMN_WIDTH = 42


def format_value(value: Any) -> str:
    """Format values consistently for terminal output."""
    if value is None:
        return "NULL"
    if isinstance(value, (float, Decimal)):
        return f"{value:,.2f}"
    return str(value).replace("\n", " ")


def print_table(rows: list[dict[str, Any]]) -> None:
    """Print query results as a readable ASCII table."""
    if not rows:
        print("  No records found.")
        return

    headers = list(rows[0].keys())
    formatted_rows = [
        [format_value(row.get(header)) for header in headers]
        for row in rows
    ]

    widths = [
        min(
            max(len(header), max(len(row[index]) for row in formatted_rows)),
            MAX_COLUMN_WIDTH,
        )
        for index, header in enumerate(headers)
    ]

    def render_row(values: list[str]) -> str:
        cells = [
            value[:width].ljust(width)
            for value, width in zip(values, widths)
        ]
        return "| " + " | ".join(cells) + " |"

    separator = "+-" + "-+-".join("-" * width for width in widths) + "-+"

    print(separator)
    print(render_row(headers))
    print(separator)
    for row in formatted_rows:
        print(render_row(row))
    print(separator)
    print(f"  {len(rows)} row(s)")


def run_question(
    connection: Connection,
    number: int,
    question: str,
    sql: str,
) -> None:
    """Execute one read-only query and display its results."""
    print(f"\n{'=' * 88}")
    print(f"QUESTION {number}: {question}")
    print("-" * 88)

    result = connection.execute(text(sql))
    rows = [dict(row) for row in result.mappings().all()]
    print_table(rows)


QUESTIONS = [
    (
        "Which tables exist in the public schema?",
        """
        SELECT table_name, table_type
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
        """,
    ),
    (
        "What columns and data types does public.prospects contain?",
        """
        SELECT
            ordinal_position,
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'prospects'
        ORDER BY ordinal_position
        """,
    ),
    (
        "What indexes exist on public.prospects?",
        """
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE schemaname = 'public'
          AND tablename = 'prospects'
        ORDER BY indexname
        """,
    ),
    (
        "How many prospects are in the database?",
        """
        SELECT COUNT(*) AS total_prospects
        FROM public.prospects
        """,
    ),
    (
        "What are the ten highest-value prospects?",
        """
        SELECT
            company_name,
            industry,
            opportunity_stage,
            opportunity_value_usd,
            region,
            risk_level
        FROM public.prospects
        ORDER BY opportunity_value_usd DESC NULLS LAST
        LIMIT 10
        """,
    ),
    (
        "Which industries are represented?",
        """
        SELECT DISTINCT industry
        FROM public.prospects
        ORDER BY industry
        """,
    ),
    (
        "Which opportunity stages are represented?",
        """
        SELECT DISTINCT opportunity_stage
        FROM public.prospects
        ORDER BY opportunity_stage
        """,
    ),
    (
        "Which regions are represented?",
        """
        SELECT DISTINCT region
        FROM public.prospects
        ORDER BY region
        """,
    ),
    (
        "Which risk levels are represented?",
        """
        SELECT DISTINCT risk_level
        FROM public.prospects
        ORDER BY risk_level
        """,
    ),
    (
        "What is the pipeline value by opportunity stage?",
        """
        SELECT
            opportunity_stage,
            COUNT(*) AS prospect_count,
            SUM(opportunity_value_usd) AS total_value_usd,
            ROUND(AVG(opportunity_value_usd), 2) AS avg_value_usd
        FROM public.prospects
        GROUP BY opportunity_stage
        ORDER BY total_value_usd DESC NULLS LAST
        """,
    ),
    (
        "How is opportunity value distributed by risk level?",
        """
        SELECT
            risk_level,
            COUNT(*) AS prospect_count,
            SUM(opportunity_value_usd) AS total_value_usd
        FROM public.prospects
        GROUP BY risk_level
        ORDER BY prospect_count DESC, risk_level
        """,
    ),
    (
        "What is the pipeline value by region?",
        """
        SELECT
            region,
            COUNT(*) AS prospect_count,
            SUM(opportunity_value_usd) AS total_value_usd
        FROM public.prospects
        GROUP BY region
        ORDER BY total_value_usd DESC NULLS LAST
        """,
    ),
]


def main() -> int:
    settings = get_settings()
    engine = create_engine(settings.database_url, pool_pre_ping=True)

    print("=" * 88)
    print("ORION POC | POSTGRESQL DATABASE EXPLORER")
    print("=" * 88)
    print("Database: configured through config.py / .env")
    print("Mode: READ ONLY — no data or schema changes")
    print(f"Questions to run: {len(QUESTIONS)}")

    try:
        with engine.connect() as connection:
            # Keep this transaction read-only even if connection settings change.
            connection.execute(text("SET TRANSACTION READ ONLY"))

            for number, (question, sql) in enumerate(QUESTIONS, start=1):
                run_question(connection, number, question, sql)

            connection.rollback()

        print(f"\n{'=' * 88}")
        print("DATABASE EXPLORATION COMPLETED SUCCESSFULLY")
        print("=" * 88)
        return 0

    except Exception as exc:
        print(f"\nDatabase exploration failed: {exc}", file=sys.stderr)
        return 1

    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
