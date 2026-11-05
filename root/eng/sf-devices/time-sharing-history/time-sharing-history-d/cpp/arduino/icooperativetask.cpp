#include <Arduino.h>
#include <cstdint>

// Базовий інтерфейс кооперативного автомата стану (Coroutine / Task)
class ICooperativeTask {
public:
    virtual ~ICooperativeTask() = default;
    virtual void RunStep() = 0; // Добровільний крок виконання без блокування
};

class SensorTask : public ICooperativeTask {
public:
    void RunStep() override {
        switch (state_) {
            case State::kReadAdc:
                raw_adc_ = analogRead(A0);
                state_ = State::kProcess;
                break; // Завершення кроку — добровільна віддача
            case State::kProcess:
                filtered_ = raw_adc_ * 0.1f + filtered_ * 0.9f;
                state_ = State::kReadAdc;
                break;
        }
    }

private:
    enum class State { kReadAdc, kProcess };
    State state_{State::kReadAdc};
    uint16_t raw_adc_{0};
    float filtered_{0.0f};
};

class CooperativeScheduler {
public:
    void AddTask(ICooperativeTask* task) {
        if (task_count_ < kMaxTasks) {
            tasks_[task_count_++] = task;
        }
    }

    void Dispatch() {
        for (uint8_t i = 0; i < task_count_; ++i) {
            if (tasks_[i] != nullptr) {
                tasks_[i]->RunStep(); // Викликаємо по одному кроку кожної задачі
            }
        }
    }

private:
    static constexpr uint8_t kMaxTasks = 4;
    ICooperativeTask* tasks_[kMaxTasks]{nullptr};
    uint8_t task_count_{0};
};

SensorTask g_sensor_task;
CooperativeScheduler g_scheduler;

void setup() {
    g_scheduler.AddTask(&g_sensor_task);
}

void loop() {
    g_scheduler.Dispatch(); // Неблокувальний цикл кооперативного планувальника
}
