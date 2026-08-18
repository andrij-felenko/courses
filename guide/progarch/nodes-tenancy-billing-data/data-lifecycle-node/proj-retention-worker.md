# ⚙️ Автоматизований рушій вилучення партицій та криптографічного знищення

Ця практична вставка детально розбирає реалізацію асинхронного рушія життєвого циклу даних (Data Retention Worker). Код демонструє оцінку політик TTL, вивід застарілих партицій PostgreSQL (`DETACH PARTITION`), експорт даних у холодний формат Parquet, управління таймаутами блокувань СУБД та виконання криптографічного знищення ключів користувача (Crypto-Shredding) в KMS.

## Призначення та архітектура фонового демона

У високонавантажених платформах фонові утиліти очищення баз даних не повинні працювати як некеровані cron-скрипти, які просто відправляють важкі SQL-запити в OLTP-базу. Фоновий рушій життєвого циклу даних — це ізольований, спостережуваний та надійний сервіс-демон, який працює за алгоритмом оцінки станів та забезпечує повну відсутність деструктивного впливу на основний гарячий транзакційний потік.

Головні завдання рушія:

1. **Безбезпечне від'єднання партицій без виключних блокувань**: Використання модифікатора `CONCURRENTLY` під час операцій `ALTER TABLE ... DETACH PARTITION` для запобігання тривалим затримкам запитів користувачів.
2. **Гарантія атомарності експорту**: Перевірка того, що партиція успішно вивантажена у холодний шар S3 та її цілісність підтверджена контрольною сумою до того, як буде виконана команда `DROP TABLE`.
3. **Обробка таймаутів та відкатів**: Визначення спеціальних строгих таймаутів блокування (`lock_timeout` та `statement_timeout`) для запобігання ситуаціям, коли фоновий процес ротації стає в чергу за блокуванням і починає блокувати нові транзакції користувачів.
4. **Гарантоване виконання GDPR Article 17**: Атомарне знищення персональних ключів шифрування у KMS із фіксацією хешованого запису у журналі аудиту.

## Послідовність дій рушія вилучення партицій

Процес обробки однієї застарілої партиції складається з чотирьох послідовних етапів:

* **Етап 1: Опитування системного каталогу `pg_class`**. Рушій запитує список усіх дитячих партицій для заданої батьківської таблиці, аналізує діапазон дат у назвах партицій та відбирає ті, чий верхній поріг часу менший за розраховану дату зрізу (`cutoffDate`).
* **Етап 2: Налаштування таймаутів та виконання `DETACH PARTITION CONCURRENTLY`**. Рушій встановлює `lock_timeout = '5s'`. Якщо протягом 5 секунд СУБД не може отримати короткочасне блокування `AccessExclusiveLock` (наприклад, через довгий аналітичний `SELECT`), операція скасовується, рушій відступає і робить повторну спробу пізніше, не створюючи затор у черзі транзакцій.
* **Етап 3: Потоковий експорт у Cold Storage (Parquet/S3)**. Рушій зчитує від'єднану таблицю, перетворює записи у стиснений колонковий формат Apache Parquet та завантажує файл у об'єктне сховище S3. Після завантаження перевіряється розмір файлу та MD5/SHA256 контрольна сума.
* **Етап 4: Фізичне видалення від'єднаної таблиці**. Лише після успішного підтвердження від S3 рушій виконує команду `DROP TABLE partition_name`. Оскільки таблиця вже від'єднана від логічного B-tree індексу батьківської таблиці, її вилучення оновлює лише кілька рядків у системному каталозі й не генерує WAL для вмісту.

## Робочий код рушія вилучення

:::tabs
```ts
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
```
```py
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
```
:::

## Крайові випадки та обробка відмов

У реальних виробничих середовищах виконання політик життєвого циклу стикається з трьома основними класами аварійних ситуацій:

### 1. Збій мережі під час завантаження у Cold Storage S3

Якщо під час виконання третього етапу (завантаження Parquet-файла у S3) мережеве з'єднання розривається або S3 повертає помилку `503 SlowDown`, процес експорту переривається винятком. Оскільки партицію вже від'єднано від головної таблиці на другому етапі (`DETACH PARTITION`), вона залишається у базі як ізольована автономна таблиця `telemetry_readings_2026_01`.

У цій ситуації транзакційні OLTP-запити користувачів не зазнають жодного впливу. Партиція не навантажує B-tree індекси батьківської таблиці. Рушій повторить спробу експорту під час наступного ітераційного запуску, перевірить наявність від'єднаної таблиці, вивантажить її у S3 і лише після успішного підтвердження виконає `DROP TABLE`.

### 2. Затор блокувань (Lock Contention) на операції DETACH

Хоча `ALTER TABLE ... DETACH PARTITION CONCURRENTLY` мінімізує час утримання блокувань, СУБД усе ж вимагає короткочасного захоплення `AccessExclusiveLock` на батьківську таблицю для оновлення метаданих системного каталогу. Якщо в цей самий момент аналітичний сервіс виконує довгий `SELECT` протягом 30 секунд, команда `ALTER TABLE` встане в чергу й почне блокувати всі наступні `INSERT` та `UPDATE` від реальних користувачів.

Саме для запобігання цьому рушій виконує `SET LOCAL lock_timeout = '5s';`. Якщо через 5 секунд замок не отримано, СУБД генерує виняток `lock_not_available`, рушій відкачує поточну спробу, занотовує попередження у метрики спостережності та повертається до цієї партиції в наступному циклі.

### 3. Невдале знищення ключа KMS при Crypto-Shredding

Знищення ключа KMS є незворотною операцією. Якщо сервіс KMS повертає помилку зв'язку або помилку авторизації під час запиту `kms.destroyKey(K_user)`, рушій не повинен фіксувати запис у журналі `audit_erasure_events`. Тільки після отримання криптографічно підписаного квитка-підтвердження від KMS про зміну стану ключа на `DESTRUCTED` / `DISABLED` запис про вилучення реєструється в журналі аудиту.

## Вимога спостережності та метрики рушія

Фоновий рушій життєвого циклу експортує наступні обов'язкові Prometheus-метрики для контролю здоров'я системи:

* `data_lifecycle_partitions_detached_total{entity="..."}` — загальна кількість успішно від'єднаних партицій.
* `data_lifecycle_bytes_archived_total{entity="..."}` — обсяг даних у байтах, вивантажених у холодний шар Parquet/S3.
* `data_lifecycle_crypto_shreddings_total{status="success|failure"}` — кількість виконаних операцій знищення ключів KMS за GDPR Article 17.
* `data_lifecycle_lock_timeouts_total{entity="..."}` — кількість скасованих операцій `DETACH` через затор блокувань СУБД.

Завдяки цьому черговий інженер або архітектор завжди бачать дійсний стан очищення сховищ та можуть своєчасно реагувати на затримки виконання SLA.
