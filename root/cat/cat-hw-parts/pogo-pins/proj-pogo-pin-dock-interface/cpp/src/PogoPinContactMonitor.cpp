#include "PogoPinContactMonitor.hpp"

#include <iostream>
#include <iomanip>

PogoPinContactMonitor::PogoPinContactMonitor(Config config)
    : config_(config), is_closed_(true), last_transition_time_(Clock::now()) {
    events_.reserve(64);
}

void PogoPinContactMonitor::registerEdge(bool closed, TimePoint now) {
    if (closed == is_closed_) {
        return;
    }

    auto duration = std::chrono::duration_cast<Microseconds>(now - last_transition_time_);

    // Перехід із розімкненого стану (false) у замкнений (true) означає завершення мікророзриву
    if (closed && !is_closed_) {
        if (duration >= config_.min_glitch_duration) {
            events_.push_back({last_transition_time_, duration});
        }
    }

    is_closed_ = closed;
    last_transition_time_ = now;
}

PogoPinContactMonitor::Report PogoPinContactMonitor::finalizeReport(Microseconds total_test_duration) {
    Report report{};
    report.total_glitch_count = events_.size();

    for (const auto& event : events_) {
        report.total_loss_time += event.duration;
        if (event.duration > report.max_glitch_time) {
            report.max_glitch_time = event.duration;
        }
    }

    if (total_test_duration.count() > 0) {
        report.failure_rate_percent = (static_cast<double>(report.total_loss_time.count()) /
                                       static_cast<double>(total_test_duration.count())) * 100.0;
    }

    return report;
}

void PogoPinContactMonitor::printReport(const Report& report) const {
    std::cout << "\n======================================================\n";
    std::cout << "  ЗВІТ СТАБІЛЬНОСТІ КОНТАКТУ POGO PIN (C++ MONITOR)  \n";
    std::cout << "======================================================\n";
    std::cout << " Зафіксовано мікророзривів : " << report.total_glitch_count << "\n";
    std::cout << " Сумарний час втрати зв'язку: " << report.total_loss_time.count() << " мкс\n";
    std::cout << " Максимальна тривалість розриву: " << report.max_glitch_time.count() << " мкс\n";
    std::cout << " Відсоток часу відмови    : " << std::fixed << std::setprecision(4)
              << report.failure_rate_percent << " %\n";
    std::cout << "------------------------------------------------------\n";
    std::cout << " ЕКСПЕРТНА ОЦІНКА ВІБРОСТІЙКОСТІ:\n";

    if (report.total_glitch_count == 0) {
        std::cout << " [ВІДМІННО] Жодного розриву не зафіксовано. Притиск плунжера стабільний.\n";
    } else if (report.failure_rate_percent < 0.05) {
        std::cout << " [ЗАДОВІЛЬНО] Виявлено поодинокі вібраційні мікророзриви.\n"
                  << " Контакт надійний для кіл живлення, але потребує апаратного демпфування для шин даних.\n";
    } else {
        std::cout << " [НЕБЕЗПЕКА] Висока деградація контакту! Ознака сильного фретингу\n"
                  << " або недостатнього попереднього натягу пружини.\n";
    }
    std::cout << "======================================================\n";
}
