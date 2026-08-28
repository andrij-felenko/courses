// Ковзне середнє на кільцевому буфері (для однієї осі).
#define WIN 8
struct MovAvg {
    float buf[WIN];
    int   idx;
    float sum;
    bool  filled;
};

void maInit(MovAvg* m) {
    m->idx = 0; m->sum = 0; m->filled = false;
    for (int i = 0; i < WIN; i++) m->buf[i] = 0;
}

float maStep(MovAvg* m, float x) {
    m->sum -= m->buf[m->idx];   // прибрати найстаріше
    m->buf[m->idx] = x;         // покласти нове на його місце
    m->sum += x;
    m->idx = (m->idx + 1) % WIN;
    if (m->idx == 0) m->filled = true;
    int n = m->filled ? WIN : m->idx;   // поки буфер не повний — ділимо на стільки, скільки є
    if (n == 0) n = WIN;
    return m->sum / n;
}
