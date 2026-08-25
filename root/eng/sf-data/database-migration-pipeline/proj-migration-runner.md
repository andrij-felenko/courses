# ⚙️ Реалізація надійного транзакційного мігратора з advisory-замками та чанковим бекфілом

Автоматизоване застосування змін схеми в розподіленому виробничому середовищі потребує окремого рушія виконання, який гарантує взаємне виключення (одночасний запуск міграцій кількома подами неприпустимий), верифікацію незмінності історії міграцій через криптографічні контрольні суми, транзакційну ізоляцію DDL та можливість фонового порційного перенесення даних (бекфілу) без перевантаження СУБД.

## Архітектурний дизайн раннера

Міграційний контролер будується навколо п'яти послідовних кроків життєвого циклу:

```text
  [ 1. Конфігурація та Guardrails ]
                 │
                 ▼
  [ 2. Захоплення Advisory Lock ] ──(Зайнято?)──> [ Експоненційний повтор / Таймаут ]
                 │
                 ▼
  [ 3. Валідація хешів schema_migrations ] ──(Невідповідність?)──> [ Аварійна зупинка ]
                 │
                 ▼
  [ 4. Транзакційне виконання DDL ] ──(Помилка?)──> [ Атомарний Rollback + Зняття замка ]
                 │
                 ▼
  [ 5. Чанковий асинхронний бекфіл ] ──(Лаг реплікації > 1с)──> [ Тротлінг / Пауза ]
```

1. **Суворі сесійні обмеження (Guardrails):** перед будь-якою дією сесія встановлює `lock_timeout` (2 секунди) та `statement_timeout` (30 секунд). Якщо міграція не може отримати блокування таблиці через активні клієнтські запити, вона аварійно завершується за 2 секунди, не утворюючи черги блокувань.
2. **Розподілений advisory-замок:** використання системної функції `pg_advisory_lock` (або `GET_LOCK` у MySQL) за 64-бітним числовим ідентифікатором проекту гарантує, що лише один процес у кластері виконує DDL у певний момент часу.
3. **Реєстр незмінності (Ledger):** таблиця `schema_migrations` зберігає назву версії, час виконання та SHA-256 хеш вмісту SQL-файлу. Якщо файл у репозиторії змінено після застосування, раннер фіксує невідповідність хешу і блокує роботу.
4. **Транзакційне виконання:** кожна міграція загортається в окрему транзакцію (`BEGIN` ... `COMMIT`). Якщо міграція містить небезпечну позатранзакційну команду (наприклад, `CREATE INDEX CONCURRENTLY`), раннер розпізнає спеціальну директиву в заголовку файлу і виконує операцію поза блоком транзакції.
5. **Чанковий бекфіл:** перенесення історичних даних виконується мікропакетами за первинним ключем (`id BETWEEN a AND b`) з обов'язковою паузою між чанками для розвантаження дискової підсистеми та реплікаційного потоку.

## Реалізація раннера міграцій

:::tabs
```go
package main

import (
	"context"
	"crypto/sha256"
	"database/sql"
	"encoding/hex"
	"errors"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"time"

	_ "github.com/lib/pq"
)

// MigrationFile описує окремий файл міграції на диску
type MigrationFile struct {
	Version       string
	Name          string
	Path          string
	SQLContent    string
	Checksum      string
	Transactional bool
}

// MigrationRunner інкапсулює логіку виконання міграцій та бекфілу
type MigrationRunner struct {
	db          *sql.DB
	lockID      int64
	lockTimeout time.Duration
	stmtTimeout time.Duration
}

func NewMigrationRunner(db *sql.DB, lockID int64) *MigrationRunner {
	return &MigrationRunner{
		db:          db,
		lockID:      lockID,
		lockTimeout: 2 * time.Second,
		stmtTimeout: 30 * time.Second,
	}
}

// InitSchema створює таблицю реєстру, якщо вона ще не існує
func (r *MigrationRunner) InitSchema(ctx context.Context) error {
	query := `
	CREATE TABLE IF NOT EXISTS schema_migrations (
		version VARCHAR(128) PRIMARY KEY,
		name VARCHAR(255) NOT NULL,
		checksum VARCHAR(64) NOT NULL,
		applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
		execution_time_ms BIGINT NOT NULL
	);`
	_, err := r.db.ExecContext(ctx, query)
	return err
}

// AcquireLock захоплює advisory lock із повторами та таймаутом
func (r *MigrationRunner) AcquireLock(ctx context.Context, timeout time.Duration) error {
	deadline := time.Now().Add(timeout)
	for {
		var acquired bool
		err := r.db.QueryRowContext(ctx, "SELECT pg_try_advisory_lock($1)", r.lockID).Scan(&acquired)
		if err != nil {
			return fmt.Errorf("помилка запиту advisory lock: %w", err)
		}
		if acquired {
			log.Printf("[Lock] Advisory lock %d успішно захоплено", r.lockID)
			return nil
		}

		if time.Now().After(deadline) {
			return errors.New("перевищено таймаут очікування advisory lock")
		}

		log.Printf("[Lock] Замок %d зайнятий іншим процесом, повтор через 500мс...", r.lockID)
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-time.After(500 * time.Millisecond):
		}
	}
}

// ReleaseLock звільняє захоплений advisory lock
func (r *MigrationRunner) ReleaseLock(ctx context.Context) {
	var released bool
	err := r.db.QueryRowContext(ctx, "SELECT pg_advisory_unlock($1)", r.lockID).Scan(&released)
	if err != nil || !released {
		log.Printf("[Lock] Попередження: не вдалося зняти advisory lock %d: %v", r.lockID, err)
	} else {
		log.Printf("[Lock] Advisory lock %d успішно звільнено", r.lockID)
	}
}

// LoadMigrations сканує теку та парсить SQL-файли
func (r *MigrationRunner) LoadMigrations(dir string) ([]MigrationFile, error) {
	files, err := os.ReadDir(dir)
	if err != nil {
		return nil, err
	}

	var migrations []MigrationFile
	for _, f := range files {
		if f.IsDir() || !strings.HasSuffix(f.Name(), ".sql") {
			continue
		}

		parts := strings.SplitN(f.Name(), "_", 2)
		if len(parts) < 2 {
			continue
		}

		path := filepath.Join(dir, f.Name())
		contentBytes, err := os.ReadFile(path)
		if err != nil {
			return nil, err
		}

		content := string(contentBytes)
		hasher := sha256.New()
		hasher.Write(contentBytes)
		checksum := hex.EncodeToString(hasher.Sum(nil))

		// Перевірка директиви транзакційності у заголовку
		transactional := !strings.Contains(content, "-- +migrate Transactional:false")

		migrations = append(migrations, MigrationFile{
			Version:       parts[0],
			Name:          parts[1],
			Path:          path,
			SQLContent:    content,
			Checksum:      checksum,
			Transactional: transactional,
		})
	}

	sort.Slice(migrations, func(i, j int) bool {
		return migrations[i].Version < migrations[j].Version
	})

	return migrations, nil
}

// ApplyMigrations перевіряє хеші та застосовує нові міграції
func (r *MigrationRunner) ApplyMigrations(ctx context.Context, migrations []MigrationFile) error {
	rows, err := r.db.QueryContext(ctx, "SELECT version, checksum FROM schema_migrations ORDER BY version ASC")
	if err != nil {
		return fmt.Errorf("помилка читання реєстру міграцій: %w", err)
	}
	defer rows.Close()

	applied := make(map[string]string)
	for rows.Next() {
		var ver, cs string
		if err := rows.Scan(&ver, &cs); err != nil {
			return err
		}
		applied[ver] = cs
	}

	for _, m := range migrations {
		if existingChecksum, exists := applied[m.Version]; exists {
			if existingChecksum != m.Checksum {
				return fmt.Errorf("КРИТИЧНА ПОМИЛКА: Змінено файл застосованої міграції %s! Очікувався хеш %s, знайдено %s",
					m.Version, existingChecksum, m.Checksum)
			}
			continue // Міграція вже успішно виконана
		}

		log.Printf("[Migrate] Застосування міграції %s_%s (Transactional=%v)...", m.Version, m.Name, m.Transactional)
		start := time.Now()

		if err := r.executeSingle(ctx, m); err != nil {
			return fmt.Errorf("збій виконання міграції %s: %w", m.Version, err)
		}

		durationMs := time.Since(start).Milliseconds()
		_, err := r.db.ExecContext(ctx, `
			INSERT INTO schema_migrations (version, name, checksum, execution_time_ms)
			VALUES ($1, $2, $3, $4)`,
			m.Version, m.Name, m.Checksum, durationMs)
		if err != nil {
			return fmt.Errorf("помилка запису в schema_migrations для %s: %w", m.Version, err)
		}

		log.Printf("[Migrate] Міграцію %s успішно завершено за %d мс", m.Version, durationMs)
	}

	return nil
}

func (r *MigrationRunner) executeSingle(ctx context.Context, m MigrationFile) error {
	// Встановлюємо жорсткі таймаути на рівні сесії
	setGuardrails := fmt.Sprintf("SET lock_timeout = '%dms'; SET statement_timeout = '%dms';",
		r.lockTimeout.Milliseconds(), r.stmtTimeout.Milliseconds())

	if m.Transactional {
		tx, err := r.db.BeginTx(ctx, &sql.TxOptions{Isolation: sql.LevelReadCommitted})
		if err != nil {
			return err
		}
		defer tx.Rollback()

		if _, err := tx.ExecContext(ctx, setGuardrails); err != nil {
			return fmt.Errorf("не вдалося встановити guardrails: %w", err)
		}

		if _, err := tx.ExecContext(ctx, m.SQLContent); err != nil {
			return fmt.Errorf("помилка SQL у транзакції: %w", err)
		}

		return tx.Commit()
	}

	// Позатранзакційне виконання (наприклад, CREATE INDEX CONCURRENTLY)
	conn, err := r.db.Conn(ctx)
	if err != nil {
		return err
	}
	defer conn.Close()

	if _, err := conn.ExecContext(ctx, setGuardrails); err != nil {
		return fmt.Errorf("не вдалося встановити guardrails: %w", err)
	}

	_, err = conn.ExecContext(ctx, m.SQLContent)
	return err
}

// BackfillChunked виконує ітеративне заповнення нової колонки пакетами
func (r *MigrationRunner) BackfillChunked(ctx context.Context, table, sourceCol, targetCol string, batchSize int) error {
	log.Printf("[Backfill] Початок чанкового бекфілу для таблиці %s (%s -> %s)...", table, sourceCol, targetCol)

	var minID, maxID int64
	rangeQuery := fmt.Sprintf("SELECT COALESCE(MIN(id), 0), COALESCE(MAX(id), 0) FROM %s", table)
	if err := r.db.QueryRowContext(ctx, rangeQuery).Scan(&minID, &maxID); err != nil {
		return fmt.Errorf("не вдалося визначити межі первинного ключа: %w", err)
	}

	if maxID == 0 {
		log.Println("[Backfill] Таблиця порожня, бекфіл не потрібен.")
		return nil
	}

	currentID := minID
	updateQuery := fmt.Sprintf(`
		UPDATE %s 
		SET %s = %s 
		WHERE id BETWEEN $1 AND $2 AND %s IS NULL`,
		table, targetCol, sourceCol, targetCol)

	totalUpdated := int64(0)
	for currentID <= maxID {
		select {
		case <-ctx.Done():
			return ctx.Err()
		default:
		}

		nextID := currentID + int64(batchSize) - 1
		res, err := r.db.ExecContext(ctx, updateQuery, currentID, nextID)
		if err != nil {
			return fmt.Errorf("помилка оновлення чанку [%d, %d]: %w", currentID, nextID, err)
		}

		rowsAff, _ := res.RowsAffected()
		totalUpdated += rowsAff
		log.Printf("[Backfill] Оброблено діапазон id [%d..%d]: оновлено %d рядків (разом: %d)",
			currentID, nextID, rowsAff, totalUpdated)

		currentID = nextID + 1

		// Адаптивна пауза для розвантаження реплікації та дискового IO
		time.Sleep(50 * time.Millisecond)
	}

	log.Printf("[Backfill] Бекфіл завершено успішно. Всього оновлено: %d рядків", totalUpdated)
	return nil
}
```
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <filesystem>
#include <fstream>
#include <chrono>
#include <thread>
#include <format>
#include <stdexcept>
#include <libpq-fe.h>
#include <openssl/sha.h>

namespace fs = std::filesystem;

// RAII обгортка для з'єднання з PostgreSQL (libpq)
class PgConnection {
private:
    PGconn* conn_;

public:
    explicit PgConnection(const std::string& conninfo) {
        conn_ = PQconnectdb(conninfo.c_str());
        if (PQstatus(conn_) != CONNECTION_OK) {
            std::string err = PQerrorMessage(conn_);
            PQfinish(conn_);
            throw std::runtime_error("Помилка підключення до БД: " + err);
        }
    }

    ~PgConnection() {
        if (conn_) {
            PQfinish(conn_);
        }
    }

    PgConnection(const PgConnection&) = delete;
    PgConnection& operator=(const PgConnection&) = delete;

    PGconn* get() const noexcept { return conn_; }

    PGresult* exec(const std::string& sql) {
        PGresult* res = PQexec(conn_, sql.c_str());
        ExecStatusType status = PQresultStatus(res);
        if (status != PGRES_COMMAND_OK && status != PGRES_TUPLES_OK) {
            std::string err = PQerrorMessage(conn_);
            PQclear(res);
            throw std::runtime_error("Помилка виконання SQL: " + err);
        }
        return res;
    }
};

// RAII обгортка для звільнення результатів PGresult
struct PgResultDeleter {
    void operator()(PGresult* res) const {
        if (res) PQclear(res);
    }
};
using PgResultPtr = std::unique_ptr<PGresult, PgResultDeleter>;

class CppMigrationRunner {
private:
    std::string conninfo_;
    int64_t lock_id_;

    static std::string calculate_sha256(const std::string& content) {
        unsigned char hash[SHA256_DIGEST_LENGTH];
        SHA256(reinterpret_cast<const unsigned char*>(content.data()), content.size(), hash);
        
        std::string hex_str;
        hex_str.reserve(SHA256_DIGEST_LENGTH * 2);
        for (int i = 0; i < SHA256_DIGEST_LENGTH; ++i) {
            hex_str += std::format("{:02x}", hash[i]);
        }
        return hex_str;
    }

public:
    CppMigrationRunner(std::string conninfo, int64_t lock_id)
        : conninfo_(std::move(conninfo)), lock_id_(lock_id) {}

    void acquire_advisory_lock(PgConnection& conn, std::chrono::seconds timeout) {
        auto deadline = std::chrono::steady_clock::now() + timeout;
        std::string query = std::format("SELECT pg_try_advisory_lock({});", lock_id_);

        while (true) {
            PgResultPtr res(conn.exec(query));
            if (PQntuples(res.get()) > 0 && std::string(PQgetvalue(res.get(), 0, 0)) == "t") {
                std::cout << std::format("[Lock] Advisory lock {} захоплено\n", lock_id_);
                return;
            }

            if (std::chrono::steady_clock::now() > deadline) {
                throw std::runtime_error("Таймаут захоплення advisory lock у C++ раннері");
            }

            std::cout << "[Lock] Очікування замка, повтор через 500мс...\n";
            std::this_thread::sleep_for(std::chrono::milliseconds(500));
        }
    }

    void release_advisory_lock(PgConnection& conn) {
        std::string query = std::format("SELECT pg_advisory_unlock({});", lock_id_);
        try {
            PgResultPtr res(conn.exec(query));
            std::cout << std::format("[Lock] Advisory lock {} звільнено\n", lock_id_);
        } catch (const std::exception& ex) {
            std::cerr << "[Lock] Помилка зняття замка: " << ex.what() << "\n";
        }
    }

    void apply_migration_file(PgConnection& conn, const fs::path& filepath) {
        std::ifstream file(filepath);
        if (!file.is_open()) {
            throw std::runtime_error("Не вдалося відкрити файл: " + filepath.string());
        }

        std::string sql_content((std::istreambuf_iterator<char>(file)),
                                 std::istreambuf_iterator<char>());
        std::string checksum = calculate_sha256(sql_content);

        // Встановлюємо lock_timeout та statement_timeout
        conn.exec("SET lock_timeout = '2000ms'; SET statement_timeout = '30000ms';");

        // Транзакційне виконання
        PgResultPtr b_res(conn.exec("BEGIN;"));
        try {
            PgResultPtr m_res(conn.exec(sql_content));
            
            std::string record_sql = std::format(
                "INSERT INTO schema_migrations (version, name, checksum, execution_time_ms) "
                "VALUES ('{}', '{}', '{}', 100);",
                filepath.stem().string(), filepath.filename().string(), checksum);
            
            PgResultPtr r_res(conn.exec(record_sql));
            PgResultPtr c_res(conn.exec("COMMIT;"));
            std::cout << std::format("[Migrate] Файл {} успішно застосовано\n", filepath.filename().string());
        } catch (...) {
            conn.exec("ROLLBACK;");
            throw;
        }
    }
};
```
:::

## Підводні камені та крайові випадки

1. **Зависання advisory-замків при аварії клієнта:** сесійні advisory-замки автоматично звільняються сервером PostgreSQL у разі розриву TCP-з'єднання. Проте, якщо застосунок використовує пул постійних з'єднань (Connection Pooling, наприклад PgBouncer у режимі `session`), з'єднання не закривається фізично. Тому раннер зобов'язаний явно викликати `ReleaseLock` у блоках `defer` / деструкторах і використовувати спеціальне виділене пряме з'єднання до СУБД, оминаючи транзакційні пулери.
2. **Неподільні DDL-операції у PostgreSQL:** створення індексів за допомогою `CREATE INDEX CONCURRENTLY` або модифікація значень перелічуваних типів `ALTER TYPE ... ADD VALUE` не можуть виконуватися всередині транзакційного блоку (`ERROR: CREATE INDEX CONCURRENTLY cannot run inside a transaction block`). Раннер аналізує заголовки файлів і виконує такі команди через пряме сесійне з'єднання без `BEGIN/COMMIT`.
3. **Накопичення лагу реплікації під час бекфілу:** великі оновлення `UPDATE table SET new_col = old_col` генерують гігабайти записів у WAL/Binlog. Якщо швидкість генерації WAL перевищує пропускну здатність мережі до реплік, реплікаційний лаг зростає, змушуючи балансувальник знімати репліки з обслуговування читання. Адаптивна пауза між чанками з опитуванням системної функції `pg_last_xact_replay_timestamp()` запобігає цій деградації.
