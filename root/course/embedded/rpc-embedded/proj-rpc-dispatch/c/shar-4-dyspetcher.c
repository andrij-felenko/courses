// Кожен обробник — функція однакової форми: аргумент → результат.
typedef int32_t (*rpc_handler)(int32_t arg);

// ── Реальні обробники (тіла «віддалених» функцій) ────────────────────────
extern int32_t adc_read(int ch);           // драйвери конкретного МК
extern void    motor_set(int duty);

static int32_t h_ping(int32_t a)        { (void)a; return 0; }
static int32_t h_read_sensor(int32_t n) { return adc_read((int)n); }
static int32_t h_set_motor(int32_t d)   { motor_set((int)d); return d; }

// ── Таблиця диспетчеризації: номер функції → вказівник на обробник ────────
static const rpc_handler TABLE[] = {
    h_ping,          // func 0
    h_read_sensor,   // func 1
    h_set_motor,     // func 2
};
#define RPC_COUNT (sizeof(TABLE) / sizeof(TABLE[0]))
