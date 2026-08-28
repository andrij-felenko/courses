#define HOP  3     // ганяти мережу що HOP нових стовпчиків (реакція ↔ такти)

static int since_run = 0;   // лічильник стовпчиків між прогонами

// ГОЛОВНА точка входу модуля. Викликати на кожен новий лог-мел-стовпчик.
// Повертає true рівно в той прогін, коли розпізнано ключове слово.
bool kws_on_frame(const float col[N_MEL]) {
    ring_push(col);                       // намотати кільце — ЗАВЖДИ, щокадру
    if (fill < N_FRAMES) return false;    // кільце ще не повне — рано розгортати

    if (++since_run < HOP) return false;  // між прогонами лише намотуємо
    since_run = 0;

    float probs[N_CLASS];
    if (!kws_invoke(probs)) return false; // розгорнути+квантувати+прогнати мережу
    return kws_decide(probs);             // згладити+поріг+спокій+«чуже»
}
