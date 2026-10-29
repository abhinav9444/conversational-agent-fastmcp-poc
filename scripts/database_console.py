"""Unified Orion POC database console: database insights plus prospect CRUD.

Read-only exploration uses DATABASE_URL. CRUD operations use DATABASE_ADMIN_URL.
The conversational agent and MCP tool remain read-only.
"""

from __future__ import annotations

import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import get_settings  # noqa: E402
from scripts.prospect_crud import (  # noqa: E402
    create_prospect,
    delete_prospect,
    list_prospects,
    read_prospect,
    update_prospect,
)

MAX_COLUMN_WIDTH = 36

QUESTIONS: list[tuple[str, str]] = [
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
        SELECT ordinal_position, column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'prospects'
        ORDER BY ordinal_position
        """,
    ),
    (
        "What indexes exist on public.prospects?",
        """
        SELECT indexname, indexdef
        FROM pg_indexes
        WHERE schemaname = 'public' AND tablename = 'prospects'
        ORDER BY indexname
        """,
    ),
    (
        "How many prospects are in the database?",
        "SELECT COUNT(*) AS total_prospects FROM public.prospects",
    ),
    (
        "What are the ten highest-value prospects?",
        """
        SELECT company_name, industry, opportunity_stage, opportunity_value_usd, region, risk_level
        FROM public.prospects
        ORDER BY opportunity_value_usd DESC NULLS LAST
        LIMIT 10
        """,
    ),
    (
        "Which industries are represented?",
        "SELECT industry, COUNT(*) AS prospect_count FROM public.prospects GROUP BY industry ORDER BY prospect_count DESC, industry",
    ),
    (
        "Which opportunity stages are represented?",
        "SELECT opportunity_stage, COUNT(*) AS prospect_count FROM public.prospects GROUP BY opportunity_stage ORDER BY prospect_count DESC, opportunity_stage",
    ),
    (
        "Which regions are represented?",
        "SELECT region, COUNT(*) AS prospect_count FROM public.prospects GROUP BY region ORDER BY prospect_count DESC, region",
    ),
    (
        "How is opportunity value distributed by risk level?",
        """
        SELECT risk_level, COUNT(*) AS prospect_count,
               SUM(opportunity_value_usd) AS total_value_usd,
               ROUND(AVG(opportunity_value_usd), 2) AS avg_value_usd
        FROM public.prospects
        GROUP BY risk_level
        ORDER BY total_value_usd DESC NULLS LAST
        """,
    ),
    (
        "What is the pipeline value by opportunity stage?",
        """
        SELECT opportunity_stage, COUNT(*) AS prospect_count,
               SUM(opportunity_value_usd) AS total_value_usd,
               ROUND(AVG(opportunity_value_usd), 2) AS avg_value_usd
        FROM public.prospects
        GROUP BY opportunity_stage
        ORDER BY total_value_usd DESC NULLS LAST
        """,
    ),
    (
        "What is the pipeline value by region?",
        """
        SELECT region, COUNT(*) AS prospect_count,
               SUM(opportunity_value_usd) AS total_value_usd
        FROM public.prospects
        GROUP BY region
        ORDER BY total_value_usd DESC NULLS LAST
        """,
    ),
    (
        "Which high-risk prospects have the largest opportunities?",
        """
        SELECT company_name, industry, opportunity_stage, opportunity_value_usd, region
        FROM public.prospects
        WHERE risk_level = 'High'
        ORDER BY opportunity_value_usd DESC NULLS LAST
        """,
    ),
    (
        "What is the total pipeline value and average opportunity size?",
        """
        SELECT COUNT(*) AS prospect_count,
               COALESCE(SUM(opportunity_value_usd), 0) AS total_pipeline_usd,
               COALESCE(ROUND(AVG(opportunity_value_usd), 2), 0) AS average_opportunity_usd
        FROM public.prospects
        """,
    ),
]


def format_value(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, (float, Decimal)):
        return f"{value:,.2f}"
    return str(value).replace("\n", " ")


def print_table(rows: list[dict[str, Any]]) -> None:
    if not rows:
        print("  No records found.")
        return

    headers = list(rows[0].keys())
    formatted = [[format_value(row.get(key)) for key in headers] for row in rows]
    widths = [
        min(max(len(header), max(len(row[index]) for row in formatted)), MAX_COLUMN_WIDTH)
        for index, header in enumerate(headers)
    ]

    def render(values: list[str]) -> str:
        cells = []
        for value, width in zip(values, widths):
            # Keep wide values readable while preserving a compact terminal layout.
            shown = value if len(value) <= width else value[: width - 1] + "…"
            cells.append(shown.ljust(width))
        return "| " + " | ".join(cells) + " |"

    separator = "+-" + "-+-".join("-" * width for width in widths) + "-+"
    print(separator)
    print(render(headers))
    print(separator)
    for row in formatted:
        print(render(row))
    print(separator)
    print(f"  {len(rows)} row(s)")


def run_question(connection: Connection, number: int) -> None:
    question, sql = QUESTIONS[number - 1]
    print(f"\n{'=' * 88}\nQUESTION {number}: {question}\n{'-' * 88}")
    result = connection.execute(text(sql))
    print_table([dict(row) for row in result.mappings().all()])


def explore_database(engine: Any, selected: int | None = None) -> None:
    """Run all insight queries or one selected query in a read-only transaction."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SET TRANSACTION READ ONLY"))
            if selected is None:
                print(f"\nRunning all {len(QUESTIONS)} database insight questions...")
                for number in range(1, len(QUESTIONS) + 1):
                    run_question(connection, number)
            else:
                run_question(connection, selected)
            connection.rollback()
    except SQLAlchemyError as exc:
        print(f"\nRead-only exploration failed: {exc}")
        try:
            connection.rollback()
        except (UnboundLocalError, Exception):
            pass


def insights_menu(engine: Any) -> None:
    while True:
        print(f"\nDATABASE INSIGHTS — {len(QUESTIONS)} QUESTIONS")
        print("  A. Run all questions")
        for number, (question, _) in enumerate(QUESTIONS, start=1):
            print(f"  {number:>2}. {question}")
        print("  0. Back to main menu")
        choice = input("Select a question: ").strip().lower()
        if choice == "0":
            return
        if choice == "a":
            explore_database(engine)
            continue
        try:
            number = int(choice)
        except ValueError:
            print("Enter A, a question number, or 0.")
            continue
        if 1 <= number <= len(QUESTIONS):
            explore_database(engine, number)
        else:
            print(f"Choose a number from 1 to {len(QUESTIONS)}, A, or 0.")


def crud_menu(session: Any) -> None:
    while True:
        print(
            "\nPROSPECT CRUD — writes use DATABASE_ADMIN_URL"
            "\n  1. List all prospects (READ)"
            "\n  2. View one prospect by UUID (READ)"
            "\n  3. Create a prospect (CREATE)"
            "\n  4. Update a prospect (UPDATE)"
            "\n  5. Delete a prospect (DELETE)"
            "\n  0. Back to main menu"
        )
        choice = input("Select an operation: ").strip()
        try:
            if choice == "1":
                list_prospects(session)
            elif choice == "2":
                read_prospect(session)
            elif choice == "3":
                create_prospect(session)
            elif choice == "4":
                update_prospect(session)
            elif choice == "5":
                delete_prospect(session)
            elif choice == "0":
                return
            else:
                print("Choose 0, 1, 2, 3, 4, or 5.")
        except (SQLAlchemyError, ValueError) as exc:
            session.rollback()
            print(f"Operation failed; transaction rolled back: {exc}")


def main() -> int:
    settings = get_settings()
    # Separate connections enforce the read-only vs. administrative boundary.
    reader_engine = create_engine(settings.database_url, pool_pre_ping=True)
    admin_engine = create_engine(settings.database_admin_url, pool_pre_ping=True)
    session_factory = sessionmaker(bind=admin_engine, expire_on_commit=False)

    print("=" * 88)
    print("ORION POC | UNIFIED POSTGRESQL DATABASE CONSOLE")
    print("=" * 88)
    print("Insight queries: DATABASE_URL (read-only transaction)")
    print("CRUD operations: DATABASE_ADMIN_URL (explicit write confirmations)")
    print("The MCP server and conversational agent remain read-only.")

    try:
        # Verify the reader connection before showing the menu.
        with reader_engine.connect() as connection:
            connection.execute(text("SET TRANSACTION READ ONLY"))
            connection.execute(text("SELECT 1"))
            connection.rollback()

        with session_factory() as session:
            while True:
                print(
                    "\nMAIN MENU"
                    "\n  1. Explore database questions and results"
                    "\n  2. Manage prospects (CRUD)"
                    "\n  0. Exit"
                )
                choice = input("Select an option: ").strip()
                if choice == "1":
                    insights_menu(reader_engine)
                elif choice == "2":
                    crud_menu(session)
                elif choice == "0":
                    print("Database console closed.")
                    return 0
                else:
                    print("Choose 0, 1, or 2.")
    except SQLAlchemyError as exc:
        print(f"Database connection failed: {exc}", file=sys.stderr)
        return 1
    finally:
        reader_engine.dispose()
        admin_engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
