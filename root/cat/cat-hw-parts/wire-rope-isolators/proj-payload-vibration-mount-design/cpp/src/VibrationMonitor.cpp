#include "VibrationMonitor.hpp"
#include <iostream>
#include <iomanip>

VibrationMonitor::VibrationMonitor(double max_allowable_g, double resonance_threshold)
    : max_allowable_g_(max_allowable_g), resonance_threshold_(resonance_threshold),
      frame_buffer_(128), payload_buffer_(128) {}

void VibrationMonitor::recordFrameSample(double t_s, double ax, double ay, double az) {
    frame_buffer_.push(t_s, ax, ay, az);
}

void VibrationMonitor::recordPayloadSample(double t_s, double ax, double ay, double az) {
    payload_buffer_.push(t_s, ax, ay, az);
}

HealthStatus VibrationMonitor::evaluateHealth() const noexcept {
    HealthStatus status{};
    status.frame_rms_g = frame_buffer_.calculateRms();
    status.payload_rms_g = payload_buffer_.calculateRms();

    if (status.frame_rms_g > 0.05) {
        status.transmissibility = status.payload_rms_g / status.frame_rms_g;
    } else {
        status.transmissibility = 1.0;
    }

    status.peak_shock_g = payload_buffer_.getPeakMagnitude();
    status.resonance_detected = (status.transmissibility >= resonance_threshold_);
    status.shock_exceeded = (status.peak_shock_g >= max_allowable_g_);
    return status;
}

double VibrationMonitor::calculateLogarithmicDecrement() const noexcept {
    const auto& samples = payload_buffer_.getSamples();
    if (samples.size() < 10) return 0.0;

    // Пошук двох сусідніх піків перехідного коливального процесу
    std::vector<double> peaks;
    for (std::size_t i = 1; i + 1 < samples.size(); ++i) {
        double prev = samples[i - 1].getMagnitude();
        double curr = samples[i].getMagnitude();
        double next = samples[i + 1].getMagnitude();
        if (curr > prev && curr > next && curr > 0.5) {
            peaks.push_back(curr);
        }
    }

    if (peaks.size() >= 2 && peaks[0] > 0.0 && peaks[1] > 0.0) {
        // Логарифмічний декремент delta = ln(A1 / A2)
        return std::log(peaks[0] / peaks[1]);
    }
    return 0.25; // Типове значення декременту для тросово-силіконової пари
}

std::string_view VibrationMonitor::getDiagnosticSummary() const noexcept {
    auto health = evaluateHealth();
    if (health.shock_exceeded) {
        return "[КРИТИЧНО: ПЕРЕВАНТАЖЕННЯ] Ризик руйнування сенсорів або пробивання!";
    }
    if (health.resonance_detected) {
        return "[УВАГА: РЕЗОНАНС] Розмах коливань перевищує поріг стабільності!";
    }
    if (health.transmissibility < 0.60) {
        return "[НОРМА: ЕФЕКТИВНА ІЗОЛЯЦІЯ] Вібрації рами успішно придушуються.";
    }
    return "[НОРМА] Перехідний режим вібронавантаження.";
}

void VibrationMonitor::printTelemetryReport() const {
    auto health = evaluateHealth();
    double delta = calculateLogarithmicDecrement();

    std::cout << "\n====================================================================\n";
    std::cout << "         ПРОТОКОЛ ДІАГНОСТИКИ ВІБРОЗАХИСНОГО ПІДВІСУ (C++17)        \n";
    std::cout << "====================================================================\n";
    std::cout << " СКВ вібрацій рами носія (Frame RMS)    : " << std::fixed << std::setprecision(2) 
              << health.frame_rms_g << " G\n";
    std::cout << " СКВ вібрацій навантаження (Payload RMS) : " << health.payload_rms_g << " G\n";
    std::cout << " Коефіцієнт передатності T (Ratio)       : " << std::setprecision(3) 
              << health.transmissibility << "\n";
    std::cout << " Пікове ударне перевантаження            : " << std::setprecision(1) 
              << health.peak_shock_g << " G (ліміт: " << max_allowable_g_ << " G)\n";
    std::cout << " Логарифмічний декремент згасання delta  : " << std::setprecision(3) << delta << "\n";
    std::cout << " Діагностичний вердикт стану             : " << getDiagnosticSummary() << "\n";
    std::cout << "====================================================================\n";
}
