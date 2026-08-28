// Висхідний мотив «до-ре-мі-фа-соль» і назад, остання нота довша.
static const Note scaleUpDown[] = {
    {NOTE_C4, 200}, {NOTE_D4, 200}, {NOTE_E4, 200}, {NOTE_F4, 200},
    {NOTE_G4, 200}, {NOTE_F4, 200}, {NOTE_E4, 200}, {NOTE_D4, 200},
    {NOTE_C4, 500},
};

int main(void)
{
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_TIM3_Init();
    playMelody(scaleUpDown, sizeof(scaleUpDown) / sizeof(scaleUpDown[0]));

    while (1) {
        buzzerUpdate();   // ← мелодія рухається тут, фоном
        // ...усе інше живе паралельно: поки грає гама, пристрій опитує кнопки...
    }
}
