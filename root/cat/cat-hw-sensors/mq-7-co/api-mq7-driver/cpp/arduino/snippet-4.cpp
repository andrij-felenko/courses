void MQ7Driver::tick(uint32_t currentTimeMs, uint16_t currentAdcRaw) {
    if (state_ == MQ7State::Uninit) return;

    lastTickMs_ = currentTimeMs;
    uint32_t elapsed = currentTimeMs - lastStateChangeMs_;

    if (state_ == MQ7State::HighHeat) {
        if (elapsed >= config_.highHeatMs) {
            // Переключаємо на напругу 1.4 В (~28% ШІМ від 255 = 71)
            analogWrite(config_.pwmPin, 71);
            state_ = MQ7State::LowHeat;
            lastStateChangeMs_ = currentTimeMs;
        }
    } else if (state_ == MQ7State::LowHeat) {
        // Зчитування АЦП за 200 мс до завершення фази 90 секунд
        if (elapsed >= (config_.lowHeatMs - 200) && !dataReady_) {
            rawAdc_ = currentAdcRaw;
            float vOutMv = ((float)rawAdc_ / config_.adcMax) * config_.vRefMv;
            if (vOutMv < 1.0f) vOutMv = 1.0f;
            
            rsKohm_ = config_.rlKohm * (config_.vRefMv - vOutMv) / vOutMv;
            float ratio = rsKohm_ / config_.r0Kohm;
            coPpm_ = 98.53f * powf(ratio, -1.52f);
            dataReady_ = true;
        }

        if (elapsed >= config_.lowHeatMs) {
            // Повернення до фази високого нагріву (100% ШІМ = 255)
            analogWrite(config_.pwmPin, 255);
            state_ = MQ7State::HighHeat;
            lastStateChangeMs_ = currentTimeMs;
            dataReady_ = false;
        }
    }
}

bool MQ7Driver::getPpm(float& ppm) const {
    if (dataReady_) {
        ppm = coPpm_;
        return true;
    }
    return false;
}
