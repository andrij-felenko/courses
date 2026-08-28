// «Ода до радості», перші такти (частоти в Гц, тривалості в мс)
static const Note ODE[] = {
  {330,300},{330,300},{349,300},{392,300},   // мі мі фа соль
  {392,300},{349,300},{330,300},{294,300},   // соль фа мі ре
  {262,300},{262,300},{294,300},{330,300},   // до до ре мі
  {330,450},{294,150},{294,600},             // мі. ре ре(довга)
};

static Player buzzer;

int main(void) {
  HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_TIM3_Init();
  player_play(&buzzer, ODE, sizeof(ODE) / sizeof(ODE[0]));

  while (1) {
    player_update(&buzzer);          // рухає мелодію, НІЧОГО не блокує

    // …а тут паралельно живе решта пристрою — і воно справді працює:
    if (HAL_GPIO_ReadPin(BTN_GPIO_Port, BTN_Pin) == GPIO_PIN_RESET
        && !buzzer.active)
      player_play(&buzzer, ODE, sizeof(ODE) / sizeof(ODE[0]));  // на кнопку
    // read_sensors(); update_display(); handle_radio();  // усе встигає
  }
}
