# 📋 Специфікація IPC протоколу та топології SOF

Ця вставка містить довідкову специфікацію протоколів міжпроцесного зв'язку (IPC v3 та IPC v4) між драйвером ядра Linux та прошивкою Sound Open Firmware, а також описує бінарні структури ALSA Topology (`.tplg`), необхідні для інстанціювання аудіографів на DSP.

## 1. Протокол IPC v3 (Класичний SOF IPC)

У класичному протоколі IPC v3 обмін командами виконується через виділену ділянку оперативної пам'яті DSP SRAM, яка описується як Mailbox (поштова скринька). Кожне повідомлення розпочинається із уніфікованого заголовка `sof_ipc_cmd_hdr`, за яким у пам'яті слідують дані корисного навантаження (payload).

Поле `cmd` містить упаковану 32-бітну бітову маску, де старші біти визначають категорію команди (глобальні команди `SOF_IPC_GLB_...`, команди потоків `SOF_IPC_STREAM_...` або команди топології `SOF_IPC_TPLG_...`), а молодші біти відповідають конкретному підтипу дії.

:::tabs
```c
/* C structure definition for IPC v3 Header */
#include <stdint.h>

struct sof_ipc_cmd_hdr {
    uint32_t size;      /* Загальний розмір повідомлення у байтах, включаючи заголовок */
    uint32_t cmd;       /* Бітова маска: [31:28] Категорія | [27:16] Команда | [15:0] Підтип */
} __attribute__((packed));
```
```cpp
// C++ representation for IPC v3 Header
#include <cstdint>

struct alignas(4) IpcCmdHeader {
    std::uint32_t size{sizeof(IpcCmdHeader)};
    std::uint32_t cmd{0};

    [[nodiscard]] constexpr std::uint32_t getCategory() const noexcept {
        return (cmd >> 28) & 0x0F;
    }
    [[nodiscard]] constexpr std::uint32_t getCommand() const noexcept {
        return (cmd >> 16) & 0x0FFF;
    }
};
```
:::

### Команди створення та налаштування PCM потоків (`SOF_IPC_STREAM_...`)

Під час відкриття та конфігурації нового аудіопотоку драйвер ядра надсилає на DSP команду `SOF_IPC_STREAM_PCM_PARAMS`. Ця команда транслює параметри, отримані від виклику ALSA `hw_params` (частота дискретизації, кількість каналів, розмір буфера), у внутрішній формат прошивки.

Поле `comp_id` посилається на унікальний ідентифікатор Host-компонента в графі обробки, створеному під час зчитування топології. Поле `buffer_size` вказує точний розмір кільцевого DRAM-буфера, виділеного ядрам Linux через `dma_alloc_coherent()`.

:::tabs
```c
/* C structure for Stream Parameters configuration */
struct sof_ipc_stream_params {
    struct sof_ipc_cmd_hdr hdr;
    uint32_t comp_id;          /* ID Host-компонента в графу DSP */
    uint32_t buffer_fmt;       /* Формат буфера (interleaved / non-interleaved) */
    uint32_t frame_fmt;        /* Формат семплів (S16_LE, S24_LE, S32_LE) */
    uint32_t rate;             /* Частота дискретизації у Гц (наприклад, 48000) */
    uint32_t channels;         /* Кількість каналів (1, 2, 4, 8) */
    uint32_t buffer_size;      /* Загальний розмір ring-буфера в Host DRAM (байти) */
    uint32_t period_size;      /* Розмір одного періоду переривання (байти) */
    uint32_t sample_container_bytes; /* Розмір контейнера семпла у пам'яті (зазвичай 4 байти) */
    uint32_t host_period_bytes;/* Інтервал генерації Host DMA переривань */
    uint16_t reserved[4];      /* Резервні поля вирівнювання */
} __attribute__((packed));
```
```cpp
// C++ representation for Stream Parameters configuration
#include <cstdint>

struct alignas(4) StreamParamsConfig {
    IpcCmdHeader hdr;
    std::uint32_t compId{0};
    std::uint32_t bufferFmt{0};
    std::uint32_t frameFmt{0};
    std::uint32_t rate{48000};
    std::uint32_t channels{2};
    std::uint32_t bufferSize{16384};
    std::uint32_t periodSize{4096};
    std::uint32_t sampleContainerBytes{4};
    std::uint32_t hostPeriodBytes{4096};
    std::uint16_t reserved[4]{0};
};
```
:::

У відповідь на команду `SOF_IPC_STREAM_PCM_PARAMS` прошивка SOF заповнює та повертає структуру `sof_ipc_pcm_params_reply`, у якій вказує виділені адреси буферів SRAM у локальному просторі DSP та апаратні параметри зсуву DMA.

### Управління станом потоку (`SOF_IPC_STREAM_TRIG_...`)

Зміна стану потоку (запуск відтворення, зупинка, пауза або відновлення) виконується надсиланням атомарного тригера `struct sof_ipc_stream_trigger`.

Поле `trigger` приймає константи `SOF_IPC_STREAM_TRIG_START`, `SOF_IPC_STREAM_TRIG_STOP`, `SOF_IPC_STREAM_TRIG_PAUSE` або `SOF_IPC_STREAM_TRIG_RELEASE`. Отримавши тригер `START`, прошивка SOF запускає нитку Zephyr RTOS і переводить Host DMA у стан активного зчитування.

:::tabs
```c
/* C structure for Stream Trigger control */
struct sof_ipc_stream_trigger {
    struct sof_ipc_cmd_hdr hdr;
    uint32_t comp_id;          /* Ідентифікатор компонента пайплайна */
    uint32_t trigger;          /* Команда тригера: START / STOP / PAUSE */
} __attribute__((packed));
```
```cpp
// C++ representation for Stream Trigger control
#include <cstdint>

enum class StreamTriggerOp : std::uint32_t {
    Start   = 0,
    Stop    = 1,
    Pause   = 2,
    Release = 3
};

struct alignas(4) StreamTriggerCmd {
    IpcCmdHeader hdr;
    std::uint32_t compId{0};
    StreamTriggerOp trigger{StreamTriggerOp::Start};
};
```
:::

## 2. Протокол IPC v4 (Модульна архітектура Intel / SOF v4)

Починаючи з платформ Intel Meteor Lake та Lunar Lake, SOF застосовує протокол IPC v4. Головна відмінність IPC v4 від IPC v3 полягає у тому, що невеликі керуючі команди взагалі не вимагають запису у пам'ять Mailbox SRAM. Замість цього 64-бітна команда передається безпосередньо через два 32-бітні апаратні регістри контролера Mailbox/Doorbell (`PRIMARY` та `SECONDARY`).

### Бітова структура заголовка IPC v4

1. **Primary Register (Біти 0..31):**
   - **Біти [0..13]**: `Module ID` (Ідентифікатор цільового модуля в прошивці).
   - **Біти [14..21]**: `Instance ID` (Екземпляр модуля в даному пайплайні).
   - **Біти [24..28]**: `Type` (Тип команд: `LARGE_CONFIG_GET`, `LARGE_CONFIG_SET`, `MOD_INIT`, `MOD_DELETE`).
   - **Біт [29]**: `Response Flag` (0 — запит від Host, 1 — відповідь від DSP).
   - **Біт [30]**: `Direction` (0 — Host to DSP, 1 — DSP to Host).
   - **Біт [31]**: `BUSY / Doorbell` (Запис 1 викликає апаратне переривання на DSP).

2. **Secondary Register (Біти 0..31):**
   - **Біти [0..11]**: `Param ID` (Ідентифікатор параметра специфічної конфігурації).
   - **Біти [12..31]**: `Data Size` (Розмір додаткових даних у Mailbox SRAM, якщо розмір перевищує 64 біти).

Для передачі великих масивів даних (наприклад, конфігурації графічних фільтрів еквалайзера або моделі приглушення шуму) IPC v4 надсилає команду `LARGE_CONFIG_SET`. Драйвер ядра копіює дані у Mailbox SRAM сторінками по 4096 байт, після чого тригерує Doorbell.

## 3. Бінарна топологія ALSA (`.tplg`) та вендорні кортежі

Драйвер `snd_sof` не містить жорстко закодованих описувачів графів. Топологія графа завантажується із файлу `.tplg` під час старту пристрою за допомогою виклику `request_firmware()`.

Файл `.tplg` містить три категорії даних:

1. **Стандартні віджети ALSA DAPM**: описують вузли графа (`snd_soc_tplg_dapm_widget`), їх типи (PGA, Mixer, DAI, Effect) та зв'язки між ними (`snd_soc_tplg_dapm_graph_elem`).
2. **Елементи управління ALSA Mixer**: описують слайдери гучності та перемикачі (`snd_soc_tplg_mixer_control`), які з'являються у користувацькому просторі в `alsamixer` чи PipeWire.
3. **Приватні вендорні кортежі (Vendor Tuples)**: масиви байтів `snd_soc_tplg_vendor_array`, які містять спеціальні токени SOF.

### Процес аналізу вендорних кортежів у ядрі Linux

Під час зчитування `.tplg` файлу драйвер ядра викликає функцію `sof_parse_tokens()`. Драйвер сканує масив кортежів `SOF_TPLG_KBOX_...` і перетворює їх на C-структури IPC:

- `SOF_TPLG_KBOX_PIPELINE_ID` -> формує `struct sof_ipc_pipe_new`.
- `SOF_TPLG_KBOX_COMP_TYPE` -> формує `struct sof_ipc_comp_config`.
- `SOF_TPLG_KBOX_BUFFER_SIZE` -> формує `struct sof_ipc_buffer`.

Після того, як драйвер ядра розпакував вендорні кортежі для всіх віджетів, він послідовно відправляють серію IPC-команд `SOF_IPC_TPLG_PIPELINE_NEW` та `SOF_IPC_TPLG_COMP_NEW` на DSP. Прошивка SOF у відповідь створює об'єкти C++ компонентів всередині Zephyr RTOS і виділяє локальну пам'ять під буфери обробки.
