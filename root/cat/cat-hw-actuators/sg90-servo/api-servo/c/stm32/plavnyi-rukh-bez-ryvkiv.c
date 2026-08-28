#define STEP_MS 15                        // темп: 15 мс на градус

static int cur_angle = 90;                // де серво зараз (наша модель)
static int tgt_angle = 90;                // куди хочемо
static uint32_t last_step;                // коли робили крок востаннє

void servo_set_target(int deg) {          // задати нову ціль (миттєво повертається)
  if (deg < 0)   deg = 0;
  if (deg > 180) deg = 180;
  tgt_angle = deg;
}

static void servo_update(void) {          // кликати ЩОРАЗУ в головному циклі
  if (cur_angle == tgt_angle) return;               // уже на місці — нема що робити
  uint32_t now = HAL_GetTick();                     // мілісекунди від старту
  if (now - last_step < STEP_MS) return;            // ще рано для кроку
  last_step = now;
  cur_angle += (tgt_angle > cur_angle) ? 1 : -1;    // один градус у бік цілі
  servo_write_us(deg_to_us(cur_angle));
}

int main(void) {
  HAL_Init(); SystemClock_Config();
  MX_GPIO_Init(); MX_TIM3_Init();
  HAL_TIM_PWM_Start(&htim3, TIM_CHANNEL_1);
  servo_write_us(deg_to_us(cur_angle));

  while (1) {
    servo_update();          // рух серва — неблокувальний, крок за кроком
    // ...тут вільно робимо будь-що інше: кнопки, давачі, зв'язок...
  }
}
