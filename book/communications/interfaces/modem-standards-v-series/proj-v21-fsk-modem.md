# ⚙️ Реалізація модема V.21 FSK на C та C++

Практична реалізація програмного модема за стандартом ITU-T V.21 базується на фундаментальних принципах цифрової обробки сигналів (DSP — *Digital Signal Processing*). Програмний модем виконує два зворотних завдання: цифровий синтез аналогового звукового сигналу з частотною модуляцією (модулятор FSK) та розпізнавання тональних частот у вхідному звуковому потоці з відновленням початкової послідовності двійкових бітів (демодулятор FSK).

Стандарт ITU-T V.21 визначає дуплексний асинхронний зв'язок на швидкості 300 біт/с. Для забезпечення одночасної передачі й прийому по двох дротах телефонної лінії смуга частот 300–3400 Гц розділяється на два незалежні частотні канали:
- **Канал 1 (Originate / Викликовий):** Біт `1` (Mark) = **980 Гц**, Біт `0` (Space) = **1180 Гц**. Середня частота каналу становить 1080 Гц з девіацією частоти `Δf = ±100 Гц`.
- **Канал 2 (Answer / Відповідний):** Біт `1` (Mark) = **1650 Гц**, Біт `0` (Space) = **1850 Гц**. Середня частота каналу становить 1750 Гц з девіацією частоти `Δf = ±100 Гц`.

Приймач та передавач модема, що ініціює виклик (Originate), працюють на протилежних частотних парах відносно модема, що відповідає на виклик (Answer). Це унеможливлює взаємну перехресну заваду між власним передавачем та власним приймачем на одному пристрої.

## 1. Теоретичні основи цифрового синтезу та демодуляції

### Цифровий керований генератор (NCO — Numerical Control Oscillator)

Для передавача V.21 критичноважливо забезпечити **безперервність фази** (CPFSK — *Continuous Phase Frequency Shift Keying*). Якщо при переключенні частоти між 980 Гц та 1180 Гц фаза синусоїди буде стрибати, у вихідному звуковому сигналі виникнуть високочастотні сплески напруги. Ці сплески розширюють спектр сигналу за межі виділеного каналу та створюють позасмугові завади сусіднім пристроям.

Модулятор використовує фазовий акумулятор `phase_acc`. На кожному відліку часу фаза збільшується на величину кроку `phase_inc`:

```
phase_inc = 2 · π · f_current / Fs    [де Fs = 8000 Гц]
```

Значення відліку обчислюється як `sin(phase_acc)`. Оскільки акумулятор не скидається при зміні переданого біта, підсумкова синусоїда залишається гладкою й неперервною на межах символьних інтервалів.

### Квадратурна кореляційна демодуляція

Приймач повинен визначати, яка з двох частот (Mark чи Space) присутня у вхідному блоці з `N` відліків (`N = Fs / Baud = 8000 / 300 ≈ 26.67` відліків на біт).

Оскільки початкова фаза вхідного сигналу `φ` є невідомою, звичайна скалярна кореляція з синусом може дати нульовий результат, якщо сигнал прийшов у протифазі (`cos(φ) = 0`). Тому приймач застосовує квадратурну кореляцію — підраховує скалярний добуток вхідного сигналу `s[n]` із двома ортогональними гармоніками (`cos` та `sin`) для обох опорних частот:

```
I_mark = ∑ s[n] · cos(2·π · f_mark · n / Fs)    [квадратурна складова I]
Q_mark = ∑ s[n] · sin(2·π · f_mark · n / Fs)    [квадратурна складова Q]

Mag_mark = (I_mark)² + (Q_mark)²                [потужність сигналу на частоті f_mark]
```

Аналогічно обчислюється потужність `Mag_space` для частоти `f_space`. Якщо `Mag_mark > Mag_space`, приймач приймає рішення на користь логічної `1`, інакше — на користь `0`.

### Автоматичне регулювання підсилення (AGC) та детектор несучої (CD)

У реальних телефонних лініях рівень вхідного сигналу може коливатися від `-3 dBm` (на коротких абонентських петлях) до `-43 dBm` (на довгих зашумлених лініях). Для стабільної роботи демодулятора застосовується каскад автоматичного регулювання підсилення (AGC — *Automatic Gain Control*), який нормує середньоквадратичну амплітуду вхідного потоку.

Детектор несучої (Carrier Detect — CD) обчислює сумарну енергію `Mag_total = Mag_mark + Mag_space`. Якщо значення `Mag_total` падає нижче порогового значення шуму протягом понад 10–20 мілісекунд, приймач скидає коло V.24 DCD у пасивний стан, сигналізуючи про втрату зв'язку або розрив телефонного з'єднання.

## 2. Програмна реалізація мовами C та C++

Нижче наведено повний код модулятора та демодулятора V.21 для частоти дискретизації `Fs = 8000 Гц`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define SAMPLE_RATE 8000.0
#define BAUD_RATE   300.0
#define SAMPLES_PER_BIT ((size_t)(SAMPLE_RATE / BAUD_RATE)) // 26 відліків на біт

typedef enum {
    V21_MODE_ORIGINATE, // TX: 980/1180 Гц, RX: 1650/1850 Гц
    V21_MODE_ANSWER     // TX: 1650/1850 Гц, RX: 980/1180 Гц
} V21Mode;

typedef struct {
    V21Mode mode;
    double phase_acc;
    double f_mark;
    double f_space;
} V21Modulator;

typedef struct {
    V21Mode mode;
    double f_mark;
    double f_space;
} V21Demodulator;

void v21_modulator_init(V21Modulator *mod, V21Mode mode) {
    mod->mode = mode;
    mod->phase_acc = 0.0;
    if (mode == V21_MODE_ORIGINATE) {
        mod->f_mark = 980.0;
        mod->f_space = 1180.0;
    } else {
        mod->f_mark = 1650.0;
        mod->f_space = 1850.0;
    }
}

// Модуляція одного біта у масив відліків PCM
void v21_modulate_bit(V21Modulator *mod, uint8_t bit, float *output_samples) {
    double freq = (bit != 0) ? mod->f_mark : mod->f_space;
    double phase_inc = 2.0 * M_PI * freq / SAMPLE_RATE;

    for (size_t i = 0; i < SAMPLES_PER_BIT; i++) {
        output_samples[i] = (float)sin(mod->phase_acc);
        mod->phase_acc += phase_inc;
        if (mod->phase_acc >= 2.0 * M_PI) {
            mod->phase_acc -= 2.0 * M_PI;
        }
    }
}

void v21_demodulator_init(V21Demodulator *demod, V21Mode mode) {
    demod->mode = mode;
    // Приймач працює на протилежній частотній парі відносно передавача
    if (mode == V21_MODE_ORIGINATE) {
        demod->f_mark = 1650.0;
        demod->f_space = 1850.0;
    } else {
        demod->f_mark = 980.0;
        demod->f_space = 1180.0;
    }
}

// Квадратурна демодуляція блоку відліків одного біта
uint8_t v21_demodulate_bit(V21Demodulator *demod, const float *input_samples) {
    double i_mark = 0.0, q_mark = 0.0;
    double i_space = 0.0, q_space = 0.0;

    double omega_mark = 2.0 * M_PI * demod->f_mark / SAMPLE_RATE;
    double omega_space = 2.0 * M_PI * demod->f_space / SAMPLE_RATE;

    for (size_t n = 0; n < SAMPLES_PER_BIT; n++) {
        double sample = (double)input_samples[n];
        
        i_mark += sample * cos(omega_mark * n);
        q_mark += sample * sin(omega_mark * n);

        i_space += sample * cos(omega_space * n);
        q_space += sample * sin(omega_space * n);
    }

    double mag_mark = i_mark * i_mark + q_mark * q_mark;
    double mag_space = i_space * i_space + q_space * q_space;

    return (mag_mark > mag_space) ? 1 : 0;
}

int main(void) {
    V21Modulator mod;
    V21Demodulator demod;

    v21_modulator_init(&mod, V21_MODE_ORIGINATE);
    v21_demodulator_init(&demod, V21_MODE_ANSWER);

    uint8_t test_bits[8] = {1, 0, 1, 1, 0, 0, 1, 0};
    float buffer[SAMPLES_PER_BIT];

    printf("=== V.21 FSK Modem Simulation (C) ===\n");
    printf("Передача 8 бітів на швидкості 300 бод...\n");

    for (int i = 0; i < 8; i++) {
        v21_modulate_bit(&mod, test_bits[i], buffer);
        uint8_t rx_bit = v21_demodulate_bit(&demod, buffer);
        printf("Біт %d: TX = %d -> RX = %d [%s]\n", 
               i, test_bits[i], rx_bit, (test_bits[i] == rx_bit) ? "OK" : "ERROR");
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <complex>
#include <cstdint>
#include <numeric>

class V21Modem {
public:
    enum class Mode {
        Originate, // TX: 980/1180 Hz, RX: 1650/1850 Hz
        Answer     // TX: 1650/1850 Hz, RX: 980/1180 Hz
    };

    static constexpr double SampleRate = 8000.0;
    static constexpr double BaudRate = 300.0;
    static constexpr std::size_t SamplesPerBit = static_cast<std::size_t>(SampleRate / BaudRate);

    explicit V21Modem(Mode mode) : mode_(mode), phase_acc_(0.0) {
        if (mode_ == Mode::Originate) {
            tx_mark_ = 980.0;  tx_space_ = 1180.0;
            rx_mark_ = 1650.0; rx_space_ = 1850.0;
        } else {
            tx_mark_ = 1650.0; tx_space_ = 1850.0;
            rx_mark_ = 980.0;  rx_space_ = 1180.0;
        }
    }

    // Модуляція послідовності бітів у потік PCM-відліків
    [[nodiscard]] std::vector<float> modulate(const std::vector<uint8_t>& bits) {
        std::vector<float> pcm;
        pcm.reserve(bits.size() * SamplesPerBit);

        for (uint8_t bit : bits) {
            double freq = (bit != 0) ? tx_mark_ : tx_space_;
            double phase_inc = 2.0 * M_PI * freq / SampleRate;

            for (std::size_t i = 0; i < SamplesPerBit; ++i) {
                pcm.push_back(static_cast<float>(std::sin(phase_acc_)));
                phase_acc_ += phase_inc;
                if (phase_acc_ >= 2.0 * M_PI) {
                    phase_acc_ -= 2.0 * M_PI;
                }
            }
        }
        return pcm;
    }

    // Квадратурна демодуляція блоку PCM-відліків у біти
    [[nodiscard]] std::vector<uint8_t> demodulate(const std::vector<float>& pcm) const {
        std::size_t num_bits = pcm.size() / SamplesPerBit;
        std::vector<uint8_t> rx_bits;
        rx_bits.reserve(num_bits);

        double omega_mark = 2.0 * M_PI * rx_mark_ / SampleRate;
        double omega_space = 2.0 * M_PI * rx_space_ / SampleRate;

        for (std::size_t b = 0; b < num_bits; ++b) {
            std::complex<double> corr_mark{0.0, 0.0};
            std::complex<double> corr_space{0.0, 0.0};

            std::size_t offset = b * SamplesPerBit;
            for (std::size_t n = 0; n < SamplesPerBit; ++n) {
                double sample = pcm[offset + n];
                corr_mark += sample * std::polar(1.0, omega_mark * n);
                corr_space += sample * std::polar(1.0, omega_space * n);
            }

            rx_bits.push_back((std::norm(corr_mark) > std::norm(corr_space)) ? 1 : 0);
        }
        return rx_bits;
    }

private:
    Mode mode_;
    double phase_acc_;
    double tx_mark_, tx_space_;
    double rx_mark_, rx_space_;
};

int main() {
    V21Modem modem_tx(V21Modem::Mode::Originate);
    V21Modem modem_rx(V21Modem::Mode::Answer);

    const std::vector<uint8_t> tx_bits = {1, 0, 1, 1, 0, 0, 1, 0, 1, 1};

    std::cout << "=== V.21 FSK Modem Simulation (C++17) ===\n";
    std::cout << "Генерація модуляції FSK для " << tx_bits.size() << " бітів...\n";

    // 1. Модуляція
    auto pcm_signal = modem_tx.modulate(tx_bits);
    std::cout << "Згенеровано " << pcm_signal.size() << " відліків PCM.\n";

    // 2. Демодуляція
    auto rx_bits = modem_rx.demodulate(pcm_signal);

    // 3. Перевірка
    std::size_t errors = 0;
    for (std::size_t i = 0; i < tx_bits.size(); ++i) {
        bool match = (tx_bits[i] == rx_bits[i]);
        if (!match) ++errors;
        std::cout << "Біт " << i << ": TX=" << static_cast<int>(tx_bits[i])
                  << " -> RX=" << static_cast<int>(rx_bits[i])
                  << " [" << (match ? "OK" : "ERR") << "]\n";
    }

    std::cout << "Результат: " << (tx_bits.size() - errors) << "/" << tx_bits.size()
              << " бітів прийнято безпомилково.\n";

    return 0;
}
```
:::

## 3. Детальний розбір інженерних рішень

1. **Безперервність фази модулятора (Continuous Phase):** Збереження стану фазового акумулятора `phase_acc_` між викликами методів модуляції забезпечує повну відсутність розривів напруги сигналу FSK на межах символьних інтервалів. Завдяки цьому спектр випромінювання спадає зі швидкістю `1/f²`, мінімізуючи витік потужності в сусідній частотний канал.
2. **Застосування `std::polar` у C++:** Використання комплексного числа `std::polar(1.0, omega * n)` у вкладці C++ є виключно прозорим і точно відповідає математичній формулі обчислення комплексної експоненти `e^(j·ω·n)`. Виклики `std::norm()` повертають квадрат квадратурної амплітуди `I² + Q²`, що позбавляє від обчислення трудомісткого квадратного кореня `sqrt()`.
3. **Полосова фільтрація у реальних мобільних демодуляторах:** У реальних комерційних модемах V.21 перед квадратурним демодулятором обов'язково встановлюється цифровий смуговий фільтр Баттерворта або Чебишева (Bandpass IIR/FIR filter). Фільтр першого каналу відсікає гармоніки 1650/1850 Гц від власного локального передавача, які можуть бути на 30–40 дБ потужнішими за слабкий прийомний сигнал віддаленої станції.
4. **Відновлення бітової синхронізації (Bit Clock Recovery):** Наведений приклад припускає ідеальну фреймову синхронізацію по межах символів. У реальних реалізаціях демодулятор містить цифрову систему фазового автопідлаштування тактів (DPLL — *Digital Phase-Locked Loop*). DPLL відстежує моменти переходу сигналу через нуль (Zero-Crossing Detection) і підлаштовує розмір інтеграційного вікна так, щоб скалярний добуток обчислювався строго по центру символьного інтервалу, подалі від фазових перехідних процесів на межах бітів.
5. **Алгоритм Герцеля (Goertzel Algorithm) як альтернатива:** При обмежених обчислювальних ресурсах мікроконтролера (наприклад, 8-бітного AVR чи Cortex-M0) квадратурну кореляцію часто замінюють алгоритмом Герцеля. Він обчислює потужність однієї спектральної гармоніки через рекурсивний резонаторний фільтр другого порядку, вимагаючи лише одне множення та два додавання на кожен вхідний відлік звуку.
