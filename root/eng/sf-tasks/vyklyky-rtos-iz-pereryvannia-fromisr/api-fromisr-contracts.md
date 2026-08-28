# 📋 Контракти та інтерфейси викликів FromISR у RTOS

Ця довідка містить детальну специфікацію контрактів, часових гарантій, вимог до контексту та сигнатур спеціалізованих функцій RTOS для роботи в апаратних обробниках переривань (ISR, від англ. *Interrupt Service Routine*). Вона призначена для системних інженерів та розробників вбудованого програмного забезпечення, яким необхідно забезпечити надійний, детермінований і безпечний обмін даними між апаратним рівнем мікроконтролера та задачами операційної системи реального часу.

---

### Загальні інваріанти інтерфейсів FromISR

Будь-яка функція RTOS із суфіксом `FromISR` підпорядковується суворим системним інваріантам, які фундаментально відрізняють її від стандартного API рівня задач:

1. **Детермінована алгоритмічна складність `O(1)`**: функція не містить циклів очікування, динамічного виділення пам'яті з купи чи обходу списків довільної довжини. Вона виконує фіксовану кількість процесорних інструкцій для атомарної модифікації черги, семафора або бітового поля стану задачі.
2. **Відсутність блокування та тайм-аутів**: у сигнатурах `FromISR` принципово відсутній параметр тайм-ауту (`xTicksToWait`). Якщо буфер черги заповнений або семафор недоступний, функція негайно повертає код помилки (`errQUEUE_FULL` або `pdFAIL`), не зупиняючи виконання процесора.
3. **Керування відкладеним витісненням**: функція приймає покажчик `BaseType_t *pxHigherPriorityTaskWoken`. Якщо операція розблокувала задачу з пріоритетом, вищим за поточну перервану задачу, ядро записує за цією адресою значення `pdTRUE`. Сама функція контекст не перемикає, залишаючи це рішення коду обробника перед виходом.
4. **Контекст виклику та апаратний пріоритет**: виклик дозволений виключно з переривань, чий числовий пріоритет у контролері NVIC є не меншим (апаратний пріоритет не вищим) за константу `configMAX_SYSCALL_INTERRUPT_PRIORITY`. Виклик із високопріоритетного переривання нульового джитеру призводить до невиправного пошкодження структур ядра через порушення критичних секцій.

---

### Специфікація API черг (Queue API)

#### `xQueueSendToBackFromISR` / `xQueueSendFromISR`
Копіює елемент даних у кінець черги з обробника переривання без блокування.

:::tabs
```c
BaseType_t xQueueSendFromISR(
    QueueHandle_t xQueue,
    const void *pvItemToQueue,
    BaseType_t *pxHigherPriorityTaskWoken
);
```
:::code api-fromisr-contracts/cpp/xqueuesendtobackfromisr.cpp
:::

* **Параметри**:
  * `xQueue`: дескриптор створеної черги.
  * `pvItemToQueue`: покажчик на буфер із даними фіксованого розміру, які копіюються у внутрішнє кільце черги через `memcpy`.
  * `pxHigherPriorityTaskWoken`: покажчик на змінну-прапорець. Ядро записує `pdTRUE`, якщо запис розблокував задачу з пріоритетом, вищим за перервану. Якщо значення вже було `pdTRUE`, воно не перезаписується в `pdFALSE`.
* **Повертає**: `pdPASS` при успішному розміщенні в буфері; `errQUEUE_FULL`, якщо буфер переповнений.
* **Внутрішній механізм**: всередині ядра FreeRTOS функція викликає `prvCopyDataToQueue()`, після чого перевіряє список задач, які чекають на читання з черги (`xTasksWaitingToReceive`). Якщо список не порожній, найвища за пріоритетом задача видаляється зі списку очікування і переноситься до списку готових (`pxReadyTasksLists`).

#### `xQueueOverwriteFromISR`
Записує елемент у чергу одиничної глибини (`uxQueueLength == 1`), безумовно перезаписуючи старе значення, якщо воно не було прочитане.

:::tabs
```c
BaseType_t xQueueOverwriteFromISR(
    QueueHandle_t xQueue,
    const void *pvItemToQueue,
    BaseType_t *pxHigherPriorityTaskWoken
);
```
:::code api-fromisr-contracts/cpp/xqueueoverwritefromisr.cpp
:::

* **Призначення**: ідеально підходить для телеметрії та високочастотних давачів, де важливе лише найсвіжіше вимірювання, а пропуск проміжних станів не є критичним.
* **Повертає**: завжди `pdPASS`.

---

### Специфікація API семафорів (Semaphore API)

#### `xSemaphoreGiveFromISR`
Звільняє бінарний семафор або інкрементує значення лічильного семафора з контексту ISR.

:::tabs
```c
BaseType_t xSemaphoreGiveFromISR(
    SemaphoreHandle_t xSemaphore,
    BaseType_t *pxHigherPriorityTaskWoken
);
```
:::code api-fromisr-contracts/cpp/xsemaphoregivefromisr.cpp
:::

* **Застосування**: сигналізація про завершення апаратних передач по шинах SPI, I2C або каналах прямого доступу до пам'яті (DMA).
* **Повертає**: `pdPASS` у разі успіху; `errQUEUE_FULL`, якщо семафор уже виставлений (для бінарного) або досяг ліміту (для лічильного).
* **Категорична заборона**: не можна викликати з м'ютексами (`xSemaphoreCreateMutex`), оскільки м'ютекси реалізують протокол успадкування пріоритетів і жорстко прив'язані до TCB задачі-власника.

---

### Прямі сповіщення задач (Direct Task Notifications)

Прямі сповіщення задач дозволяють обійтися без створення додаткових структур синхронізації в динамічній пам'яті. Кожен TCB у FreeRTOS уже містить 32-бітний масив сповіщень.

#### `vTaskNotifyGiveFromISR`
Виконує швидкий атомарний інкремент 32-бітного лічильника сповіщень цільової задачі.

:::tabs
```c
void vTaskNotifyGiveFromISR(
    TaskHandle_t xTaskToNotify,
    BaseType_t *pxHigherPriorityTaskWoken
);
```
:::code api-fromisr-contracts/cpp/vtasknotifygivefromisr.cpp
:::

#### `xTaskNotifyFromISR`
Комплексне надсилання сповіщення з можливістю встановлення бітових прапорців або прямого запису 32-бітного значення.

:::tabs
```c
BaseType_t xTaskNotifyFromISR(
    TaskHandle_t xTaskToNotify,
    uint32_t ulValue,
    eNotifyAction eAction,
    BaseType_t *pxHigherPriorityTaskWoken
);
```
:::code api-fromisr-contracts/cpp/xtasknotifyfromisr.cpp
:::

* **Дії `eAction`**:
  * `eSetBits`: порозрядне бітове «АБО» (аналог Event Groups без накладних витрат).
  * `eIncrement`: збільшення лічильника на одиницю.
  * `eSetValueWithOverwrite`: примусовий запис числа у комірку сповіщення задачі.
  * `eSetValueWithoutOverwrite`: запис значення лише у випадку, якщо попереднє значення вже оброблене задачею.

---

### Потокові буфери та групи подій (Stream Buffers & Event Groups)

#### Потокові буфери (`xStreamBufferSendFromISR`)
Потокові буфери (Stream Buffers) спеціально оптимізовані для сценаріїв «один письменник — один читач» (SPSC). На відміну від звичайних черг, які копіюють дані фіксованими блоками, потоковий буфер дозволяє передавати неперервний потік байтів довільної довжини без накладних витрат на дескриптори черги.

:::tabs
```c
size_t xStreamBufferSendFromISR(
    StreamBufferHandle_t xStreamBuffer,
    const void *pvTxData,
    size_t xDataLengthBytes,
    BaseType_t *pxHigherPriorityTaskWoken
);
```
:::code api-fromisr-contracts/cpp/potokovi-bufery.cpp
:::

#### Групи подій (`xEventGroupSetBitsFromISR` та демон таймерів)
Групи подій (Event Groups) мають важливу архітектурну особливість: встановлення бітів події може розблокувати не одну, а довільну кількість задач, які очікують на різні комбінації прапорців.

Виконання такої операції всередині апаратного ISR порушило б детермінізм `O(1)` і затримало б інші переривання. Тому функція `xEventGroupSetBitsFromISR` використовує спеціальний механізм: вона записує команду в чергу системного демона таймерів (`xTimerPendFunctionCallFromISR`). Реальне розблокування задач виконується пізніше, у контексті системної задачі `prvTimerTask` (Daemon Task).

:::tabs
```c
BaseType_t xEventGroupSetBitsFromISR(
    EventGroupHandle_t xEventGroup,
    const EventBits_t uxBitsToSet,
    BaseType_t *pxHigherPriorityTaskWoken
);
```
:::code api-fromisr-contracts/cpp/hrupy-podii.cpp
:::

---

### Механіка макросів виходу та перемикання контексту

Після завершення всіх операцій введення-виведення обробник переривання викликає архітектурний макрос передачі керування.

:::tabs
```c
/* Виклик макросу перемикання контексту на C */
void SysTick_Handler_Custom(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    /* Логіка обробника */
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}
```
:::code api-fromisr-contracts/cpp/mekhanika-makrosiv-vykhodu.cpp
:::

* **Внутрішня робота макросу**:
  * В архітектурі ARM Cortex-M макрос `portYIELD_FROM_ISR(xHigherPriorityTaskWoken)` розгортається в запис біта `SCB_ICSR_PENDSVSET_Msk` у системний регістр `SCB->ICSR`.
  * В архітектурі RISC-V макрос виставляє програмне переривання в контролері CLINT/PLIC (`msip` біт у регістрі `mip`).
  * В архітектурі Espressif Xtensa (ESP32) макрос задіює спеціальний рівень переривання крос-ядерної сигналізації через регістри DPORT.

---

### Зведена таблиця API переривань

| Призначення | Звичайний API задачі | Аналог для переривань (FromISR) | Гарантія часу | Вплив на перемикання |
|---|---|---|---|---|
| Черга: відправка | `xQueueSend(q, item, t)` | `xQueueSendFromISR(q, item, &w)` | `O(1)` | Виставляє `w = pdTRUE` при розбудженні |
| Черга: вичитка | `xQueueReceive(q, buf, t)` | `xQueueReceiveFromISR(q, buf, &w)` | `O(1)` | Виставляє `w = pdTRUE` якщо задача чекала місце |
| Семафор: віддати | `xSemaphoreGive(s)` | `xSemaphoreGiveFromISR(s, &w)` | `O(1)` | Будить задачу на семафорі |
| Сповіщення: лічильник | `xTaskNotifyGive(t)` | `vTaskNotifyGiveFromISR(t, &w)` | `O(1)` | Найшвидший спосіб розбудити воркер |
| Сповіщення: біти | `xTaskNotify(t, v, act)` | `xTaskNotifyFromISR(t, v, act, &w)` | `O(1)` | Встановлює біти подій у TCB |
| Потоковий буфер | `xStreamBufferSend(b, d, len, t)` | `xStreamBufferSendFromISR(b, d, len, &w)` | `O(1)` | Записує байти в буфер SPSC |
| Група подій: біти | `xEventGroupSetBits(g, b)` | `xEventGroupSetBitsFromISR(g, b, &w)` | `O(1)` | Делегує подію демону таймерів |
| Перемикання контексту | `taskYIELD()` | `portYIELD_FROM_ISR(w)` | `O(1)` | Активує відкладений перемикач PendSV |

---

### Порівняльний аналіз із Zephyr OS та POSIX

* **Zephyr RTOS**:
  * В ядрі Zephyr реалізовано автоматичне детектування контексту: макрос `k_is_in_isr()` дозволяє примітивам (як-от `k_sem_give`) працювати однаково безпечно як із нитки, так і з переривання.
  * Якщо розробник спробує викликати блокуючу операцію `k_sem_take(&sem, K_FOREVER)` зсередини переривання, ядро миттєво викличе апаратну паніку `k_panic()`.
  * Для передачі даних між ISR та нитками Zephyr надає lock-free черги без блокувань: `k_fifo_put` та `k_lifo_put`.

* **POSIX / Linux Signal Context**:
  * У настільних операційних системах аналогом контексту ISR є обробник сигналу (Signal Handler).
  * Стандарт POSIX чітко визначає набір функцій, безпечних для асинхронного виклику (англ. *Async-Signal-Safe Functions*): `write()`, `read()`, `sigaction()`.
  * Функції, які захоплюють м'ютекси або виділяють динамічну пам'ять (`malloc`, `free`, `printf`), категорично заборонені в обробниках сигналів через загрозу мертвого заклинювання (*Deadlock*).
