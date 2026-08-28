// Цифровий підсилювач похибки (ПІ-регулятор).
// Викликається з постійним кроком (наприклад, у перерві таймера).
// setpoint — уставка в тих самих одиницях, що й measured (відлік АЦП).
typedef struct {
    float kp;        // пропорційна частка: реакція на миттєву похибку
    float ki;        // інтегральна частка: прибирає сталу похибку
    float integ;     // накопичена історія похибки
    float out_min;   // межі виходу (наприклад, 0..1 для шпаруватості ШІМ)
    float out_max;
} ErrorAmp;

float error_amp_step(ErrorAmp *e, float setpoint, float measured)
{
    float error = setpoint - measured;       // та сама різниця «де треба − де є»
    e->integ += error;                       // інтегратор: усе додаємо в часі

    float out = e->kp * error + e->ki * e->integ;

    // Обмеження виходу + захист інтегратора від «розбухання» на упорі:
    if (out > e->out_max) { out = e->out_max; e->integ -= error; }
    else if (out < e->out_min) { out = e->out_min; e->integ -= error; }

    return out;                              // керує силовим вузлом (шпаруватість ШІМ)
}
