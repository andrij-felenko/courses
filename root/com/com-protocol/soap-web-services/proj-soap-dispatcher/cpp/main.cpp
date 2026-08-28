#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <optional>
#include <expected>
#include <format>
#include <chrono>
#include <regex>

namespace soap {

// Версія стандарту протоколу
enum class SoapVersion {
    Soap11,
    Soap12
};

// Вхідна структура HTTP-запиту
struct HttpRequest {
    std::string method;
    std::string contentType;
    std::string soapAction;
    std::string body;
};

// Вихідна структура HTTP-відповіді
struct HttpResponse {
    int statusCode;
    std::string contentType;
    std::string body;
};

// Параметри фінансового платежу
struct PaymentRequest {
    std::string accountNumber;
    double amount;
    std::string currency;
};

// Результат успішного проведення платежу
struct PaymentResponse {
    std::string transactionId;
    std::string status;
    std::string timestamp;
};

// Клас диспетчера обробки та маршрутизації SOAP-запитів
class SoapDispatcher {
public:
    explicit SoapDispatcher(SoapVersion version = SoapVersion::Soap11)
        : version_(version) {}

    // Головна функція обробки життєвого циклу запиту
    HttpResponse dispatch(const HttpRequest& req) {
        // Крок 1: Валідація HTTP-методу (SOAP вимагає виключно POST)
        if (req.method != "POST") {
            return {405, "text/plain; charset=utf-8", "Метод не підтримується. Вимагається HTTP POST."};
        }

        // Крок 2: Валідація заголовка Content-Type
        if (!validateContentType(req.contentType)) {
            return buildFaultResponse(
                "soap:Client",
                "Несумісний MIME-тип Content-Type для встановленої версії SOAP",
                "INVALID_CONTENT_TYPE",
                415
            );
        }

        // Крок 3: Перевірка базової структури XML-документа
        if (!req.body.contains("Envelope") || !req.body.contains("Body")) {
            return buildFaultResponse(
                "soap:Client",
                "XML-документ не містить обов'язкових елементів Envelope або Body",
                "MALFORMED_ENVELOPE",
                400
            );
        }

        // Крок 4: Аналіз обов'язкових заголовків mustUnderstand
        auto mustUnderstandCheck = checkMustUnderstandHeaders(req.body);
        if (!mustUnderstandCheck.has_value()) {
            return buildFaultResponse(
                "soap:MustUnderstand",
                mustUnderstandCheck.error(),
                "UNHANDLED_MANDATORY_HEADER",
                500
            );
        }

        // Крок 5: Розбір та валідація схеми параметрів платежу
        auto paymentData = parsePaymentRequest(req.body);
        if (!paymentData.has_value()) {
            return buildFaultResponse(
                "soap:Client",
                paymentData.error(),
                "SCHEMA_VALIDATION_ERROR",
                version_ == SoapVersion::Soap11 ? 500 : 400
            );
        }

        // Крок 6: Виконання прикладної бізнес-логіки
        PaymentResponse result = executePayment(*paymentData);

        // Крок 7: Побудова успішного вихідного конверта
        return buildSuccessResponse(result);
    }

private:
    SoapVersion version_;

    bool validateContentType(std::string_view ct) const {
        if (version_ == SoapVersion::Soap11) {
            return ct.starts_with("text/xml");
        }
        return ct.starts_with("application/soap+xml");
    }

    // Перевірка блоків <soap:Header> на наявність обов'язкових інструкцій
    std::expected<void, std::string> checkMustUnderstandHeaders(std::string_view xml) const {
        auto hStart = xml.find("<soap:Header>");
        if (hStart == std::string_view::npos) {
            hStart = xml.find("<Header>");
        }
        auto hEnd = xml.find("</soap:Header>");
        if (hEnd == std::string_view::npos) {
            hEnd = xml.find("</Header>");
        }

        // Якщо блок заголовка відсутній — перевірка успішна
        if (hStart == std::string_view::npos || hEnd == std::string_view::npos) {
            return {};
        }

        std::string_view headerContent = xml.substr(hStart, hEnd - hStart);

        // Пошук атрибута mustUnderstand="1" або "true"
        std::regex muRegex(R"(<([a-zA-Z0-9_:]+)[^>]*mustUnderstand\s*=\s*["'](1|true)["'][^>]*>)");
        std::string hStr(headerContent);
        std::smatch match;

        if (std::regex_search(hStr, match, muRegex)) {
            std::string tagName = match[1].str();
            // Диспетчер підтримує виключно заголовок безпеки Security
            if (!tagName.contains("Security")) {
                return std::unexpected(
                    std::format("Невідомий заголовок '{}' з атрибутом mustUnderstand='1'", tagName)
                );
            }
        }
        return {};
    }

    // Допоміжна функція вилучення текстового вмісту тегу
    std::optional<std::string> extractTag(std::string_view xml, std::string_view tag) const {
        std::string openTag = std::format("<{}>", tag);
        std::string closeTag = std::format("</{}>", tag);

        auto start = xml.find(openTag);
        if (start == std::string_view::npos) {
            std::regex tagRegex(std::format(R"(<([a-zA-Z0-9_]+:)?{}>([^<]*)</([a-zA-Z0-9_]+:)?{}>)", tag, tag));
            std::string s(xml);
            std::smatch m;
            if (std::regex_search(s, m, tagRegex)) {
                return m[2].str();
            }
            return std::nullopt;
        }

        start += openTag.length();
        auto end = xml.find(closeTag, start);
        if (end == std::string_view::npos) return std::nullopt;

        return std::string(xml.substr(start, end - start));
    }

    std::expected<PaymentRequest, std::string> parsePaymentRequest(std::string_view xml) const {
        auto acc = extractTag(xml, "accountNumber");
        auto amtStr = extractTag(xml, "amount");
        auto curr = extractTag(xml, "currency");

        if (!acc || !amtStr || !curr) {
            return std::unexpected("Відсутні обов'язкові елементи: accountNumber, amount або currency");
        }

        if (acc->length() < 10) {
            return std::unexpected(std::format("Некоректний рахунок '{}': довжина має бути не менше 10 символів", *acc));
        }

        double amount = 0.0;
        try {
            amount = std::stod(*amtStr);
        } catch (...) {
            return std::unexpected(std::format("Нечислове значення суми: '{}'", *amtStr));
        }

        if (amount <= 0.0) {
            return std::unexpected("Сума транзакції повинна бути строго додатним числом");
        }

        return PaymentRequest{
            .accountNumber = *acc,
            .amount = amount,
            .currency = *curr
        };
    }

    PaymentResponse executePayment(const PaymentRequest& req) const {
        return PaymentResponse{
            .transactionId = "TX-20260820-9941",
            .status = "SUCCESS",
            .timestamp = "2026-08-20T10:30:00Z"
        };
    }

    HttpResponse buildSuccessResponse(const PaymentResponse& res) const {
        std::string xml;
        if (version_ == SoapVersion::Soap11) {
            xml = std::format(
                "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
                "<soap:Envelope xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\"\n"
                "               xmlns:m=\"http://bank.example.com/payments\">\n"
                "  <soap:Body>\n"
                "    <m:ProcessPaymentResponse>\n"
                "      <m:transactionId>{}</m:transactionId>\n"
                "      <m:status>{}</m:status>\n"
                "      <m:timestamp>{}</m:timestamp>\n"
                "    </m:ProcessPaymentResponse>\n"
                "  </soap:Body>\n"
                "</soap:Envelope>",
                res.transactionId, res.status, res.timestamp
            );
            return {200, "text/xml; charset=utf-8", xml};
        } else {
            xml = std::format(
                "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
                "<soap12:Envelope xmlns:soap12=\"http://www.w3.org/2003/05/soap-envelope\"\n"
                "                 xmlns:m=\"http://bank.example.com/payments\">\n"
                "  <soap12:Body>\n"
                "    <m:ProcessPaymentResponse>\n"
                "      <m:transactionId>{}</m:transactionId>\n"
                "      <m:status>{}</m:status>\n"
                "      <m:timestamp>{}</m:timestamp>\n"
                "    </m:ProcessPaymentResponse>\n"
                "  </soap12:Body>\n"
                "</soap12:Envelope>",
                res.transactionId, res.status, res.timestamp
            );
            return {200, "application/soap+xml; charset=utf-8", xml};
        }
    }

    HttpResponse buildFaultResponse(std::string_view code, std::string_view reason,
                                    std::string_view errCode, int httpCode) const {
        std::string xml;
        if (version_ == SoapVersion::Soap11) {
            xml = std::format(
                "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
                "<soap:Envelope xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">\n"
                "  <soap:Body>\n"
                "    <soap:Fault>\n"
                "      <faultcode>{}</faultcode>\n"
                "      <faultstring>{}</faultstring>\n"
                "      <detail>\n"
                "        <err:PaymentFault xmlns:err=\"http://bank.example.com/errors\">\n"
                "          <err:errorCode>{}</err:errorCode>\n"
                "        </err:PaymentFault>\n"
                "      </detail>\n"
                "    </soap:Fault>\n"
                "  </soap:Body>\n"
                "</soap:Envelope>",
                code, reason, errCode
            );
            return {httpCode, "text/xml; charset=utf-8", xml};
        } else {
            std::string soap12Code = code.contains("Client") ? "soap12:Sender" :
                                    (code.contains("Server") ? "soap12:Receiver" : std::string(code));
            xml = std::format(
                "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
                "<soap12:Envelope xmlns:soap12=\"http://www.w3.org/2003/05/soap-envelope\">\n"
                "  <soap12:Body>\n"
                "    <soap12:Fault>\n"
                "      <soap12:Code>\n"
                "        <soap12:Value>{}</soap12:Value>\n"
                "      </soap12:Code>\n"
                "      <soap12:Reason>\n"
                "        <soap12:Text xml:lang=\"uk-UA\">{}</soap12:Text>\n"
                "      </soap12:Reason>\n"
                "      <soap12:Detail>\n"
                "        <err:PaymentFault xmlns:err=\"http://bank.example.com/errors\">\n"
                "          <err:errorCode>{}</err:errorCode>\n"
                "        </err:PaymentFault>\n"
                "      </soap12:Detail>\n"
                "    </soap12:Fault>\n"
                "  </soap12:Body>\n"
                "</soap12:Envelope>",
                soap12Code, reason, errCode
            );
            return {httpCode, "application/soap+xml; charset=utf-8", xml};
        }
    }
};

} // namespace soap

int main() {
    soap::SoapDispatcher dispatcher(soap::SoapVersion::Soap11);

    // Приклад 1: Коректний вхідний запит на переказ коштів
    soap::HttpRequest validReq{
        .method = "POST",
        .contentType = "text/xml; charset=utf-8",
        .soapAction = "\"http://bank.example.com/payments/ProcessPayment\"",
        .body = R"(<?xml version="1.0"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:m="http://bank.example.com/payments">
  <soap:Header>
    <wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd"
                   soap:mustUnderstand="1">
      <wsse:UsernameToken>
        <wsse:Username>client_app</wsse:Username>
      </wsse:UsernameToken>
    </wsse:Security>
  </soap:Header>
  <soap:Body>
    <m:ProcessPayment>
      <m:accountNumber>UA42300001000002600123456789</m:accountNumber>
      <m:amount>4500.00</m:amount>
      <m:currency>UAH</m:currency>
    </m:ProcessPayment>
  </soap:Body>
</soap:Envelope>)"
    };

    auto resp1 = dispatcher.dispatch(validReq);
    std::cout << "--- Тест 1: Успішна транзакція (HTTP " << resp1.statusCode << ") ---\n"
              << resp1.body << "\n\n";

    // Приклад 2: Запит з невідомим заголовком mustUnderstand="1"
    soap::HttpRequest unknownHeaderReq = validReq;
    unknownHeaderReq.body = R"(<?xml version="1.0"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Header>
    <custom:RoutingToken xmlns:custom="http://custom.example.com/router"
                         soap:mustUnderstand="1">
      <custom:RouteId>99</custom:RouteId>
    </custom:RoutingToken>
  </soap:Header>
  <soap:Body>
    <m:ProcessPayment xmlns:m="http://bank.example.com/payments">
      <m:accountNumber>UA42300001000002600123456789</m:accountNumber>
      <m:amount>4500.00</m:amount>
      <m:currency>UAH</m:currency>
    </m:ProcessPayment>
  </soap:Body>
</soap:Envelope>)";

    auto resp2 = dispatcher.dispatch(unknownHeaderReq);
    std::cout << "--- Тест 2: Помилка mustUnderstand (HTTP " << resp2.statusCode << ") ---\n"
              << resp2.body << "\n\n";

    // Приклад 3: Запит з некоректними аргументами (від'ємна сума)
    soap::HttpRequest invalidDataReq = validReq;
    invalidDataReq.body = R"(<?xml version="1.0"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:m="http://bank.example.com/payments">
  <soap:Body>
    <m:ProcessPayment>
      <m:accountNumber>UA42300001000002600123456789</m:accountNumber>
      <m:amount>-100.00</m:amount>
      <m:currency>UAH</m:currency>
    </m:ProcessPayment>
  </soap:Body>
</soap:Envelope>)";

    auto resp3 = dispatcher.dispatch(invalidDataReq);
    std::cout << "--- Тест 3: Помилка валідації схеми даних (HTTP " << resp3.statusCode << ") ---\n"
              << resp3.body << "\n";

    return 0;
}
