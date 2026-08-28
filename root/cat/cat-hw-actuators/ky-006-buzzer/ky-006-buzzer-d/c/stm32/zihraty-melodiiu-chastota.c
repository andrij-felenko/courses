extern TIM_HandleTypeDef htim3;     // TIM3_CH1 на ніжці зумера

// частоти нот у герцах
#define C4 262
#define D4 294
#define E4 330
#define F4 349
#define G4 392

// мелодія: пари {частота, тривалість у мс}. 0 = пауза (тиша)
static const struct { uint16_t freq; uint16_t ms; } melody[] = {
    {E4, 300}, {E4, 300}, {F4, 300}, {G4, 300},
    {G4, 300}, {F4, 300}, {E4, 300}, {D4, 300}, {C4, 500},
};

void play_melody(void)
{
    for (size_t i = 0; i < sizeof melody / sizeof melody[0]; i++) {
        if (melody[i].freq > 0)
            buzzer_tone(melody[i].freq);   // перелаштувати ARR і пустити ШІМ
        HAL_Delay(melody[i].ms);

        // між нотами — маленький проміжок тиші, щоб ноти не зливались
        HAL_TIM_PWM_Stop(&htim3, TIM_CHANNEL_1);
        HAL_Delay(40);
    }
}
