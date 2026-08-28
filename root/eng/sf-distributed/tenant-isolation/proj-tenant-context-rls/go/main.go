package main

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
	"log"
	"net/http"
)

type contextKey string

const tenantContextKey contextKey = "tenantID"

// TenantMiddleware вилучає та валідує ідентифікатор орендаря з вхідного HTTP-запиту
func TenantMiddleware(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		tenantID := r.Header.Get("X-Tenant-ID")
		if tenantID == "" {
			http.Error(w, "Unauthorized: missing X-Tenant-ID", http.StatusUnauthorized)
			return
		}

		// Збереження ідентифікатора у незмінному контексті запиту
		ctx := context.WithValue(r.Context(), tenantContextKey, tenantID)
		next.ServeHTTP(w, r.WithContext(ctx))
	})
}

// GetTenantID витягує ідентифікатор орендаря з поточного контексту
func GetTenantID(ctx context.Context) (string, error) {
	val, ok := ctx.Value(tenantContextKey).(string)
	if !ok || val == "" {
		return "", errors.New("tenant context is missing in execution context")
	}
	return val, nil
}

// WithTenantTx відкриває транзакцію та безпечно встановлює змінну сесії RLS
func WithTenantTx(ctx context.Context, db *sql.DB, fn func(tx *sql.Tx) error) error {
	tenantID, err := GetTenantID(ctx)
	if err != nil {
		return err
	}

	tx, err := db.BeginTx(ctx, nil)
	if err != nil {
		return fmt.Errorf("failed to begin transaction: %w", err)
	}
	defer tx.Rollback()

	// SET LOCAL обмежує дію змінної сесії межами поточної транзакції
	setQuery := "SET LOCAL app.current_tenant_id = $1;"
	if _, err := tx.ExecContext(ctx, setQuery, tenantID); err != nil {
		return fmt.Errorf("failed to inject tenant session context: %w", err)
	}

	// Виконання прикладної бізнес-логіки
	if err := fn(tx); err != nil {
		return err
	}

	return tx.Commit()
}

// QueryTenantDocuments демонструє безпечне читання даних без ручного WHERE tenant_id
func QueryTenantDocuments(ctx context.Context, db *sql.DB) error {
	return WithTenantTx(ctx, db, func(tx *sql.Tx) error {
		// Запит не вимагає ручного фільтра: СУБД автоматично застосує RLS
		rows, err := tx.QueryContext(ctx, "SELECT id, title, content FROM documents;")
		if err != nil {
			return err
		}
		defer rows.Close()

		for rows.Next() {
			var id, title, content string
			if err := rows.Scan(&id, &title, &content); err != nil {
				return err
			}
			fmt.Printf("Document retrieved: [%s] %s\n", id, title)
		}
		return rows.Err()
	})
}

func main() {
	fmt.Println("Мультиарендний сервіс із підтримкою RLS успішно ініціалізовано.")
}
