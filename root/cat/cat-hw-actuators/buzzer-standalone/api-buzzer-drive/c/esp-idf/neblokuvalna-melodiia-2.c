// «Ода до радості», перші такти (частоти в Гц, тривалості в мс)
static const note_t ODE[] = {
  {330,300},{330,300},{349,300},{392,300},   // мі мі фа соль
  {392,300},{349,300},{330,300},{294,300},   // соль фа мі ре
  {262,300},{262,300},{294,300},{330,300},   // до до ре мі
  {330,450},{294,150},{294,600},             // мі. ре ре(довга)
};

static player_t buzzer;

void app_main(void) {
  buzzer_init();
  player_play(&buzzer, ODE, sizeof(ODE) / sizeof(ODE[0]));

  while (1) {
    player_update(&buzzer);          // рухає мелодію, НІЧОГО не блокує

    // …а тут паралельно живе решта пристрою — і воно справді працює:
    if (gpio_get_level(BUTTON) == 0 && !buzzer.active)
      player_play(&buzzer, ODE, sizeof(ODE) / sizeof(ODE[0]));  // на кнопку
    vTaskDelay(pdMS_TO_TICKS(1));    // віддати такт іншим задачам
  }
}
