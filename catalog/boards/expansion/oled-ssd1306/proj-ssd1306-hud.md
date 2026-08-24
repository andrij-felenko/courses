# ⚙️ HUD на SSD1306: стан автомата, велика цифра давача, меню з курсором

На дрібному приладі OLED 0.96″ ставлять заради одного — **HUD** (англ. *Head-Up Display* — індикатор, що показує стан, не відриваючи оператора від справи): у верхньому рядку режим, у якому зараз прилад, посередині велике число з давача, унизу рядок меню з рухомим курсором. Зберімо такий HUD цілком і зрозуміймо, чому кадр 128×64 будують саме так — на реальному коді трьох доріжок: скетч Arduino (Adafruit_GFX), ESP-IDF і STM32 HAL (обидві — на U8g2). Сам контракт «як заговорити з дисплеєм» — адреса, ініціалізація з зарядним насосом, виштовхування буфера — винесено в [довідник «SSD1306 у коді»](topic:boards/oled-ssd1306/api-ssd1306.md); тут ми ним уже користуємося як даним і зосереджуємось на **малюванні кадру**.

Три зони HUD різні за характером — текст-стан, велика цифра, інтерактивний список, — і на них добре видно, як усе це вживається в тісних 128×64 та як правильно поділити роботу на «модель окремо, малювання кадру окремо».

Спочатку домовмося про модель того, що показуємо. Прилад живе як [скінченний автомат](topic:electronics/finite-state-machines): у кожен момент він рівно в одному зі станів, і HUD показує, у якому саме. Візьмімо чотири стани, як у типового вимірювального приладу:

```
enum HudState {
  ST_IDLE,        // чекаємо
  ST_MEASURE,     // міряємо
  ST_ALARM,       // вихід за межу
  ST_CONFIG       // налаштування
};
```

Головна пастка великої цифри — **не тягти float заради краси**. Давач часто дає ціле в якихось сотих (наприклад, температуру як `int` у сотих градуса: `2537` = 25.37 °C). Виводити її через дробові числа на мікроконтролері марнотратно й повільно; куди дешевше й точніше **лишити ціле й самому поставити кому**: ціла частина — `value / 100`, дробова — `value % 100`. Це та сама ідея, що [фіксована кома](topic:programming/fixed-point) — тримати «дробове» число як звичайне ціле в обраному масштабі; тут вона економить і час, і пам'ять.

Кадр на будь-якому мікроконтролері збирають однаково: почистити буфер у пам'яті, намалювати в ньому три зони, штовхнути готовий буфер у контролер дисплея. Від платформи залежить не малювання, а глей довкола нього — чим підняти шину, чим витримати паузу, у чому крутити цикл. Ось той самий повний HUD трьома доріжками. Логіку датчика й кнопок зведено до мінімуму (у справжньому приладі тут читання давача й опитування кнопок), щоб не затуляти саме **малювання кадру** — те, заради чого ця вставка.

:::tabs
```arduino
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_W 128
#define SCREEN_H  64
Adafruit_SSD1306 display(SCREEN_W, SCREEN_H, &Wire, -1);

enum HudState { ST_IDLE, ST_MEASURE, ST_ALARM, ST_CONFIG };

// Людські назви станів для верхнього рядка.
const char* stateName(HudState s) {
  switch (s) {
    case ST_IDLE:    return "IDLE";
    case ST_MEASURE: return "MEASURE";
    case ST_ALARM:   return "ALARM";
    case ST_CONFIG:  return "CONFIG";
  }
  return "?";
}

const char* MENU[] = { "Run", "Zero", "Rng", "Set" };   // підписи КОРОТКІ навмисне — щоб рядок уклався в 128 px (розрахунок нижче)
const int   MENU_N = 4;

// Намалювати ВЕСЬ кадр за поточним станом. Викликається щоразу, коли щось змінилось.
void drawHud(HudState st, int32_t centi, int cursor) {
  display.clearDisplay();                 // чистимо буфер, малюємо кадр з нуля

  // — Зона 1: рядок стану вгорі, у рамці-плашці ————————————————
  display.drawRect(0, 0, SCREEN_W, 14, SSD1306_WHITE);
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(4, 3);
  display.print("St: ");
  display.print(stateName(st));

  // — Зона 2: велике число посередині, ціле «з комою вручну» ————————
  int32_t whole = centi / 100;            // ціла частина
  int32_t frac  = centi % 100;            // дві цифри після коми
  if (frac < 0) frac = -frac;             // модуль, щоб «-1.05» не став «-1.-5»
  char big[16];
  snprintf(big, sizeof(big), "%ld.%02ld", (long)whole, (long)frac);
  display.setTextSize(3);                 // розмір 3 ≈ 18x24 пікселі на символ
  display.setCursor(6, 20);
  display.print(big);
  display.setTextSize(1);                 // одиниці — дрібним, у куточку
  display.setCursor(104, 30);
  display.print("C");

  // — Зона 3: рядок меню внизу, курсор «>» перед активним пунктом ——————
  // Пікселний бюджет вирішує все: на кожен пункт іде (курсор + літери + проміжок) × 6 px.
  // {Run,Zero,Rng,Set} = (5+6+5+5)·6 = 126 px — влазить у 128 з малим запасом;
  // з довгими «Start»,«Range» останній пункт зрізало б за правим краєм екрана.
  display.drawFastHLine(0, 50, SCREEN_W, SSD1306_WHITE);  // відділити меню лінією
  int x = 2;
  for (int i = 0; i < MENU_N; i++) {
    display.setCursor(x, 54);
    display.print(i == cursor ? ">" : " ");   // курсор перед активним пунктом
    display.print(MENU[i]);
    x += (strlen(MENU[i]) + 2) * 6;           // курсор + підпис + проміжок, по 6 px на символ
  }

  display.display();                      // ← штовхаємо весь кадр на скло
}

void setup() {
  Wire.begin();
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) { for (;;) {} }
}

void loop() {
  // Демонстрація: ганяємо стани й число, курсор повзе по меню.
  static int32_t t = 2500;                // 25.00 °C у сотих
  static int cursor = 0;
  static HudState st = ST_MEASURE;

  t += 7;                                 // «давач» поволі росте
  if (t > 8000) { st = ST_ALARM; }        // перейшли в тривогу за межею
  else          { st = ST_MEASURE; }

  drawHud(st, t, cursor);                 // перемалювали кадр
  cursor = (cursor + 1) % MENU_N;         // курсор на наступний пункт
  delay(400);
}
```
```esp-idf
#include <string.h>
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "driver/i2c.h"          // шину тримає драйвер IDF
#include "u8g2.h"
#include "u8g2_esp32_hal.h"      // порт u8g2 під ESP-IDF: колбеки на driver/i2c

static const char *TAG = "hud";
static u8g2_t u8g2;

typedef enum { ST_IDLE, ST_MEASURE, ST_ALARM, ST_CONFIG } hud_state_t;

// Людські назви станів для верхнього рядка.
static const char *state_name(hud_state_t s) {
  switch (s) {
    case ST_IDLE:    return "IDLE";
    case ST_MEASURE: return "MEASURE";
    case ST_ALARM:   return "ALARM";
    case ST_CONFIG:  return "CONFIG";
  }
  return "?";
}

static const char *MENU[] = { "Run", "Zero", "Rng", "Set" };  // підписи КОРОТКІ навмисне
#define MENU_N 4

// Намалювати ВЕСЬ кадр за поточним станом.
static void draw_hud(hud_state_t st, int32_t centi, int cursor) {
  char s[16];
  u8g2_ClearBuffer(&u8g2);                       // чистимо буфер, малюємо кадр з нуля

  // — Зона 1: рядок стану вгорі, у рамці-плашці ————————————————
  u8g2_SetFont(&u8g2, u8g2_font_6x10_tf);        // у u8g2 розмір задає САМ шрифт
  u8g2_DrawFrame(&u8g2, 0, 0, 128, 14);
  snprintf(s, sizeof(s), "St: %s", state_name(st));
  u8g2_DrawStr(&u8g2, 4, 11, s);                 // y — БАЗОВА лінія, не верх рядка

  // — Зона 2: велике число посередині, ціле «з комою вручну» ————————
  int32_t whole = centi / 100;                   // ціла частина
  int32_t frac  = centi % 100;                   // дві цифри після коми
  if (frac < 0) frac = -frac;                    // модуль, щоб «-1.05» не став «-1.-5»
  snprintf(s, sizeof(s), "%ld.%02ld", (long)whole, (long)frac);
  u8g2_SetFont(&u8g2, u8g2_font_logisoso24_tn);  // «велику цифру» дає великий шрифт
  u8g2_DrawStr(&u8g2, 6, 44, s);
  u8g2_SetFont(&u8g2, u8g2_font_6x10_tf);        // одиниці — дрібним, у куточку
  u8g2_DrawStr(&u8g2, 104, 38, "C");

  // — Зона 3: рядок меню внизу, курсор «>» перед активним пунктом ——————
  u8g2_DrawHLine(&u8g2, 0, 50, 128);             // відділити меню лінією
  int x = 2;
  for (int i = 0; i < MENU_N; i++) {
    snprintf(s, sizeof(s), "%c%s", i == cursor ? '>' : ' ', MENU[i]);
    u8g2_DrawStr(&u8g2, x, 62, s);
    x += (strlen(MENU[i]) + 2) * 6;              // той самий пікселний бюджет: 6 px на символ
  }

  u8g2_SendBuffer(&u8g2);                        // ← штовхаємо весь кадр на скло
}

void app_main(void) {
  u8g2_esp32_hal_t hal = U8G2_ESP32_HAL_DEFAULT; // глей: які саме виводи несуть шину
  hal.bus.i2c.sda = GPIO_NUM_21;
  hal.bus.i2c.scl = GPIO_NUM_22;
  u8g2_esp32_hal_init(hal);

  u8g2_Setup_ssd1306_i2c_128x64_noname_f(&u8g2, U8G2_R0,
      u8g2_esp32_i2c_byte_cb, u8g2_esp32_gpio_and_delay_cb);
  u8x8_SetI2CAddress(&u8g2.u8x8, 0x3C << 1);     // адреса, зсунута на біт R/W
  u8g2_InitDisplay(&u8g2);
  u8g2_SetPowerSave(&u8g2, 0);                   // прокинути скло після ініціалізації
  ESP_LOGI(TAG, "SSD1306 готовий");

  int32_t t = 2500;                              // 25.00 °C у сотих
  int cursor = 0;
  for (;;) {
    t += 7;                                      // «давач» поволі росте
    hud_state_t st = (t > 8000) ? ST_ALARM : ST_MEASURE;
    draw_hud(st, t, cursor);                     // перемалювали кадр
    cursor = (cursor + 1) % MENU_N;              // курсор на наступний пункт
    vTaskDelay(pdMS_TO_TICKS(400));              // ← не delay(): віддаємо час планувальнику
  }
}
```
```stm32
#include <string.h>
#include <stdio.h>
#include "main.h"                // HAL і hi2c1, згенеровані CubeMX
#include "u8g2.h"

extern I2C_HandleTypeDef hi2c1;
static u8g2_t u8g2;
#define SSD1306_ADDR (0x3C << 1) // HAL теж чекає адресу, зсунуту на біт R/W

typedef enum { ST_IDLE, ST_MEASURE, ST_ALARM, ST_CONFIG } hud_state_t;

static const char *state_name(hud_state_t s) {
  switch (s) {
    case ST_IDLE:    return "IDLE";
    case ST_MEASURE: return "MEASURE";
    case ST_ALARM:   return "ALARM";
    case ST_CONFIG:  return "CONFIG";
  }
  return "?";
}

static const char *MENU[] = { "Run", "Zero", "Rng", "Set" };
#define MENU_N 4

// Уся платформозалежність — у двох колбеках: байти в шину і пауза.
static uint8_t u8x8_hal_i2c(u8x8_t *u8x8, uint8_t msg, uint8_t len, void *arg) {
  static uint8_t buf[32], n;
  switch (msg) {
    case U8X8_MSG_BYTE_START_TRANSFER: n = 0; break;
    case U8X8_MSG_BYTE_SEND: memcpy(buf + n, arg, len); n += len; break;
    case U8X8_MSG_BYTE_END_TRANSFER:
      HAL_I2C_Master_Transmit(&hi2c1, SSD1306_ADDR, buf, n, HAL_MAX_DELAY);
      break;
    default: break;
  }
  return 1;
}
static uint8_t u8x8_hal_delay(u8x8_t *u8x8, uint8_t msg, uint8_t len, void *arg) {
  if (msg == U8X8_MSG_DELAY_MILLI) HAL_Delay(len);
  return 1;
}

static void draw_hud(hud_state_t st, int32_t centi, int cursor) {
  char s[16];
  u8g2_ClearBuffer(&u8g2);

  // — Зона 1: рядок стану вгорі, у рамці-плашці ————————————————
  u8g2_SetFont(&u8g2, u8g2_font_6x10_tf);
  u8g2_DrawFrame(&u8g2, 0, 0, 128, 14);
  snprintf(s, sizeof(s), "St: %s", state_name(st));
  u8g2_DrawStr(&u8g2, 4, 11, s);                 // y — базова лінія рядка

  // — Зона 2: велике число посередині, ціле «з комою вручну» ————————
  int32_t whole = centi / 100;
  int32_t frac  = centi % 100;
  if (frac < 0) frac = -frac;
  snprintf(s, sizeof(s), "%ld.%02ld", (long)whole, (long)frac);
  u8g2_SetFont(&u8g2, u8g2_font_logisoso24_tn);
  u8g2_DrawStr(&u8g2, 6, 44, s);
  u8g2_SetFont(&u8g2, u8g2_font_6x10_tf);
  u8g2_DrawStr(&u8g2, 104, 38, "C");

  // — Зона 3: рядок меню внизу, курсор «>» перед активним пунктом ——————
  u8g2_DrawHLine(&u8g2, 0, 50, 128);
  int x = 2;
  for (int i = 0; i < MENU_N; i++) {
    snprintf(s, sizeof(s), "%c%s", i == cursor ? '>' : ' ', MENU[i]);
    u8g2_DrawStr(&u8g2, x, 62, s);
    x += (strlen(MENU[i]) + 2) * 6;
  }

  u8g2_SendBuffer(&u8g2);                        // ← штовхаємо весь кадр на скло
}

int main(void) {
  HAL_Init();
  SystemClock_Config();
  MX_GPIO_Init();
  MX_I2C1_Init();                                // шину підняв CubeMX

  u8g2_Setup_ssd1306_i2c_128x64_noname_f(&u8g2, U8G2_R0, u8x8_hal_i2c, u8x8_hal_delay);
  u8g2_InitDisplay(&u8g2);
  u8g2_SetPowerSave(&u8g2, 0);

  int32_t t = 2500;
  int cursor = 0;
  for (;;) {
    t += 7;
    hud_state_t st = (t > 8000) ? ST_ALARM : ST_MEASURE;
    draw_hud(st, t, cursor);
    cursor = (cursor + 1) % MENU_N;
    HAL_Delay(400);
  }
}
```
:::

Придивімося, чому кадр збудовано саме так. **Увесь HUD малюється однією функцією `drawHud()`, що починається з `clearDisplay()` і закінчується `display()`.** Це не випадковість, а найздоровіший спосіб працювати з кадровим буфером: не «підтирати» окремі ділянки старого кадру (звідки беруться «привиди» недочищених пікселів), а щоразу малювати весь екран з чистого аркуша. 1024 байти на кадр — копійки; зате не треба стежити, що там лишилося від попереднього стану.

Далі — компоновка під **тісні 128×64**. Розмір тексту `3` в Adafruit_GFX — це базовий шрифт 6×8, помножений утричі, тобто приблизно 18×24 пікселі на символ. П'ять таких символів (`25.00`) з'їдають майже всю ширину — тому одиниці («C») ставлять дрібним шрифтом у куточок, а не поруч тим самим кеглем. Верхня плашка стану — 14 пікселів заввишки (рамка плюс рядок висотою 8), лінія меню — на `y=50`, велика цифра між ними. Це не єдина можлива розкладка, але вона показує головне: на такому екрані **місце рахують у пікселях**, і великий шрифт треба «бюджетувати» під ширину 128.

І курсор меню. Тут він елементарний — символ `>` перед активним пунктом і пробіл перед рештою; курсор рухається, змінюючи змінну `cursor`, а весь рядок перемальовується. Але й цей рядок підпорядкований тому самому пікселному бюджету: чотири пункти з курсором і проміжками мусять укластися в 128 px по ширині, тому підписи навмисне короткі — `Run`, `Zero`, `Rng`, `Set` замість повних слів. Порахуймо: на кожен пункт іде (курсор + літери + проміжок) символів, по 6 px на символ базового шрифту 6×8 (у U8g2 те саме дає `u8g2_font_6x10_tf`), разом (5+6+5+5)·6 = 126 px — якраз влазить. Постав довші «Start» чи «Range» — і останній пункт виїхав би за правий край, зрізаний і невидимий, хоч у коді все ніби гаразд: саме такі мовчазні переповнення й ловить точний облік пікселів. У справжньому приладі `cursor` рухали б кнопки «вниз/вгору», а `Run`/`Set` запускали б перехід автомата — але механіка кадру та сама: змінилося щось у стані → перемалювали весь HUD → штовхнули буфер.

> 🔧 **Навіщо це.** Зверніть увагу, що `drawHud()` **нічого не знає про те, коли її кличуть**. Вона — чиста функція «дано стан → намалюй кадр». Це правильний поділ: логіка (автомат, читання давача, кнопки) окремо змінює `st`, `centi`, `cursor`, а `drawHud()` лише відбиває їх на склі. Тоді дисплей ніколи не бреше — він завжди показує поточний стан, — і код не плутається у «що вже намальовано, а що ні». Такий поділ «модель окремо, малювання кадру окремо» масштабується від цього HUD до будь-якого інтерфейсу.

Наостанок — окремо про саму велику цифру в U8g2 (вкладки ESP-IDF і STM32 вище). Логіка та сама, лише виклики U8g2-ні; головна відмінність у тому, що в U8g2 **шрифт задає й розмір, і накреслення** (окремого множника розміру, як `setTextSize`, немає — ви обираєте готовий шрифт потрібної величини). Тому «велику цифру» дає вибір великого шрифту, а не множник.

```stm32
// STM32 / U8g2: велике число посередині, ціле «з комою вручну», без float.
void draw_big_value(int32_t centi) {
  int32_t whole = centi / 100;
  int32_t frac  = centi % 100;
  if (frac < 0) frac = -frac;
  char s[16];
  snprintf(s, sizeof(s), "%ld.%02ld", (long)whole, (long)frac);

  u8g2_ClearBuffer(&u8g2);
  u8g2_SetFont(&u8g2, u8g2_font_logisoso24_tn);  // великий шрифт, лише цифри й «.»
  u8g2_DrawStr(&u8g2, 4, 44, s);                 // (x, baseline_y, текст)
  u8g2_SendBuffer(&u8g2);
}
```

Зверніть увагу на суфікс шрифту `_tn` (*text, numbers*): він містить лише цифри, крапку й мінус — саме те, що треба великій цифрі, і при цьому не тягне у флеш увесь набір літер. У U8g2 координата `y` в `DrawStr` — це **базова лінія** (низ літер), а не верх рядка, як звик той, хто прийшов з Adafruit_GFX; переплутавши, дістанете текст, зрізаний за верхнім краєм. Дрібна різниця, але саме такі дрібниці й коштують півгодини, коли переходиш між бібліотеками.
