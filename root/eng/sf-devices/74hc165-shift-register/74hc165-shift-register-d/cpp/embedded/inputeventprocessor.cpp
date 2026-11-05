#include <cstdint>
#include <array>
#include <functional>

template <std::size_t PinCount>
class InputEventProcessor {
public:
    enum class EventType {
        None,
        Pressed,
        Released
    };

    using EventCallback = std::function<void(std::size_t pinIndex, EventType type)>;

    explicit InputEventProcessor(EventCallback cb = nullptr)
        : m_callback(cb) {
        m_history.fill(0xFF);
        m_filteredState.fill(true);
        m_previousState.fill(true);
    }

    // Обробка сирих даних вибірки (кожен біт — стан одного входу)
    void processRawInputs(const std::array<uint8_t, PinCount / 8>& rawBytes) {
        for (std::size_t pin = 0; pin < PinCount; ++pin) {
            std::size_t byteIdx = pin / 8;
            std::size_t bitIdx = pin % 8;
            bool rawSample = (rawBytes[byteIdx] & (1U << bitIdx)) != 0;

            // Накопичення вибірки у 8-бітному вікні
            m_history[pin] = static_cast<uint8_t>((m_history[pin] << 1) | (rawSample ? 1U : 0U));

            if (m_history[pin] == 0xFF) {
                m_filteredState[pin] = true;
            } else if (m_history[pin] == 0x00) {
                m_filteredState[pin] = false;
            }

            // Детекція зміни стану та виклики колбеків
            if (m_filteredState[pin] != m_previousState[pin]) {
                EventType evt = m_filteredState[pin] ? EventType::Released : EventType::Pressed;
                if (m_callback) {
                    m_callback(pin, evt);
                }
                m_previousState[pin] = m_filteredState[pin];
            }
        }
    }

    bool getState(std::size_t pinIndex) const {
        if (pinIndex >= PinCount) return true;
        return m_filteredState[pinIndex];
    }

private:
    std::array<uint8_t, PinCount> m_history;
    std::array<bool, PinCount> m_filteredState;
    std::array<bool, PinCount> m_previousState;
    EventCallback m_callback;
};
