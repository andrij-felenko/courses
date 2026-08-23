# ⚙️ Ізоляція орендарів: RLS у PostgreSQL та прокидання контексту

Практична реалізація моделі **Pool** (спільна база даних та спільна схема) вимагає суворого гарантування того, що жоден SQL-запит не зможе прочитати чи модифікувати дані чужого орендаря. Наївний підхід — покладатися на сумлінність розробників, які мають вручну додавати `WHERE tenant_id = ...` у кожен запит, — неминуче призводить до витоків даних при першій же забудькуватості чи під час складних JOIN-операцій.

Найбільш надійним архітектурним рішенням у PostgreSQL є комбінація **Row-Level Security (RLS)** на рівні бази даних та **прокидання контексту орендаря (Tenant Context Propagation)** у middleware сервісу.

## Як працює Row-Level Security всередині PostgreSQL

Коли в базі даних увімкнено RLS, парсер і переписувач запитів (Query Rewriter) PostgreSQL модифікують дерево виклику SQL-запиту ще до того, як оптимізатор почне будувати план виконання. Якщо додаток надсилає запит `SELECT * FROM devices`, переписувач автоматично підставляє вираз з політики безпеки, перетворюючи його на `SELECT * FROM devices WHERE (tenant_id = current_setting('app.current_tenant', true))`.

Механізм RLS працює на прозорому рівні ядра ДБЖ:
* **Безпека за замовчуванням (Deny by Default):** Якщо сесійна змінна `app.current_tenant` не була встановлена перед виконанням запиту, функція `current_setting(..., true)` повертає `NULL`. У реляційній логіці порівняння `tenant_id = NULL` завжди оцінюється як `FALSE` (або `UNKNOWN`), і запит повертає 0 рядків, оминаючи можливість витоку даних.
* **Перевірка на запис (WITH CHECK):** Політика RLS контролює не лише вибірку даних (`USING`), а й операції `INSERT` та `UPDATE` (`WITH CHECK`). Якщо додаток спробує вставити рядок із `tenant_id = 'tenant_B'`, коли в сесії встановлено `'tenant_A'`, база даних згенерує помилку порушення політики `new row violates row-level security policy`.

## Крок 1. Конфігурація Row-Level Security та тригерів автоматичного запобігання

Нижче наведено повний виробничий сценарій налаштування RLS у PostgreSQL, який включає створення обмеженої ролі доступу, примусове застосування політики та автоматичний тригер для запобігання помилкам при вставці:

```sql
-- 1. Створення обмеженої ролі доступу для додатку (НЕ суперкористувача!)
CREATE ROLE app_user WITH LOGIN PASSWORD 'secure_password';

-- 2. Створення таблиці пристроїв із колонкою tenant_id
CREATE TABLE devices (
    id UUID DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL,
    name VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT clock_timestamp(),
    PRIMARY KEY (tenant_id, id)
);

-- Надаємо права обмеженій ролі
GRANT SELECT, INSERT, UPDATE, DELETE ON devices TO app_user;

-- 3. Вмикаємо Row-Level Security для таблиці
ALTER TABLE devices ENABLE ROW LEVEL SECURITY;

-- 4. Примусове застосування RLS навіть для власника таблиці (FORCE RLS)
ALTER TABLE devices FORCE ROW LEVEL SECURITY;

-- 5. Створення політики доступу на основі сесійної змінної app.current_tenant
CREATE POLICY tenant_isolation_policy ON devices
    FOR ALL
    TO app_user
    USING (tenant_id = current_setting('app.current_tenant', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant', true));

-- 6. Допоміжний тригер: автоматично підставляє tenant_id із сесії, якщо додаток його не вказав
CREATE OR REPLACE FUNCTION set_tenant_id_from_session()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.tenant_id IS NULL OR NEW.tenant_id = '' THEN
        NEW.tenant_id := current_setting('app.current_tenant', false);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_set_tenant_id
    BEFORE INSERT ON devices
    FOR EACH ROW
    EXECUTE FUNCTION set_tenant_id_from_session();
```

Примусовий прапорець `FORCE ROW LEVEL SECURITY` є критично важливим. За замовчуванням власник таблиці (роль, яка виконала `CREATE TABLE`) ігнорує політики RLS. Якщо додаток підключається під тим самим користувачем, який створював схему, RLS не працюватиме без `FORCE RLS`.

## Крок 2. Прокидання контексту в коді сервісу

Кожен вхідний HTTP-запит або фонова задача отримує ідентифікатор орендаря (з підписаного JWT-токена або заголовка API Gateway). Контекст додається до локального середовища виконання і при кожному зверненні до БД перед виконанням основними запитами встановлюється змінна сесії `SET LOCAL app.current_tenant = '...'`.

Використання модифікатора `LOCAL` у `SET LOCAL` або третього параметра `true` у `set_config('app.current_tenant', val, true)` гарантує, що значення змінної діє **лише у межах поточної SQL-транзакції** і автоматично скидається при поверненні підключення до пулу (Connection Pool).

Нижче наведено ідіоматичні реалізації захищеного сесійного guards для популярних мов програмування:

:::tabs
```go
package main

import (
	"context"
	"database/sql"
	"fmt"
)

type tenantKey struct{}

// WithTenant додає tenant_id до контексту Go
func WithTenant(ctx context.Context, tenantID string) context.Context {
	return context.WithValue(ctx, tenantKey{}, tenantID)
}

// TenantFromContext витягує tenant_id з контексту
func TenantFromContext(ctx context.Context) (string, bool) {
	tenantID, ok := ctx.Value(tenantKey{}).(string)
	return tenantID, ok
}

// ExecWithTenantIsolation виконує функцію у транзакції з встановленим RLS контекстом
func ExecWithTenantIsolation(ctx context.Context, db *sql.DB, fn func(tx *sql.Tx) error) error {
	tenantID, ok := TenantFromContext(ctx)
	if !ok || tenantID == "" {
		return fmt.Errorf("security violation: missing tenant_id in execution context")
	}

	// Починаємо транзакцію. Спеціальний режим заперечує брудні читання
	tx, err := db.BeginTx(ctx, &sql.TxOptions{Isolation: sql.LevelReadCommitted})
	if err != nil {
		return fmt.Errorf("failed to begin transaction: %w", err)
	}
	defer tx.Rollback()

	// Встановлюємо змінну сесії з is_local = true (третій аргумент set_config)
	_, err = tx.ExecContext(ctx, "SELECT set_config('app.current_tenant', $1, true)", tenantID)
	if err != nil {
		return fmt.Errorf("failed to set tenant context: %w", err)
	}

	if err := fn(tx); err != nil {
		return err
	}

	return tx.Commit()
}
```
```ts
import { AsyncLocalStorage } from 'node:async_hooks';
import { Pool, PoolClient } from 'pg';

const tenantStorage = new AsyncLocalStorage<string>();

export class TenantContext {
  static run<T>(tenantId: string, store: () => Promise<T>): Promise<T> {
    if (!tenantId) {
      throw new Error('Security violation: tenantId is required');
    }
    return tenantStorage.run(tenantId, store);
  }

  static current(): string {
    const tenantId = tenantStorage.getStore();
    if (!tenantId) {
      throw new Error('Security violation: no tenant context bound to current async execution');
    }
    return tenantId;
  }
}

export async function withTenantClient<T>(
  pool: Pool,
  action: (client: PoolClient) => Promise<T>
): Promise<T> {
  const tenantId = TenantContext.current();
  const client = await pool.connect();

  try {
    await client.query('BEGIN');
    // set_config z is_local = true ізолює параметр у межах цієї транзакції
    await client.query('SELECT set_config($1, $2, true)', ['app.current_tenant', tenantId]);

    const result = await action(client);

    await client.query('COMMIT');
    return result;
  } catch (err) {
    await client.query('ROLLBACK');
    throw err;
  } finally {
    // При поверненні до пулу підключення гарантовано чисте за рахунок ROLLBACK/COMMIT
    client.release();
  }
}
```
```cpp
#include <iostream>
#include <memory>
#include <string_view>
#include <expected>
#include <stdexcept>
#include <libpq-fe.h>

// RAII обгортка для управління з'єднанням PostgreSQL
class PGConnWrapper {
    PGconn* conn_;
public:
    explicit PGConnWrapper(PGconn* conn) : conn_(conn) {}
    ~PGConnWrapper() {
        if (conn_) PQfinish(conn_);
    }
    PGConnWrapper(const PGConnWrapper&) = delete;
    PGConnWrapper& operator=(const PGConnWrapper&) = delete;
    PGConnWrapper(PGConnWrapper&& o) noexcept : conn_(o.conn_) { o.conn_ = nullptr; }

    [[nodiscard]] PGconn* get() const noexcept { return conn_; }
};

// RAII Guard для ізоляції сесії орендаря у транзакції
class TenantSessionGuard {
    PGconn* conn_;
    bool committed_ = false;
public:
    static std::expected<TenantSessionGuard, std::string> create(PGconn* conn, std::string_view tenant_id) {
        if (tenant_id.empty()) {
            return std::unexpected("Security violation: tenant_id cannot be empty");
        }

        PGresult* res = PQexec(conn, "BEGIN");
        if (PQresultStatus(res) != PGRES_COMMAND_OK) {
            PQclear(res);
            return std::unexpected("Failed to start transaction");
        }
        PQclear(res);

        // Встановлюємо змінну сесії з is_local = true
        const char* paramValues[1] = { tenant_id.data() };
        res = PQexecParams(conn,
                           "SELECT set_config('app.current_tenant', $1, true)",
                           1, nullptr, paramValues, nullptr, nullptr, 0);

        if (PQresultStatus(res) != PGRES_TUPLES_OK) {
            PQclear(res);
            PQexec(conn, "ROLLBACK");
            return std::unexpected("Failed to set app.current_tenant setting");
        }
        PQclear(res);

        return TenantSessionGuard(conn);
    }

    ~TenantSessionGuard() {
        if (!committed_ && conn_) {
            PGresult* res = PQexec(conn_, "ROLLBACK");
            PQclear(res);
        }
    }

    std::expected<void, std::string> commit() {
        PGresult* res = PQexec(conn_, "COMMIT");
        if (PQresultStatus(res) != PGRES_COMMAND_OK) {
            PQclear(res);
            return std::unexpected("Failed to commit transaction");
        }
        PQclear(res);
        committed_ = true;
        return {};
    }

private:
    explicit TenantSessionGuard(PGconn* conn) : conn_(conn) {}
};
```
:::

## Поєднання RLS із декларативним партиціюванням (Partition Pruning)

При досягненні мільйонів рядків у спільній Pool-базі RLS-політика сама по собі перестає забезпечувати максимальну швидкість вибірок, якщо ДБЖ змушена сканувати гігабайтні індекси.

Поєднання **Row-Level Security** із **декларативним партиціюванням за списком (LIST Partitioning)** дає фундаментальний приріст продуктивності через механізм **Partition Pruning**:

```sql
-- 1. Базово партиційована таблиця пристроїв за значенням tenant_id
CREATE TABLE devices_partitioned (
    id UUID DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(64) NOT NULL,
    name VARCHAR(128) NOT NULL,
    status VARCHAR(32) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT clock_timestamp(),
    PRIMARY KEY (tenant_id, id)
) PARTITION BY LIST (tenant_id);

-- 2. Створення окремих партицій для великих орендарів або пулу дрібних
CREATE TABLE devices_tenant_101 PARTITION OF devices_partitioned
    FOR VALUES IN ('tenant_101');

CREATE TABLE devices_tenant_102 PARTITION OF devices_partitioned
    FOR VALUES IN ('tenant_102');

-- 3. Вмикаємо RLS на базі партиційованої таблиці
ALTER TABLE devices_partitioned ENABLE ROW LEVEL SECURITY;
ALTER TABLE devices_partitioned FORCE ROW LEVEL SECURITY;

CREATE POLICY tenant_partition_policy ON devices_partitioned
    FOR ALL
    TO app_user
    USING (tenant_id = current_setting('app.current_tenant', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant', true));
```

Коли запит виконується під сесійною змінною `app.current_tenant = 'tenant_101'`, планировальник PostgreSQL здійснює **Static & Dynamic Partition Pruning**. ДБЖ на рівні планера відсікає всі фізичні файли таблиць інших партицій (`devices_tenant_102`, `devices_default`) і виконує пошук виключно у файлі партиції `devices_tenant_101`.

Це поєднує низьку інфраструктурну вартість пулу із продуктивністю й можливістю миттєвого від'єднання фізичних файлів (`ALTER TABLE DETACH PARTITION`), як у Silo-моделі.

## Поодиничне шифрування колонок із pgcrypto в межах RLS

Для виконання суворих вимог безпеки при обробці персональних даних (PII) RLS-ізоляцію доповнюють нативним шифруванням колонок за допомогою розширення `pgcrypto`.

Замість збереження відкритих даних у таблиці, чутливі колонки (наприклад, номер телефону чи токен доступу до замка) зберігаються як зашифрований байтовий масив `BYTEA`. Ключ шифрування передається в сесію разом із контекстом орендаря:

```sql
-- Встановлюємо унікальний симетричний ключ орендаря для поточної транзакції
SELECT set_config('app.tenant_encryption_key', 'kms_key_tenant_101_secret', true);

-- Вставка даних із прозорим шифруванням pgcrypto
INSERT INTO devices (tenant_id, name, status, secret_token)
VALUES (
    current_setting('app.current_tenant'),
    'Front Door Lock',
    'active',
    pgp_sym_encrypt('unlock_code_9876', current_setting('app.tenant_encryption_key'))
);

-- Читання зашифрованих даних
SELECT 
    name, 
    pgp_sym_decrypt(secret_token, current_setting('app.tenant_encryption_key')) AS secret_token 
FROM devices;
```

Цей підхід забезпечує **двошаровий захист (Defense in Depth)**. Навіть якщо системний адміністратор бази даних виконає запит `SELECT * FROM devices` під обліковим записом `postgres` (минаючи перевірку RLS), він побачить лише зашифровані блоби даних, оскільки симетричний ключ `app.tenant_encryption_key` зберігається у сховищі KMS додатку і розкривається лише у межах активного сесійного транзакційного блоку користувача.

## Маршрутизація контексту на рівні Service Mesh (Envoy / Istio)

У сучасних хмарних Kubernetes-кластерах прокидання контексту орендаря починається ще до того, як HTTP-запит потрапляє до бекенд-сервісу.

На рівні Ingress Controller або Service Mesh (Istio / Envoy Proxy) реалізуються спеціальні фільтри маршрутизації:

1. **JWT Validation Filter:** Ingress перевіряє підпис токена доступу та декодує claim `tenant_id`.
2. **Header Injection:** Envoy підставляє захищений заголовок `x-tenant-id` у внутрішній мережевий запит до сервісу.
3. **Rate Limiting per Tenant:** Sidecar-проксі Envoy аналізує ліміти швидкості (Rate Limits) у розрізі `x-tenant-id`. Якщо орендар `tenant_101` перевищує свій ліміт 100 RPS, Envoy відхиляє його надлишкові запити відповіддю HTTP 429 Too Many Requests ще на підході до додатку, не витрачаючи CPU бекенда та з'єднання з базою даних.

```yaml
# Приклад конфігурації Envoy RateLimitFilter за ідентифікатором орендаря
domain: tenant-ratelimit
descriptors:
  - key: tenant_id
    rate_limit:
      unit: minute
      requests_per_unit: 600
```

Цей шар захисту дозволяє вирішити проблему «шумного сусіда» на мережевому рівні ще до того, як виклики здатні заблокувати з'єднання з базою даних.

## Взаємодія ORM із Row-Level Security

При використанні ORM-фреймворків (Prisma, GORM, Hibernate, Entity Framework Core) розробники часто намагаються реалізувати мультиарендність на рівні коду додатка за допомогою автоматичних фільтрів (Global Query Filters). 

Проте цей підхід має принципову слабкість:
* **Незахищені сирі запити (Raw SQL):** Якщо розробник виконує `db.Raw("SELECT * FROM devices ...")` або використовує складний Native Query, ORM-фреймворк не підставляє фільтр `tenant_id`, і додаток виконує запит без ізоляції.
* **Каскадні завантаження (Eager Loading / Joins):** При завантаженні зв'язаних сутностей ORM може згенерувати SQL-запит без урахування контексту орендаря у дочірніх таблицях.

Надійним рішенням є поєднання ORM з нативним RLS PostgreSQL. ORM-фреймворк налаштовується так, щоб перед виконанням будь-якої транзакції перехоплювач (Middleware / Interceptor) виконував команду `SELECT set_config('app.current_tenant', ?, true)`.

Наприклад, у Prisma це реалізується через розширення клієнта (Client Extensions):

```ts
// Prisma Client Extension для автоматичного RLS контексту
export const prismaWithTenant = (tenantId: string) => {
  return prisma.$extends({
    query: {
      $allModels: {
        async $allOperations({ args, query }) {
          return prisma.$transaction(async (tx) => {
            await tx.$executeRaw`SELECT set_config('app.current_tenant', ${tenantId}, true)`;
            return query(args);
          });
        },
      },
    },
  });
};
```

Цей підхід гарантує, що навіть при використанні сирих SQL-виразів всередині ORM нативний рушій PostgreSQL примусово застосує політики безпеки RLS.

## Перехоплення метаданих у gRPC та HTTP Interceptors

У мікросервісній архітектурі контекст орендаря має неявно транслюватися між сервісами при gRPC-викликах. Для цього реалізується gRPC Unary Server Interceptor, який перехоплює вхідні метадані:

```go
// TenantUnaryServerInterceptor перехоплює gRPC метадані й збагачує контекст
func TenantUnaryServerInterceptor() grpc.UnaryServerInterceptor {
	return func(
		ctx context.Context,
		req interface{},
		info *grpc.UnaryServerInfo,
		handler grpc.UnaryHandler,
	) (interface{}, error) {
		md, ok := metadata.FromIncomingContext(ctx)
		if !ok {
			return nil, status.Errorf(codes.Unauthenticated, "missing gRPC metadata")
		}

		tenantIDs := md.Get("x-tenant-id")
		if len(tenantIDs) == 0 || tenantIDs[0] == "" {
			return nil, status.Errorf(codes.Unauthenticated, "missing x-tenant-id in metadata")
		}

		// Збагачуємо контекст Go і передаємо далі по ланцюжку обробників
		newCtx := WithTenant(ctx, tenantIDs[0])
		return handler(newCtx, req)
	}
}
```

Такий інтерцептор гарантує, що жоден gRPC-метод не буде виконаний без наявності валідного `tenant_id` у контексті виконання Go-рутини.

## Багатовимірні політики доступу (RLS + ABAC)

У складних B2B-системах ізоляція за `tenant_id` є лише першим рівнем безпеки. Всередині одного орендаря користувачі мають різні ролі (наприклад, `admin`, `operator`, `viewer`). 

PostgreSQL дозволяє поєднувати мультиарендність (Tenancy) із розмежовуванням доступу на основі атрибутів (Attribute-Based Access Control — ABAC) у єдиній політиці RLS:

```sql
-- Політика доступу з урахуванням tenant_id ТА ролі користувача
CREATE POLICY tenant_abac_policy ON devices
    FOR ALL
    TO app_user
    USING (
        tenant_id = current_setting('app.current_tenant', true)
        AND (
            current_setting('app.current_user_role', true) = 'admin'
            OR (current_setting('app.current_user_role', true) = 'operator' AND status != 'archived')
            OR (created_by = current_setting('app.current_user_id', true))
        )
    );
```

Перед виконанням запиту сервіс встановлює три сесійні змінні у транзакції:

```sql
SELECT set_config('app.current_tenant', 'tenant_101', true);
SELECT set_config('app.current_user_role', 'operator', true);
SELECT set_config('app.current_user_id', 'usr_55', true);
```

Це дозволяє перенести не лише мультиарендну ізоляцію, а й усю складну логіку внутрішньоорганзаційних прав доступу на рівень рушія реляційної бази даних.

## Моніторинг RLS через pg_stat_statements

Для виявлення повільних запитів під RLS використовується системний модуль `pg_stat_statements`.

Оскільки `current_setting('app.current_tenant')` параметризує запит, у метаданих `pg_stat_statements` усі виклики для різних орендарів агрегуються у єдиний нормалізований SQL-шаблон. Це дозволяє аналізувати середній час виконання запиту (Mean Exec Time), кількість зчитаних блоків з буферного кешу та дискових IOPS у розрізі типів запитів незалежно від того, який саме орендар його викликав.

У результаті інженери отримають чітке розуміння продуктивності політики RLS без розбухання системної статистики бази даних.

## Навантажувальне тестування RLS (Performance Benchmarking)

Використання RLS додає додаткові накладні витрати на перевірку умов політики при кожному SQL-запиті. Проведення бенчмаркінгу під високим навантаженням (наприклад, за допомогою `pgbench` чи k6) демонструє наступні результати:

1. **Накладні витрати на виконання `set_config`:** Додатковий виклик `SELECT set_config(...)` у межах кожної транзакції збільшує latency запиту приблизно на 0.02..0.05 мс, що є незначним планом за гарантію ізоляції.
2. **Паралельне виконання (Concurrency & Lock Contention):** Оскільки змінна `app.current_tenant` є локальною для сесії транзакції (`is_local = true`), вона зберігається у пам'яті бекенд-процесу PostgreSQL (`PgProc`) і не викликає блокувань на рівні глобальних засувів (LwLocks).
3. **Ефективність кешування планів:** При використанні складених індексів `(tenant_id, id)` продуктивність вибірок у Pool-моделі з RLS поступається вибірці без RLS менше ніж на 3%, але повністю усуває ризик cross-tenant витоку даних.

## Автоматизоване інтеграційне тестування RLS

Для виявлення витоків даних у CI/CD пайплайнах пишуться спеціальні інтеграційні тести, які свідомо намагаються порушити межі доступу:

```go
func TestCrossTenantIsolation(t *testing.T) {
	db := setupTestDB(t)

	// 1. Створюємо пристрій для tenant_A
	ctxA := WithTenant(context.Background(), "tenant_A")
	var devID string
	err := ExecWithTenantIsolation(ctxA, db, func(tx *sql.Tx) error {
		return tx.QueryRow("INSERT INTO devices (tenant_id, name, status) VALUES ('tenant_A', 'Lock A', 'active') RETURNING id").Scan(&devID)
	})
	require.NoError(t, err)

	// 2. Спроба прочитати пристрій tenant_A під контекстом tenant_B
	ctxB := WithTenant(context.Background(), "tenant_B")
	err = ExecWithTenantIsolation(ctxB, db, func(tx *sql.Tx) error {
		var name string
		return tx.QueryRow("SELECT name FROM devices WHERE id = $1", devID).Scan(&name)
	})

	// Очікуємо sql.ErrNoRows, оскільки RLS має приховати рядок tenant_A від tenant_B
	require.ErrorIs(t, err, sql.ErrNoRows, "CRITICAL: RLS failed to prevent cross-tenant read!")
}
```

Такий автоматичний тест гарантує, що ніякі зміни у коді чи схемах даних не зможуть зламати межу ізоляції RLS незаміченими.

## Аналіз планів виконання запитів під RLS (EXPLAIN ANALYZE)

Щоб переконатися, що RLS не призводить до повнотабличного сканування (Seq Scan), проаналізуємо вивід `EXPLAIN ANALYZE` для запиту під активною политикою:

```sql
SET LOCAL app.current_tenant = 'tenant_101';
EXPLAIN ANALYZE SELECT * FROM devices WHERE status = 'active';
```

Результат виконання плану вказує на наявність внутрішньої фільтрації:

```text
Index Scan using idx_devices_tenant_status on devices  (cost=0.42..8.44 rows=1 width=78) (actual time=0.015..0.018 rows=3 loops=1)
  Index Cond: ((tenant_id)::text = 'tenant_101'::text)
  Filter: ((status)::text = 'active'::text)
```

Завдяки складеному індексу `(tenant_id, status)` ДБЖ спочатку відсікає всі сторінки інших орендарів через `Index Cond`, і лише потім застосовує додаткові фільтри. Це гарантує лінійну продуктивність незалежно від кількості орендарів у спільній базі.

## Стратегія безперервної міграції (Zero-Downtime RLS Migration)

Впровадження RLS у вже працюючу систему з мільйонами рядків вимагає поетапного підходу, щоб не заблокувати таблиці для запису:

1. **Етап 1: Додавання дискримінатора та індексів.** Додаємо колонку `tenant_id` у режимі `NULL` і створюємо складені індекси `CONCURRENTLY`, щоб не викликати блокування таблиць.
2. **Етап 2: Заповнення даних у фоні (Backfill).** Фоновий скрипт порціями по 1 000 рядків проставляє `tenant_id` на основі зв'язаних таблиць.
3. **Етап 3: Вмикання RLS у прозорому режимі.** Вмикаємо `ENABLE ROW LEVEL SECURITY`, але створюємо тимчасову політику `FOR ALL USING (true)`, яка дозволяє читати всі рядки.
4. **Етап 4: Перемикання на сесійну політику.** Оновлюємо код додатку, вмикаємо транзакційні обгортки `set_config` та замінюємо тимчасову політику на сувору `tenant_id = current_setting('app.current_tenant')`.

Ця чотикрокова стратегія дозволяє перевести legacy-систему на RLS-ізоляцію без зупинки обробки користувацького трафіку.

## Трасування та аудит сесійних змінних у логах

Для розслідування інцидентів безпеки та моніторингу активності орендарів конфігурацію PostgreSQL доповнюють параметром `log_line_prefix`, який включає значення сесійної змінної в кожен рядок логу бази даних:

```text
# postgresql.conf
log_line_prefix = '%t [%p] tenant=%X{app.current_tenant} user=%u db=%d: '
```

У результаті системні логи PostgreSQL виглядають наступним чином:

```text
2026-08-18 10:15:02 UTC [12345] tenant=tenant_101 user=app_user db=dh_prod: LOG: statement: SELECT * FROM devices;
2026-08-18 10:15:05 UTC [12346] tenant=tenant_102 user=app_user db=dh_prod: ERROR: new row violates row-level security policy for table "devices"
```

Це дозволяє інженерам з безпеки негайно ловити спроби горизонтальної ескалації та бачити, який саме орендар згенерував помилку безпеки RLS на рівні баз даних.

## Глибокий аналіз пасток та крайових випадків

Використання RLS та сесійних змінних у високонавантажених мультиарендних системах ховає декілька серйозних інженерних викликів, які виникають на стику роботи пулу з'єднань, індексування та підготовлених виразів (Prepared Statements).

### 1. Витік сесійного стану у пулі з'єднань (Connection Pool Dirtying)

Найпоширеніша помилка — використання глобальної команди `SET app.current_tenant = 'tenant_A'` поза блоком транзакції. 

Коли додаток використовує пулер з'єднань (наприклад, PgBouncer у режимі transaction pooling чи внутрішній пул мови Go/Node.js):
1. Запит А бере з'єднання №5 з пулу і виконує `SET app.current_tenant = 'tenant_A'`.
2. Запит А завершується, але з'єднання повертається до пулу без виконання `DISCARD ALL` або `RESET ALL`.
3. Запит Б бере з'єднання №5 для обробки запиту від `tenant_B`. Якщо додаток з певної причини забув встановити свій контекст, сесійна змінна залишається рівною `'tenant_A'`.
4. Запит Б читає або модифікує дані `tenant_A`!

**Рішення:** Використовувати виключно `SELECT set_config('app.current_tenant', $1, true)` (де `is_local = true`) усередині чіткого транзакційного блоку `BEGIN...COMMIT`. При завершенні транзакції PostgreSQL автоматично скидає локальну змінну до початкового стану (`NULL`).

### 2. Вплив на підготовлені вирази (Prepared Statements & Query Cache)

Оптимізатор PostgreSQL будує план виконання для підготовлених виразів (`PREPARE stmt AS SELECT ...`). При використанні RLS план запиту може суттєво змінюватися залежно від того, які індекси доступні для конкретного `tenant_id`.

Якщо `tenant_id` передається як сесійна змінна `current_setting()`, PostgreSQL змушений будувати загальний план запиту (Generic Plan). Якщо у вас є один «гігантський» орендар (наприклад, 10 мільйонів рядків) і тисяча дрібних (по 100 рядків):
* Оптимізатор може обрати `Index Scan` для дрібного орендаря, що чудово працює.
* Але для гігантського орендаря той самий `Index Scan` може виявитися повільнішим за `Bitmap Heap Scan`.

**Рішення:** Завжди будувати складені індекси (Compound Indexes), де `tenant_id` стоїть на **першому місці**:

```sql
-- Правильний індекс для мультиарендної таблиці
CREATE INDEX idx_devices_tenant_status ON devices (tenant_id, status, created_at);
```

Такий індекс гарантує, що B-Tree дерево індексу спочатку відріже всі сторінки інших орендарів, і селективність вибірки залишатиметься високою незалежно від того, використовується Generic чи Custom план запиту.

### 3. Проблема авторизації у підзапитах (Subquery RLS Leakage)

Коли запит містить складні підзапити чи представлення (Views), RLS за замовчуванням застосовується до кожнаї таблиці окремо. Проте якщо розробник створює представлення з прапорцем `SECURITY DEFINER` від імені суперкористувача, перевірка RLS може бути пропущена!

```sql
-- ПАСТКА: VIEW створене від імені postgres з SECURITY DEFINER обходить RLS!
CREATE VIEW public_device_stats WITH (security_barrier=true) AS
SELECT tenant_id, count(*) FROM devices GROUP BY tenant_id;
```

Прапорець `security_barrier=true` є обов'язковим при створенні будь-яких представлень над таблицями з RLS. Без нього оптимізатор PostgreSQL може переставити умови push-down фільтрації місцями та виконати користувацьку функцію раніше за перевірку політики безпеки RLS, що дозволить зловмиснику витягнути чужі дані через побічні ефекти (Side-Channel Leaks).

### 4. Втрата контексту у фонових асинхронних задачах

Коли вхідний HTTP-запит публікує подію в чергу задач (наприклад, `TaskQueue.Enqueue(DeviceReportTask{DeviceID: "123"})`), контекст HTTP-запиту вмирає разом із відповіддю клієнту.

Асинхронний воркер читає задачу з черги у новому потоці execution context, де немає HTTP-заголовків або сесії. Якщо розробник явним чином не передасть `TenantID` у тілі чи metadata повідомлення:

```go
// Правильна структура обгортки задачі в черзі
type QueueMessage struct {
    TenantID string          `json:"tenant_id"`
    Payload  json.RawMessage `json:"payload"`
}
```

Воркер не зможе встановити RLS-контекст і запит до бази даних поверне порожній результат або падає з помилкою безпеки. Прокидання `tenant_id` у метаданих черг та OpenTelemetry-контексті є обов'язковим стандартом для всіх фонових процесів мультиарендної системи.
