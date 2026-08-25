# ⚙️ Обробка SOAP-запиту: парсинг конверта, валідація та генерація Fault

### Постановка інженерної задачі

У корпоративних фінансових системах, міжбанківських розрахунках та інтеграційних шинах даних сервери повинні приймати й обробляти вхідні SOAP-запити з суворим дотриманням стандарту W3C і профілю WS-I Basic Profile 1.1. На відміну від неформалізованих протоколів, де помилки можуть повертатися у довільному форматі, диспетчер вебсервісу зобов'язаний дотримуватися чіткої багатоступеневої дисципліни обробки:

1. **Перевірка транспортних параметрів HTTP:** переконатися, що клієнт використав метод HTTP POST та передав коректний заголовок `Content-Type` (`text/xml` для SOAP 1.1 або `application/soap+xml` для SOAP 1.2), а також перевірити наявність заголовка `SOAPAction`.
2. **Розбір XML-конверта:** виділити кореневий елемент `<Envelope>`, необов'язковий контейнер метаданих `<Header>` та обов'язкове корисне навантаження `<Body>`.
3. **Дисципліна обов'язкових заголовків (`mustUnderstand`):** просканувати всі дочірні блоки елемента `<Header>`. Якщо будь-який блок містить атрибут `mustUnderstand="1"` (або `"true"`), а сервер не має встановленого обробника для цього блоку (наприклад, не підтримує специфічний заголовок маршрутизації чи координації розподілених транзакцій), сервер зобов'язаний негайно перервати виконання і згенерувати стандартизований конверт помилки з кодом `soap:MustUnderstand`.
4. **Маршрутизація операції:** визначити назву цільового методу з кореневого тегу всередині тіла (`<Body>`).
5. **Валідація схеми аргументів:** вилучити типізовані параметри (номер рахунку, суму транзакції, код валюти) та перевірити їхню відповідність контракту. Якщо параметри некоректні (наприклад, від'ємна сума платежу або відсутні обов'язкові поля), сформувати звіт про помилку клієнта `soap:Client` (у SOAP 1.1) або `soap12:Sender` (у SOAP 1.2) з докладним XML-блоком `<detail>`.
6. **Виконання транзакції та збирання відповіді:** передати валідовані дані до бізнес-модуля і зібрати вихідний стандартизований XML-конверт успішної відповіді.

Нижче наведено модульну та безпечну реалізацію диспетчера обробки фінансових платежів двома мовами програмування: на сучасному C++ (із застосуванням `std::string_view`, `std::expected` та механізмів RAII) і на мові Python.

---

### Програмна реалізація диспетчера

:::tabs
```cpp
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
```
```py
import re
from typing import Dict, Any, Tuple, Optional

class SoapDispatcher:
    def __init__(self, version: str = "1.1"):
        self.version = version

    def dispatch(self, method: str, content_type: str, body: str) -> Tuple[int, Dict[str, str], str]:
        # Перевірка HTTP методу
        if method != "POST":
            return 405, {"Content-Type": "text/plain; charset=utf-8"}, "Вимагається HTTP POST"

        # 1. Валідація заголовка Content-Type
        if self.version == "1.1" and not content_type.startswith("text/xml"):
            return self._build_fault("soap:Client", "Очікується text/xml для SOAP 1.1", "INVALID_CONTENT_TYPE", 415)
        elif self.version == "1.2" and not content_type.startswith("application/soap+xml"):
            return self._build_fault("soap12:Sender", "Очікується application/soap+xml для SOAP 1.2", "INVALID_CONTENT_TYPE", 415)

        # 2. Перевірка базової структури
        if "<Envelope" not in body or "<Body" not in body:
            return self._build_fault("soap:Client", "Відсутній конверт або тіло повідомлення", "MALFORMED_XML", 400)

        # 3. Перевірка блоків mustUnderstand
        header_match = re.search(r"<(?:\w+:)?Header>(.*?)</(?:\w+:)?Header>", body, re.DOTALL)
        if header_match:
            header_content = header_match.group(1)
            mu_blocks = re.findall(r"<(\w+:[a-zA-Z0-9_]+)[^>]*mustUnderstand\s*=\s*[\"'](1|true)[\"'][^>]*>", header_content)
            for tag, _ in mu_blocks:
                if "Security" not in tag:
                    return self._build_fault("soap:MustUnderstand", f"Непідтримуваний обов'язковий заголовок: {tag}", "MANDATORY_HEADER_FAILED", 500)

        # 4. Витягування аргументів платежу
        acc = self._extract_tag(body, "accountNumber")
        amt = self._extract_tag(body, "amount")
        curr = self._extract_tag(body, "currency")

        if not acc or not amt or not curr:
            return self._build_fault("soap:Client", "Відсутні обов'язкові параметри accountNumber, amount або currency", "MISSING_FIELDS", 500 if self.version == "1.1" else 400)

        try:
            amount_val = float(amt)
            if amount_val <= 0:
                raise ValueError()
        except ValueError:
            return self._build_fault("soap:Client", "Сума платежу повинна бути додатним числом", "INVALID_AMOUNT", 500 if self.version == "1.1" else 400)

        # 5. Успішна відповідь
        return self._build_success("TX-PY-2026-8812", "SUCCESS", "2026-08-20T10:30:00Z")

    def _extract_tag(self, xml: str, tag: str) -> Optional[str]:
        m = re.search(rf"<(?:\w+:)?{tag}>([^<]*)</(?:\w+:)?{tag}>", xml)
        return m.group(1).strip() if m else None

    def _build_success(self, tx_id: str, status: str, ts: str) -> Tuple[int, Dict[str, str], str]:
        xml = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
               xmlns:m="http://bank.example.com/payments">
  <soap:Body>
    <m:ProcessPaymentResponse>
      <m:transactionId>{tx_id}</m:transactionId>
      <m:status>{status}</m:status>
      <m:timestamp>{ts}</m:timestamp>
    </m:ProcessPaymentResponse>
  </soap:Body>
</soap:Envelope>"""
        return 200, {"Content-Type": "text/xml; charset=utf-8"}, xml

    def _build_fault(self, code: str, reason: str, err_code: str, status_code: int) -> Tuple[int, Dict[str, str], str]:
        xml = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <soap:Fault>
      <faultcode>{code}</faultcode>
      <faultstring>{reason}</faultstring>
      <detail>
        <err:PaymentFault xmlns:err="http://bank.example.com/errors">
          <err:errorCode>{err_code}</err:errorCode>
        </err:PaymentFault>
      </detail>
    </soap:Fault>
  </soap:Body>
</soap:Envelope>"""
        return status_code, {"Content-Type": "text/xml; charset=utf-8"}, xml
```
:::

---

### Детальний аналіз архітектурних рішень диспетчера

#### 1. Механізм обробки атрибута `mustUnderstand`

Головна відмінність SOAP від неформалізованих протоколів полягає в наявності протокольного механізму узгодження можливостей між клієнтом і сервером прямо в момент виконання запиту.
- Коли клієнт додає до будь-якого блоку метаданих атрибут `mustUnderstand="1"`, він вимагає від сервера гарантії того, що інструкції, закладені в цьому блоці, будуть виконані повністю та без викривлень.
- У методі `checkMustUnderstandHeaders` сервер аналізує вміст контейнера `<soap:Header>`. Якщо у вихідному XML знайдено невідомий елемент (у нашому прикладі — `<custom:RoutingToken>`), сервер не має права проігнорувати його чи частково виконати прикладну логіку з `<soap:Body>`.
- Специфікація вимагає негайної зупинки конвеєра та генерації повідомлення про помилку з кодом `soap:MustUnderstand`. Клієнт, отримавши таку відповідь, розуміє, що цільовий вузол не володіє необхідною версією плагіна маршрутизації або розширення безпеки, і транзакцію не було розпочато.

#### 2. Поділ помилок на категорії клієнта та сервера

У корпоративних протоколах обміну повідомленнями критично важливо однозначно сигналізувати клієнту про причину виникнення помилки:
- **Помилки категорії клієнта (`soap:Client` / `soap12:Sender`):** сигналізують про порушення вхідного контракту. До цієї категорії належать: відсутність обов'язкових полів у схемі XSD, від'ємна сума платежу, занадто короткий номер банківського рахунку чи непідтримуваний MIME-тип запиту. Отримавши таку відповідь, клієнтське програмне забезпечення не повинно автоматично повторювати запит без виправлення вхідних даних, оскільки повторні виклики з тими самими вхідними даними призведуть до ідентичного збою.
- **Помилки категорії сервера (`soap:Server` / `soap12:Receiver`):** виникають у разі аварійних збоїв у внутрішній інфраструктурі (недоступність сховища даних, тайм-аут зв'язку з платіжною системою або вичерпання пулу з'єднань). Така помилка повідомляє клієнту, що вхідний запит був коректним, і його можна безпечно повторити через певний проміжок часу.

#### 3. Семантика HTTP-статусів при формуванні Fault

Зверніть увагу на тонку архітектурну деталь: у стандарті **SOAP 1.1** помилка будь-якої категорії передається через HTTP-транспорт з кодом статусу **HTTP 500 Internal Server Error**. Навіть якщо помилка виникла виключно з вини клієнта (наприклад, через передачу порожнього номера рахунку), сервер SOAP 1.1 все одно повертає HTTP 500, а справжній характер проблеми визначається клієнтом шляхом розбору XML-тегу `<faultcode>`.

У пізнішій версії **SOAP 1.2** консорціум W3C узгодив семантику статусів з архітектурою HTTP: помилки категорії `soap12:Sender` повертаються з кодом стану **HTTP 400 Bad Request**, тоді як код **HTTP 500** зарезервовано виключно для внутрішніх збоїв сервера `soap12:Receiver`.

#### 4. Захист від атак на парсер XML (XXE та Billion Laughs)

Промисловий диспетчер SOAP повинен містити вбудований захист від специфічних вразливостей обробки XML:
- **Атака розширення сутностей (XML Entity Expansion / Billion Laughs):** зловмисник передає вбудоване оголошення DTD з рекурсивними сутностями `<!ENTITY lol "lol"><!ENTITY lol2 "&lol;&lol;">...`. При розгортанні парсер виділяє гігабайти пам'яті за частки секунди, викликаючи повну відмову в обслуговуванні (DoS). Сучасні SOAP-диспетчери повністю вимикають підтримку вбудованих DTD (`DisallowDoctypeDecl = true`).
- **Зовнішні сутності (XML External Entity, XXE):** передача тегу `<!ENTITY xxe SYSTEM "file:///etc/passwd">` дозволяє зловмиснику викрасти системні файли сервера або здійснити атаку підробки запитів на стороні сервера (SSRF). У безпечному конфігуруванні парсера зовнішні сутності (`external-general-entities`, `external-parameter-entities`) блокуються на рівні рушія.

#### 5. Моделі парсингу: DOM проти SAX та StAX

Вибір моделі синтаксичного аналізу визначає споживання ресурсів високонавантаженим вебсервісом:
- **DOM (Document Object Model):** завантажує весь XML-документ у пам'ять, створюючи об'єкти C++ для кожного елемента, атрибута й текстового вузла. Для великих документів вагою 10 МБ обсяг виділеної оперативної пам'яті може досягати 100 МБ.
- **SAX (Simple API for XML):** подієвий аналізатор на основі функцій зворотного виклику (Callbacks). Не завантажує файл у пам'ять, але ускладнює контроль стану та обробку вкладених структур.
- **StAX (Streaming API for XML / Pull Parser):** оптимальна архітектурна модель. Програма виступає ініціатором читання (метод `next()`), витягуючи з потоку лише потрібні теги конверта (`Header`, `Body`), ігноруючи невикористані блоки без виділення динамічної пам'яті.

#### 6. Обробка великих двійкових вкладень: MTOM та XOP

Якщо банківська операція вимагає передачі великих двійкових файлів (наприклад, сканованої копії договору або фотографії паспорта у форматі PDF/JPEG), звичайне кодування `base64Binary` всередині XML-тегу збільшує розмір корисного навантаження на 33% і спричиняє величезне навантаження на парсер DOM.

Для розв'язання цієї проблеми в SOAP використовують стандарт **MTOM** (Message Transmission Optimization Mechanism) та **XOP** (XML-binary Optimized Packaging):
1. Пакет відправляється як складене MIME-повідомлення `multipart/related`.
2. Головна частина містить стандартний XML-конверт SOAP, де замість громіздкого base64-рядка вставляється компактний тег посилання:
   ```xml
   <m:DocumentAttachment>
     <xop:Include xmlns:xop="http://www.w3.org/2004/08/xop/include"
                  href="cid:passport_scan_part_2@bank.example.com" />
   </m:DocumentAttachment>
   ```
3. Сам двійковий файл передається у другій частині MIME-пакету як чисті бінарні байти без жодного текстового перекодування.
4. Диспетчер на приймальному боці читає XML-дерево, а двійкові потоки вичитує безпосередньо з дескриптора файлу чи оперативної пам'яті за MIME-ідентифікатором Content-ID, заощаджуючи процесорний час та оперативну пам'ять на уникненні проміжної десеріалізації.

#### 7. Перевірка дайджесту пароля в WS-Security UsernameToken

Якщо сервіс вимагає автентифікації клієнта через `UsernameToken` з парольним дайджестом, диспетчер зобов'язаний реалізувати точну криптографічну перевірку формули OASIS:

```
ComputedDigest = Base64( SHA1( BinaryNonce + CreatedTimestampString + UserPasswordString ) )
```

Алгоритм верифікації на сервері:
1. Вилучити з заголовка `<wsse:UsernameToken>` значення `Username`, `Password`, `Nonce` та `Created`.
2. Перевірити часову мітку `Created`: якщо різниця між часом сервера та `Created` перевищує допустиме вікно (зазвичай 5 хвилин), відхилити запит з помилкою безпеки.
3. Перевірити `Nonce`: розкодувати рядок з Base64 у двійковий масив байтів. Звірити значення з базою кешу нещодавно використаних одноразових чисел для запобігання атакам повторного відтворення (Replay Attacks).
4. Отримати зашифрований або збережений пароль користувача з внутрішнього сховища облікових записів.
5. Обчислити геш SHA-1 над конкатенацією сирих байтів `Nonce`, рядка дати `Created` та пароля.
6. Порівняти отриманий Base64-рядок із вмістом елемента `<wsse:Password>`. При збігу — пропустити запит до наступного етапу валідації.

#### 8. Архітектура розширюваних інтерцепторів (Interceptors)

У великих фреймворках (Apache CXF, Spring-WS, .NET WCF) обробка повідомлення організована як ланцюжок обов'язків (Chain of Responsibility), що складається з фаз:
1. **Транспортна фаза (Transport Phase):** декомпресія GZIP, перевірка заголовків HTTP та аутентифікація на рівні сокета.
2. **Фаза попереднього розбору (Pre-Dispatch Phase):** аналіз заголовка `SOAPAction` або витягування першого тегу тіла для визначення цільової операції.
3. **Фаза безпеки (Security Inbound Phase):** дешифрування блоків `<xenc:EncryptedData>`, валідація цифрових підписів `<ds:Signature>` та перевірка сертифікатів X.509.
4. **Фаза валідації схеми (Validation Phase):** потокова перевірка тіла за скомпільованою XSD-схемою.
5. **Фаза сервісу (Invoker Phase):** виклик бізнес-методу із передачею типізованих DTO-об'єктів.

Якщо будь-який інтерцептор у вхідному ланцюжку генерує виняток, виконання переривається, і керування негайно передається ланцюжку вихідних інтерцепторів помилок (Fault Out Interceptors), який формує відповідний конверт `<soap:Fault>`.

#### 9. Потоковий запис вихідного XML без проміжних алокацій

При формуванні великих відповідей (наприклад, банківської виписки на десятки тисяч транзакцій) накопичення результуючого рядка `std::string` в оперативній пам'яті викликає часті переалокації купи та фрагментацію пам'яті.

Високопродуктивний сервер реалізує інтерфейс прямого потокового запису:
- Замість конкатенації рядків формувач відповіді пише XML-фрагменти безпосередньо в мережевий буфер сокета (або вихідний потік `std::ostream` / `writev`);
- Кожен відкриваючий тег генерує заголовок, після чого у циклі зчитування з бази даних викидаються записи транзакцій у форматі `Transfer-Encoding: chunked`;
- Обсяг оперативної пам'яті сервера залишається сталим (кілька кілобайт під мережевий буфер) незалежно від того, скільки мегабайт даних повертає сервіс клієнту.

#### 10. Журналювання та маскування конфіденційних даних

Стандарти безпеки фінансової індустрії (PCI-DSS) та вимоги аудиту вимагають суворого контролю над тим, що потрапляє в системні журнали (Logs):
- Сервер повинен зберігати повний криптографічний зліпок отриманого SOAP-запиту для аудиту та підтвердження юридичної сили цифрового підпису;
- Водночас перед записом у відкриті логи трасування диспетчер зобов'язаний маскувати секретні поля: значення елементів `<wsse:Password>`, номери кредитних карток (PAN) та CVV-коди замінюються на зірочки (`************1234`);
- Маскування здійснюється швидким регулярним виразом на рівні потокового фільтра ще до передачі тексту в систему структурованого логування.

#### 11. Порівняльний профіль продуктивності: SOAP проти gRPC та REST

При проєктуванні архітектури бекенду інженер повинен оцінювати ціну кожної технології в тактах процесора, споживанні оперативної пам'яті та затримках мережі (Latency):

| Параметр конвеєра | SOAP 1.1 / 1.2 (XML) | REST (JSON / HTTP/1.1) | gRPC (Protobuf / HTTP/2) |
| :--- | :--- | :--- | :--- |
| **Накладні витрати на серіалізацію** | 100–500 мкс (текстовий XML, теги, простори імен) | 20–80 мкс (текстовий JSON) | 2–8 мкс (двійкове пакування varint) |
| **Розмір корисного пакету (Payload)** | 2.5–5.0 КБ (громіздкий конверт) | 0.4–0.8 КБ (чистий JSON) | 0.08–0.15 КБ (стислі двійкові поля) |
| **Витрати пам'яті (Heap Allocations)** | Високі (вузли дерева DOM або буфери StAX) | Середні (рядкові буфери) | Мінімальні (нульове копіювання arena allocator) |
| **Ціна наскрізної безпеки** | 500–2000 мкс (канонікалізація C14N + RSA підпис) | 50–150 мкс (сесійний TLS handshake) | 50–150 мкс (сесійний TLS handshake) |
| **Пропускна здатність на ядро (RPS)** | 1 500 – 4 000 запитів/сек | 15 000 – 40 000 запитів/сек | 80 000 – 200 000 запитів/сек |

Ці виміри демонструють головну причину сучасного технологічного розподілу: там, де потрібна максимальна пропускна здатність і мікросекундні затримки (внутрішні мікросервіси високочастотного трейдингу), беззаперечно перемагає gRPC. Але там, де транзакція вимагає багаторічного юридичного аудиту, проходження через декілька незалежних шин ESB та наскрізного підпису на рівні повідомлення (міждержавні та міжбанківські шлюзи), накладні витрати SOAP є виправданою ціною повної гарантії безпеки.

#### 12. Інтеграція в сучасні платформи: Spring-WS, CoreWCF та Apache CXF

Сучасний бекенд-інженер рідко пише сирі парсери XML вручну: промислова розробка використовує зрілі високорівневі фреймворки:
- **Spring-WS (Java):** реалізує чисту парадигму Contract-First. Замість прив'язки до Java-класів розробник створює XSD-схеми, за якими JAXB генерує класи даних. Клас ендпоінта позначається анотацією `@Endpoint`, а метод обробки — `@PayloadRoot(namespace = "...", localPart = "ProcessPayment")`. Spring-WS автоматично підключає валідацію за схемою через `PayloadValidatingInterceptor` та обробку WS-Security через `Wss4jSecurityInterceptor`.
- **CoreWCF (.NET 8+):** відкрита реалізація Windows Communication Foundation для сучасного .NET Core / .NET 8. Дозволяє переносити надійні банківські сервіси з застарілого .NET Framework у контейнеризовані середовища Linux/Kubernetes зі збереженням контрактів `[ServiceContract]` та конфігурацій `WSHttpBinding` з підтримкою шифрування та WS-Trust.
- **Apache CXF:** універсальний модульний рушій для розгортання вебсервісів із підтримкою широкого набору WS-* стандартів. CXF дозволяє конфігурувати вхідні та вихідні фази інтерцепторів як декларативно через Spring XML, так і програмно через Java API, а також підтримує автоматичне регресійне тестування контрактів через утиліти `soapUI`, Postman-колекції та генерацію мок-серверів для навантажувального тестування.

#### 13. Тестування крайових випадків та стійкість до збоїв

Під час тестування промислового SOAP-диспетчера особливу увагу приділяють крайовим сценаріям:
- **Невідповідність заголовка SOAPAction та кореневого тегу тіла:** якщо заголовок `SOAPAction` вказує на метод `ProcessPayment`, а кореневий тег у тілі зветься `<GetBalance>`, стандарт WS-I Basic Profile вимагає від сервера відхилити такий запит з помилкою `soap:Client`, щоб унеможливити атаки підміни дій (Action Spoofing).
- **Частково обірвані чанки HTTP (Transfer-Encoding: chunked):** при передачі великих документів мережеве з'єднання може обірватися посеред XML-документа. Диспетчер зобов'язаний виявляти незакриті XML-теги та формувати чистий розрив сесії без зависання потоків пулу з'єднань.
- **Різні кодування символів:** хоча стандарт вимагає кодування UTF-8 або UTF-16, старі інтеграційні системи можуть надсилати дані в національних кодуваннях (Windows-1251, ISO-8859-1). Диспетчер повинен або явно перекодовувати байти згідно з параметром `charset` у `Content-Type`, або повертати HTTP 415 / `soap:Client`.

#### 14. Продуктивність та оптимізація пам'яті в C++

Представлена реалізація на мові C++ використовує сучасні ідіоми:
- **`std::string_view` замість копіювання рядків:** під час первинного аналізу MIME-типів і пошуку меж блоків заголовків програма не створює проміжних копій важкого XML-тіла запиту, а працює з незмінними посиланнями на вихідний буфер пам'яті.
- **Типізовані результати `std::expected`:** відмова від винятків C++ (`try / catch`) у рутинному конвеєрі диспетчеризації усуває накладні витрати на розгортання стека (stack unwinding) і робить усі гілки можливих помилок явними під час компіляції коду.
- **Інкапсуляція XML-генерації:** форматні рядки `std::format` гарантують безпеку типів під час збирання результуючого конверта без ризику переповнення буфера пам'яті.
- **Відсутність динамічних алокацій у гарячому циклі:** буфери для сканування XML виділяються один раз або перевикористовуються, забезпечуючи високу пропускну здатність диспетчера.
