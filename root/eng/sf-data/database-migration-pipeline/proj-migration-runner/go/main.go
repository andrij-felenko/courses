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
