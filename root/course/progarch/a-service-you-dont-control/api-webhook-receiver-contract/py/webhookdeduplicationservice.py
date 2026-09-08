from typing import Dict, Any, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor

class WebhookDeduplicationService:
    def __init__(self, db_connection_pool):
        self.pool = db_connection_pool

    def process_inbound_event(
        self,
        event_id: str,
        provider: str,
        event_type: str,
        payload: Dict[str, Any]
    ) -> Tuple[int, str, bool]:
        """
        Атомарно реєструє подію та визначає необхідність постановки в чергу.
        Повертає кортеж (http_status, reason, should_enqueue).
        """
        insert_query = """
            INSERT INTO inbound_webhook_events (event_id, provider, event_type, status, payload)
            VALUES (%s, %s, %s, 'RECEIVED', %s)
            ON CONFLICT (event_id) DO NOTHING
            RETURNING event_id;
        """
        import json
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    insert_query,
                    (event_id, provider, event_type, json.dumps(payload))
                )
                inserted = cursor.fetchone()
                conn.commit()

                if inserted:
                    return 200, "EVENT_ACCEPTED", True

                # Обробка дубліката: зчитуємо поточний стан
                cursor.execute(
                    "SELECT status FROM inbound_webhook_events WHERE event_id = %s;",
                    (event_id,)
                )
                row = cursor.fetchone()
                current_status = row[0] if row else "UNKNOWN"

                # Ідемпотентне повернення 200 OK без повторної обробки
                return 200, f"DUPLICATE_ACKNOWLEDGED_STATE_{current_status}", False
        finally:
            self.pool.putconn(conn)
