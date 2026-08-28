import { Client } from "pg";

export interface RetentionPolicy {
  entity: string;
  retentionDays: number;
  archiveToS3: boolean;
  cryptoShreddingEnabled: boolean;
}

export interface DetachResult {
  partitionName: string;
  rowsAffected: number;
  archivedPath?: string;
  shreddedKeysCount: number;
}

export class DataRetentionWorker {
  constructor(
    private readonly db: Client,
    private readonly kmsClient: { destroyKey(keyId: string): Promise<void> },
    private readonly s3Uploader: { uploadParquet(path: string, data: Buffer): Promise<string> }
  ) {}

  /**
   * Головний цикл обробки застарілих партицій за політикою retention
   */
  async processPartitionRetention(policy: RetentionPolicy): Promise<DetachResult[]> {
    const results: DetachResult[] = [];
    const cutoffDate = new Date(Date.now() - policy.retentionDays * 86400 * 1000);

    // 1. Пошук партицій, що випередили поріг retention Cutoff
    const query = `
      SELECT relname AS partition_name,
             parent.relname AS parent_name
      FROM pg_class c
      JOIN pg_inherits i ON c.oid = i.inhrelid
      JOIN pg_class parent ON i.inhparent = parent.oid
      WHERE parent.relname = $1
        AND c.relname ~ '_[0-9]{4}_[0-9]{2}$'
        AND to_date(substring(c.relname from '_([0-9]{4}_[0-9]{2})$'), 'YYYY_MM') < $2;
    `;

    const res = await this.db.query(query, [policy.entity, cutoffDate]);

    for (const row of res.rows) {
      const partitionName = row.partition_name;
      const parentName = row.parent_name;

      // Налаштовуємо короткий lock_timeout, щоб не блокувати OLTP у разі конфлікту
      await this.db.query("SET LOCAL lock_timeout = '5s';");

      // 2. Атомарний DETACH без тривалих блокувань OLTP
      await this.db.query(
        `ALTER TABLE ${parentName} DETACH PARTITION ${partitionName} CONCURRENTLY;`
      );

      let archivedPath: string | undefined;
      if (policy.archiveToS3) {
        // 3. Експорт у Cold Storage (Parquet)
        const dumpRes = await this.db.query(`SELECT * FROM ${partitionName}`);
        const parquetBuffer = Buffer.from(JSON.stringify(dumpRes.rows)); // Спрощено для прикладу
        archivedPath = await this.s3Uploader.uploadParquet(
          `archives/${parentName}/${partitionName}.parquet`,
          parquetBuffer
        );
      }

      // 4. Фізичне вилучення від'єднаної таблиці
      await this.db.query(`DROP TABLE ${partitionName};`);

      results.push({
        partitionName,
        rowsAffected: res.rowCount || 0,
        archivedPath,
        shreddedKeysCount: 0,
      });
    }

    return results;
  }

  /**
   * Виконання Crypto-Shredding для конкретного користувача у KMS
   */
  async executeCryptoShredding(userId: string, kmsKeyId: string): Promise<void> {
    // Знищення ключа в KMS робить усі зашифровані записи у базі та S3 нечитабельною трухою
    await this.kmsClient.destroyKey(kmsKeyId);
    
    // Фіксація в лозі аудиту вилучення (аудит-лог зберігає факт знищення без PII)
    await this.db.query(
      `INSERT INTO audit_erasure_events (user_id_hash, erased_at, method) VALUES (sha256($1), NOW(), 'CRYPTO_SHREDDING')`,
      [Buffer.from(userId)]
    );
  }
}
