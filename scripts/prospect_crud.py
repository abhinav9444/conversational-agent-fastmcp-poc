"""Interactive CRUD utility for fictional Orion POC prospect records.

Uses DATABASE_ADMIN_URL for writes. The MCP-facing repository and
get_prospects tool remain read-only.
"""

from __future__ import annotations

import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy import create_engine, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import get_settings  # noqa: E402
from database.models import Prospect  # noqa: E402


STAGES = (
    "New", "Qualified", "In Discussion", "Proposal Sent",
    "Negotiation", "Closed Won", "Closed Lost",
)
REGIONS = ("North America", "Europe", "APAC")
RISK_LEVELS = ("Low", "Medium", "High")


def print_prospect(prospect: Prospect) -> None:
    """Print a prospect record in a readable format."""
    print("-" * 72)
    print(f"ID:                {prospect.prospect_id}")
    print(f"Company:           {prospect.company_name}")
    print(f"Industry:          {prospect.industry}")
    print(f"Description:       {prospect.opportunity_description}")
    print(f"Stage:             {prospect.opportunity_stage}")
    print(f"Opportunity value: \${prospect.opportunity_value_usd:,.2f}")
    print(f"Region:            {prospect.region}")
    print(f"Risk:              {prospect.risk_level}")
    print(f"Created:           {prospect.created_at}")
    print(f"Updated:           {prospect.updated_at}")
    print("-" * 72)


def ask_required(prompt: str, current: str | None = None) -> str:
    """Prompt for a non-empty value; Enter retains current value when supplied."""
    suffix = f" [{current}]" if current is not None else ""
    while True:
        value = input(f"{prompt}{suffix}: ").strip()
        if not value and current is not None:
            return current
        if value:
            return value
        print("This field is required.")


def ask_choice(prompt: str, choices: tuple[str, ...], current: str | None = None) -> str:
    """Prompt for a value in the database's allowed set."""
    print(f"{prompt} options: {', '.join(choices)}")
    while True:
        value = input(f"{prompt}{f' [{current}]' if current else ''}: ").strip()
        if not value and current:
            return current
        match = next((choice for choice in choices if choice.casefold() == value.casefold()), None)
        if match:
            return match
        print(f"Choose one of: {', '.join(choices)}")


def ask_value(current: Decimal | None = None) -> Decimal:
    """Prompt for a non-negative USD opportunity value."""
    while True:
        suffix = f" [{current}]" if current is not None else ""
        raw = input(f"Opportunity value in USD{suffix}: ").strip()
        if not raw and current is not None:
            return current
        try:
            value = Decimal(raw)
            if not value.is_finite() or value < 0:
                raise InvalidOperation
            return value.quantize(Decimal("0.01"))
        except (InvalidOperation, ValueError):
            print("Enter a valid non-negative amount, for example 1250000.00.")


def find_prospect(session: Session) -> Prospect | None:
    """Fetch one prospect using its exact UUID."""
    raw_id = input("Enter prospect UUID: ").strip()
    try:
        prospect_id = UUID(raw_id)
    except ValueError:
        print("That is not a valid UUID.")
        return None

    prospect = session.get(Prospect, prospect_id)
    if prospect is None:
        print("No prospect found with that ID.")
    return prospect


def list_prospects(session: Session) -> None:
    """List prospects ordered by opportunity value."""
    prospects = session.scalars(
        select(Prospect).order_by(
            Prospect.opportunity_value_usd.desc(),
            Prospect.company_name,
        )
    ).all()
    if not prospects:
        print("No prospects found.")
        return
    print(f"\nFound {len(prospects)} prospect(s):")
    for prospect in prospects:
        print_prospect(prospect)


def read_prospect(session: Session) -> None:
    """Read one prospect by UUID."""
    prospect = find_prospect(session)
    if prospect:
        print_prospect(prospect)


def create_prospect(session: Session) -> None:
    """Create a validated prospect after showing the proposed values."""
    company_name = ask_required("Company name")
    duplicate = session.scalar(
        select(Prospect.prospect_id).where(Prospect.company_name.ilike(company_name))
    )
    if duplicate is not None:
        print("A company with that name already exists; creation cancelled.")
        return

    values: dict[str, Any] = {
        "company_name": company_name,
        "industry": ask_required("Industry"),
        "opportunity_description": ask_required("Opportunity description"),
        "opportunity_stage": ask_choice("Opportunity stage", STAGES),
        "opportunity_value_usd": ask_value(),
        "region": ask_choice("Region", REGIONS),
        "risk_level": ask_choice("Risk level", RISK_LEVELS),
    }
    print("\nReview new prospect:")
    for field, value in values.items():
        print(f"  {field}: {value}")
    if input("Create this prospect? Type YES to confirm: ").strip() != "YES":
        print("Creation cancelled; no changes saved.")
        return

    prospect = Prospect(**values)
    session.add(prospect)
    session.commit()
    session.refresh(prospect)
    print("Prospect created successfully:")
    print_prospect(prospect)


def update_prospect(session: Session) -> None:
    """Update an existing prospect; blank input retains its current value."""
    prospect = find_prospect(session)
    if prospect is None:
        return

    print("\nCurrent record:")
    print_prospect(prospect)
    print("Enter replacement values. Press Enter to keep each current value.")
    proposed = {
        "company_name": ask_required("Company name", prospect.company_name),
        "industry": ask_required("Industry", prospect.industry),
        "opportunity_description": ask_required(
            "Opportunity description", prospect.opportunity_description
        ),
        "opportunity_stage": ask_choice("Opportunity stage", STAGES, prospect.opportunity_stage),
        "opportunity_value_usd": ask_value(prospect.opportunity_value_usd),
        "region": ask_choice("Region", REGIONS, prospect.region),
        "risk_level": ask_choice("Risk level", RISK_LEVELS, prospect.risk_level),
    }

    if proposed["company_name"].casefold() != prospect.company_name.casefold():
        duplicate = session.scalar(
            select(Prospect.prospect_id).where(
                Prospect.company_name.ilike(proposed["company_name"]),
                Prospect.prospect_id != prospect.prospect_id,
            )
        )
        if duplicate is not None:
            print("Another prospect already uses that company name; update cancelled.")
            return

    print("\nProposed changes:")
    for field, value in proposed.items():
        print(f"  {field}: {getattr(prospect, field)} -> {value}")
    if input("Save these changes? Type YES to confirm: ").strip() != "YES":
        print("Update cancelled; no changes saved.")
        return

    for field, value in proposed.items():
        setattr(prospect, field, value)
    session.commit()
    session.refresh(prospect)
    print("Prospect updated successfully:")
    print_prospect(prospect)


def delete_prospect(session: Session) -> None:
    """Delete one record only after explicit UUID-specific confirmation."""
    prospect = find_prospect(session)
    if prospect is None:
        return

    print("\nRecord selected for deletion:")
    print_prospect(prospect)
    confirmation = f"DELETE {prospect.prospect_id}"
    print("This permanently deletes this one prospect record.")
    if input(f"To confirm, type exactly '{confirmation}': ").strip() != confirmation:
        print("Deletion cancelled; no changes saved.")
        return

    session.delete(prospect)
    session.commit()
    print("Prospect deleted successfully.")


def main() -> int:
    settings = get_settings()
    # CRUD is intentionally separated from the read-only explorer connection.
    engine = create_engine(settings.database_admin_url, pool_pre_ping=True)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    print("=" * 72)
    print("ORION POC | PROSPECT CRUD")
    print("=" * 72)
    print("Database: configured through DATABASE_ADMIN_URL / .env")
    print("Scope: public.prospects only")
    print("Writes require explicit confirmation; delete requires the exact UUID.")

    try:
        with session_factory() as session:
            while True:
                print(
                    "\nChoose an operation:\n"
                    "  1. List all prospects (READ)\n"
                    "  2. View one prospect by UUID (READ)\n"
                    "  3. Create a prospect (CREATE)\n"
                    "  4. Update a prospect (UPDATE)\n"
                    "  5. Delete a prospect (DELETE)\n"
                    "  0. Exit"
                )
                choice = input("Selection: ").strip()
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
                        print("Exiting CRUD utility.")
                        break
                    else:
                        print("Choose 0, 1, 2, 3, 4, or 5.")
                except (SQLAlchemyError, ValueError) as exc:
                    session.rollback()
                    print(f"Operation failed; transaction rolled back: {exc}")

        return 0
    except SQLAlchemyError as exc:
        print(f"Database connection failed: {exc}", file=sys.stderr)
        return 1
    finally:
        engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
