#include "RotarySelector.h"

// Таблиця цільових значень АЦП для 12 позицій резистивного дільника (12-біт АЦП)
static const uint16_t ADC_POSITION_TARGETS[12] = {
    310,   620,   930,  1240,  1550,  1860,
   2170,  2480,  2790,  3100,  3410,  3720
};

RotarySelector::RotarySelector(uint8_t adcPin, uint32_t debounceMs)
    : m_adcPin(adcPin),
      m_debounceMs(debounceMs),
      m_callback(nullptr),
      m_filterIdx(0),
      m_bufferFull(false),
      m_confirmedPosition(0),
      m_pendingPosition(0),
      m_debounceStartTime(0),
      m_status(SelectorStatus::OK)
{
    for (uint8_t i = 0; i < MEDIAN_WINDOW; ++i) {
        m_filterWindow[i] = 0;
    }
}

void RotarySelector::setCallback(EventCallback callback) {
    m_callback = callback;
}

uint16_t RotarySelector::applyMedianFilter(uint16_t sample) {
    m_filterWindow[m_filterIdx] = sample;
    m_filterIdx = (m_filterIdx + 1) % MEDIAN_WINDOW;
    if (m_filterIdx == 0) {
        m_bufferFull = true;
    }

    uint8_t count = m_bufferFull ? MEDIAN_WINDOW : m_filterIdx;
    if (count == 0) return sample;

    uint16_t temp[MEDIAN_WINDOW];
    for (uint8_t i = 0; i < count; ++i) {
        temp[i] = m_filterWindow[i];
    }

    for (uint8_t i = 0; i < count - 1; ++i) {
        for (uint8_t j = 0; j < count - i - 1; ++j) {
            if (temp[j] > temp[j + 1]) {
                uint16_t t = temp[j];
                temp[j] = temp[j + 1];
                temp[j + 1] = t;
            }
        }
    }

    return temp[count / 2];
}

uint8_t RotarySelector::decodeAdcToPosition(uint16_t adcVal, SelectorStatus& statusOut) const {
    if (adcVal < 100) {
        statusOut = SelectorStatus::FAULT_SHORT_CIRCUIT;
        return 0;
    }
    if (adcVal > 3950) {
        statusOut = SelectorStatus::FAULT_OPEN_CIRCUIT;
        return 0;
    }

    statusOut = SelectorStatus::OK;

    for (uint8_t pos = 1; pos <= NUM_POSITIONS; ++pos) {
        uint16_t target = ADC_POSITION_TARGETS[pos - 1];
        uint16_t lowBound = (target > 150) ? (target - 150) : 0;
        uint16_t highBound = target + 150;

        if (pos == m_confirmedPosition) {
            lowBound = (lowBound > HYSTERESIS_ADC) ? (lowBound - HYSTERESIS_ADC) : 0;
            highBound += HYSTERESIS_ADC;
        }

        if (adcVal >= lowBound && adcVal <= highBound) {
            return pos;
        }
    }

    statusOut = SelectorStatus::DEBOUNCING;
    return m_pendingPosition;
}

void RotarySelector::update(uint32_t currentMs, uint16_t rawAdcValue) {
    uint16_t filteredAdc = applyMedianFilter(rawAdcValue);

    SelectorStatus currentStatus = SelectorStatus::OK;
    uint8_t detectedPos = decodeAdcToPosition(filteredAdc, currentStatus);

    if (currentStatus == SelectorStatus::FAULT_OPEN_CIRCUIT ||
        currentStatus == SelectorStatus::FAULT_SHORT_CIRCUIT) {
        if (m_status != currentStatus) {
            m_status = currentStatus;
            m_confirmedPosition = 0;
            if (m_callback) {
                SelectorEvent ev = { 0, filteredAdc, m_status };
                m_callback(ev);
            }
        }
        return;
    }

    if (detectedPos != m_pendingPosition) {
        m_pendingPosition = detectedPos;
        m_debounceStartTime = currentMs;
        m_status = SelectorStatus::DEBOUNCING;
    } else if (m_pendingPosition != m_confirmedPosition && m_pendingPosition != 0) {
        if (currentMs - m_debounceStartTime >= m_debounceMs) {
            m_confirmedPosition = m_pendingPosition;
            m_status = SelectorStatus::OK;

            if (m_callback) {
                SelectorEvent ev = { m_confirmedPosition, filteredAdc, m_status };
                m_callback(ev);
            }
        }
    }
}
