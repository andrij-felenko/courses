// Go — рідний дім цього стилю: жодного ORM, рядок збираєш явним Scan.
func (r *SqliteDeviceRepo) FindSilentOver(minutes int) ([]Device, error) {
    rows, err := r.db.Query(`
        SELECT d.id, d.type, d.room, d.state, d.last_seen
        FROM devices d
        LEFT JOIN (
            SELECT device_id, MAX(at) AS last_at
            FROM telemetry GROUP BY device_id
        ) t ON t.device_id = d.id
        WHERE t.last_at IS NULL
           OR t.last_at < CAST(strftime('%s','now') AS INTEGER) - ?*60`, minutes)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var out []Device
    for rows.Next() {
        var d Device                                  // збираємо об'єкт із рядка РУКАМИ
        if err := rows.Scan(&d.ID, &d.Type, &d.Room, &d.State, &d.LastSeen); err != nil {
            return nil, err
        }
        out = append(out, d)
    }
    return out, rows.Err()
}
