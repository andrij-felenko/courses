# ⚙️ Емуляція обробки PCM потоку та IPC зв'язку з SOF DSP

Ця вставка містить практичну емуляцію взаємодії між драйвером ядра Linux та цифровим сигнальним процесором Sound Open Firmware. Приклад наочно показує, як у ядрі будується конфігурація PCM-потоку, як кодуються та надсилаються IPC-повідомлення через область розділюваної пам'яті Mailbox SRAM, а також як обслуговується кільцевий буфер (Ring Buffer) під час відтворення аудіо.

## 1. Механізм обміну даними та синхронізація кільцевого буфера

У реальних аудіосистемах передача даних між програмами користувацького простору (PipeWire, PulseAudio) та апаратним DSP проходит через два рівні пам'яті:

1. **Системний Ring Buffer у Host DRAM**: фізично неперервна ділянка пам'яті, виділена ядрам Linux за допомогою `dma_alloc_coherent()`. Користувацькі програми записують сюди аудіосемпли за допомогою системного виклику `writei()`.
2. **Локальні буфери DSP у SRAM**: внутрішня пам'ять сигнального процесора, куди контролер Host DMA перекачує семпли за безпосередніми вказівками прошивки SOF.

Для координації роботи ядро та DSP спілкуються через двосторонні повідомлення **IPC (Inter-Process Communication)**. Коли ядро бажає налаштувати потік, воно пакує заголовок `sof_ipc_stream_params`, записує його у пам'ять Mailbox SRAM та встановлює біт в апаратному регістрі Doorbell. Це викликає апаратне переривання на DSP. Отримавши переривання, прошивка SOF зчитує команду з Mailbox SRAM, налаштовує нитки Zephyr RTOS і надсилає підтвердження (ACK) зворотним дзвінком у Doorbell ядра Linux.

Оскільки операції з кільцевим буфером відбуваються паралельно (Host CPU пише дані на поточну позицію `host_ptr`, а DSP DMA читає дані з позиції `dsp_ptr`), кодуванню подібних систем притаманна необхідність суворого дотримання бар'єрів пам'яті та правильного розрахунку залишку вільного місця у буфері.

У разі когерентного DMA виділення системної пам'яті ядро Linux застосовує макроси `smp_wmb()` (Write Memory Barrier) перед встановленням біта в регістрі Doorbell. Це гарантує, що всі записи у Mailbox SRAM потраплять із кєш-ліній CPU до фізичних комірок пам'яті раніше, ніж DSP перехопить апаратне переривання.

## 2. Аналіз алгоритму заповнення кільцевого буфера

Функція `sof_pcm_write_samples()` демонструє обробку циклічного зсуву в кільцевому буфері. Запис даних розбивається на два сценарії:

- **Лінійний запис (без переходу через межу)**: якщо обсяг нових семплів `count` не перевищує залишок вільного місця від поточного `host_ptr` до кінця буфера `dma_bytes`, дані копіюються одним суцільним блоком `memcpy()`.
- **Запис із розбиттям (wrap-around)**: якщо нові семпли перетинають фізичну межу буфера, копіювання розбивається на дві фази. Перша фаза заповнює вільну ділянку до кінця масиву (`chunk = dma_bytes - host_ptr`), а друга фаза копіює залишок семплів (`remainder = count - chunk`), починаючи з нульового індексу буфера.

Такий підхід запобігає виходу за межі пам'яті без необхідності постійного перевиділення буферів під час відтворення потокового звуку.

## 3. Порівняння реалізацій мовами C та C++

Наведені нижче вкладки демонструють два підходи до проектування емулятора IPC-зв'язку та керування PCM-потоками:

- **Вкладка C**: показує низькорівневий підхід, аналогічний C-коду ядра Linux (`sound/soc/sof/`). Вона використовує ручне управління пам'яттю (`malloc`/`free`), яві покажчики, вирівнювання структур атрибутом `__attribute__((packed))` та явну перевірку числових кодів помилок.
- **Вкладка C++**: показує ідіоматичний об'єктно-орієнтований підхід для емуляційних утиліт користувацького простору чи юніт-тестів. Вона застосовує принципи **RAII** для автоматичного звільнення ресурсів буфера у деструкторі, безпечний тип `std::span` для передачі зрізів пам'яті без копіювання, константні вирази `constexpr` та суворо типізовані перелічення `enum class`.

:::tabs
```c
/* C implementation of SOF IPC stream emulator */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define SOF_IPC_STREAM_PCM_PARAMS 0x0001
#define SOF_IPC_STREAM_TRIG_START 0x0002
#define SOF_IPC_STREAM_TRIG_STOP  0x0003

struct sof_ipc_cmd_hdr {
    uint32_t size;
    uint32_t cmd;
} __attribute__((packed));

struct sof_ipc_stream_params {
    struct sof_ipc_cmd_hdr hdr;
    uint32_t comp_id;
    uint32_t rate;
    uint32_t channels;
    uint32_t buffer_size;
    uint32_t period_size;
} __attribute__((packed));

struct sof_dsp_ipc_mailbox {
    uint8_t sram_buffer[1024];
    uint32_t doorbell_host_to_dsp;
    uint32_t doorbell_dsp_to_host;
};

struct sof_pcm_stream {
    uint32_t stream_id;
    uint8_t *dma_area;
    size_t dma_bytes;
    size_t period_bytes;
    size_t host_ptr;
    struct sof_dsp_ipc_mailbox *mailbox;
};

int sof_ipc_send_message(struct sof_dsp_ipc_mailbox *mb, const void *msg, size_t msg_len) {
    if (msg_len > sizeof(mb->sram_buffer)) {
        return -1;
    }
    /* Копіювання команди у SRAM Mailbox та дзвінок у Doorbell */
    memcpy(mb->sram_buffer, msg, msg_len);
    mb->doorbell_host_to_dsp = 1;
    
    /* Імітація обробки команди на боці DSP та відповіді */
    mb->doorbell_host_to_dsp = 0;
    mb->doorbell_dsp_to_host = 1;
    return 0;
}

struct sof_pcm_stream *sof_pcm_create(struct sof_dsp_ipc_mailbox *mb, uint32_t rate, uint32_t channels) {
    struct sof_pcm_stream *stream = (struct sof_pcm_stream *)malloc(sizeof(struct sof_pcm_stream));
    if (!stream) return NULL;

    stream->stream_id = 1;
    stream->period_bytes = 4096;
    stream->dma_bytes = stream->period_bytes * 4;
    stream->dma_area = (uint8_t *)calloc(1, stream->dma_bytes);
    if (!stream->dma_area) {
        free(stream);
        return NULL;
    }
    stream->host_ptr = 0;
    stream->mailbox = mb;

    struct sof_ipc_stream_params params;
    memset(&params, 0, sizeof(params));
    params.hdr.size = sizeof(params);
    params.hdr.cmd = SOF_IPC_STREAM_PCM_PARAMS;
    params.comp_id = stream->stream_id;
    params.rate = rate;
    params.channels = channels;
    params.buffer_size = (uint32_t)stream->dma_bytes;
    params.period_size = (uint32_t)stream->period_bytes;

    if (sof_ipc_send_message(mb, &params, sizeof(params)) != 0) {
        free(stream->dma_area);
        free(stream);
        return NULL;
    }

    printf("[SOF C] Stream %u configured: %u Hz, %u ch, buffer %zu B\n",
           stream->stream_id, rate, channels, stream->dma_bytes);
    return stream;
}

void sof_pcm_write_samples(struct sof_pcm_stream *stream, const uint8_t *data, size_t count) {
    if (!stream || !data) return;
    
    size_t space = stream->dma_bytes - stream->host_ptr;
    size_t chunk = (count < space) ? count : space;
    
    memcpy(stream->dma_area + stream->host_ptr, data, chunk);
    stream->host_ptr = (stream->host_ptr + chunk) % stream->dma_bytes;
    
    if (count > chunk) {
        size_t remainder = count - chunk;
        memcpy(stream->dma_area, data + chunk, remainder);
        stream->host_ptr = remainder;
    }
}

void sof_pcm_destroy(struct sof_pcm_stream *stream) {
    if (!stream) return;
    free(stream->dma_area);
    free(stream);
}
```
```cpp
// C++ implementation of SOF IPC stream emulator using RAII and std::span
#include <iostream>
#include <vector>
#include <memory>
#include <span>
#include <array>
#include <system_error>
#include <algorithm>
#include <cstring>

namespace sof {

enum class IpcCmd : uint32_t {
    StreamParams = 0x0001,
    StreamTriggerStart = 0x0002,
    StreamTriggerStop = 0x0003
};

struct alignas(4) IpcHeader {
    uint32_t size;
    uint32_t cmd;
};

struct alignas(4) StreamParamsMsg {
    IpcHeader hdr;
    uint32_t comp_id;
    uint32_t rate;
    uint32_t channels;
    uint32_t buffer_size;
    uint32_t period_size;
};

class DspMailbox {
public:
    static constexpr size_t SRAM_SIZE = 1024;

    bool sendMessage(std::span<const uint8_t> msg) {
        if (msg.size() > SRAM_SIZE) {
            return false;
        }
        std::copy(msg.begin(), msg.end(), m_sram.begin());
        m_doorbellHostToDsp = true;
        // Mock DSP acknowledgement
        m_doorbellHostToDsp = false;
        m_doorbellDspToHost = true;
        return true;
    }

private:
    std::array<uint8_t, SRAM_SIZE> m_sram{};
    bool m_doorbellHostToDsp{false};
    bool m_doorbellDspToHost{false};
};

class PcmStream {
public:
    PcmStream(std::shared_ptr<DspMailbox> mailbox, uint32_t rate, uint32_t channels)
        : m_mailbox(std::move(mailbox)), m_periodBytes(4096), m_dmaBuffer(m_periodBytes * 4, 0)
    {
        StreamParamsMsg msg{};
        msg.hdr.size = sizeof(StreamParamsMsg);
        msg.hdr.cmd = static_cast<uint32_t>(IpcCmd::StreamParams);
        msg.comp_id = 1;
        msg.rate = rate;
        msg.channels = channels;
        msg.buffer_size = static_cast<uint32_t>(m_dmaBuffer.size());
        msg.period_size = static_cast<uint32_t>(m_periodBytes);

        auto bytesSpan = std::span<const uint8_t>(
            reinterpret_cast<const uint8_t*>(&msg), sizeof(msg));

        if (!m_mailbox->sendMessage(bytesSpan)) {
            throw std::runtime_error("Failed to send IPC StreamParams to DSP Mailbox");
        }

        std::cout << "[SOF C++] Stream configured: " << rate << " Hz, "
                  << channels << " ch, buffer " << m_dmaBuffer.size() << " B\n";
    }

    ~PcmStream() {
        std::cout << "[SOF C++] Stream destroyed, resources freed via RAII.\n";
    }

    void writePcmData(std::span<const uint8_t> samples) {
        size_t available = m_dmaBuffer.size() - m_hostPtr;
        size_t toWrite = std::min(samples.size(), available);
        
        std::copy_n(samples.begin(), toWrite, m_dmaBuffer.begin() + m_hostPtr);
        m_hostPtr = (m_hostPtr + toWrite) % m_dmaBuffer.size();

        if (samples.size() > toWrite) {
            size_t remainder = samples.size() - toWrite;
            std::copy_n(samples.begin() + toWrite, remainder, m_dmaBuffer.begin());
            m_hostPtr = remainder;
        }
    }

    [[nodiscard]] size_t getHostPointer() const noexcept {
        return m_hostPtr;
    }

private:
    std::shared_ptr<DspMailbox> m_mailbox;
    size_t m_periodBytes;
    std::vector<uint8_t> m_dmaBuffer;
    size_t m_hostPtr{0};
};

} // namespace sof
```
:::

## 4. Переваги типу `std::span` та принципу RAII в C++ реалізації

У версії мовою C++ виділення буфера та керування пам'яттю Mailbox винесено у стандартні контейнери `std::vector` та `std::array`. Це дає суттєві переваги в надійності:

1. **Відсутність витоків пам'яті (Memory Leak Safety)**: конструктор `PcmStream` запитує ресурси, а деструктор `~PcmStream()` звільняє їх автоматично при виході з області видимості. Якщо надсилання IPC повертає помилку, виняток `std::runtime_error` розгортає стек, очищаючи вектор `m_dmaBuffer` без потреби в явних викликах `free()` у гілках `goto out`.
2. **Типобезпека без копіювання з `std::span`**: метод `writePcmData` приймає `std::span<const uint8_t>`. Це дозволяє передавати масиви семплів із будь-яких джерел (вектори, сирі буфери, сталі масиви) без створення тимчасових копій у пам'яті DRAM і без передачі покажчика та довжини двома окремими аргументами.
3. **Безпека відходів за межі (Bounds Checking)**: алгоритм `std::copy_n` разом із розміром `m_dmaBuffer.size()` унеможливлює випадкове перезаписування чужих ділянок системної пам'яті.

## 5. Крайові випадки та обробка спустошення буфера (Buffer Underrun)

У реальній роботі аудіодрайверів часто виникають крайові ситуації, які вимагають обережної обробки у коді:

1. **Спустошення буфера (Underrun / Xrun)**:
   Якщо програма користувацького простору затрималася через високе завантаження CPU і не встигла викликати `writei()` до того, як DSP DMA прочитав останній доступний період, позиції `host_ptr` та `dsp_ptr` збігаються. У цьому випадку DSP призупиняє Host DMA і надсилає на ядро IPC-сповіщення `SOF_IPC_STREAM_XRUN`. Драйвер ядра повертає помилку `-EPIPE` під час наступного виклику ALSA API, вимагаючи від програми повторного виклику `snd_pcm_prepare()`.

2. **Зависання шини або IPC Timeout**:
   Якщо апаратна шина PCIe або I2C зависає і DSP не скидає біт `Doorbell`, функція надсилання IPC у драйвері ядра (наприклад, `sof_ipc_tx_message()`) тайм-аутить через 500 мс. У C-реалізації це вимагає очищення локальних ресурсів та переініціалізації апаратури, а в C++ реалізації — викиду винятку `std::runtime_error` або повернення об'єкта `std::expected<void, std::error_code>`.
