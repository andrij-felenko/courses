# ⚙️ Розробка власного модуля PAM: від SPI-точок входу до динамічного завантаження

Розробка власного модуля для платформи PAM реалізується як динамічно завантажувана бібліотека `.so`, яка розширює системний стек безпеки Linux кастомними механізмами автентифікації — перевіркою криптографічних токенів, двофакторною автентифікацією через одноразові паролі (TOTP), апаратними ключами YubiKey або інтеграцією з корпоративним REST API. Модуль взаємодіє з бібліотекою `libpam` через інтерфейс провайдера послуг (Service Provider Interface, SPI), експортуючи стандартизовані C-функції для перевірки даних користувача, керування сесіями та обробки фаз автентифікації.

## Практична доцільність та сценарії застосування

У системному програмуванні для Linux потреба в написанні власного модуля PAM виникає у таких ситуаціях:

1. **Інтеграція з корпоративною Identity Provider (IdP):** Якщо організація використовує власний внутрішній сервіс авторизації (наприклад, OAuth2/OIDC або REST API), модуль PAM може перехоплювати спробу входу через SSH чи `sudo`, відправляти HTTPS-запит до серверного API та приймати рішення на основі відповіді.
2. **Апаратні фактори доступу:** Створення модуля для зчитування даних зі спеціалізованих USB-токенів, смарт-карток або криптографічних модулів HSM (Hardware Security Module).
3. **Контроль доступу за біометрією або геолокацією:** Створення додаткового рубежу захисту, який перевіряє IP-адресу, розпізнає відбиток пальця чи перевіряє наявність підключеного Bluetooth-пристрою поруч із сервером.
4. **Кастомне лімітування та захист від brute-force:** Впровадження специфічних правил локування облікових записів або динамічного затримування відповідей залежно від навантаження на систему.

## Контракт інтерфейсу SPI (Service Provider Interface)

На відміну від прикладних програм, які викликають високорівневі функції `pam_authenticate()` або `pam_acct_mgmt()`, модуль PAM є сервісним провайдером. Бібліотека `libpam.so` завантажує `.so` модуль через виклик `dlopen()` і шукає в ньому стандартизовані C-символи з префіксом `pam_sm_` (Service Module).

Динамічний модуль повинен експортувати точки входу для тих фаз, які він підтримує:

- `pam_sm_authenticate(pamh, flags, argc, argv)` — виконує перевірку токена автентифікації користувача (фаза `auth`).
- `pam_sm_setcred(pamh, flags, argc, argv)` — встановлює, поновлює або видаляє облікові дані користувача (фаза `auth`).
- `pam_sm_acct_mgmt(pamh, flags, argc, argv)` — перевіряє стан та термін дії облікового запису (фаза `account`).
- `pam_sm_open_session(pamh, flags, argc, argv)` — ініціалізує сесійне середовище (фаза `session`).
- `pam_sm_close_session(pamh, flags, argc, argv)` — вивільняє сесійні ресурси (фаза `session`).
- `pam_sm_chauthtok(pamh, flags, argc, argv)` — керує процедурою зміни пароля (фаза `password`).

Кожна функція модуля приймає чотири параметри:
1. `pamh` (`pam_handle_t*`): Непрозорий дескриптор поточної сесії PAM.
2. `flags` (`int`): Бітова маска прапорців виклику (наприклад, `PAM_SILENT`).
3. `argc` (`int`): Кількість аргументів, переданих модулю в рядочку конфігураційного файла `/etc/pam.d/`.
4. `argv` (`const char**`): Масив рядків-аргументів (наприклад, `["pin=9988", "debug"]`).

## Детальний розбір алгоритму роботи модуля

Для безпечної роботи модуль PAM повинен дотримуватися суворого алгоритму взаємодії з дескриптором PAM та пам'яттю:

1. **Отримання імені користувача:** Модуль звертається до функції `pam_get_user(pamh, &username, prompt)`. Якщо ім'я ще не встановлено, `pam_get_user` самостійно запитає його через функцію розмови `pam_conv`.
2. **Парсинг аргументів конфігурації:** Модуль ітерується за масивом `argv`, витягуючи налаштування (шляхи до конфігураційних файлів, секретні PIN-коди, прапорці налагодження `debug`).
3. **Отримання функції розмови:** Через виклик `pam_get_item(pamh, PAM_CONV, &conv)` модуль отримує вказівник на структуру `struct pam_conv`, надану прикладним застосунком.
4. **Виконання запиту до користувача:** Модуль формує масив `struct pam_message` із запитом (наприклад, `"Enter Security PIN: "`) та стилем `PAM_PROMPT_ECHO_OFF`. Викликаючи `conv->conv()`, модуль отримує від застосунку відповідь `struct pam_response`.
5. **Валідація та перевірка:** Введений токен порівнюється з очікуваним значенням. Якщо токен некоректний, модуль занотовує факт помилки у системний журнал за допомогою `pam_syslog(pamh, LOG_WARNING, ...)` і повертає код `PAM_AUTH_ERR`.
6. **Очищення секретів у пам'яті:** Перед звільненням буфера відповіді модуль **зобов'язаний затерти чутливі дані** в пам'яті за допомогою `explicit_bzero()` або `memset_s()`. Звичайний виклик `free()` залишає секретні рядки в купі (heap), що дозволяє зчитати їх при аналізі дампів пам'яті (core dump).

## Повна реалізація кастомного модуля: C та C++

Нижче наведено практичну реалізацію модуля `pam_custom_pin.so`, який підтримує перевірку кастомного PIN-коду, переданого в аргументах конфігурації.

:::tabs
```c
/* Модуль PAM мовою C: pam_custom_pin.c */
#define PAM_SM_AUTH
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <security/pam_modules.h>
#include <security/pam_ext.h>

PAM_EXTERN int pam_sm_authenticate(pam_handle_t *pamh, int flags,
                                   int argc, const char **argv) {
    const char *username = NULL;
    int retval = pam_get_user(pamh, &username, "Username: ");
    if (retval != PAM_SUCCESS || !username) {
        return PAM_USER_UNKNOWN;
    }

    /* Зчитування аргументу модуля з /etc/pam.d/ (наприклад, pin=1234) */
    const char *expected_pin = "1234";
    for (int i = 0; i < argc; ++i) {
        if (strncmp(argv[i], "pin=", 4) == 0) {
            expected_pin = argv[i] + 4;
        }
    }

    /* Отримання функції розмови від прикладного застосунку */
    const struct pam_conv *conv = NULL;
    retval = pam_get_item(pamh, PAM_CONV, (const void **)&conv);
    if (retval != PAM_SUCCESS || !conv || !conv->conv) {
        return PAM_CONV_ERR;
    }

    /* Формування запиту до користувача */
    struct pam_message msg;
    const struct pam_message *pmsg = &msg;
    struct pam_response *resp = NULL;

    msg.msg_style = PAM_PROMPT_ECHO_OFF;
    msg.msg = "Enter Security PIN: ";

    retval = conv->conv(1, &pmsg, &resp, conv->appdata_ptr);
    if (retval != PAM_SUCCESS || !resp || !resp->resp) {
        if (resp) free(resp);
        return PAM_AUTH_ERR;
    }

    /* Перевірка PIN-коду */
    int auth_res = PAM_AUTH_ERR;
    if (strcmp(resp->resp, expected_pin) == 0) {
        auth_res = PAM_SUCCESS;
    } else {
        pam_syslog(pamh, LOG_WARNING, "Invalid PIN attempt for user %s", username);
    }

    /* Очищення чутливих даних у пам'яті за допомогою explicit_bzero */
    explicit_bzero(resp->resp, strlen(resp->resp));
    free(resp->resp);
    free(resp);

    return auth_res;
}

PAM_EXTERN int pam_sm_setcred(pam_handle_t *pamh, int flags,
                              int argc, const char **argv) {
    return PAM_SUCCESS;
}
```
```cpp
// Модуль PAM мовою C++20 з C ABI експортом: pam_custom_pin.cpp
#define PAM_SM_AUTH
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <cstring>
#include <memory>
#include <security/pam_modules.h>
#include <security/pam_ext.h>

namespace {
    // Автоматичний deleter для безпечного очищення та звільнення pam_response
    struct PamResponseDeleter {
        void operator()(struct pam_response* resp) const {
            if (resp) {
                if (resp->resp) {
                    ::explicit_bzero(resp->resp, ::strlen(resp->resp));
                    ::free(resp->resp);
                }
                ::free(resp);
            }
        }
    };
}

extern "C" {

PAM_EXTERN int pam_sm_authenticate(pam_handle_t *pamh, int flags,
                                   int argc, const char **argv) {
    const char *raw_user = nullptr;
    if (pam_get_user(pamh, &raw_user, "Username: ") != PAM_SUCCESS || !raw_user) {
        return PAM_USER_UNKNOWN;
    }
    std::string_view username{raw_user};

    std::string_view expected_pin = "1234";
    for (int i = 0; i < argc; ++i) {
        std::string_view arg{argv[i]};
        if (arg.starts_with("pin=")) {
            expected_pin = arg.substr(4);
        }
    }

    const struct pam_conv *conv = nullptr;
    if (pam_get_item(pamh, PAM_CONV, reinterpret_cast<const void**>(&conv)) != PAM_SUCCESS || !conv || !conv->conv) {
        return PAM_CONV_ERR;
    }

    struct pam_message msg{.msg_style = PAM_PROMPT_ECHO_OFF, .msg = "Enter Security PIN: "};
    const struct pam_message *pmsg = &msg;
    struct pam_response *raw_resp = nullptr;

    if (conv->conv(1, &pmsg, &raw_resp, conv->appdata_ptr) != PAM_SUCCESS || !raw_resp || !raw_resp->resp) {
        return PAM_AUTH_ERR;
    }

    std::unique_ptr<struct pam_response, PamResponseDeleter> resp(raw_resp);

    if (expected_pin == resp->resp) {
        return PAM_SUCCESS;
    }

    pam_syslog(pamh, LOG_WARNING, "Invalid PIN attempt for user %.*s",
               static_cast<int>(username.size()), username.data());
    return PAM_AUTH_ERR;
}

PAM_EXTERN int pam_sm_setcred(pam_handle_t *pamh, int flags,
                              int argc, const char **argv) {
    return PAM_SUCCESS;
}

} // extern "C"
```
:::

## Правила потокобезпечності та ізоляції пам'яті

При розробці системних модулів PAM критично важливо утримуватися від типових помилок кодування:

1. **Заборона глобального стану:** Оскільки бібліотека `libpam` може завантажуватися у багатопотокових демонах (наприклад, у веб-серверах або високонавантажених серверах SSH), модуль **не повинен використовувати глобальних несинхронізованих змінних**. Якщо модулю потрібен стан між викликами, його слід зберігати в контексті PAM через `pam_set_data()` або використовувати локальну пам'ять потоку (`thread_local`).
2. **Захист від неперехоплених винятків (Exceptions):** У коді мовою C++ уся логіка всередині експортованих `extern "C"` функцій повинна огортатися в блок `try { ... } catch (...)`. Якщо виняток C++ вилетить за межі C ABI кордону модуля, це призведе до негайного аварійного завершення (`std::terminate`) всієї прикладної програми (наприклад, демона `sshd`), створивши можливість для атаки на відмову в обслуговуванні (DoS).
3. **Безпечне журналювання:** Для логування слід використовувати функцію `pam_syslog()`. Категорично заборонено виводити в журнал вхідні паролі чи секретні токени користувача.

## Компільована збірка та встановлення

Модуль PAM є динамічною бібліотекою, яка повинна компілюватися як позиційно-незалежний код (Position-Independent Code) та збиратися прапорцем `-shared`.

```bash
# Збірка C-версії модуля
gcc -fPIC -c pam_custom_pin.c -o pam_custom_pin.o
gcc -shared -o pam_custom_pin.so pam_custom_pin.o -lpam

# Збірка C++20-версії модуля
g++ -std=c++20 -fPIC -c pam_custom_pin.cpp -o pam_custom_pin.o
g++ -shared -o pam_custom_pin.so pam_custom_pin.o -lpam

# Встановлення в системну директорію модулів PAM
sudo cp pam_custom_pin.so /lib/x86_64-linux-gnu/security/
sudo chmod 644 /lib/x86_64-linux-gnu/security/pam_custom_pin.so
```

## Тестування в конфігурації /etc/pam.d/

Під час виконання прикладної програми автентифікації бібліотека `libpam` зчитує конфігурацію відповідного сервісу з каталогу `/etc/pam.d/`. Знайшовши задекларований рядок модуля, `libpam` через системний виклик `dlopen()` динамічно завантажує бібліотеку `pam_custom_pin.so` в адресний простір процесу, за допомогою `dlsym()` знаходить експортовану точку входу `pam_sm_authenticate` та викликає її, передаючи аргумент `pin=9988`.

Для тестування створеного модуля додаємо його в конфігураційний файл тестувального сервісу (наприклад, `/etc/pam.d/check_service`):

```pam
# /etc/pam.d/check_service
auth       required     pam_custom_pin.so pin=9988
auth       required     pam_unix.so
account    required     pam_unix.so
```

## Методика налагодження та аналізу помилок

Налагодження модулів PAM ускладнюється тим, що вони виконуються всередині сторонніх процесів. Для ефективної відладки використовують такі підходи:

- **Використання прапорця `debug`:** Модуль повинен аналізувати наявність аргументу `"debug"` у `argv` та вмикати розширене виведення діагностичних повідомлень у `syslog`.
- **Запуск утиліти `pamtester`:** Спеціалізована системна утиліта `pamtester` дозволяє тестувати довільні стеки PAM без запуску реальних демонів:
  ```bash
  pamtester check_service user_test authenticate
  ```
- **Відладка через gdb:** Для покрокового аналізу роботи модуля підключають відлагоджувач `gdb` до тестової програми з встановленням точок зупинки на функції модуля після виклику `dlopen()`.
