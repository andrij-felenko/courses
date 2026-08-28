// Логіка оновлення профілю у версії коду v1.1 (Dual Write)
func UpdateUserPhone(ctx context.Context, db *sql.DB, userID int64, rawPhone string) error {
    normalizedPhone, err := formatE164(rawPhone)
    if err != nil {
        return fmt.Errorf("невалідний телефон: %w", err)
    }

    query := `
        UPDATE users 
        SET phone = $1, 
            phone_e164 = $2, 
            updated_at = NOW() 
        WHERE id = $3`
    _, err = db.ExecContext(ctx, query, rawPhone, normalizedPhone, userID)
    return err
}
