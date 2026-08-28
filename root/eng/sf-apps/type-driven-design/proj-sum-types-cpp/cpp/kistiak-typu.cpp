#include <variant>
#include <string>
#include <cstdint>

struct Data {                    // те, що зрештою отримали (умовно)
    int32_t  code;
    uint16_t length;
};

struct Loading {};                             // жодного поля — сам факт «триває»
struct Failed  { std::string message;          // текст помилки для лога/екрана
                 int          httpCode; };      // і код відповіді, якщо був
struct Ready   { Data value; };                // лише корисне навантаження

using RequestState = std::variant<Loading, Failed, Ready>;
