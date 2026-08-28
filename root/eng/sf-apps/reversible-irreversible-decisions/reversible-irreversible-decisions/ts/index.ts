// ЗІ ШВОМ: логіка знає тільки інтерфейс, база — за адаптером
interface OrderRepo {                     // порт: контракт без бази
    total(orderId: number): Promise<number>;
}

function orderTotal(repo: OrderRepo, orderId: number): Promise<number> {
    return repo.total(orderId);           // жодного сліду конкретної бази
}

// Конкретна база живе в ОДНОМУ місці — в адаптері:
class PgOrderRepo implements OrderRepo {  // сьогодні PostgreSQL...
    async total(orderId: number): Promise<number> { /* pg-запит саме тут */ return 0; }
}
// Завтра інша база — новий адаптер, а orderTotal і виклики не міняються.
