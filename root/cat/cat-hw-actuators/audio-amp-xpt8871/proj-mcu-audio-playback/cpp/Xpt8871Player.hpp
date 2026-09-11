#pragma once

#include <algorithm>
#include <array>
#include <cstddef>
#include <cstdint>
#include <span>

// Клас аудіопрогравача для керування монофонічним підсилювачем XPT8871 (5 Вт).
// Забезпечує подвійну буферизацію (ping-pong), неблокувальну чергу сповіщень,
// усунення паразитних клацань (anti-pop) та автоматичне засинання мікросхеми через лінію SHDN.
class Xpt8871Player {
public:
    // Розмір половини подвійного буфера у вибірках (128 вибірок = 8 мс при 16 кГц)
    static constexpr size_t BUFFER_SIZE = 128;

    // Максимальна кількість аудіосповіщень у черзі
    static constexpr size_t QUEUE_CAPACITY = 8;

    // Кількість вибірок для програмного плавного наростання/згасання (anti-pop ramp)
    static constexpr size_t FADE_SAMPLES = 32;

    // Стан кінцевого автомата програвача
    enum class State : uint8_t {
        Idle,            // Підсилювач вимкнено (SHDN = LOW), споживання струму менше 1 мкА
        PoweringUp,      // SHDN = HIGH, триває заряд конденсатора BYP (стабілізація VDD/2)
        Playing,         // Активне відтворення: почергова трансляція пінг-понг буферів через DMA
        StandbyPending   // Очікування нових звуків перед автоматичним переходом у режим сну
    };

    // Опис елемента черги аудіосповіщень
    struct SoundClip {
        uint16_t id{0};                         // Ідентифікатор звукової події
        std::span<const int16_t> samples{};     // Вказівник на PCM-дані (16-бітні вибірки)
        size_t playbackOffset{0};               // Поточний зсув зчитування вибірок
    };

    // Апаратні зворотні виклики (HAL) для взаємодії з периферією мікроконтролера
    struct HardwareCallbacks {
        void (*setShutdownPin)(bool enable){nullptr};              // Керування лінією SHDN (true = увімкнено)
        void (*transmitDma)(std::span<const int16_t> buffer){nullptr}; // Запуск апаратної передачі блоку даних через DMA
        bool (*isDmaBusy)(){nullptr};                              // Перевірка зайнятості каналу DMA
        uint32_t (*getMillis)(){nullptr};                          // Отримання поточного системного часу в мс
    };

    // Параметри часових інтервалів підсилювача
    struct Config {
        uint32_t stabilizationDelayMs{60}; // Час заряду конденсатора виводу BYP (40-80 мс усувають DC-клацання)
        uint32_t autoSleepDelayMs{500};     // Час очікування після завершення аудіо перед вимкненням SHDN
    };

    // Ініціалізація програвача з прив'язкою до апаратних функцій та налаштувань
    explicit Xpt8871Player(HardwareCallbacks callbacks, Config config = {});

    // Деструктор (RAII): гарантує надійне вимкнення підсилювача при знищенні об'єкта
    ~Xpt8871Player();

    // Заборона копіювання: об'єкт безпосередньо керує фізичним апаратним ресурсом
    Xpt8871Player(const Xpt8871Player&) = delete;
    Xpt8871Player& operator=(const Xpt8871Player&) = delete;

    // Дозволено переміщення
    Xpt8871Player(Xpt8871Player&&) noexcept = default;
    Xpt8871Player& operator=(Xpt8871Player&&) noexcept = default;

    // Додавання звукового фрагмента в неблокувальну чергу відтворення.
    // Повертає true у разі успішного розміщення або false, якщо черга переповнена чи дані порожні.
    bool enqueue(std::span<const int16_t> samples, uint16_t id = 0);

    // Періодичний диспетчер станів: викликається у головному циклі (не блокує виконання)
    void update();

    // Примусова зупинка відтворення, очищення черги та вимкнення живлення підсилювача
    void stop();

    // Очищення черги очікування без негайного переривання поточного звукового буфера
    void clearQueue();

    // Інформаційні методи стану
    [[nodiscard]] State getState() const noexcept { return state_; }
    [[nodiscard]] bool isPlaying() const noexcept { return state_ == State::Playing; }
    [[nodiscard]] bool isQueueEmpty() const noexcept { return queueCount_ == 0; }
    [[nodiscard]] bool isQueueFull() const noexcept { return queueCount_ >= QUEUE_CAPACITY; }
    [[nodiscard]] size_t getQueuedCount() const noexcept { return queueCount_; }

private:
    // Керування живленням мікросхеми XPT8871
    void wakeUp();
    void powerDown();

    // Робота з аудіопотоком та пінг-понг буферизацією
    void startPlayback();
    void processPlayingState();
    size_t fillBuffer(std::span<int16_t> dest);
    void applySoftFade(std::span<int16_t> buffer, size_t count, bool fadeIn);

    HardwareCallbacks hw_{};
    Config config_{};
    State state_{State::Idle};
    uint32_t stateTimestamp_{0};

    // Подвійний буфер (ping-pong): поки один передається через DMA, інший наповнюється ЦП
    std::array<std::array<int16_t, BUFFER_SIZE>, 2> pingPongBuffers_{};
    std::array<bool, 2> bufferHasAudio_{false, false};
    size_t activeDmaBuffer_{0};

    // Кільцева статична черга аудіосповіщень (без динамічного виділення пам'яті в купі)
    std::array<SoundClip, QUEUE_CAPACITY> queue_{};
    size_t queueHead_{0};
    size_t queueTail_{0};
    size_t queueCount_{0};
};
