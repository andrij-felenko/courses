#include <array>
#include <cstdint>

class PrechargeSequencer {
public:
    enum class State { Idle, Precharge, Run, Fault };
    enum class Fault { None, Timeout, BusLost, Sensor };

    // Межа із залізом — своя реалізація на кожній платі.
    struct Hal {
        virtual void     relayPrecharge(bool on) = 0;   // котушка Kпз
        virtual void     relayMain(bool on)      = 0;   // котушка Kгол
        virtual uint16_t adcReadBus()            = 0;
        virtual uint32_t millis()                = 0;
        virtual void     faultReport(Fault)      {}
        virtual ~Hal() = default;
    };

    explicit PrechargeSequencer(Hal& hal) : hal_(hal) {}

    void  start() { startReq_ = true; }
    void  stop()  { hal_.relayMain(false); hal_.relayPrecharge(false);
                    mainClosed_ = false; state_ = State::Idle; }
    bool  reset() { if (state_ != State::Fault) return false;
                    fault_ = Fault::None; mainClosed_ = false;
                    state_ = State::Idle; return true; }
    State state() const { return state_; }

    // Викликати рівно кожні TICK_ms.
    void tick()
    {
        const uint32_t now  = hal_.millis();
        const uint32_t vbus = filter_.push(adcToBusmV(hal_.adcReadBus()));

        if (vbus > kBusMaxPlausible_mV && state_ != State::Fault) {
            enterFault(Fault::Sensor, now);
            return;
        }

        switch (state_) {
        case State::Idle:
            hal_.relayPrecharge(false);
            hal_.relayMain(false);
            mainClosed_ = false;
            if (startReq_) {
                startReq_ = false;
                hal_.relayPrecharge(true);        // 1) замкнути передзарядне реле
                state_ = State::Precharge; tEnter_ = now;
            }
            break;

        case State::Precharge:
            if (!mainClosed_) {
                if (vbus >= thresholdmV()) {
                    hal_.relayMain(true);         // 2) заряджено -> замкнути головний
                    mainClosed_ = true; tMain_ = now;
                } else if (now - tEnter_ >= kTimeout_ms) {
                    enterFault(Fault::Timeout, now);
                }
            } else if (now - tMain_ >= kSettle_ms) {
                hal_.relayPrecharge(false);       // 3) зняти передзаряд
                state_ = State::Run; tEnter_ = now;
            }
            break;

        case State::Run:
            if (vbus < kBusNominal_mV / 2) enterFault(Fault::BusLost, now);
            break;

        case State::Fault:
            hal_.relayPrecharge(false);
            hal_.relayMain(false);
            break;
        }
    }

private:
    void enterFault(Fault c, uint32_t now)
    {
        hal_.relayMain(false);            // ПЕРШЕ — зняти обидва ключі
        hal_.relayPrecharge(false);
        fault_ = c; state_ = State::Fault; tEnter_ = now;
        hal_.faultReport(c);
    }

    static constexpr uint32_t thresholdmV()
    { return kBusNominal_mV * kTargetPct / 100; }

    static uint32_t adcToBusmV(uint16_t raw)
    {
        const uint32_t uadc = static_cast<uint32_t>(
            static_cast<uint64_t>(raw) * kAdcVref_mV / kAdcFullScale);
        return static_cast<uint32_t>(
            static_cast<uint64_t>(uadc) * (kRtop + kRbot) / kRbot);
    }

    // Компактне ковзне середнє (N — степінь двійки: ділення = зсув).
    template <std::size_t N> struct Moving {
        std::array<uint32_t, N> buf{}; uint32_t sum = 0;
        std::size_t i = 0, fill = 0;
        uint32_t push(uint32_t x) {
            sum -= buf[i]; buf[i] = x; sum += x;
            i = (i + 1) % N; if (fill < N) ++fill;
            return sum / (fill ? fill : 1);
        }
    };

    static constexpr uint32_t kBusNominal_mV     = 400000;
    static constexpr uint32_t kBusMaxPlausible_mV = kBusNominal_mV + kBusNominal_mV / 4;
    static constexpr uint32_t kTargetPct = 95, kTimeout_ms = 500, kSettle_ms = 40;
    static constexpr uint32_t kAdcVref_mV = 3300, kAdcFullScale = 4095;
    static constexpr uint32_t kRtop = 990000, kRbot = 8200;

    Hal&       hal_;
    State      state_     = State::Idle;
    Fault      fault_     = Fault::None;
    Moving<8>  filter_;
    uint32_t   tEnter_ = 0, tMain_ = 0;
    bool       startReq_ = false, mainClosed_ = false;
};
