#include "PulloutTestRig.hpp"
#include <iostream>
#include <iomanip>

PulloutTestRig::PulloutTestRig(LoadCell& sensor, std::size_t buffer_size)
    : sensor_(sensor), buffer_capacity_(buffer_size) {}

void PulloutTestRig::startSession() {
    sensor_.tare(10);
    ring_buffer_.clear();
    current_force_n_ = 0.0;
    peak_force_n_ = 0.0;
    yield_force_n_ = 0.0;
    initial_stiffness_ = 0.0;
    state_ = State::ElasticLoading;
    test_finished_ = false;
    start_time_ = std::chrono::steady_clock::now();
}

void PulloutTestRig::update() {
    if (test_finished_) return;

    auto now = std::chrono::steady_clock::now();
    double elapsed_s = std::chrono::duration<double>(now - start_time_).count();

    current_force_n_ = sensor_.readForceNewtons();

    // Оновлення кільцевого буфера вимірювань
    if (ring_buffer_.size() >= buffer_capacity_) {
        ring_buffer_.pop_front();
    }
    ring_buffer_.push_back({elapsed_s, current_force_n_});

    analyzeDynamics(elapsed_s, current_force_n_);
}

void PulloutTestRig::analyzeDynamics(double elapsed_s, double force) {
    if (force > peak_force_n_) {
        peak_force_n_ = force;
    }

    if (ring_buffer_.size() < 4) return;

    // Обчислення поточної похідної dF/dt
    const auto& prev = ring_buffer_[ring_buffer_.size() - 4];
    double dt = elapsed_s - prev.timestamp_s;
    double dF = (dt > 0.0001) ? (force - prev.force_n) / dt : 0.0;

    if (state_ == State::ElasticLoading) {
        if (initial_stiffness_ == 0.0 && force > 50.0) {
            initial_stiffness_ = dF;
        }
        // Якщо темп приросту зусилля спадає більш ніж удвічі — досягнуто межу плинності бобишки
        if (initial_stiffness_ > 0.0 && force > 250.0 && dF < initial_stiffness_ * 0.45) {
            yield_force_n_ = force;
            state_ = State::PlasticYield;
        }
    } else if (state_ == State::PlasticYield) {
        // Зрив різьбової посадки: спад сили нижче 75% від зареєстрованого максимуму
        if (peak_force_n_ > 300.0 && force < peak_force_n_ * 0.75) {
            state_ = State::PulloutFailure;
            test_finished_ = true;
        }
    }

    if (elapsed_s > 6.0) {
        test_finished_ = true;
    }
}

bool PulloutTestRig::isTestFinished() const noexcept {
    return test_finished_;
}

std::string_view PulloutTestRig::getStateName() const noexcept {
    switch (state_) {
        case State::Idle: return "Очікування";
        case State::ElasticLoading: return "Пружне навантаження";
        case State::PlasticYield: return "Пластична плинність бобишки";
        case State::PulloutFailure: return "ЗРИВ ВТУЛКИ (Руйнування посадки)";
        case State::Complete: return "Випробування завершено";
    }
    return "Невідомо";
}

bool PulloutTestRig::passesSpecification(double required_min_force_n) const noexcept {
    return peak_force_n_ >= required_min_force_n;
}

void PulloutTestRig::printReport() const {
    std::cout << "\n====================================================================\n";
    std::cout << "         ПРОТОКОЛ МЕХАНІЧНОГО ВИПРОБУВАННЯ НАРІЗНОЇ ВТУЛКИ          \n";
    std::cout << "====================================================================\n";
    std::cout << " Датчик зусилля                 : " << sensor_.getName() << "\n";
    std::cout << " Зсув тари нуля                 : " << sensor_.getTareOffset() << " відліків АЦП\n";
    std::cout << " Калібрувальний фактор          : " << sensor_.getCountsPerNewton() << " відліків/Н\n";
    std::cout << "--------------------------------------------------------------------\n";
    std::cout << " Межа плинності пластику (Yield): " << std::fixed << std::setprecision(1) << yield_force_n_ << " Н\n";
    std::cout << " Пікове зусилля виривання (Peak): " << std::fixed << std::setprecision(1) << peak_force_n_ << " Н\n";
    std::cout << " Фінальний статус процесу       : " << getStateName() << "\n";
    std::cout << "--------------------------------------------------------------------\n";
    if (passesSpecification(500.0)) {
        std::cout << " ВИСНОВОК: [СЕРТИФІКОВАНО] Міцність запресування відповідає ТУ (> 500 Н).\n";
    } else {
        std::cout << " ВИСНОВОК: [НЕ ВІДПОВІДАЄ] Зрив відбувся до досягнення критичного порогу.\n";
    }
    std::cout << "====================================================================\n";
}
