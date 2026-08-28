// adapters/pg.go ── ДРАЙВОВАНИЙ АДАПТЕР. Реалізує ЗамовленняСховище через Postgres.
package adapters

import (
    "context"
    "database/sql"
    "encoding/json"

    "example/order"
    "github.com/jackc/pgx/v5/pgxpool"
)

type PgСховище struct{ DB *pgxpool.Pool }

func (r *PgСховище) Зберегти(з order.Замовлення) error {
    поз, _ := json.Marshal(з.Позиції)
    _, err := r.DB.Exec(context.Background(), // ← SQL живе ТІЛЬКИ в цьому файлі
        `INSERT INTO orders(id, email, positions, total) VALUES ($1,$2,$3,$4)`,
        з.ID, з.Пошта, поз, з.Сума())
    return err
}

func (r *PgСховище) Узяти(id string) (*order.Замовлення, error) {
    var email, поз string
    err := r.DB.QueryRow(context.Background(),
        "SELECT email, positions FROM orders WHERE id=$1", id).Scan(&email, &поз)
    if err == sql.ErrNoRows {
        return nil, nil
    }
    if err != nil {
        return nil, err
    }
    var позиції []order.Позиція
    json.Unmarshal([]byte(поз), &позиції)
    з, err := order.Створити(id, email, позиції)
    return &з, err
}
