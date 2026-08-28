#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Еквівалентна C-модель обробки помилок через статусний код
typedef struct {
    int is_error;
    char message[128];
} c_status_t;

c_status_t parse_config_file_c(const char* path) {
    c_status_t status = {0, ""};
    if (path == NULL || strlen(path) == 0) {
        status.is_error = 1;
        strncpy(status.message, "Конфігураційний шлях порожній", sizeof(status.message) - 1);
    }
    return status;
}

void execute_safe_operation_c(void) {
    c_status_t res = parse_config_file_c("");
    if (res.is_error) {
        printf("C-style помилка: %s\n", res.message);
    }
}
:::

---

## 5. Інтеграція системних помилок операційної системи: std::system_error, std::error_code та std::error_category

До появу стандарту C++11 розробники системного коду були змушені вручну форматувати числові коди системних помилок (POSIX `errno` або Windows `GetLastError()`) у текстові рядки перед створенням винятку `std::runtime_error`. Це призводило до витоків пам'яті та унеможливлювало програмну перевірку типів помилок у блоках `catch`.

Стандарт C++11 розв'язав цю проблему через запровадження винятку `std::system_error`, який поєднує поліморфізм C++ із детермінованими кодами помилок операційної системи.

![Макет пам'яті std::system_error](img/exception-memory-layout.svg)
*Анатомія std::system_error: поєднання коду помилки, статичної категорії та динамічно сформованого повідомлення what().*

### Структура std::error_code та категорій помилок

Об'єкт `std::system_error` містить всередині легковаговий екземпляр `std::error_code`, який складається з двох елементів:
