// Висхідний мотив «до-ре-мі-фа-соль» і назад, остання нота довша.
static const note_t scaleUpDown[] = {
    {NOTE_C4, 200}, {NOTE_D4, 200}, {NOTE_E4, 200}, {NOTE_F4, 200},
    {NOTE_G4, 200}, {NOTE_F4, 200}, {NOTE_E4, 200}, {NOTE_D4, 200},
    {NOTE_C4, 500},
};

void app_main(void)
{
    buzzerBegin();
    playMelody(scaleUpDown, sizeof(scaleUpDown) / sizeof(scaleUpDown[0]));

    while (1) {
        buzzerUpdate();                 // ← мелодія рухається тут, фоном
        vTaskDelay(pdMS_TO_TICKS(2));   // ...інші задачі живуть паралельно...
    }
}
