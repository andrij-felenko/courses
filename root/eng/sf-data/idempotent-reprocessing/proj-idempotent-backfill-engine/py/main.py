import datetime
import hashlib
import sqlite3
from typing import List, Dict, Any, Tuple, Optional

class IdempotentBackfillEngine:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_storage()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA synchronous = NORMAL;")
        return conn

    def _init_storage(self) -> None:
        """Ініціалізація сирих логів, історичних тарифів та агрегатних таблиць."""
        with self._get_connection() as conn:
            conn.executescript("""
            -- Сирий незмінний лог подій (Raw Bronze Layer)
            CREATE TABLE IF NOT EXISTS raw_events (
                event_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                amount_cents INTEGER NOT NULL,
                event_time TEXT NOT NULL -- ISO8601 UTC
            );

            -- Довідник тарифів (SCD Type 2: Point-in-Time розмітка)
            CREATE TABLE IF NOT EXISTS tariff_history (
                user_id TEXT NOT NULL,
                discount_percent INTEGER NOT NULL,
                valid_from TEXT NOT NULL,
                valid_to TEXT NOT NULL,
                PRIMARY KEY (user_id, valid_from)
            );

            -- Цільова аналітична таблиця з партиціями за датою
            CREATE TABLE IF NOT EXISTS daily_user_revenue (
                partition_date TEXT NOT NULL,
                user_id TEXT NOT NULL,
                raw_total_cents INTEGER NOT NULL,
                discounted_total_cents INTEGER NOT NULL,
                events_count INTEGER NOT NULL,
                checksum_hash TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (partition_date, user_id)
            );

            -- Журнал стану виконання бекфілу (Checkpoints)
            CREATE TABLE IF NOT EXISTS backfill_checkpoints (
                chunk_id TEXT PRIMARY KEY,
                window_start TEXT NOT NULL,
                window_end TEXT NOT NULL,
                status TEXT NOT NULL, -- 'PENDING', 'COMMITTED', 'FAILED'
                rows_processed INTEGER NOT NULL,
                error_message TEXT,
                completed_at TEXT
            );
            """)

    def process_chunk(self, window_start: str, window_end: str, partition_date: str) -> bool:
        """Ідемпотентна обробка одного чанка: читання, AS-OF join, валідація, атомарний SWAP."""
        chunk_id = f"chunk_{partition_date}"

        with self._get_connection() as conn:
            # 1. Реєстрація старту чанка в журналі
            conn.execute("""
                INSERT INTO backfill_checkpoints (
                    chunk_id, window_start, window_end, status, rows_processed, error_message, completed_at
                ) VALUES (?, ?, ?, 'PENDING', 0, NULL, NULL)
                ON CONFLICT(chunk_id) DO UPDATE SET 
                    status = 'PENDING', 
                    error_message = NULL,
                    completed_at = NULL;
            """, (chunk_id, window_start, window_end))

            try:
                # 2. Обчислення агрегату з точним AS-OF з'єднанням за часом події
                cursor = conn.execute("""
                    SELECT 
                        e.user_id,
                        SUM(e.amount_cents) AS raw_sum,
                        SUM(CAST(e.amount_cents * (100 - COALESCE(t.discount_percent, 0)) / 100 AS INTEGER)) AS discounted_sum,
                        COUNT(e.event_id) AS ev_count,
                        GROUP_CONCAT(e.event_id, ',') AS event_ids
                    FROM raw_events e
                    LEFT JOIN tariff_history t ON e.user_id = t.user_id
                        AND e.event_time >= t.valid_from 
                        AND e.event_time < t.valid_to
                    WHERE e.event_time >= ? AND e.event_time < ?
                    GROUP BY e.user_id;
                """, (window_start, window_end))

                rows = cursor.fetchall()

                # 3. Валідація інваріантів перед фіксацією (Data Quality Assertions)
                staged_records = []
                now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

                for user_id, raw_sum, discounted_sum, ev_count, ev_ids in rows:
                    if discounted_sum > raw_sum:
                        raise ValueError(f"Порушення інваріанту: знижка перевищує базу для {user_id}")
                    if raw_sum < 0:
                        raise ValueError(f"Порушення інваріанту: від'ємна виручка для {user_id}")

                    # Детермінований контрольний хеш набору подій для перевірки цілісності
                    hasher = hashlib.sha256(ev_ids.encode('utf-8'))
                    checksum = hasher.hexdigest()[:16]

                    staged_records.append((
                        partition_date, user_id, raw_sum, discounted_sum, ev_count, checksum, now_iso
                    ))

                # 4. Атомарний SWAP: очищення цільової партиції та запис свіжого результату
                conn.execute("DELETE FROM daily_user_revenue WHERE partition_date = ?;", (partition_date,))
                conn.executemany("""
                    INSERT INTO daily_user_revenue (
                        partition_date, user_id, raw_total_cents, discounted_total_cents, 
                        events_count, checksum_hash, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """, staged_records)

                # 5. Фіксація чекпоінта
                conn.execute("""
                    UPDATE backfill_checkpoints 
                    SET status = 'COMMITTED', rows_processed = ?, completed_at = ?
                    WHERE chunk_id = ?;
                """, (len(staged_records), now_iso, chunk_id))

                conn.commit()
                return True

            except Exception as e:
                conn.rollback()
                conn.execute("""
                    UPDATE backfill_checkpoints 
                    SET status = 'FAILED', error_message = ?
                    WHERE chunk_id = ?;
                """, (str(e), chunk_id))
                conn.commit()
                raise e

    def run_backfill(self, start_date: datetime.date, end_date: datetime.date) -> None:
        """Послідовний прогін бекфілу за днями з можливістю безболісного перезапуску."""
        curr = start_date
        while curr < end_date:
            part_str = curr.strftime("%Y-%m-%d")
            w_start = f"{part_str}T00:00:00Z"
            next_day = curr + datetime.timedelta(days=1)
            w_end = f"{next_day.strftime('%Y-%m-%d')}T00:00:00Z"

            print(f"[BACKFILL] Обробка партиції: {part_str} ...", end=" ")
            self.process_chunk(w_start, w_end, part_str)
            print("✓ Успішно зафіксовано.")
            curr = next_day
