// Порт — інтерфейс. Домен залежить лише від нього.
type TelemetryStore interface {
    Write(ctx context.Context, r Reading) error
    Query(ctx context.Context, home HomeID, from, to time.Time) (Series, error)
}

// Адаптер #1 — Postgres. Задовольняє інтерфейс НЕЯВНО:
// має потрібні методи — отже вже TelemetryStore, без жодного "implements".
type PostgresStore struct{ db *pgxpool.Pool }

func (s *PostgresStore) Write(ctx context.Context, r Reading) error {
    _, err := s.db.Exec(ctx,
        `insert into readings(home, ts, metric, value) values ($1,$2,$3,$4)`,
        r.Home, r.TS, r.Metric, r.Value)
    return err
}

func (s *PostgresStore) Query(ctx context.Context, home HomeID, from, to time.Time) (Series, error) {
    rows, err := s.db.Query(ctx,
        `select ts, value from readings where home=$1 and ts between $2 and $3 order by ts`,
        home, from, to)
    if err != nil {
        return nil, err
    }
    defer rows.Close()

    var out Series
    for rows.Next() {
        var p Point
        if err := rows.Scan(&p.TS, &p.Value); err != nil {
            return nil, err
        }
        out = append(out, p)
    }
    return out, rows.Err()
}

// Домен бере будь-який TelemetryStore — і не знає, який саме.
type EnergyPanel struct{ store TelemetryStore }

func (p *EnergyPanel) Daily(ctx context.Context, home HomeID, day time.Time) (Series, error) {
    return p.store.Query(ctx, home, startOfDay(day), endOfDay(day))
}
