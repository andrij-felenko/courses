// Максимальна зміна швидкості за такт — це і є нахил рампи.
// Приклад: гальмуємо не різкіше ніж 2.0 м/с за секунду.
#define BRAKE_DECEL   2.0f    // м/с за секунду (темп зниження швидкості)

// Плавно тягне поточну швидкість current до цілі target, не швидше нахилу рампи.
// dt_s — тривалість такту в секундах. Повертає нову швидкість.
static float ramp_to(float current, float target, float dt_s)
{
    float max_step = BRAKE_DECEL * dt_s;   // скільки можна змінити за цей такт
    float delta    = target - current;

    if (delta >  max_step) delta =  max_step;   // не розганяймося різкіше рампи
    if (delta < -max_step) delta = -max_step;   // не гальмуймо різкіше рампи
    return current + delta;
}

// Зупинка = рампа до нуля. Викликається щотакту в стані SAFE-STOP.
static float ramp_to_stop(float current, float dt_s)
{
    return ramp_to(current, 0.0f, dt_s);
}
