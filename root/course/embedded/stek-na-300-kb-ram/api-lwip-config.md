# 📋 Довідник конфігурації пам'яті та буферів lwIP: параметри lwipopts.h

Управління ресурсами в легкому мережевому стеку lwIP повністю визначається на етапі компіляції через макроси у заголовному файлі `lwipopts.h`. Оскільки стек розрахований на роботу в умовах жорсткого ліміту оперативної пам'яті (від десятків до кількох сотень кілобайтів), кожен виділений буфер, блок керування або черга сегментів має точний вимір у байтах. Помилка у співвідношенні розмірів вікна прийому, пулу пакетів та черги передачі призводить або до нераціонального простою пам'яті, або до раптового блокування з'єднань через вичерпання пулів.

---

## 1. Базова підсистема пам'яті: Heap проти Pools

Мережевий стек lwIP розділяє пам'ять на дві незалежні підсистеми: купу змінного розміру (`mem.c`) для динамічних алокацій та набір фіксованих пулів блоків однакового розміру (`memp.c`) для швидкої алокації структур за константний час O(1) без ризику фрагментації.

```
+-------------------------------------------------------------------------------+
|                      Розподіл пам'яті в lwipopts.h                            |
+---------------------------------------+---------------------------------------+
|        Купа стека (Heap, mem.c)       |      Фіксовані пули (Pools, memp.c)   |
|   Розмір: MEM_SIZE                    |   Керується макросами MEMP_NUM_*      |
|   • Буфери PBUF_RAM (вихідні дані)    |   • PBUF_POOL (вхідні кадри DMA)      |
|   • Збірка IP-фрагментів (IP_REASS)   |   • TCP_PCB (блоки стану сокетів)     |
|   • Динамічні структури протоколів    |   • TCP_SEG, UDP_PCB, NETCONN, тощо   |
+---------------------------------------+---------------------------------------+
```

### Принцип роботи купи стека (`mem.c`)

Внутрішня купа `mem.c` є простим блоковим менеджером пам'яті, побудованим на двозв'язному списку вільних ділянок. На відміну від стандартного системного `malloc()`, вона виділяє пам'ять зі статично оголошеного масиву `ram_heap` розміром `MEM_SIZE` байтів, розташованого у секції `.bss`.

Головні властивості купи `mem.c`:
1. **Ізоляція від системної купи:** Будь-який витік або дефіцит пам'яті всередині мережевого стека не може пошкодити купу операційної системи FreeRTOS або прикладних задач.
2. **Об'єднання сусідніх вільних блоків:** При виклику `mem_free()` звільнений блок негайно зливається з попереднім та наступним суміжними блоками, якщо вони вільні. Це суттєво зменшує зовнішню фрагментацію пам'яті під час частого виділення та звільнення буферів різного розміру.
3. **Небезпека тривалої роботи:** Якщо додаток постійно виділяє буфери різної довжини під вихідні TCP-сегменти, довгі ланцюжки дрібних фрагментів можуть призвести до ситуації, коли сумарно в купі є 10 КБ вільного місця, але виділити суцільний блок на 1500 байтів неможливо.

### Принцип роботи пулів фіксованого розміру (`memp.c`)

Підсистема `memp.c` організована як набір окремих масивів для кожного типу структур даних:
* `MEMP_TCP_PCB`: керуючі блоки з'єднань TCP;
* `MEMP_TCP_PCB_LISTEN`: блоки прослуховування портів;
* `MEMP_TCP_SEG`: дескриптори черги відправлення сегментів;
* `MEMP_PBUF_POOL`: пакетні буфери прийому фіксованого розміру.

Усі невикористані блоки кожного типу об'єднані в однозв'язний стек вільних елементів. Операція виділення полягає у вилученні верхнього елемента зі стека (зсув одного вказівника), а звільнення — у поверненні елемента на вершину стека. Обидві операції виконуються за кілька тактів процесора, не потребують циклічного пошуку і повністю унеможливлюють фрагментацію пам'яті.

### Ключові параметри конфігурації купи та пулів

| Макрос | Типове значення | Опис та вплив на пам'ять |
| :--- | :--- | :--- |
| `MEM_LIBC_MALLOC` | `0` | Використовувати стандартний `malloc()` платформи замість власного менеджера lwIP. Для мікроконтролерів рекомендується `0` для уникнення фрагментації системної купи. |
| `MEM_ALIGNMENT` | `4` (або `32`) | Байтне вирівнювання структур у пам'яті. Для ARM Cortex-M4 — `4` байти; для Cortex-M7 з увімкненим D-Cache — `32` байти (розмір рядка кеша). |
| `MEM_SIZE` | `16384` | Розмір внутрішньої купи lwIP у байтах. З неї виділяються буфери типу `PBUF_RAM` для передачі та збірки фрагментованих пакетів. |
| `MEMP_MEM_MALLOC` | `0` | Якщо `1`, пули `memp` виділяються з купи `MEM_SIZE`. Якщо `0`, кожен пул оголошується як окремий статичний масив у секції `.bss`. |
| `MEMP_OVERFLOW_CHECK` | `0` (налагодження: `1` або `2`) | Перевірка переповнення буферів через магічні байти-канарки навколо кожного блоку пулу. |

---

## 2. Пакетні буфери (Pbuf Pool): вхідний трафік

Пул `PBUF_POOL` є критичним для прийому даних від мережевого інтерфейсу (Ethernet MAC або Wi-Fi). Контролер DMA або переривання драйвера захоплює вільні буфери з цього пулу для запису вхідного кадру.

```
+-------------------------------------------------------------------------------+
|                       Структура елемента PBUF_POOL                            |
|  +---------------------------+---------------------------------------------+  |
|  | struct pbuf (≈ 16 байтів) | Корисне навантаження (PBUF_POOL_BUFSIZE Б) |  |
|  +---------------------------+---------------------------------------------+  |
|  <------------------------- Загальний розмір блоку -------------------------> |
+-------------------------------------------------------------------------------+
```

### Формула розрахунку розміру пулу

```
Загальна_пам'ять_PBUF_POOL = PBUF_POOL_SIZE * (PBUF_POOL_BUFSIZE + sizeof(struct pbuf) + MEM_ALIGNMENT)
```

При виборі значення `PBUF_POOL_BUFSIZE` інженер стикається з вибором між витратою пам'яті та ефективністю DMA:
* **Значення `512` байтів:** Дозволяє економно витрачати пам'ять на коротких пакетах (ARP-запити, TCP ACK, ICMP ping), оскільки вони займають лише один блок замість повного кадру. Великі кадри на 1514 байтів розбиваються на ланцюжок із трьох блоків. Проте такий підхід ускладнює налаштування контролера DMA, вимагаючи ланцюжкових дескрипторів.
* **Значення `1536` байтів:** Дозволяє помістити будь-який стандартний кадр Ethernet в один суцільний буфер пам'яті. Це є обов'язковою вимогою для простої та високоефективної реалізації апаратного Zero-Copy через дескриптори Ethernet MAC DMA.

| Макрос | Типове значення | Формула або рекомендація |
| :--- | :--- | :--- |
| `PBUF_POOL_SIZE` | `16` | Кількість буферів у пулі прийому. Повинна вміщувати як мінімум 2 повні кадри Ethernet на максимальній швидкості плюс запас на затримку обробки задачею TCP/IP. |
| `PBUF_POOL_BUFSIZE` | `512` або `1536` | Розмір корисного навантаження кожного буфера в пулі. При значенні `512` стандартний кадр 1514 байтів розбивається на ланцюжок із 3 буферів. При `1536` — кожен кадр лягає в один суцільний буфер (ідеально для Zero-Copy DMA). |
| `PBUF_LINK_ENCAPSULATION_HLEN` | `0` | Додатковий запас байтів перед заголовком кадру для нестандартних апаратних тегів або заголовків тунелювання. |

---

## 3. Протокол TCP: вікна, сегменти та черги

Протокол TCP вимагає найбільше оперативної пам'яті через необхідність підтримувати стан з'єднання, буферизувати непідтверджені дані для можливого повторного надсилання та збирати сегменти, які надійшли не по порядку.

```
+-------------------------------------------------------------------------------+
|               Взаємозв'язок параметрів TCP у lwipopts.h                       |
|                                                                               |
|   TCP_MSS (1460 Б)  ──────► Максимальний розмір корисних даних у сегменті     |
|          │                                                                    |
|          ▼                                                                    |
|   TCP_WND (4 * MSS) ──────► Розмір вікна прийому (буфери в PBUF_POOL)         |
|                                                                               |
|   TCP_SND_BUF (4 * MSS) ──► Буфер вихідних даних (виділяється в MEM_SIZE)      |
|          │                                                                    |
|          ▼                                                                    |
|   TCP_SND_QUEUELEN ───────► Ліміт pbuf у черзі TX: (2 * TCP_SND_BUF / MSS)    |
+-------------------------------------------------------------------------------+
```

### Фізичний зміст та балансування параметрів TCP

1. **`TCP_MSS` (Maximum Segment Size):**
   Визначає найбільший обсяг корисних даних в одному IP-пакеті. Для Ethernet зі стандартним MTU 1500 байтів розмір `TCP_MSS` дорівнює 1500 − 20 (IP) − 20 (TCP) = 1460 байтів. Зменшення MSS до 536 байтів (мінімум за стандартом RFC 879) дозволяє суттєво зменшити буфери передачі, але збільшує накладні витрати на заголовки пакетів утричі.
2. **`TCP_WND` (Receive Window):**
   Визначає пропускну здатність каналу зв'язку за формулою BDP (*Bandwidth-Delay Product*):

```
Пропускна_здатність <= TCP_WND / Час_кругового_обігу_RTT
```

Якщо RTT становить 50 мс, а вікно налаштовано всього на 1 × MSS (1460 байтів), швидкість завантаження фізично не перевищить 29 КБ/с навіть на гігабітному лінку. Для досягнення швидкості 1 МБ/с на такому каналі вікно `TCP_WND` має бути не меншим за 50 КБ. Проте на мікроконтролері з 300 КБ SRAM вікно зазвичай обмежують значенням 3 × MSS або 4 × MSS (4380–5840 байтів).

3. **`TCP_SND_BUF` та `TCP_SND_QUEUELEN`:**
   Визначають, скільки байтів та пакетних буферів додаток може передати стеку до моменту, коли функція відправлення заблокується в очікуванні підтверджень ACK від отримувача.

| Макрос | Формула / Значення | Пояснення інженерного змісту |
| :--- | :--- | :--- |
| `TCP_MSS` | `1460` (MTU 1500 − 40) | Максимальний розмір сегмента. Визначає найбільшу порцію даних без урахування заголовків IP та TCP. Для захищених тунелів або VPN може зменшуватись до `1360–1420`. |
| `TCP_WND` | `2 * TCP_MSS` .. `6 * TCP_MSS` | Розмір вікна прийому. Кількість байтів, яку віддалений вузол може надіслати без очікування ACK. |
| `TCP_SND_BUF` | `2 * TCP_MSS` .. `4 * TCP_MSS` | Розмір буфера відправлення. Обсяг даних, який додаток може передати функції `tcp_write()` або `send()` до моменту блокування. |
| `TCP_SND_QUEUELEN` | `(4 * (TCP_SND_BUF) / (TCP_MSS))` | Максимальна кількість елементів `pbuf` у черзі відправлення. Запобігає ситуації, коли передача тисячі однобайтних пакетів вичерпує всі дескриптори сегментів. |
| `MEMP_NUM_TCP_PCB` | `4` .. `32` | Максимальна кількість одночасно відкритих активних TCP-з'єднань у стані ESTABLISHED або напівзакритих станах. |
| `MEMP_NUM_TCP_PCB_LISTEN` | `2` .. `8` | Кількість сокетів, які можуть одночасно перебувати в режимі прослуховування портів (`listen()`). |
| `MEMP_NUM_TCP_SEG` | `16` .. `64` | Кількість одночасно виділених заголовків сегментів TCP. Повинна перевищувати сумарний `TCP_SND_QUEUELEN` по всіх активних сокетах. |
| `TCP_QUEUE_OOSEQ` | `1` (або `0`) | Черга сегментів, що надійшли не за порядком. Значення `1` запобігає зайвим повторним передачам у зашумленій мережі, але потребує до 4–8 додаткових pbuf на сокет. У системах із гострим дефіцитом RAM вимикається (`0`). |

---

## 4. Інтерфейси API та системна інтеграція (RTOS)

Вибір рівня API визначає накладні витрати пам'яті на рівні задач операційної системи реального часу.

| Макрос | Значення за замовчуванням | Вплив на пам'ять і функціонал |
| :--- | :--- | :--- |
| `NO_SYS` | `1` (Bare-Metal) / `0` (RTOS) | При `1` вимикається багатопоточність; доступний лише Raw Callback API. При `0` активуються черги `sys_mbox`, семафори `sys_sem` та потік `tcpip_thread`. |
| `LWIP_NETCONN` | `1` (якщо `NO_SYS == 0`) | Вмикає послідовний блокуючий інтерфейс Netconn. Додає пул `MEMP_NUM_NETCONN`. |
| `LWIP_SOCKET` | `1` (якщо `NO_SYS == 0`) | Вмикає стандартні BSD сокети POSIX. Створює таблицю дескрипторів сокетів `NUM_SOCKETS`. |
| `MEMP_NUM_NETCONN` | `MEMP_NUM_TCP_PCB + MEMP_NUM_UDP_PCB` | Кількість структур керування зв'язком між потоком lwIP та задачами додатку. |
| `MEMP_NUM_NETBUF` | `8` .. `16` | Пул буферів `netbuf`, що передаються через поштові скриньки `sys_mbox`. |
| `TCPIP_MBOX_SIZE` | `16` .. `32` | Розмір черги повідомлень головного потоку стека `tcpip_thread`. Переповнення черги призводить до відхилення пакетів на рівні драйвера. |
| `TCPIP_THREAD_STACKSIZE` | `1024` .. `2048` слів | Розмір стека задачі `tcpip_thread` у FreeRTOS (у байтах це `4096–8192` Б). |

---

## 5. Діагностика вичерпання ресурсів через підсистему lwIP Stats

:::tabs

@tab C (Виклик діагностики)
```c
#if LWIP_STATS
    stats_display(); /* Друк повної карти використання пам'яті в UART/консоль */
#endif
```

@tab C++ (Діагностична обгортка)
```cpp
#include <cstdint>

extern "C" {
#include "lwip/opt.h"
#include "lwip/stats.h"
}

namespace embedded::diag {

inline void dumpMemoryStatistics() noexcept {
#if LWIP_STATS
    stats_display();
#endif
}

} // namespace embedded::diag
```

:::

Поля структури статистики дозволяють точно локалізувати вузьке місце:
* `lwip_stats.memp[MEMP_PBUF_POOL]->err`: кількість відхилених пакетів через вичерпання вхідних буферів;
* `lwip_stats.memp[MEMP_TCP_PCB]->max`: пікова кількість одночасно відкритих сокетів від моменту старту системи;
* `lwip_stats.mem.err`: кількість відмов у виділенні динамічної купи `MEM_SIZE`.

---

## 6. Готові профілі конфігурації під реальні сценарії

Нижче наведено три збалансовані пресети конфігурації для різних апаратних платформ та вимог до швидкодії, оформлені мовами C (`lwipopts.h`) та C++ (параметризований конфігуратор структури).

### Профіль 1: «Мікроконтролерний мінімум» (Bare-Metal, SRAM 16–24 КБ)
*Ціль:* Давачі IoT, прості веб-сторінки конфігурації, протоколи MQTT/CoAP на STM32F103/F401 без RTOS.

:::tabs

@tab C (lwipopts.h)
```c
#ifndef LWIPOPTS_H
#define LWIPOPTS_H

#define NO_SYS                          1
#define MEM_LIBC_MALLOC                 0
#define MEM_ALIGNMENT                   4
#define MEM_SIZE                        (8 * 1024)

#define MEMP_NUM_PBUF                   8
#define MEMP_NUM_TCP_PCB                2
#define MEMP_NUM_TCP_PCB_LISTEN         1
#define MEMP_NUM_TCP_SEG                12
#define MEMP_NUM_UDP_PCB                2

#define PBUF_POOL_SIZE                  8
#define PBUF_POOL_BUFSIZE               512

#define TCP_MSS                         536
#define TCP_WND                         (2 * TCP_MSS)
#define TCP_SND_BUF                     (2 * TCP_MSS)
#define TCP_SND_QUEUELEN                4
#define TCP_QUEUE_OOSEQ                 0

#define LWIP_NETCONN                    0
#define LWIP_SOCKET                     0
#define LWIP_DHCP                       1
#define LWIP_DNS                        1

#endif /* LWIPOPTS_H */
```

@tab C++ (Опис параметрів профілю)
```cpp
#include <cstdint>
#include <cstddef>

namespace embedded::config {

struct MinimalProfile {
    static constexpr bool kNoSys = true;
    static constexpr size_t kMemAlignment = 4;
    static constexpr size_t kMemSize = 8 * 1024;

    static constexpr size_t kNumPbuf = 8;
    static constexpr size_t kNumTcpPcb = 2;
    static constexpr size_t kNumTcpListen = 1;
    static constexpr size_t kNumTcpSeg = 12;

    static constexpr size_t kPbufPoolSize = 8;
    static constexpr size_t kPbufPoolBufSize = 512;

    static constexpr uint16_t kTcpMss = 536;
    static constexpr uint16_t kTcpWnd = 2 * kTcpMss;
    static constexpr uint16_t kTcpSndBuf = 2 * kTcpMss;
};

} // namespace embedded::config
```

:::

### Профіль 2: «Промисловий стандарт RTOS» (FreeRTOS, SRAM 48–64 КБ)
*Ціль:* Контролери автоматики, шлюзи Modbus TCP, веб-сервери керування на STM32F407 або ESP32 з 4–8 одночасними з'єднаннями.

:::tabs

@tab C (lwipopts.h)
```c
#ifndef LWIPOPTS_H
#define LWIPOPTS_H

#define NO_SYS                          0
#define MEM_LIBC_MALLOC                 0
#define MEM_ALIGNMENT                   4
#define MEM_SIZE                        (20 * 1024)

#define MEMP_NUM_PBUF                   16
#define MEMP_NUM_TCP_PCB                8
#define MEMP_NUM_TCP_PCB_LISTEN         4
#define MEMP_NUM_TCP_SEG                32
#define MEMP_NUM_UDP_PCB                4
#define MEMP_NUM_NETCONN                12
#define MEMP_NUM_NETBUF                 16

#define PBUF_POOL_SIZE                  16
#define PBUF_POOL_BUFSIZE               512

#define TCP_MSS                         1460
#define TCP_WND                         (3 * TCP_MSS)
#define TCP_SND_BUF                     (3 * TCP_MSS)
#define TCP_SND_QUEUELEN                8
#define TCP_QUEUE_OOSEQ                 1

#define TCPIP_MBOX_SIZE                 16
#define DEFAULT_RAW_RECVMBOX_SIZE       8
#define DEFAULT_UDP_RECVMBOX_SIZE       8
#define DEFAULT_TCP_RECVMBOX_SIZE       16
#define DEFAULT_ACCEPTMBOX_SIZE         8

#define LWIP_NETCONN                    1
#define LWIP_SOCKET                     1
#define SO_REUSE                        1
#define TCP_LISTEN_BACKLOG              1

#endif /* LWIPOPTS_H */
```

@tab C++ (Опис параметрів профілю)
```cpp
#include <cstdint>
#include <cstddef>

namespace embedded::config {

struct IndustrialRtosProfile {
    static constexpr bool kNoSys = false;
    static constexpr size_t kMemAlignment = 4;
    static constexpr size_t kMemSize = 20 * 1024;

    static constexpr size_t kNumPbuf = 16;
    static constexpr size_t kNumTcpPcb = 8;
    static constexpr size_t kNumTcpListen = 4;
    static constexpr size_t kNumTcpSeg = 32;

    static constexpr size_t kPbufPoolSize = 16;
    static constexpr size_t kPbufPoolBufSize = 512;

    static constexpr uint16_t kTcpMss = 1460;
    static constexpr uint16_t kTcpWnd = 3 * kTcpMss;
    static constexpr uint16_t kTcpSndBuf = 3 * kTcpMss;
    static constexpr bool kEnableSockets = true;
};

} // namespace embedded::config
```

:::

### Профіль 3: «Високошвидкісний Zero-Copy» (100 Мбіт/с, SRAM 100–128 КБ)
*Ціль:* Потокове передавання даних (аудіо, камери, осцилографи) на STM32F7 / H7 з апаратним D-Cache та прямим зв'язуванням DMA.

:::tabs

@tab C (lwipopts.h)
```c
#ifndef LWIPOPTS_H
#define LWIPOPTS_H

#define NO_SYS                          0
#define MEM_LIBC_MALLOC                 0
#define MEM_ALIGNMENT                   32      /* Вирівнювання за рядком D-Cache */
#define MEM_SIZE                        (32 * 1024)

#define MEMP_NUM_PBUF                   32
#define MEMP_NUM_TCP_PCB                16
#define MEMP_NUM_TCP_PCB_LISTEN         4
#define MEMP_NUM_TCP_SEG                64
#define MEMP_NUM_UDP_PCB                8
#define MEMP_NUM_NETCONN                24
#define MEMP_NUM_NETBUF                 32

/* Повний розмір Ethernet кадру в одному pbuf для прямої роботи DMA */
#define PBUF_POOL_SIZE                  24
#define PBUF_POOL_BUFSIZE               1536

#define TCP_MSS                         1460
#define TCP_WND                         (6 * TCP_MSS)
#define TCP_SND_BUF                     (6 * TCP_MSS)
#define TCP_SND_QUEUELEN                16
#define TCP_QUEUE_OOSEQ                 1

#define TCPIP_MBOX_SIZE                 32
#define DEFAULT_TCP_RECVMBOX_SIZE       32

#define LWIP_NETCONN                    1
#define LWIP_SOCKET                     1
#define LWIP_CHECKSUM_CTRL_PER_NETIF    1       /* Апаратний розрахунок контрольних сум */
#define CHECKSUM_GEN_IP                 0
#define CHECKSUM_GEN_UDP                0
#define CHECKSUM_GEN_TCP                0
#define CHECKSUM_CHECK_IP               0
#define CHECKSUM_CHECK_UDP              0
#define CHECKSUM_CHECK_TCP              0

#endif /* LWIPOPTS_H */
```

@tab C++ (Опис параметрів профілю)
```cpp
#include <cstdint>
#include <cstddef>

namespace embedded::config {

struct ZeroCopyHighSpeedProfile {
    static constexpr bool kNoSys = false;
    static constexpr size_t kMemAlignment = 32; /* D-Cache Line Size */
    static constexpr size_t kMemSize = 32 * 1024;

    static constexpr size_t kNumPbuf = 32;
    static constexpr size_t kNumTcpPcb = 16;
    static constexpr size_t kNumTcpListen = 4;
    static constexpr size_t kNumTcpSeg = 64;

    static constexpr size_t kPbufPoolSize = 24;
    static constexpr size_t kPbufPoolBufSize = 1536; /* Single full Ethernet frame */

    static constexpr uint16_t kTcpMss = 1460;
    static constexpr uint16_t kTcpWnd = 6 * kTcpMss;
    static constexpr uint16_t kTcpSndBuf = 6 * kTcpMss;
    static constexpr bool kHardwareChecksumOffload = true;
};

} // namespace embedded::config
```

:::
