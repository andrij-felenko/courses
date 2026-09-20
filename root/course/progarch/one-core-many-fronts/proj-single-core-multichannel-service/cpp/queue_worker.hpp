#pragma once

#include "temperature_core.hpp"

#include <cctype>
#include <iomanip>
#include <iostream>
#include <memory>
#include <optional>
#include <string>
#include <string_view>

// ============================================================================
// ПРОТОКОЛЬНІ СИГНАЛИ ТА ПАКЕТИ БРОКЕРА ЧЕРГ
// ============================================================================

/// @brief Протокольні дії брокера повідомлень у відповідь на обробку пакета.
enum class MessageAction {
    Ack,   ///< Підтвердження (Acknowledge) — успіх, повідомлення вилучається з черги
    Nack,  ///< Негативне підтвердження (Negative Ack) — тимчасовий збій, повторна обробка (re-queue)
    Dlq    ///< Переміщення в Dead Letter Queue — фатальна помилка, запобігання зацикленню
};

/// @brief Текстове представлення протокольного сигналу.
[[nodiscard]] constexpr std::string_view to_string(MessageAction action) noexcept {
    switch (action) {
        case MessageAction::Ack:  return "ACK (Підтверджено)";
        case MessageAction::Nack: return "NACK (Повторна спроба / re-queue)";
        case MessageAction::Dlq:  return "DLQ (Черга помилкових повідомлень)";
    }
    return "UNKNOWN";
}

/// @brief Модель повідомлення з черги брокера.
struct QueueMessage {
    std::string message_id;      ///< Унікальний ідентифікатор повідомлення
    std::string payload;         ///< Корисне навантаження JSON
    int delivery_attempt{1};     ///< Номер поточної спроби доставки (1..N)
    int max_retries{3};          ///< Максимальна кількість повторних спроб перед DLQ
};

// ============================================================================
// АСИНХРОННИЙ ДРАЙВУЮЧИЙ АДАПТЕР ЧЕРГИ (QUEUE WORKER ADAPTER)
// ============================================================================

/// @brief Драйвуючий адаптер брокера черг: здійснює тригілкову трансляцію
/// доменних відповідей у протокольні дії життєвого циклу: ACK, NACK та DLQ.
class QueueWorkerAdapter {
public:
    explicit QueueWorkerAdapter(std::shared_ptr<ISetTemperatureUseCase> use_case)
        : use_case_(std::move(use_case)) {}

    /// @brief Опрацювати пакет повідомлення з брокера.
    [[nodiscard]] MessageAction process_message(const QueueMessage& message, 
                                                std::ostream& log = std::cout) const {
        log << "[QueueWorker] Отримано повідомлення ID=" << message.message_id 
            << " (спроба " << message.delivery_attempt << "/" << message.max_retries << ")\n";

        // 1. Десеріалізація та перевірка цілісності корисного навантаження
        auto payload = parse_message_payload(message.payload);
        if (!payload.has_value()) {
            // «Отруйне повідомлення» (Poison message) з невалідним форматом — ніколи не NACK'ати,
            // оскільки повторні спроби лише заблокують чергу. Одразу ізолюємо в DLQ.
            log << "  [DLQ] Синтаксична помилка або пошкоджений JSON. Переміщено в Dead Letter Queue.\n";
            return MessageAction::Dlq;
        }

        // 2. Формування незмінного Command DTO ядра
        SetTemperatureCommand command(payload->zone_id, payload->temperature, payload->user_id);

        // 3. Виклик вхідного порту прикладного ядра
        auto result = use_case_->execute(command);

        // 4. Тригілкова трансляція результату в протокольні сигнали брокера
        if (result) {
            log << std::fixed << std::setprecision(1);
            log << "  [ACK] Бізнес-сценарій виконано успішно: зона '" << result->zone_id 
                << "' встановлена на " << result->new_temperature << "°C. Повідомлення видалено з черги.\n";
            return MessageAction::Ack;
        }

        const DomainError error = result.error();

        // Гілка NACK: тимчасовий апаратний збій (транзієнтний), який може зникнути при повторі
        if (error == DomainError::DeviceBusy) {
            if (message.delivery_attempt < message.max_retries) {
                log << "  [NACK] Тимчасовий збій (" << to_string(error) 
                    << "). Повернення в чергу для повторної спроби (re-queue).\n";
                return MessageAction::Nack;
            }
            // Якщо ліміт повторних спроб вичерпано — переміщуємо в DLQ
            log << "  [DLQ] Вичерпано ліміт повторних спроб (" << message.max_retries 
                << "). Переміщено в Dead Letter Queue.\n";
            return MessageAction::Dlq;
        }

        // Гілка DLQ: фатальні доменні помилки (невідома зона, відмова доступу, порушення діапазону)
        // Повторна обробка таких повідомлень ніколи не завершиться успіхом, тому повтори (NACK) заборонені
        log << "  [DLQ] Фатальне порушення доменних правил (" << to_string(error) 
            << "). Відправлено в Dead Letter Queue для аналізу інциденту.\n";
        return MessageAction::Dlq;
    }

private:
    struct ParsedPayload {
        std::string zone_id;
        double temperature{0.0};
        std::string user_id;
    };

    [[nodiscard]] static std::optional<ParsedPayload> parse_message_payload(std::string_view json) {
        auto extract_field = [&](std::string_view key) -> std::optional<std::string> {
            std::string needle = "\"" + std::string(key) + "\"";
            auto pos = json.find(needle);
            if (pos == std::string_view::npos) return std::nullopt;
            auto colon = json.find(':', pos + needle.size());
            if (colon == std::string_view::npos) return std::nullopt;
            auto first_quote = json.find('"', colon + 1);
            if (first_quote == std::string_view::npos) return std::nullopt;
            auto second_quote = json.find('"', first_quote + 1);
            if (second_quote == std::string_view::npos) return std::nullopt;
            return std::string(json.substr(first_quote + 1, second_quote - first_quote - 1));
        };

        auto extract_num = [&](std::string_view key) -> std::optional<double> {
            std::string needle = "\"" + std::string(key) + "\"";
            auto pos = json.find(needle);
            if (pos == std::string_view::npos) return std::nullopt;
            auto colon = json.find(':', pos + needle.size());
            if (colon == std::string_view::npos) return std::nullopt;
            auto start = colon + 1;
            while (start < json.size() && std::isspace(static_cast<unsigned char>(json[start]))) start++;
            auto end = start;
            while (end < json.size() && (std::isdigit(static_cast<unsigned char>(json[end])) || json[end] == '.' || json[end] == '-')) {
                end++;
            }
            if (start == end) return std::nullopt;
            try {
                return std::stod(std::string(json.substr(start, end - start)));
            } catch (...) {
                return std::nullopt;
            }
        };

        auto zone = extract_field("zone_id");
        auto user = extract_field("user_id");
        auto temp = extract_num("temperature");

        if (!zone || !user || !temp || zone->empty() || user->empty()) {
            return std::nullopt;
        }

        return ParsedPayload{
            .zone_id = std::move(*zone),
            .temperature = *temp,
            .user_id = std::move(*user)
        };
    }

    std::shared_ptr<ISetTemperatureUseCase> use_case_;
};
