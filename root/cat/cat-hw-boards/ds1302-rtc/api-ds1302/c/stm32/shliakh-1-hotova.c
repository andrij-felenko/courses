/* У STM32 HAL драйвера DS1302 нема взагалі: три ніжки GPIO плюс тонкий модуль
   ds1302_* — ті самі ds_* із другої частини, загорнуті в стандартний struct tm. */
#include "main.h"        /* CubeMX: піни, huart2, SystemClock_Config() */
#include <string.h>
#include <time.h>

extern UART_HandleTypeDef huart2;

void ds1302_init(void);              /* напрями ніжок, CE у 0 */
void ds1302_write_protect(int on);   /* регістр 0x8E */
void ds1302_start(void);             /* скинути CH */
void ds1302_get_time(struct tm *t);  /* burst-читання */
void ds1302_set_time(const struct tm *t);

static void say(const char *s) {     /* друк у термінал через UART */
  HAL_UART_Transmit(&huart2, (uint8_t *)s, strlen(s), HAL_MAX_DELAY);
}

int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();
  MX_USART2_UART_Init();

  ds1302_init();
  ds1302_write_protect(0);           /* 1) зняти WP, інакше запис зникає мовчки */
  ds1302_start();                    /* 2) скинути CH, інакше генератор стоїть  */

  struct tm t = {0};
  ds1302_get_time(&t);
  if (t.tm_year + 1900 < 2025) {     /* 3) час недійсний — ставимо один раз */
    struct tm init = { .tm_sec = 30, .tm_min = 47, .tm_hour = 10,
                       .tm_mday = 4, .tm_mon = 6, .tm_year = 126 };
    ds1302_set_time(&init);
    say("RTC був порожній — виставив стартовий час\r\n");
  }

  char buf[32];
  while (1) {
    ds1302_get_time(&t);
    strftime(buf, sizeof(buf), "%Y-%m-%d %H:%M:%S\r\n", &t);
    say(buf);
    HAL_Delay(5000);                 /* читати раз на 5 с досить */
  }
}
