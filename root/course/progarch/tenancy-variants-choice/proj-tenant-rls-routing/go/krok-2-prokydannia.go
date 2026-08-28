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
