  // Прочитати страп двічі — з внутрішнім pull-up і pull-down.
  // Збіг → зовнішній резистор є, значення справжнє. Розбіжність → резистора нема.
  static bool strap_read_checked(GPIO_TypeDef *port, uint16_t pin, uint8_t *value) {
      GPIO_InitTypeDef g = {0};
      g.Pin  = pin;
      g.Mode = GPIO_MODE_INPUT;

      g.Pull = GPIO_PULLUP;   HAL_GPIO_Init(port, &g);   // тягнемо вгору
      for (volatile int d = 0; d < 500; d++) { }         // дати рівню встоятися
      uint8_t with_pu = (HAL_GPIO_ReadPin(port, pin) == GPIO_PIN_SET);

      g.Pull = GPIO_PULLDOWN; HAL_GPIO_Init(port, &g);   // тягнемо вниз
      for (volatile int d = 0; d < 500; d++) { }
      uint8_t with_pd = (HAL_GPIO_ReadPin(port, pin) == GPIO_PIN_SET);

      // Наприкінці ОБОВ'ЯЗКОВО вимкнути внутрішню підтяжку (див. крок 1).
      g.Pull = GPIO_NOPULL;   HAL_GPIO_Init(port, &g);

      *value = with_pu;                 // за наявного резистора обидва однакові
      return (with_pu == with_pd);      // true = резистор на місці; false = плаває
  }
