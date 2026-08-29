#include "hw/i2c_bus.hpp"

#include <utility>

#include "hw/clock_gate.hpp"
#include "hw/registers.hpp"
#include "hw/silicon.hpp"

namespace hw {
namespace {

constexpr Hertz bus_hz = 100'000U;             // стандартний режим
constexpr unsigned recovery_pulses = 9U;       // стільки біт лишається у веденого

/* Затримка. Точності тут не потрібно — потрібна гарантія «не швидше за
 * 100 кГц»: ведений на повільній лінії має встигнути відпустити SDA.
 * Тіло циклу — три інструкції на ітерацію; volatile не дає оптимізатору
 * викинути цикл цілком. */
void delay_us(Hertz cpu, std::uint32_t us) noexcept
{
    const std::uint32_t cycles_per_us = (cpu != 0U) ? cpu / 1'000'000U : 16U;
    volatile std::uint32_t iterations = us * cycles_per_us / 3U + 1U;

    while (iterations != 0U) {
        --iterations;
        nop();
    }
}

/* Одна ніжка порту B. Поля MODER, OTYPER, PUPDR і AFR — це та сама матриця
 * мультиплексування, яку Datasheet подає таблицею альтернативних функцій. */
class Pin {
public:
    explicit constexpr Pin(unsigned index) noexcept : index_{index} {}

    void set_mode(std::uint32_t mode) const noexcept
    {
        write_field(gpiob().moder, index_ * 2U, 2U, mode);
    }

    void set_pull(std::uint32_t pull) const noexcept
    {
        write_field(gpiob().pupdr, index_ * 2U, 2U, pull);
    }

    void set_open_drain() const noexcept
    {
        /* Шина монтажна: жоден пристрій не видає одиницю транзистором,
         * високий рівень створює зовнішній підтяжний резистор. */
        gpiob().otyper |= bit(index_);
    }

    void set_alternate(std::uint32_t af) const noexcept
    {
        write_field(gpiob().afr[index_ / 8U], (index_ % 8U) * 4U, 4U, af);
    }

    /* BSRR має тип доступу W1S/W1C: молодша половина слова встановлює ніжку,
     * старша скидає. Одна інструкція STR, жодного read-modify-write — сусідні
     * ніжки порту не можуть постраждати від переривання посеред запису. */
    void write(bool high) const noexcept
    {
        gpiob().bsrr = high ? bit(index_) : bit(index_ + 16U);
    }

    /* Читаємо IDR, а не ODR: цікавить реальний рівень на лінії, який може
     * тримати внизу ведений, а не те, що ми самі туди записали. */
    [[nodiscard]] bool read() const noexcept
    {
        return (gpiob().idr & bit(index_)) != 0U;
    }

private:
    unsigned index_;
};

constexpr Pin scl{i2c1_scl_pin};
constexpr Pin sda{i2c1_sda_pin};

/* Вартовий на час ручного ногодрингу: конструктор забирає ніжки в режим
 * виходу, деструктор повертає їх контролеру I2C. Саме тому нижче можна
 * виходити з функції в будь-якій точці — ніжки повернуться самі, і
 * жодного «не забути відновити» на кожній гілці помилки. */
class ManualPins {
public:
    ManualPins() noexcept
    {
        /* Спершу відпускаємо обидві лінії у високий рівень, аж потім
         * перемикаємо режим: інакше ніжка на мить смикне шину вниз. */
        scl.write(true);
        sda.write(true);
        scl.set_mode(gpio_mode::output);
        sda.set_mode(gpio_mode::output);
    }

    ~ManualPins()
    {
        scl.set_mode(gpio_mode::alternate);
        sda.set_mode(gpio_mode::alternate);
    }

    ManualPins(const ManualPins&) = delete;
    ManualPins& operator=(const ManualPins&) = delete;
};

} // namespace

std::expected<I2cBus, BusError> I2cBus::open(Hertz apb1, Hertz cpu) noexcept
{
    I2cBus bus{apb1, cpu};

    /* Крок 1: тактування порту й самого блоку. */
    clocks::enable_ahb1(rcc_bits::ahb1en_gpiob);
    clocks::enable_apb1(rcc_bits::apb1en_i2c1);

    /* Крок 2: матриця виводів. Тип каскаду й підтяжку задаємо до
     * перемикання в альтернативну функцію. */
    scl.set_open_drain();
    sda.set_open_drain();
    scl.set_pull(gpio_pull::up);
    sda.set_pull(gpio_pull::up);
    scl.set_alternate(i2c1_af);
    sda.set_alternate(i2c1_af);
    scl.set_mode(gpio_mode::alternate);
    sda.set_mode(gpio_mode::alternate);

    if (auto result = bus.configure(); !result) {
        return std::unexpected{result.error()};
    }
    return bus;
}

std::expected<void, BusError> I2cBus::configure() noexcept
{
    const std::uint32_t freq_mhz = apb1_ / 1'000'000U;

    /* RM0090 §27.6.2: поле FREQ дорівнює частоті APB1 у мегагерцах і має
     * лежати в межах 2..50. */
    if (freq_mhz < 2U || freq_mhz > 50U) {
        return std::unexpected{BusError::bad_clock};
    }

    I2cBlock& dev = i2c1();

    /* Крок 3: усе пишеться при вимкненому блоці. */
    dev.cr1 &= ~i2c_bits::cr1_pe;
    dev.cr2 = freq_mhz & i2c_bits::cr2_freq_mask;

    std::uint32_t ccr = apb1_ / (2U * bus_hz);
    if (ccr < 4U) {
        ccr = 4U;  // мінімум, дозволений довідником
    }
    dev.ccr = ccr;
    dev.trise = freq_mhz + 1U;

    /* Аналоговий фільтр — саме той вузол, чий дефект описує еррата.
     * Вимикати його дозволено лише при PE = 0, і робимо це тільки на
     * уражених ревізіях: на виправленому кремнії фільтр корисний. */
    if (silicon::affected(silicon::Erratum::i2c_busy_lock)) {
        dev.fltr |= i2c_bits::fltr_anoff;
    } else {
        dev.fltr &= ~i2c_bits::fltr_anoff;
    }

    dev.cr1 |= i2c_bits::cr1_pe;  // крок 4: активація
    return {};
}

bool I2cBus::busy() const noexcept
{
    return (i2c1().sr2 & i2c_bits::sr2_busy) != 0U;
}

std::expected<void, BusError> I2cBus::recover() noexcept
{
    const std::uint32_t half_period_us = 1'000'000U / bus_hz / 2U;  // 5 мкс
    I2cBlock& dev = i2c1();

    /* 1. Відібрати лінії в завислого автомата: доки PE = 1, блок керує
     *    ніжками через матрицю альтернативних функцій. */
    dev.cr1 &= ~i2c_bits::cr1_pe;

    {
        /* 2. Ручне керування. Вартовий поверне ніжки блоку на виході
         *    з області видимості — на будь-якій гілці, зокрема на помилковій. */
        const ManualPins manual;
        delay_us(cpu_, half_period_us);

        /* 3. SCL унизу, коли її ніхто не тримає, — це вже не еррата, а
         *    замикання чи мертвий ведений: програмного обходу не існує. */
        if (!scl.read()) {
            /* Вартовий поверне ніжки блоку, але PE лишиться нулем:
             * користуватися шиною однаково не можна. */
            return std::unexpected{BusError::scl_stuck_low};
        }

        /* 4. Дев'ять тактів на SCL: ведений, що завис посеред байта,
         *    дорахує свій зсувний регістр і відпустить SDA. Перевіряємо
         *    лінію щотакту — вийти раніше дешевше, ніж дотактувати всі. */
        for (unsigned pulse = 0; pulse < recovery_pulses && !sda.read(); ++pulse) {
            scl.write(false);
            delay_us(cpu_, half_period_us);
            scl.write(true);
            delay_us(cpu_, half_period_us);
        }

        /* 5. Ведений відпустив лінію посеред кадру — ставимо крапку вручну:
         *    STOP це наростання SDA при високій SCL. */
        sda.write(false);
        delay_us(cpu_, half_period_us);
        scl.write(true);
        delay_us(cpu_, half_period_us);
        sda.write(true);
        delay_us(cpu_, half_period_us);

        if (!sda.read()) {
            return std::unexpected{BusError::sda_stuck_low};
        }
    }

    /* 6. Кінцевий автомат блоку так і стоїть у зависі: тактування ліній його
     *    не зрушило. Єдиний шлях — програмне скидання бітом SWRST, який
     *    тримає блок під скиданням, доки його не знято вручну. */
    dev.cr1 |= i2c_bits::cr1_swrst;
    delay_us(cpu_, half_period_us);
    dev.cr1 &= ~i2c_bits::cr1_swrst;
    delay_us(cpu_, half_period_us);

    /* 7. Скидання стерло конфігурацію — набираємо її наново. */
    if (auto result = configure(); !result) {
        return result;
    }

    /* 8. Перевірка, а не віра. */
    if (busy()) {
        return std::unexpected{BusError::still_busy};
    }
    return {};
}

I2cBus::I2cBus(I2cBus&& other) noexcept
    : apb1_{other.apb1_}, cpu_{other.cpu_}, owns_{std::exchange(other.owns_, false)}
{
}

I2cBus& I2cBus::operator=(I2cBus&& other) noexcept
{
    if (this != &other) {
        release();
        apb1_ = other.apb1_;
        cpu_  = other.cpu_;
        owns_ = std::exchange(other.owns_, false);
    }
    return *this;
}

I2cBus::~I2cBus()
{
    release();
}

void I2cBus::release() noexcept
{
    if (!owns_) {
        return;
    }
    owns_ = false;

    i2c1().cr1 &= ~i2c_bits::cr1_pe;
    clocks::disable_apb1(rcc_bits::apb1en_i2c1);
}

} // namespace hw
