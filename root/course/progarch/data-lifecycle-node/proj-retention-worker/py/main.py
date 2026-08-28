import datetime
import json

class DataRetentionWorker:
    def __init__(self, db_conn, kms_client, s3_client):
        self.db = db_conn
        self.kms = kms_client
        self.s3 = s3_client

    def process_partition_retention(self, entity_name: str, retention_days: int, archive_to_s3: bool = True):
        cutoff_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=retention_days)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d")

        cursor = self.db.cursor()
        
        # 1. Пошук застарілих партицій
        find_sql = """
            SELECT c.relname AS partition_name, parent.relname AS parent_name
            FROM pg_class c
            JOIN pg_inherits i ON c.oid = i.inhrelid
            JOIN pg_class parent ON i.inhparent = parent.oid
            WHERE parent.relname = %s
              AND c.relname ~ '_[0-9]{4}_[0-9]{2}$'
              AND to_date(substring(c.relname from '_([0-9]{4}_[0-9]{2})$'), 'YYYY_MM') < %s;
        """
        cursor.execute(find_sql, (entity_name, cutoff_str))
        partitions = cursor.fetchall()

        processed = []
        for part_name, parent_name in partitions:
            # Налаштування безпечного таймауту блокування
            cursor.execute("SET LOCAL lock_timeout = '5s';")

            # 2. Від'єднання партиції від OLTP без затримування індексів
            detach_sql = f"ALTER TABLE {parent_name} DETACH PARTITION {part_name} CONCURRENTLY;"
            cursor.execute(detach_sql)

            # 3. Експорт даних у холодний шар S3
            archived_path = None
            if archive_to_s3:
                cursor.execute(f"SELECT * FROM {part_name};")
                rows = cursor.fetchall()
                data_payload = json.dumps(rows).encode('utf-8')
                archived_path = f"archives/{parent_name}/{part_name}.parquet"
                self.s3.put_object(Bucket="cold-archive", Key=archived_path, Body=data_payload)

            # 4. Фізичне видалення від'єднаної таблиці (без WAL для рядків)
            cursor.execute(f"DROP TABLE {part_name};")
            processed.append({"partition": part_name, "archive": archived_path})

        self.db.commit()
        return processed

    def execute_crypto_shredding(self, user_id: str, kms_key_id: str):
        """Знищення ключа шифрування у KMS для виконання GDPR Article 17"""
        self.kms.disable_and_schedule_deletion(key_id=kms_key_id, pending_window_days=0)
        
        cursor = self.db.cursor()
        audit_sql = """
            INSERT INTO audit_erasure_events (user_id_hash, erased_at, method)
            VALUES (digest(%s, 'sha256'), NOW(), 'CRYPTO_SHREDDING');
        """
        cursor.execute(audit_sql, (user_id,))
        self.db.commit()
