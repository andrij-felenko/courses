// billing/projection.go — та сама згортка, явним SQL без ORM
func onDeviceEvent(db *sql.DB, e DeviceEvent) error {
    active := e.Type == "device.activated"
    _, err := db.Exec(`
        INSERT INTO home_device_state (device_id, home_id, active, at)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (device_id) DO UPDATE
            SET active = EXCLUDED.active, at = EXCLUDED.at
            WHERE EXCLUDED.at > home_device_state.at`, // дубль/стара подія → пустий хід
        e.DeviceID, e.HomeID, active, e.At)
    return err
}

// нарахування читає ВЛАСНУ табличку білінга
func activeDeviceCount(db *sql.DB, homeID int) (int, error) {
    var n int
    err := db.QueryRow(`
        SELECT count(*) FROM home_device_state
        WHERE home_id = $1 AND active = true`, homeID).Scan(&n)
    return n, err
}
