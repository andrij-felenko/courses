// інтерфейс давача — vtable вручну:
typedef struct {
    int  (*read_temp)(void *ctx);    // повертає температуру
    void *ctx;                       // стан конкретної реалізації (за потреби)
} TempSensor;

// логіка залежить від ІНТЕРФЕЙСУ, не від конкретного давача:
bool overheat(const TempSensor *s) {
    return s->read_temp(s->ctx) > 80;
}

// у бою — справжній драйвер:
static int i2c_temp(void *ctx) { (void)ctx; return read_i2c_sensor(); }
// у тесті — заглушка під тим самим інтерфейсом:
static int fake_temp(void *ctx) { return *(int *)ctx; }

// тест без жодного чипа:
int scenario = 95;
TempSensor mock = { .read_temp = fake_temp, .ctx = &scenario };
assert( overheat(&mock) == true );    // 95 > 80 → перегрів
scenario = 30;
assert( overheat(&mock) == false );   // 30 → норми
