# data_reconciliation_worker.py - Служба фонового відновлення даних після відкату
import time
import psycopg2

def reconcile_orphan_records(db_conn, batch_size=1000):
    """
    Знаходить усі записи, створені версією v2, де заповнено tax_identifier,
    але старе поле tax_code залишилося NULL.
    """
    cursor = db_conn.cursor()
    total_reconciled = 0

    while True:
        cursor.execute("""
            UPDATE customer_invoices
            SET tax_code = tax_identifier
            WHERE id IN (
                SELECT id FROM customer_invoices
                WHERE tax_code IS NULL AND tax_identifier IS NOT NULL
                LIMIT %s
                FOR UPDATE SKIP LOCKED
            )
            RETURNING id;
        """, (batch_size,))

        updated_rows = cursor.fetchall()
        db_conn.commit()

        if not updated_rows:
            break

        total_reconciled += len(updated_rows)
        print(f"[RECONCILIATION] Оброблено батч з {len(updated_rows)} записів...")
        time.sleep(0.1)  # Запобігання піковому навантаженню на БД

    print(f"[RECONCILIATION COMPLETE] Успішно відновлено {total_reconciled} сирітських записів.")
