import datetime
import json

class DataLifecycleNode:
    def __init__(self, db_connection, kms_client, s3_client):
        self.db = db_connection
        self.kms = kms_client
        self.s3 = s3_client

    def execute_policy_step(self, entity_name: str, retention_days: int, archive_to_s3: bool = True) -> int:
        cutoff_date = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=retention_days)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d")

        cursor = self.db.cursor()
        
        # 1. Пошук застарілих партицій
        find_sql = """
            SELECT c.relname AS partition_name
            FROM pg_class c
            JOIN pg_inherits i ON c.oid = i.inhrelid
            JOIN pg_class parent ON i.inhparent = parent.oid
            WHERE parent.relname = %s
              AND c.relname ~ '_[0-9]{4}_[0-9]{2}$'
              AND to_date(substring(c.relname from '_([0-9]{4}_[0-9]{2})$'), 'YYYY_MM') < %s;
        """
        cursor.execute(find_sql, (entity_name, cutoff_str))
        partitions = cursor.fetchall()

        count = 0
        for (part_name,) in partitions:
            # 2. Атомарний DETACH від гарячого B-tree
            cursor.execute(f"ALTER TABLE {entity_name} DETACH PARTITION {part_name} CONCURRENTLY;")

            # 3. Експорт у Cold Storage S3
            if archive_to_s3:
                cursor.execute(f"SELECT * FROM {part_name};")
                rows = cursor.fetchall()
                data = json.dumps(rows).encode('utf-8')
                self.s3.put_object(Bucket="cold-archive", Key=f"archives/{entity_name}/{part_name}.json", Body=data)

            # 4. Фізичний DROP без WAL-вибуху
            cursor.execute(f"DROP TABLE {part_name};")
            count += 1

        self.db.commit()
        return count

    def shred_user_data(self, user_id: str, kms_key_id: str):
        """Виконання Crypto-Shredding шляхом вилучення ключа KMS"""
        self.kms.destroy_key(kms_key_id)
        
        cursor = self.db.cursor()
        cursor.execute(
            "INSERT INTO erasure_audit_log (user_id_hash, erased_at, strategy) VALUES (digest(%s, 'sha256'), NOW(), 'CRYPTO_SHREDDING');",
            (user_id,)
        )
        self.db.commit()
