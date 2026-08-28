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
