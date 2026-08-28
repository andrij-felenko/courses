import { Client } from "pg";

export interface LifecyclePolicy {
  entityName: string;
  retentionDays: number;
  archiveToS3: boolean;
  cryptoShredding: boolean;
}

export class DataLifecycleNode {
  constructor(
    private readonly db: Client,
    private readonly kms: { deleteKey(id: string): Promise<void> },
    private readonly s3: { putObject(key: string, body: Buffer): Promise<void> }
  ) {}

  /**
   * Асинхронний крок обробки застарілих партицій за політикою retention
   */
  async executePolicyStep(policy: LifecyclePolicy): Promise<number> {
    const cutoffDate = new Date(Date.now() - policy.retentionDays * 86400 * 1000);
    
    // 1. Пошук застарілих партицій у системному каталозі
    const { rows } = await this.db.query(
      `SELECT c.relname AS partition_name
       FROM pg_class c
       JOIN pg_inherits i ON c.oid = i.inhrelid
       JOIN pg_class parent ON i.inhparent = parent.oid
       WHERE parent.relname = $1
         AND c.relname ~ '_[0-9]{4}_[0-9]{2}$'
         AND to_date(substring(c.relname from '_([0-9]{4}_[0-9]{2})$'), 'YYYY_MM') < $2;`,
      [policy.entityName, cutoffDate]
    );

    let processedCount = 0;

    for (const row of rows) {
      const partName = row.partition_name;

      // 2. Атомарне від'єднання партиції від гарячого B-tree індексу
      await this.db.query(
        `ALTER TABLE ${policy.entityName} DETACH PARTITION ${partName} CONCURRENTLY;`
      );

      // 3. Експорт у Cold Storage (Parquet/S3) за потреби
      if (policy.archiveToS3) {
        const dump = await this.db.query(`SELECT * FROM ${partName}`);
        const payload = Buffer.from(JSON.stringify(dump.rows));
        await this.s3.putObject(`cold-archives/${policy.entityName}/${partName}.json`, payload);
      }

      // 4. Фізичне вилучення від'єднаної таблиці без WAL для рядків
      await this.db.query(`DROP TABLE ${partName};`);
      processedCount++;
    }

    return processedCount;
  }

  /**
   * Виконання Crypto-Shredding для конкретного користувача (GDPR Article 17)
   */
  async shredUserData(userId: string, kmsKeyId: string): Promise<void> {
    // Знищуємо ключ шифрування у KMS
    await this.kms.deleteKey(kmsKeyId);

    // Робимо запис в аудит-лог про виконання знищення (без PII)
    await this.db.query(
      `INSERT INTO erasure_audit_log (user_id_hash, erased_at, strategy)
       VALUES (sha256($1), NOW(), 'CRYPTO_SHREDDING')`,
      [Buffer.from(userId)]
    );
  }
}
