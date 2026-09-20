#include "temperature_core.hpp"
#include "http_controller.hpp"
#include "cli_adapter.hpp"
#include "queue_worker.hpp"

#include <iostream>
#include <memory>
#include <string>
#include <vector>

// ============================================================================
// ДЕМОНСТРАЦІЙНИЙ ЧЕТВЕРТИЙ АДАПТЕР (OPEN-CLOSED PRINCIPLE)
// ============================================================================

/// @brief Демонстраційний четвертий адаптер за розкладом (SchedulerTemperatureAdapter).
/// Підключається до того самого абстрактного вхідного порту ISetTemperatureUseCase,
/// доводячи легкість додавання нових точок входу без жодної модифікації коду ядра.
class SchedulerTemperatureAdapter {
public:
    explicit SchedulerTemperatureAdapter(std::shared_ptr<ISetTemperatureUseCase> use_case)
        : use_case_(std::move(use_case)) {}

    /// @brief Спрацювання системного таймера (наприклад, нічний режим зниження енергоспоживання).
    void trigger_event(const std::string& zone_id, double target_temp, const std::string& schedule_name) {
        std::cout << "[Scheduler] Спрацював розклад '" << schedule_name 
                  << "': переведення зони '" << zone_id << "' на " << target_temp << "°C\n";

        // Формування команди від імені системного планувальника з правами admin
        SetTemperatureCommand cmd(zone_id, target_temp, "admin");
        auto result = use_case_->execute(cmd);

        if (result) {
            std::cout << "  [Scheduler OK] Зону '" << result->zone_id 
                      << "' успішно переведено на " << result->new_temperature << "°C "
                      << "(було " << result->previous_temperature << "°C)\n";
        } else {
            std::cerr << "  [Scheduler ERROR] Помилка виконання: " 
                      << to_string(result.error()) << "\n";
        }
    }

private:
    std::shared_ptr<ISetTemperatureUseCase> use_case_;
};

// ============================================================================
// ТОЧКА ВХОДУ ТА КОРІНЬ КОМПОЗИЦІЇ (COMPOSITION ROOT)
// ============================================================================

int main() {
    std::cout << "======================================================================\n";
    std::cout << " АРХІТЕКТУРА 'ОДНЕ ЯДРО, КІЛЬКА ФРОНТІВ' (HEXAGONAL ARCHITECTURE)\n";
    std::cout << " Демонстрація ізоляції прикладного ядра та роботи трьох адаптерів\n";
    std::cout << "======================================================================\n\n";

    // ------------------------------------------------------------------------
    // 1. Створення єдиного спільного екземпляра ядра
    // ------------------------------------------------------------------------
    auto core = std::make_shared<TemperatureControlService>();

    // ------------------------------------------------------------------------
    // 2. Корінь композиції: інжекція ядра (через вхідний порт) в адаптери
    // ------------------------------------------------------------------------
    HttpTemperatureController   http_adapter(core);
    CliTemperatureAdapter       cli_adapter(core);
    QueueWorkerAdapter          queue_adapter(core);
    SchedulerTemperatureAdapter scheduler_adapter(core);

    // ========================================================================
    // ДЕМОНСТРАЦІЯ 1: REST API АДАПТЕР (HttpTemperatureController)
    // Трансляція результатів та доменних помилок у коди HTTP: 200, 400, 403, 404, 422
    // ========================================================================
    std::cout << "--- [1] КАНАЛ REST API: HttpTemperatureController ---\n";

    // Запит 1.1: Успішна зміна температури -> HTTP 200 OK
    {
        HttpRequest req{
            .method = "POST",
            .path = "/api/v1/temperature",
            .body = R"({"zone_id":"living-room","temperature":22.5,"user_id":"operator_1"})"
        };
        auto resp = http_adapter.handle_request(req);
        std::cout << "Запит: living-room -> 22.5°C (operator_1)\n";
        std::cout << "  Відповідь HTTP " << resp.status_code << ": " << resp.body << "\n\n";
    }

    // Запит 1.2: Некоректний синтаксис JSON -> HTTP 400 Bad Request
    {
        HttpRequest req{
            .method = "POST",
            .path = "/api/v1/temperature",
            .body = R"({"zone_id":"living-room","broken_json)"
        };
        auto resp = http_adapter.handle_request(req);
        std::cout << "Запит: пошкоджений JSON\n";
        std::cout << "  Відповідь HTTP " << resp.status_code << ": " << resp.body << "\n\n";
    }

    // Запит 1.3: Недостатньо прав для зони -> HTTP 403 Forbidden
    {
        HttpRequest req{
            .method = "POST",
            .path = "/api/v1/temperature",
            .body = R"({"zone_id":"server-room","temperature":19.0,"user_id":"operator_1"})"
        };
        auto resp = http_adapter.handle_request(req);
        std::cout << "Запит: server-room від operator_1 (потрібен admin)\n";
        std::cout << "  Відповідь HTTP " << resp.status_code << ": " << resp.body << "\n\n";
    }

    // Запит 1.4: Неіснуюча кліматична зона -> HTTP 404 Not Found
    {
        HttpRequest req{
            .method = "POST",
            .path = "/api/v1/temperature",
            .body = R"({"zone_id":"attic-roof","temperature":20.0,"user_id":"operator_1"})"
        };
        auto resp = http_adapter.handle_request(req);
        std::cout << "Запит: неіснуюча зона 'attic-roof'\n";
        std::cout << "  Відповідь HTTP " << resp.status_code << ": " << resp.body << "\n\n";
    }

    // Запит 1.5: Порушення фізичних меж безпеки зони -> HTTP 422 Unprocessable Entity
    {
        HttpRequest req{
            .method = "POST",
            .path = "/api/v1/temperature",
            .body = R"({"zone_id":"living-room","temperature":32.0,"user_id":"operator_1"})"
        };
        auto resp = http_adapter.handle_request(req);
        std::cout << "Запит: living-room -> 32.0°C (максимум зони 28.0°C)\n";
        std::cout << "  Відповідь HTTP " << resp.status_code << ": " << resp.body << "\n\n";
    }

    // ========================================================================
    // ДЕМОНСТРАЦІЯ 2: CLI АДАПТЕР (CliTemperatureAdapter)
    // Мапінг результатів у коди виходу процесу: 0 (успіх), 1 (домен), 2 (синтаксис)
    // ========================================================================
    std::cout << "--- [2] КАНАЛ CLI: CliTemperatureAdapter ---\n";

    // Сценарій 2.1: Успішна зміна через прапорці -> Код 0
    {
        std::cout << "Виклик: cli --zone bedroom --temp 21.0 --user operator_1\n";
        int exit_code = cli_adapter.run({"--zone", "bedroom", "--temp", "21.0", "--user", "operator_1"});
        std::cout << "  Код завершення процесу: " << exit_code << "\n\n";
    }

    // Сценарій 2.2: Доменна помилка (температура вище максимуму) -> Код 1
    {
        std::cout << "Виклик: cli --zone bedroom --temp 29.0 --user operator_1\n";
        int exit_code = cli_adapter.run({"--zone", "bedroom", "--temp", "29.0", "--user", "operator_1"});
        std::cout << "  Код завершення процесу: " << exit_code << "\n\n";
    }

    // Сценарій 2.3: Помилка синтаксису (пропущено --temp) -> Код 2
    {
        std::cout << "Виклик: cli --zone bedroom --user operator_1\n";
        int exit_code = cli_adapter.run({"--zone", "bedroom", "--user", "operator_1"});
        std::cout << "  Код завершення процесу: " << exit_code << "\n\n";
    }

    // ========================================================================
    // ДЕМОНСТРАЦІЯ 3: АСИНХРОННИЙ ВОРКЕР ЧЕРГИ (QueueWorkerAdapter)
    // Тригілкова трансляція: ACK (успіх), NACK (re-queue), DLQ (ізоляція збою)
    // ========================================================================
    std::cout << "--- [3] КАНАЛ ЧЕРГИ ПОВІДОМЛЕНЬ: QueueWorkerAdapter ---\n";

    // Повідомлення 3.1: Коректний пакет -> ACK
    {
        QueueMessage msg{
            .message_id = "msg-001",
            .payload = R"({"zone_id":"living-room","temperature":21.0,"user_id":"operator_1"})",
            .delivery_attempt = 1,
            .max_retries = 3
        };
        auto action = queue_adapter.process_message(msg);
        std::cout << "  Результат брокера: " << to_string(action) << "\n\n";
    }

    // Повідомлення 3.2: Тимчасова зайнятість пристрою -> NACK (спроба 1 з 3)
    {
        core->set_zone_busy("living-room", true); // Імітуємо апаратне калібрування

        QueueMessage msg{
            .message_id = "msg-002",
            .payload = R"({"zone_id":"living-room","temperature":20.5,"user_id":"operator_1"})",
            .delivery_attempt = 1,
            .max_retries = 3
        };
        auto action = queue_adapter.process_message(msg);
        std::cout << "  Результат брокера: " << to_string(action) << "\n\n";
    }

    // Повідомлення 3.3: Тимчасова зайнятість, але спроба остання (3 з 3) -> DLQ
    {
        QueueMessage msg{
            .message_id = "msg-002-retry3",
            .payload = R"({"zone_id":"living-room","temperature":20.5,"user_id":"operator_1"})",
            .delivery_attempt = 3,
            .max_retries = 3
        };
        auto action = queue_adapter.process_message(msg);
        std::cout << "  Результат брокера: " << to_string(action) << "\n\n";

        core->set_zone_busy("living-room", false); // Знімаємо блокування
    }

    // Повідомлення 3.4: Фатальна бізнес-помилка (заборонена зона) -> одразу DLQ без NACK
    {
        QueueMessage msg{
            .message_id = "msg-003",
            .payload = R"({"zone_id":"server-room","temperature":15.0,"user_id":"operator_2"})",
            .delivery_attempt = 1,
            .max_retries = 3
        };
        auto action = queue_adapter.process_message(msg);
        std::cout << "  Результат брокера: " << to_string(action) << "\n\n";
    }

    // Повідомлення 3.5: Пошкоджене повідомлення (Poison Message) -> DLQ
    {
        QueueMessage msg{
            .message_id = "msg-004",
            .payload = "NOT_A_VALID_JSON_STRING",
            .delivery_attempt = 1,
            .max_retries = 3
        };
        auto action = queue_adapter.process_message(msg);
        std::cout << "  Результат брокера: " << to_string(action) << "\n\n";
    }

    // ========================================================================
    // ДЕМОНСТРАЦІЯ 4: ЧЕТВЕРТИЙ АДАПТЕР (SchedulerTemperatureAdapter)
    // Додавання нової точки входу без жодної модифікації ядра
    // ========================================================================
    std::cout << "--- [4] РОЗШИРЕННЯ: SchedulerTemperatureAdapter (Open-Closed Principle) ---\n";
    scheduler_adapter.trigger_event("greenhouse", 20.0, "NightEcoMode_Greenhouse");
    scheduler_adapter.trigger_event("bedroom", 17.5, "NightSetback_Bedroom");

    std::cout << "\n======================================================================\n";
    std::cout << " Всі 4 адаптери працюють з єдиним ядром без дублювання бізнес-логіки!\n";
    std::cout << "======================================================================\n";

    return 0;
}
