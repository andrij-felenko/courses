#include <Arduino.h>

// Перелічення типів відповідей для FSM парсера
enum class AtResponseType {
    Payload,
    Ok,
    Error,
    Fail,
    Busy,
    Urc
};

class AtResponseClassifier {
public:
    static AtResponseType classify(const String& line) {
        String trimmed = line;
        trimmed.trim(); // Видалення пробілів та \r\n

        if (trimmed == "OK") return AtResponseType::Ok;
        if (trimmed == "ERROR") return AtResponseType::Error;
        if (trimmed == "FAIL") return AtResponseType::Fail;
        if (trimmed.startsWith("busy") || trimmed.startsWith("BUSY")) return AtResponseType::Busy;

        // Виявлення незапитаних асинхронних подій URC
        if (trimmed.startsWith("WIFI ") || 
            trimmed == "ready" || 
            trimmed.startsWith("+IPD,")) {
            return AtResponseType::Urc;
        }

        return AtResponseType::Payload;
    }
};
