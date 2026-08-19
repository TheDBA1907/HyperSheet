from uuid import uuid4

from sqlalchemy import text

from app.data.market_instruments import MARKET_INSTRUMENTS
from app.db.session import SessionLocal


def seed_market_instruments():
    db = SessionLocal()

    try:
        for instrument in MARKET_INSTRUMENTS:
            db.execute(
                text(
                    """
                    INSERT INTO market_instruments (
                        id,
                        code,
                        name,
                        category,
                        source,
                        unit,
                        frequency,
                        is_active
                    )
                    VALUES (
                        :id,
                        :code,
                        :name,
                        :category,
                        :source,
                        :unit,
                        :frequency,
                        true
                    )
                    ON CONFLICT (code)
                    DO UPDATE SET
                        name = EXCLUDED.name,
                        category = EXCLUDED.category,
                        source = EXCLUDED.source,
                        unit = EXCLUDED.unit,
                        frequency = EXCLUDED.frequency,
                        is_active = true,
                        updated_at = CURRENT_TIMESTAMP
                    """
                ),
                {
                    "id": str(uuid4()),
                    "code": instrument["code"],
                    "name": instrument["name"],
                    "category": instrument["category"],
                    "source": "pending",
                    "unit": instrument.get("unit"),
                    "frequency": "daily",
                },
            )

        db.commit()

        count = db.execute(
            text("SELECT COUNT(*) FROM market_instruments")
        ).scalar_one()

        print(f"Market instruments seeded successfully. Total rows: {count}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_market_instruments()