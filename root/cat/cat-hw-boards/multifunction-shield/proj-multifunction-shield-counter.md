# ⚙️ Лічильник на кнопках через бібліотеку MultiFuncShield

Задача проста на словах і болюча на практиці: зробити лічильник. Натиснув одну кнопку — число росте, натиснув другу — спадає, третьою скинув у нуль; усі чотири цифри рівно горять на дисплеї, а кожне натискання відгукується коротким писком. Це той самий «hello, world» для фізичного інтерфейсу — щойно він працює, ти вмієш і показати число, і прийняти натискання, і подати звук, і не заплутатися в мультиплексуванні.

Болить це тому, що на цьому шилді жодна з трьох дій не робиться «в лоб». Дисплей не приймає цифру у вивід — його треба безперервно перебирати по розрядах. Кнопка деренчить контактом і дає десяток хибних спрацювань на одне натискання. Зумер треба вчасно вимкнути, інакше він гуде. Готова бібліотека **MultiFuncShield** прибирає рівно цей клубок: вона забирає собі один апаратний таймер мікроконтролера і в його перериванні сама веде дисплей, сама відбиває кнопки, сама відраховує писк — тобі лишається чиста логіка лічильника. Усі її виклики та їхні параметри — `MFS.write`, `MFS.getButton`, `MFS.beep`, `MFS.writeLeds` — розібрані окремо, у [довіднику інтерфейсу](topic:cat-hw-boards/multifunction-shield/api-multifunction-shield.md); тут із них складемо завершений прилад.

Уся логіка спирається на те, що бібліотека віддає не сирий стан кнопки, а вже відбиті **події**: `MFS.getButton()` повертає один байт — яку кнопку зачепили й що саме з нею сталося (коротко клацнули, тримають, відпустили після довгого утримання). Повний перелік цих подій і готових констант `BUTTON_n_*` розібрано у згаданому довіднику; лічильникові з них вистачить кількох, і які саме — видно просто з коду.

## Повна робоча прошивка: лічильник із дисплеєм і звуком

Складімо все докупи. S1 збільшує лічильник, S2 зменшує, S3 (утримати) скидає в нуль; кожне натискання пищить; число завжди на дисплеї; коли воно від'ємне — горить перший світлодіод. Це справжня прошивка, а не псевдокод.

Від мікроконтролера задача вимагає трьох речей і байдужа до того, чий він: **виводів на два зсувні регістри дисплея**, **входів із підтяжкою під кнопки** і **фонового таймера**, який освіжає розряди та відбиває контакт, поки головний цикл рахує. На Arduino UNO з надітим шилдом усі три вже зібрані в бібліотеці — тому цей варіант найкоротший і йде першим; на ESP-IDF і STM32 такої бібліотеки немає, і фон збирають зі свого таймера та черги подій, а логіка лічильника лишається тією самою.

:::tabs
```arduino
#include <MultiFuncShield.h>

int counter = 0;   // поточне значення лічильника

void setup() {
  MFS.initialize();       // виводи + фонове переривання (дисплей, кнопки, звук)
  MFS.write(counter);     // одразу показати початкове значення
}

void loop() {
  byte btn = MFS.getButton();   // забрати одну подію з черги (0 — якщо порожньо)

  switch (btn) {

    case BUTTON_1_SHORT_RELEASE:   // S1 коротко: +1
      counter++;
      MFS.write(counter);          // оновити дисплей
      MFS.beep();                  // короткий відгук
      break;

    case BUTTON_2_SHORT_RELEASE:   // S2 коротко: −1
      counter--;
      MFS.write(counter);
      MFS.beep();
      break;

    case BUTTON_1_LONG_PRESSED:    // S1 тримають: швидко біжить угору
      counter++;
      MFS.write(counter);
      break;

    case BUTTON_2_LONG_PRESSED:    // S2 тримають: швидко біжить униз
      counter--;
      MFS.write(counter);
      break;

    case BUTTON_3_LONG_RELEASE:    // S3 утримати й відпустити: скинути в нуль
      counter = 0;
      MFS.write(counter);
      MFS.beep(200, 0, 1);         // довший писк — «скинуто»
      break;
  }

  // світлодіод-індикатор: горить, поки число від'ємне
  MFS.writeLeds(LED_1, counter < 0 ? ON : OFF);
}
```
```esp-idf
// Бібліотеки MFS тут немає: фон робимо самі — esp_timer + черга подій.
#include "driver/gpio.h"
#include "esp_timer.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"

// драйвер шилда: перебір розрядів і відбивання кнопок — див. наступний розділ
void    shield_init(void);
void    shield_show(int value);
void    shield_refresh(void);       // один розряд за виклик
uint8_t shield_scan(void);          // 0 або код уже відбитої події
void    shield_beep(int ms);
void    shield_led(int n, bool on);

static QueueHandle_t events;

// те саме, що MFS робить у своєму таймерному перериванні
static void tick(void *arg) {
  shield_refresh();                       // освіжити наступний розряд
  uint8_t ev = shield_scan();             // відбити кнопки
  if (ev) xQueueSend(events, &ev, 0);     // подію — у чергу, не в обробник
}

void app_main(void) {
  int counter = 0;
  shield_init();
  events = xQueueCreate(8, sizeof(uint8_t));

  const esp_timer_create_args_t args = { .callback = tick, .name = "shield" };
  esp_timer_handle_t timer;
  ESP_ERROR_CHECK(esp_timer_create(&args, &timer));
  ESP_ERROR_CHECK(esp_timer_start_periodic(timer, 2000));   // кожні 2 мс

  shield_show(counter);                   // одразу показати початкове значення

  uint8_t ev;
  while (1) {
    if (xQueueReceive(events, &ev, portMAX_DELAY) != pdTRUE) continue;
    switch (ev) {
      case BTN1_SHORT_RELEASE: counter++; shield_beep(50);    break;  // S1 коротко: +1
      case BTN2_SHORT_RELEASE: counter--; shield_beep(50);    break;  // S2 коротко: −1
      case BTN1_LONG_PRESSED:  counter++;                     break;  // тримають: біжить угору
      case BTN2_LONG_PRESSED:  counter--;                     break;  // тримають: біжить униз
      case BTN3_LONG_RELEASE:  counter = 0; shield_beep(200); break;  // скинути в нуль
    }
    shield_show(counter);
    shield_led(1, counter < 0);           // світлодіод, поки число від'ємне
  }
}
```
```stm32
// Фон — переривання TIM3; події з нього забираємо через кільцевий буфер.
#include "main.h"                  // згенероване CubeMX: htim3, *_GPIO_Port / *_Pin

extern TIM_HandleTypeDef htim3;    // налаштований на 2 мс, Base_Start_IT

// драйвер шилда: перебір розрядів і відбивання кнопок — див. наступний розділ
void    shield_init(void);
void    shield_show(int value);
void    shield_refresh(void);
uint8_t shield_scan(void);
void    shield_beep(uint16_t ms);
void    shield_led(uint8_t n, uint8_t on);

static volatile uint8_t evq[8], head, tail;

// те саме, що MFS робить у своєму таймерному перериванні
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim) {
  if (htim->Instance != TIM3) return;
  shield_refresh();                              // освіжити наступний розряд
  uint8_t ev = shield_scan();                    // відбити кнопки
  if (ev) { evq[head] = ev; head = (head + 1) & 7; }   // подію — у кільце
}

int main(void) {
  int counter = 0;
  HAL_Init();  SystemClock_Config();  MX_GPIO_Init();  MX_TIM3_Init();
  shield_init();
  HAL_TIM_Base_Start_IT(&htim3);
  shield_show(counter);                          // одразу показати початкове значення

  while (1) {
    if (head == tail) continue;                  // черга порожня — нема чого робити
    uint8_t ev = evq[tail];  tail = (tail + 1) & 7;
    switch (ev) {
      case BTN1_SHORT_RELEASE: counter++; shield_beep(50);    break;  // S1 коротко: +1
      case BTN2_SHORT_RELEASE: counter--; shield_beep(50);    break;  // S2 коротко: −1
      case BTN1_LONG_PRESSED:  counter++;                     break;  // тримають: біжить угору
      case BTN2_LONG_PRESSED:  counter--;                     break;  // тримають: біжить униз
      case BTN3_LONG_RELEASE:  counter = 0; shield_beep(200); break;  // скинути в нуль
    }
    shield_show(counter);
    shield_led(1, counter < 0);                  // світлодіод, поки число від'ємне
  }
}
```
:::

Придивись, який чистий вийшов головний цикл. У ньому **немає** ні перебору розрядів, ні відбивання кнопок, ні відліку звуку — сама логіка лічильника. Уся рутина крутиться у фоновому таймерному перериванні: на Arduino його запустив `MFS.initialize()`, на ESP-IDF і STM32 — твій власний `esp_timer` чи `TIM3`. Кожен прохід циклу: забрали подію, за нею вирішили, що зробити з `counter`, оновили дисплей одним `write`, за потреби пікнули й повернулися. Цикл летить тисячі разів на секунду й майже завжди дістає з `getButton()` нуль — а коли людина натисне, спіймає рівно одну чисту подію.

Зверни увагу на три рішення в цьому коді. По-перше, короткий тик (`SHORT_RELEASE`) і утримання (`LONG_PRESSED`) розведені: клацнув — крок на одиницю, затиснув — число біжить само, бо `LONG_PRESSED` летить повторно, поки тримаєш. По-друге, скидання повішене на `LONG_RELEASE` кнопки S3 — «утримати й відпустити», щоб випадковий доторк не обнулив рахунок. По-третє, показ і звук ідуть **після** зміни `counter`, тож дисплей і писк завжди відповідають новому значенню.

## Якщо бібліотеки немає: ручний перебір у головному циклі

Іноді бібліотеку брати не хочеться — навчаєшся, як усе влаштовано насправді, або таймер потрібен під інше й фоновий обробник зайвий. Тоді дисплей ведуть **вручну прямо в циклі**: перебирають чотири розряди самі, у кожному засуваючи в регістри байт сегментів і байт вибору — біт за бітом по лінії даних із тактом (в Arduino це готовий `shiftOut`, деінде — свій цикл на трьох виводах або апаратний SPI). Це той самий принцип, що й бібліотека ховає, тільки перебір тепер твій і крутиться в головному циклі.

**Показати число лічильника ручним перебором розрядів.**

:::tabs
```arduino
const byte LATCH = 4, CLK = 7, DATA = 8;   // виводи двох 74HC595 шилда

// байти сегментів для цифр 0..9 (спільний анод: 0 = сегмент світиться)
const byte SEG[10] = {
  0xC0, 0xF9, 0xA4, 0xB0, 0x99, 0x92, 0x82, 0xF8, 0x80, 0x90
};
const byte SEL[4] = { 0xF1, 0xF2, 0xF4, 0xF8 };   // вибір розряду 1..4

int counter = 0;

void setup() {
  pinMode(LATCH, OUTPUT);
  pinMode(CLK,   OUTPUT);
  pinMode(DATA,  OUTPUT);
  pinMode(A1, INPUT_PULLUP);   // кнопка S1
  pinMode(A2, INPUT_PULLUP);   // кнопка S2
}

// виставити один розряд: байт сегментів + байт вибору, клац латчем
void showDigit(byte segByte, byte pos) {
  digitalWrite(LATCH, LOW);
  shiftOut(DATA, CLK, MSBFIRST, segByte);   // спершу сегменти
  shiftOut(DATA, CLK, MSBFIRST, SEL[pos]);  // потім вибір розряду
  digitalWrite(LATCH, HIGH);
}

// показати ціле 0..9999, перебравши всі чотири розряди по колу
void refresh(int value) {
  int v = value < 0 ? -value : value;       // модуль для показу
  byte d[4] = {
    (byte)(v / 1000 % 10), (byte)(v / 100 % 10),
    (byte)(v / 10 % 10),   (byte)(v % 10)
  };
  for (byte pos = 0; pos < 4; pos++) {
    showDigit(SEG[d[pos]], pos);
    delayMicroseconds(500);                 // трохи потримати розряд
    digitalWrite(LATCH, LOW);               // погасити перед наступним
    shiftOut(DATA, CLK, MSBFIRST, 0xFF);    // усі сегменти згашені
    shiftOut(DATA, CLK, MSBFIRST, 0xFF);
    digitalWrite(LATCH, HIGH);
  }
}

void loop() {
  static bool s1was = false, s2was = false;   // попередній стан для фронту

  bool s1 = (digitalRead(A1) == LOW);
  bool s2 = (digitalRead(A2) == LOW);
  if (s1 && !s1was) counter++;                // спрацювати раз на натиск
  if (s2 && !s2was) counter--;
  s1was = s1;  s2was = s2;

  refresh(counter);                           // перебрати розряди — раз за прохід
}
```
```esp-idf
#include "driver/gpio.h"
#include "esp_rom_sys.h"                    // esp_rom_delay_us

#define LATCH GPIO_NUM_4
#define CLK   GPIO_NUM_18
#define DATA  GPIO_NUM_23
#define S1    GPIO_NUM_32                   // кнопки: входи з підтяжкою
#define S2    GPIO_NUM_33

// байти сегментів для цифр 0..9 (спільний анод: 0 = сегмент світиться)
static const uint8_t SEG[10] = { 0xC0,0xF9,0xA4,0xB0,0x99,0x92,0x82,0xF8,0x80,0x90 };
static const uint8_t SEL[4]  = { 0xF1,0xF2,0xF4,0xF8 };   // вибір розряду 1..4

// те саме, що робить shiftOut: вісім бітів старшим уперед, такт на кожен
static void shift_out(uint8_t b) {
  for (int i = 7; i >= 0; i--) {
    gpio_set_level(DATA, (b >> i) & 1);
    gpio_set_level(CLK, 1);
    gpio_set_level(CLK, 0);
  }
}

static void show_digit(uint8_t seg, uint8_t pos) {
  gpio_set_level(LATCH, 0);
  shift_out(seg);  shift_out(SEL[pos]);     // сегменти, потім вибір розряду
  gpio_set_level(LATCH, 1);
}

static void refresh(int value) {
  int v = value < 0 ? -value : value;       // модуль для показу
  uint8_t d[4] = { (uint8_t)(v/1000%10), (uint8_t)(v/100%10),
                   (uint8_t)(v/10%10),   (uint8_t)(v%10) };
  for (uint8_t pos = 0; pos < 4; pos++) {
    show_digit(SEG[d[pos]], pos);
    esp_rom_delay_us(500);                  // трохи потримати розряд
    gpio_set_level(LATCH, 0);
    shift_out(0xFF);  shift_out(0xFF);      // погасити перед наступним
    gpio_set_level(LATCH, 1);
  }
}

void app_main(void) {
  gpio_config_t out = { .pin_bit_mask = (1ULL<<LATCH)|(1ULL<<CLK)|(1ULL<<DATA),
                        .mode = GPIO_MODE_OUTPUT };
  gpio_config(&out);
  gpio_config_t in = { .pin_bit_mask = (1ULL<<S1)|(1ULL<<S2),
                       .mode = GPIO_MODE_INPUT, .pull_up_en = GPIO_PULLUP_ENABLE };
  gpio_config(&in);

  int counter = 0;
  bool s1was = false, s2was = false;         // попередній стан для фронту
  while (1) {                                // такий цикл ще й доведеться мирити
    bool s1 = gpio_get_level(S1) == 0;       // зі сторожем задач — фон недарма
    bool s2 = gpio_get_level(S2) == 0;       // виносять у таймер
    if (s1 && !s1was) counter++;             // спрацювати раз на натиск
    if (s2 && !s2was) counter--;
    s1was = s1;  s2was = s2;
    refresh(counter);                        // перебрати розряди — раз за прохід
  }
}
```
```stm32
// Два 74HC595 — це звичайний зсувний регістр, тож віддамо байти апаратному SPI,
// а латч лишиться простим виводом.
#include "main.h"                  // згенероване CubeMX: hspi1, *_GPIO_Port / *_Pin

extern SPI_HandleTypeDef hspi1;    // MSB first, CPOL = 0, CPHA = 0

// байти сегментів для цифр 0..9 (спільний анод: 0 = сегмент світиться)
static const uint8_t SEG[10] = { 0xC0,0xF9,0xA4,0xB0,0x99,0x92,0x82,0xF8,0x80,0x90 };
static const uint8_t SEL[4]  = { 0xF1,0xF2,0xF4,0xF8 };   // вибір розряду 1..4

// виставити один розряд: байт сегментів + байт вибору, клац латчем
static void latch_out(uint8_t seg, uint8_t sel) {
  uint8_t frame[2] = { seg, sel };           // спершу сегменти, потім вибір
  HAL_GPIO_WritePin(LATCH_GPIO_Port, LATCH_Pin, GPIO_PIN_RESET);
  HAL_SPI_Transmit(&hspi1, frame, 2, HAL_MAX_DELAY);
  HAL_GPIO_WritePin(LATCH_GPIO_Port, LATCH_Pin, GPIO_PIN_SET);
}

static void refresh(int value) {
  int v = value < 0 ? -value : value;        // модуль для показу
  uint8_t d[4] = { (uint8_t)(v/1000%10), (uint8_t)(v/100%10),
                   (uint8_t)(v/10%10),   (uint8_t)(v%10) };
  for (uint8_t pos = 0; pos < 4; pos++) {
    latch_out(SEG[d[pos]], SEL[pos]);
    delay_us(500);                           // трохи потримати розряд (DWT або TIMx)
    latch_out(0xFF, 0xFF);                   // погасити перед наступним
  }
}

int main(void) {
  HAL_Init();  SystemClock_Config();  MX_GPIO_Init();  MX_SPI1_Init();
  // кнопки S1/S2 — входи з підтяжкою до живлення (GPIO_PULLUP у CubeMX)

  int counter = 0;
  uint8_t s1was = 0, s2was = 0;              // попередній стан для фронту
  while (1) {
    uint8_t s1 = (HAL_GPIO_ReadPin(S1_GPIO_Port, S1_Pin) == GPIO_PIN_RESET);
    uint8_t s2 = (HAL_GPIO_ReadPin(S2_GPIO_Port, S2_Pin) == GPIO_PIN_RESET);
    if (s1 && !s1was) counter++;             // спрацювати раз на натиск
    if (s2 && !s2was) counter--;
    s1was = s1;  s2was = s2;
    refresh(counter);                        // перебрати розряди — раз за прохід
  }
}
```
:::

Тут одразу видно, що бібліотека тобі дарувала. По-перше, `refresh()` доводиться кликати **безперервно** в кожному проході головного циклу — щойно цикл затримається на чомусь довгому, дисплей смикнеться або згасне. По-друге, гасіння розряду перед наступним (два `0xFF`) прибирає «привиди», коли хвіст попередньої цифри світиться крізь сусідній розряд, — бібліотека робить це сама. По-третє, кнопки тут відбиті **грубо**, лише по фронту `!s1was`, без відліку часу — тому на деренчливій кнопці лічильник іноді стрибне на два-три за один тик; повноцінний дебаунс тут довелося б дописати вручну з відліком мілісекунд. Оце й є та рутина, яку бібліотека забирає у фонове переривання, лишаючи головний цикл вільним.

> 🔧 **Навіщо це.** Ручний варіант варто хоч раз написати — він показує *механізм*, який бібліотека ховає: чому дисплей треба безперервно освіжати, звідки беруться привиди й деренчання. Але для будь-якої задачі складнішої за «показати число» перебір у головному циклі починає воювати з рештою коду за процесорний час. Тому в реальному проєкті на цьому шилді беруть бібліотеку — і тепер ти знаєш не лише *як* її кликати, а й *що саме* вона робить за тебе під сподом.
