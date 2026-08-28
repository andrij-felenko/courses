// Store — спільний стан фільтрів. Кожен метод АТОМАРНИЙ: саме це рятує від гонок.
type Store interface {
	// SetNX: поставити ключ, лише якщо його ще нема. true = МИ перші.
	// Redis: SET key val NX EX ttl → OK або nil.
	SetNX(ctx context.Context, key string, ttl time.Duration) (bool, error)

	// Append: додати у список групи, повернути НОВУ довжину. 1 = ми відкрили групу.
	// Redis: RPUSH group item → ціле (довжина списку ПІСЛЯ додавання).
	Append(ctx context.Context, group string, item []byte, ttl time.Duration) (int, error)

	// Drain: забрати весь список групи й видалити його — за один неподільний крок.
	// Redis: LRANGE+DEL в одному Lua-скрипті.
	Drain(ctx context.Context, group string) ([][]byte, error)

	// Take: списати 1 жетон із відра (user,channel), якщо є.
	// Годинник для дозрівання — САМОГО сховища (Redis TIME), а не інстанса.
	Take(ctx context.Context, bucket string, burst, refillPerSec float64) (bool, error)

	// --- Довговічний індекс дедлайнів: щоб таймери груп пережили перезапуск. ---

	// MarkDue: записати (чи оновити) мить флашу групи в індексі за часом.
	// Redis: ZADD due <оцінка = unix-мить-флашу> <група>.
	MarkDue(ctx context.Context, group string, at time.Time) error

	// DueGroups: усі групи, чий дедлайн уже настав (оцінка ≤ now).
	// Redis: ZRANGEBYSCORE due -inf <now> → зріз груп.
	DueGroups(ctx context.Context, now time.Time) ([]string, error)

	// ClearDue: прибрати групу з індексу після вдалого флашу (щоб не флашити вдруге).
	// Redis: ZREM due <група>.
	ClearDue(ctx context.Context, group string) error
}
