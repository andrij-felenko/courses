#include <iostream>
#include <memory>
#include <chrono>
#include <string_view>

class DataPipeline {
public:
    virtual ~DataPipeline() = default;

    // Каркасний невіртуальний метод (NVI): задає незмінний порядок
    void execute_pipeline(std::string_view raw_payload) {
        std::cout << ">>> Початок обробки транзакції\n";
        auto start = std::chrono::steady_clock::now();

        // Крок 1: обов'язкова перевірка інваріанта
        if (raw_payload.empty()) {
            throw std::invalid_argument("Порожнє корисне навантаження");
        }

        // Крок 2: делегування специфічного кроку нащадку
        parse_and_transform(raw_payload);

        // Крок 3: опціональний гачок (hook)
        if (should_audit()) {
            record_audit_log();
        }

        auto end = std::chrono::steady_clock::now();
        std::cout << "<<< Завершено за "
                  << std::chrono::duration_cast<std::chrono::microseconds>(end - start).count()
                  << " мкс\n";
    }

private:
    // Чистий віртуальний метод: нащадок ЗОБОВ'ЯЗАНИЙ надати синтаксичний аналіз
    virtual void parse_and_transform(std::string_view payload) = 0;

    // Віртуальний гачок із типовою поведінкою: нащадок МОЖЕ змінити за потреби
    virtual bool should_audit() const {
        return true;
    }

    void record_audit_log() {
        std::cout << "[AUDIT]: Запис успішно збережено в журнал\n";
    }
};

class JsonPipeline final : public DataPipeline {
private:
    void parse_and_transform(std::string_view payload) override {
        std::cout << "  Парсинг JSON-дерева: " << payload << "\n";
    }

    bool should_audit() const override {
        return false; // Вимикаємо аудит для високошвидкісного JSON
    }
};
