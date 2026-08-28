#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <expected>
#include <cstdint>
#include <chrono>
#include <sstream>
#include <iomanip>

// ── 1. Канонічна модель даних (CDM Domain Contract) ─────────────────────────

enum class Currency {
    UAH,
    USD,
    EUR,
    UNKNOWN
};

enum class CanonicalOrderStatus {
    Created,
    Paid,
    Shipped,
    Cancelled
};

struct CanonicalLineItem {
    std::string sku;
    uint32_t quantity;
    uint64_t unit_price_cents; // Завжди в цілих мінімальних одиницях валюти
};

struct CanonicalMessageHeader {
    std::string message_id;      // UUIDv7 або унікальний строковий ідентифікатор
    std::string correlation_id;  // Наскрізний ідентифікатор транзакції
    std::string schema_version;  // SemVer версія канонічного контракту
    uint64_t timestamp_utc_ms;   // Unix Epoch у мілісекундах
    std::string origin_system;   // Джерело надходження повідомлення
};

struct CanonicalOrderPayload {
    std::string order_id;
    std::string customer_id;
    uint64_t total_amount_cents;
    Currency currency;
    CanonicalOrderStatus status;
    std::vector<CanonicalLineItem> items;
};

struct CanonicalOrderMessage {
    CanonicalMessageHeader header;
    CanonicalOrderPayload payload;
};

// ── 2. Вхідні сторонні формати (Raw Inbound Payloads) ────────────────────────

// Формат 1: Застаріла ERP-система (CSV/Flat рядок)
// Формат: "ORDER_ID,CUST_REF,STATUS_CODE,AMOUNT_FLOAT,CURRENCY_STR,SKU,QTY"
struct LegacyErpPayload {
    std::string raw_csv_line;
};

// Формат 2: Зовнішній веб-маркетплейс (JSON-подібний DTO)
struct PartnerWebhookPayload {
    std::string partner_id;
    std::string ext_order_ref;
    std::string user_email;
    double order_total;
    std::string curr;
    std::string state_str;
    std::string item_sku;
    int item_count;
};

// ── 3. Вхідні антикорупційні транслятори (Inbound ACL Translators) ───────────

class InboundTranslator {
public:
    static Currency parse_currency(std::string_view code) {
        if (code == "UAH") return Currency::UAH;
        if (code == "USD") return Currency::USD;
        if (code == "EUR") return Currency::EUR;
        return Currency::UNKNOWN;
    }

    static std::expected<CanonicalOrderMessage, std::string>
    from_legacy_erp(const LegacyErpPayload& input, std::string_view correlation_id) {
        std::stringstream ss(input.raw_csv_line);
        std::string order_id, cust_id, status_code_str, amount_str, curr_str, sku, qty_str;

        if (!std::getline(ss, order_id, ',') ||
            !std::getline(ss, cust_id, ',') ||
            !std::getline(ss, status_code_str, ',') ||
            !std::getline(ss, amount_str, ',') ||
            !std::getline(ss, curr_str, ',') ||
            !std::getline(ss, sku, ',') ||
            !std::getline(ss, qty_str, ',')) {
            return std::unexpected("ERP Translation Error: пошкоджений або неповний CSV рядок");
        }

        CanonicalOrderMessage msg;
        msg.header.message_id = "msg-erp-" + order_id;
        msg.header.correlation_id = std::string(correlation_id);
        msg.header.schema_version = "2.0.0";
        msg.header.timestamp_utc_ms = static_cast<uint64_t>(
            std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::system_clock::now().time_since_epoch()).count());
        msg.header.origin_system = "LEGACY_ERP_WAREHOUSE";

        msg.payload.order_id = order_id;
        msg.payload.customer_id = cust_id;

        // Нормалізація грошей: переведення float у цілі копійки без втрати точності
        try {
            double raw_amount = std::stod(amount_str);
            if (raw_amount < 0.0) {
                return std::unexpected("ERP Translation Error: від'ємна сума замовлення");
            }
            msg.payload.total_amount_cents = static_cast<uint64_t>(raw_amount * 100.0 + 0.5);
        } catch (...) {
            return std::unexpected("ERP Translation Error: невалідний числовий формат суми");
        }

        msg.payload.currency = parse_currency(curr_str);

        // Мапінг числових статусів застарілої системи
        try {
            int sc = std::stoi(status_code_str);
            switch (sc) {
                case 10: msg.payload.status = CanonicalOrderStatus::Created; break;
                case 20: msg.payload.status = CanonicalOrderStatus::Paid; break;
                case 30: msg.payload.status = CanonicalOrderStatus::Shipped; break;
                default: msg.payload.status = CanonicalOrderStatus::Cancelled; break;
            }
        } catch (...) {
            return std::unexpected("ERP Translation Error: невалідний код статусу");
        }

        uint32_t qty = 1;
        try {
            qty = static_cast<uint32_t>(std::stoul(qty_str));
            if (qty == 0) qty = 1;
        } catch (...) {
            qty = 1;
        }

        msg.payload.items.push_back({sku, qty, msg.payload.total_amount_cents / qty});

        return msg;
    }

    static std::expected<CanonicalOrderMessage, std::string>
    from_partner_webhook(const PartnerWebhookPayload& input, std::string_view correlation_id) {
        if (input.partner_id.empty() || input.ext_order_ref.empty()) {
            return std::unexpected("Partner Webhook Error: відсутній обов'язковий ідентифікатор");
        }

        CanonicalOrderMessage msg;
        msg.header.message_id = "msg-partner-" + input.ext_order_ref;
        msg.header.correlation_id = std::string(correlation_id);
        msg.header.schema_version = "2.0.0";
        msg.header.timestamp_utc_ms = static_cast<uint64_t>(
            std::chrono::duration_cast<std::chrono::milliseconds>(
                std::chrono::system_clock::now().time_since_epoch()).count());
        msg.header.origin_system = "PARTNER_" + input.partner_id;

        msg.payload.order_id = "PARTNER-" + input.ext_order_ref;
        msg.payload.customer_id = "USER-" + input.user_email;

        if (input.order_total < 0.0) {
            return std::unexpected("Partner Webhook Error: від'ємна сума в замовленні");
        }
        msg.payload.total_amount_cents = static_cast<uint64_t>(input.order_total * 100.0 + 0.5);
        msg.payload.currency = parse_currency(input.curr);

        if (input.state_str == "COMPLETED" || input.state_str == "SUCCESS") {
            msg.payload.status = CanonicalOrderStatus::Paid;
        } else if (input.state_str == "NEW") {
            msg.payload.status = CanonicalOrderStatus::Created;
        } else {
            msg.payload.status = CanonicalOrderStatus::Cancelled;
        }

        uint32_t qty = input.item_count > 0 ? static_cast<uint32_t>(input.item_count) : 1;
        msg.payload.items.push_back({input.item_sku, qty, msg.payload.total_amount_cents / qty});

        return msg;
    }
};

// ── 4. Валідатор канонічної схеми (Schema Validator) ─────────────────────────

class CanonicalSchemaValidator {
public:
    static std::expected<void, std::string> validate(const CanonicalOrderMessage& msg) {
        if (msg.header.correlation_id.empty()) {
            return std::unexpected("Validation Error: відсутній correlation_id");
        }
        if (msg.header.message_id.empty()) {
            return std::unexpected("Validation Error: відсутній message_id");
        }
        if (msg.payload.order_id.empty()) {
            return std::unexpected("Validation Error: порожній order_id");
        }
        if (msg.payload.customer_id.empty()) {
            return std::unexpected("Validation Error: порожній customer_id");
        }
        if (msg.payload.currency == Currency::UNKNOWN) {
            return std::unexpected("Validation Error: невідома або непідтримувана валюта операції");
        }
        if (msg.payload.total_amount_cents == 0) {
            return std::unexpected("Validation Error: нульова або некоректна сума замовлення");
        }
        if (msg.payload.items.empty()) {
            return std::unexpected("Validation Error: замовлення не містить жодної позиції товару");
        }
        return {};
    }
};

// ── 5. Вихідні адаптери-проектори (Outbound Projectors) ───────────────────────

struct BillingEventDto {
    std::string trace_id;
    std::string invoice_no;
    uint64_t charge_amount_cents;
    std::string currency_code;
    bool is_finalized;
};

struct FiscalXmlReportDto {
    std::string xml_document;
};

class OutboundProjector {
public:
    static BillingEventDto to_billing(const CanonicalOrderMessage& msg) {
        return BillingEventDto{
            .trace_id = msg.header.correlation_id,
            .invoice_no = "INV-" + msg.payload.order_id,
            .charge_amount_cents = msg.payload.total_amount_cents,
            .currency_code = (msg.payload.currency == Currency::UAH ? "UAH" : "USD"),
            .is_finalized = (msg.payload.status == CanonicalOrderStatus::Paid)
        };
    }

    static FiscalXmlReportDto to_fiscal_report(const CanonicalOrderMessage& msg) {
        std::ostringstream oss;
        oss << "<FiscalDocument id=\"" << msg.payload.order_id << "\">"
            << "<Origin>" << msg.header.origin_system << "</Origin>"
            << "<TotalCents>" << msg.payload.total_amount_cents << "</TotalCents>"
            << "<Timestamp>" << msg.header.timestamp_utc_ms << "</Timestamp>"
            << "<Status>" << (msg.payload.status == CanonicalOrderStatus::Paid ? "PAID" : "UNPAID") << "</Status>"
            << "</FiscalDocument>";
        return FiscalXmlReportDto{.xml_document = oss.str()};
    }
};

int main() {
    std::cout << "=== Тестування конвеєра Канонічної Моделі Даних ===" << std::endl;

    // Сценарій 1: Обробка замовлення зі застарілої ERP-системи
    LegacyErpPayload erp_input{"ORD-9021,CUST-4410,20,450.50,UAH,SKU-CHAIR-01,2"};
    auto erp_res = InboundTranslator::from_legacy_erp(erp_input, "corr-req-887123");

    if (erp_res) {
        auto val_res = CanonicalSchemaValidator::validate(*erp_res);
        if (val_res) {
            std::cout << "\n[ERP -> CDM]: Успішно нормалізовано канонічне замовлення:\n"
                      << "  ID: " << erp_res->payload.order_id << "\n"
                      << "  Сума (копійки): " << erp_res->payload.total_amount_cents << "\n"
                      << "  Джерело: " << erp_res->header.origin_system << "\n";

            auto billing = OutboundProjector::to_billing(*erp_res);
            std::cout << "  -> Вихідна проекція Billing Invoice: " << billing.invoice_no
                      << " (" << billing.charge_amount_cents << " cents)" << std::endl;
        } else {
            std::cerr << "Помилка валідації ERP: " << val_res.error() << std::endl;
        }
    } else {
        std::cerr << "Помилка трансляції ERP: " << erp_res.error() << std::endl;
    }

    // Сценарій 2: Обробка замовлення від зовнішнього партнера через Webhook
    PartnerWebhookPayload partner_input{
        .partner_id = "AMZN_STORE",
        .ext_order_ref = "EXT-554433",
        .user_email = "alex@example.com",
        .order_total = 129.99,
        .curr = "USD",
        .state_str = "SUCCESS",
        .item_sku = "SKU-HEADPHONES",
        .item_count = 1
    };

    auto partner_res = InboundTranslator::from_partner_webhook(partner_input, "corr-req-999001");
    if (partner_res) {
        auto val_res = CanonicalSchemaValidator::validate(*partner_res);
        if (val_res) {
            std::cout << "\n[Partner -> CDM]: Успішно нормалізовано канонічне замовлення:\n"
                      << "  ID: " << partner_res->payload.order_id << "\n"
                      << "  Клієнт: " << partner_res->payload.customer_id << "\n"
                      << "  Джерело: " << partner_res->header.origin_system << "\n";

            auto fiscal = OutboundProjector::to_fiscal_report(*partner_res);
            std::cout << "  -> Вихідна фіскальна XML-проекція:\n    "
                      << fiscal.xml_document << std::endl;
        } else {
            std::cerr << "Помилка валідації Partner: " << val_res.error() << std::endl;
        }
    } else {
        std::cerr << "Помилка трансляції Partner: " << partner_res.error() << std::endl;
    }

    return 0;
}
