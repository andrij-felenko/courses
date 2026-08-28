// Створення нового екземпляра солвера для вказаного пулу
Solver *solver_create(Pool *pool);

// Звільнення пам'яті екземпляра солвера
void solver_free(Solver *solv);

// Виконання процесу розв'язання залежностей
int solver_solve(Solver *solv, Queue *jobqueue);

// Створення об'єкта підсумкової транзакції
Transaction *solver_create_transaction(Solver *solv);

// Звільнення об'єкта транзакції
void transaction_free(Transaction *trans);
