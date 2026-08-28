// ЗІ ШВОМ: логіка знає тільки інтерфейс, база — за адаптером
type OrderRepo interface {                // порт: контракт без бази
    Total(orderID int) float64
}

func orderTotal(repo OrderRepo, orderID int) float64 {
    return repo.Total(orderID)            // жодного сліду конкретної бази
}

// Конкретна база живе в ОДНОМУ місці — в адаптері:
type PgOrderRepo struct{ db *pgx.Conn }  // сьогодні PostgreSQL...
func (r PgOrderRepo) Total(orderID int) float64 { /* pgx-запит саме тут */ }
// Завтра інша база — новий адаптер, а orderTotal і виклики не міняються.
