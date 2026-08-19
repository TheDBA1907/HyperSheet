import os
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

import requests
from sqlalchemy import text

from app.db.session import SessionLocal


TWELVE_DATA_BASE_URL = "https://api.twelvedata.com"


class MarketDataError(Exception):
    pass


def fetch_twelve_data_history(
    symbol: str,
    interval: str = "1day",
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    outputsize: int = 5000,
):
    api_key = os.getenv("TWELVE_DATA_API_KEY")

    if not api_key:
        raise MarketDataError(
            "TWELVE_DATA_API_KEY environment variable is not set."
        )

    params = {
        "symbol": symbol,
        "interval": interval,
        "apikey": api_key,
        "outputsize": outputsize,
        "format": "JSON",
    }

    if start_date:
        params["start_date"] = start_date.isoformat()

    if end_date:
        params["end_date"] = end_date.isoformat()

    response = requests.get(
        f"{TWELVE_DATA_BASE_URL}/time_series",
        params=params,
        timeout=30,
    )

    if response.status_code >= 400:
        try:
            error_payload = response.json()
            error_message = error_payload.get("message") or error_payload.get("code") or "Unknown provider error."
        except Exception:
            error_message = f"HTTP {response.status_code}"

        raise MarketDataError(
            f"Twelve Data request failed for {symbol}: {error_message}"
        )

    data = response.json()

    if data.get("status") == "error":
        raise MarketDataError(
            data.get("message", "Unknown Twelve Data error.")
        )

    return data


def import_price_history(
    instrument_code: str,
    symbol: str,
    outputsize: int = 5000,
):
    db = SessionLocal()

    try:
        instrument = db.execute(
            text(
                """
                SELECT id
                FROM market_instruments
                WHERE code = :code
                  AND is_active = true
                """
            ),
            {"code": instrument_code},
        ).mappings().first()

        if not instrument:
            raise MarketDataError(
                f"Instrument not found: {instrument_code}"
            )

        data = fetch_twelve_data_history(
            symbol=symbol,
            interval="1day",
            outputsize=outputsize,
        )

        values = data.get("values", [])

        if not values:
            raise MarketDataError(
                f"No historical data returned for {symbol}"
            )

        imported = 0

        for row in values:
            db.execute(
                text(
                    """
                    INSERT INTO market_history (
                        instrument_id,
                        date,
                        open,
                        high,
                        low,
                        close,
                        volume,
                        source,
                        updated_at
                    )
                    VALUES (
                        :instrument_id,
                        :date,
                        :open,
                        :high,
                        :low,
                        :close,
                        :volume,
                        :source,
                        CURRENT_TIMESTAMP
                    )
                    ON CONFLICT (instrument_id, date)
                    DO UPDATE SET
                        open = EXCLUDED.open,
                        high = EXCLUDED.high,
                        low = EXCLUDED.low,
                        close = EXCLUDED.close,
                        volume = EXCLUDED.volume,
                        source = EXCLUDED.source,
                        updated_at = CURRENT_TIMESTAMP
                    """
                ),
                {
                    "instrument_id": instrument["id"],
                    "date": row["datetime"],
                    "open": Decimal(row["open"]) if row.get("open") else None,
                    "high": Decimal(row["high"]) if row.get("high") else None,
                    "low": Decimal(row["low"]) if row.get("low") else None,
                    "close": Decimal(row["close"]) if row.get("close") else None,
                    "volume": Decimal(row["volume"]) if row.get("volume") else None,
                    "source": "twelve_data",
                },
            )

            imported += 1

        db.execute(
            text(
                """
                UPDATE market_instruments
                SET
                    source = 'twelve_data',
                    symbol = :symbol,
                    source_series = :symbol,
                    updated_at = CURRENT_TIMESTAMP
                WHERE code = :code
                """
            ),
            {
                "code": instrument_code,
                "symbol": symbol,
            },
        )

        db.commit()

        print(
            f"{instrument_code}: {imported} rows imported successfully."
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def backfill_price_history(
    instrument_code: str,
    symbol: str,
    years_per_batch: int = 10,
    earliest_year: int = 1926,
):
    db = SessionLocal()

    try:
        instrument = db.execute(
            text(
                """
                SELECT id
                FROM market_instruments
                WHERE code = :code
                  AND is_active = true
                """
            ),
            {"code": instrument_code},
        ).mappings().first()

        if not instrument:
            raise MarketDataError(
                f"Instrument not found: {instrument_code}"
            )

        oldest_date = db.execute(
            text(
                """
                SELECT MIN(date)
                FROM market_history
                WHERE instrument_id = :instrument_id
                """
            ),
            {
                "instrument_id": instrument["id"]
            },
        ).scalar_one_or_none()

        if not oldest_date:
            raise MarketDataError(
                f"No existing history found for {instrument_code}. "
                "Run import_price_history first."
            )

        print(
            f"{instrument_code}: current oldest date = {oldest_date}"
        )

        current_end = oldest_date - timedelta(days=1)

        total_imported = 0

        while current_end.year >= earliest_year:

            batch_start_year = max(
                earliest_year,
                current_end.year - years_per_batch + 1,
            )

            batch_start = date(
                batch_start_year,
                1,
                1,
            )

            if batch_start >= current_end:
                print(
                    f"Reached configured lower boundary ({earliest_year}). "
                    "Backfill finished."
                )
                break

            print(
                f"Fetching {instrument_code}: "
                f"{batch_start} -> {current_end}"
            )

            try:
                data = fetch_twelve_data_history(
                    symbol=symbol,
                    interval="1day",
                    start_date=batch_start,
                    end_date=current_end,
                    outputsize=5000,
                )

            except MarketDataError as exc:
                print(
                    f"Provider returned no usable data: {exc}"
                )
                break

            values = data.get("values", [])

            if not values:
                print(
                    "No older data returned. Backfill finished."
                )
                break

            batch_imported = 0

            for row in values:
                db.execute(
                    text(
                        """
                        INSERT INTO market_history (
                            instrument_id,
                            date,
                            open,
                            high,
                            low,
                            close,
                            volume,
                            source,
                            updated_at
                        )
                        VALUES (
                            :instrument_id,
                            :date,
                            :open,
                            :high,
                            :low,
                            :close,
                            :volume,
                            :source,
                            CURRENT_TIMESTAMP
                        )
                        ON CONFLICT (instrument_id, date)
                        DO UPDATE SET
                            open = EXCLUDED.open,
                            high = EXCLUDED.high,
                            low = EXCLUDED.low,
                            close = EXCLUDED.close,
                            volume = EXCLUDED.volume,
                            source = EXCLUDED.source,
                            updated_at = CURRENT_TIMESTAMP
                        """
                    ),
                    {
                        "instrument_id": instrument["id"],
                        "date": row["datetime"],
                        "open": Decimal(row["open"]) if row.get("open") else None,
                        "high": Decimal(row["high"]) if row.get("high") else None,
                        "low": Decimal(row["low"]) if row.get("low") else None,
                        "close": Decimal(row["close"]) if row.get("close") else None,
                        "volume": Decimal(row["volume"]) if row.get("volume") else None,
                        "source": "twelve_data",
                    },
                )

                batch_imported += 1

            db.commit()

            total_imported += batch_imported

            returned_dates = [
                date.fromisoformat(row["datetime"][:10])
                for row in values
            ]

            returned_oldest = min(returned_dates)

            print(
                f"Imported {batch_imported} rows. "
                f"Oldest returned date: {returned_oldest}"
            )

            if returned_oldest >= oldest_date:
                print(
                    "Provider did not return older history. "
                    "Stopping to avoid an endless loop."
                )
                break

            oldest_date = returned_oldest
            current_end = oldest_date - timedelta(days=1)

        print(
            f"{instrument_code}: backfill completed. "
            f"Additional rows processed: {total_imported}"
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()