# 📋 Функції libpam: як програма запускає стек і що дістає назад

Це довідка з того, чим програма керує PAM зі свого коду: які функції заводять розмову й проходять кожен зі стеків, які прапорці та елементи передають туди й назад, з яких структур складається розмовник і що означає число, яке зрештою повертається. Наприкінці — робочий приклад на C і C++.

## Базовий API застосунку (Application API)

Прикладна програма (наприклад, сервер `sshd` чи утиліта `sudo`) взаємодіє з PAM через набір функцій високого рівня. Усі виклики приймають або повертають непрозорий вказівник на дескриптор сесії `pam_handle_t`, який зберігає внутрішній стан обчислювача, накопичений статус помилок та елементи оточення.

### 1. pam_start() — Ініціалізація сесії PAM
Функція `pam_start()` створює новий контекст автентифікації PAM. Вона читає конфігураційний файл відповідного сервісу з каталогу `/etc/pam.d/` та готує внутрішні структури даних.

```c
int pam_start(
    const char *service_name,
    const char *user,
    const struct pam_conv *pam_conversation,
    pam_handle_t **pamh
);
```

- `service_name`: Рядок з іменем сервісу, що збігається з назвою файла конфігурації у `/etc/pam.d/` (наприклад, `"sshd"`, `"sudo"`, `"login"`). Якщо названий файл відсутній, бібліотека звертається до файлу `/etc/pam.d/other`.
- `user`: Запитане ім'я користувача. Якщо значення дорівнює `NULL`, модуль автентифікації запитає ім'я у користувача пізніше через розмовника `pam_conv`.
- `pam_conversation`: Вказівник на структуру `struct pam_conv`, яка містить callback-функцію для зворотного зв'язку з користувачем.
- `pamh`: Вказівник на змінну типу `pam_handle_t*`, у яку `pam_start()` записує адресу виділеного контексту.
- **Код повернення:** Повертає `PAM_SUCCESS` при успішній ініціалізації. У разі помилок зчитування конфігурації або виділення пам'яті повертає `PAM_ABORT`, `PAM_BUF_ERR` або `PAM_SYSTEM_ERR`.

### 2. pam_authenticate() та pam_setcred() — Автентифікація та встановлення привілеїв
Після успішної ініціалізації застосунок викликає `pam_authenticate()` для виконання фази `auth`. Двигун `libpam` послідовно виконує всі модулі, задекларовані у відповідному стеку.

```c
int pam_authenticate(pam_handle_t *pamh, int flags);
int pam_setcred(pam_handle_t *pamh, int flags);
```

- `flags` для `pam_authenticate()`:
  - `PAM_SILENT`: Придушити вивід текстових повідомлень модуля до користувача.
  - `PAM_DISALLOW_NULL_AUTHTOK`: Повернути помилку, якщо токен автентифікації порожній.
- `flags` для `pam_setcred()`:
  - `PAM_ESTABLISH_CRED`: Встановити облікові дані користувача (групи, квитки Kerberos).
  - `PAM_REINITIALIZE_CRED`: Скинути та заново ініціалізувати облікові дані.
  - `PAM_DELETE_CRED`: Видалити встановлені облікові дані при виході.
  - `PAM_REFRESH_CRED`: Оновити термін дії токена (наприклад, продовжити квиток Kerberos).

### 3. pam_acct_mgmt() — Перевірка стану облікового запису
Після успішної автентифікації у фазі `auth` застосунок запускає фазу `account` для перевірки статусу запису. Функція `pam_acct_mgmt()` передає керування модулям, які перевіряють, чи не закінчився термін дії пароля користувача, чи не заблоковано обліковий запис через перевищення невдалих спроб входу (`pam_faillock.so`) та чи дозволено вхід у поточний час доби чи з даного термінала (`pam_time.so`). Якщо термін дії пароля вичерпано, функція повертає код `PAM_NEW_AUTHTOK_REQD`, що сигналізує застосунку про необхідність викликати `pam_chauthtok()`.

```c
int pam_acct_mgmt(pam_handle_t *pamh, int flags);
```

### 4. pam_open_session() та pam_close_session() — Управління сеансом
Перед наданням користувачеві доступного сеансу та оболонки необхідно підготувати системне середовище, а при виході — впорядковано звільнити надані ресурси. Під час виклику `pam_open_session()` модулі фази `session` монтують домашні каталоги чи зашифровані розділи (`pam_mount.so`), налаштовують ліміти системних ресурсів `rlimit` (`pam_limits.so`), створюють сесійні зв'язки ключів у ядрі (`pam_keyinit.so`), ізолюють процес у cgroups (`pam_systemd.so`) та записують події в системні журнали `utmp/wtmp` (`pam_lastlog.so`). Виклик `pam_close_session()` розмонтовує ресурси, видаляє тимчасові каталоги та реєструє факт завершення сесії.

```c
int pam_open_session(pam_handle_t *pamh, int flags);
int pam_close_session(pam_handle_t *pamh, int flags);
```

### 5. pam_end() — Завершення сесії та звільнення пам'яті
Після завершення роботи із сесією застосунок викликає `pam_end()` для остаточного звільнення ресурсів. Ця функція не просто видаляє структуру `pam_handle_t`, а й передає підсумковий код стану `pam_status` усім завантаженим модулям PAM. Модулі використовують цей код для виконання власних очисних процедур — закриття файлових дескрипторів, видалення сесійних токенів із пам'яті або скасування тимчасових блокувань.

```c
int pam_end(pam_handle_t *pamh, int pam_status);
```

- `pam_status`: Останній код повернення, отриманий застосунком від попередніх викликів PAM (наприклад, `PAM_SUCCESS` чи `PAM_AUTH_ERR`), на основі якого модулі виконують очищення.

## Управління атрибутами сесії (pam_get_item / pam_set_item)

Оскільки динамічні модулі PAM виконуються як окремі об'єкти без спільних глобальних змінних, єдиним засобом збереження контексту сесії є дескриптор `pam_handle_t`. Протягом життя сесії застосунок та модулі обмінюються даними через функцію запису `pam_set_item()` та функцію читання `pam_get_item()`. Модулі використовують цей механізм для збереження імен користувачів (`PAM_USER`), точок розмови (`PAM_CONV`), назв терміналів (`PAM_TTY`) або для кешування введеного пароля в атрибуті `PAM_AUTHTOK`: якщо перший модуль у стеку отримав пароль через `pam_conv`, він зберігає його за допомогою `pam_set_item(pamh, PAM_AUTHTOK, pass)`, дозволяючи наступним модулям стеку читати пароль без повторного турбування користувача.

```c
int pam_set_item(pam_handle_t *pamh, int item_type, const void *item);
int pam_get_item(const pam_handle_t *pamh, int item_type, const void **item);
```

### Основні типи атрибутів (`item_type`):
- `PAM_USER` (`const char*`): Ім'я користувача, що автентифікується.
- `PAM_SERVICE` (`const char*`): Назва сервісу (наприклад, `"sshd"`).
- `PAM_TTY` (`const char*`): Назва термінального пристрою (наприклад, `"tty1"` або `"pts/0"`).
- `PAM_RHOST` (`const char*`): Назва або IP-адреса віддаленого хоста, з якого здійснюється підключення.
- `PAM_CONV` (`const struct pam_conv*`): Вказівник на поточну структуру розмови.
- `PAM_AUTHTOK` (`const char*`): Введений користувачем токен автентифікації (пароль).
- `PAM_OLDAUTHTOK` (`const char*`): Старий пароль при виконанні процедури зміни пароля.
- `PAM_RUSER` (`const char*`): Ім'я віддаленого користувача, який ініціював запит.
- `PAM_USER_PROMPT` (`const char*`): Текст підказки для запиту імені користувача.

## Допоміжний API для отримання паролів (pam_get_authtok)

Коли у стеку задіяно кілька модулів автентифікації, повторний запит пароля через інтерактивний діалог створить незручності для користувача. Для уніфікації отримання паролів та усунення дублювання викликів розмовника `pam_conv` у Linux-PAM розроблено допоміжну функцію `pam_get_authtok()`. Вона автоматично перевіряє, чи не збережено вже пароль у внутрішньому кеші в атрибуті `PAM_AUTHTOK`. Якщо пароль відсутній, вона самостійно викликає розмовника `pam_conv`, запитує пароль у користувача, зберігає його в атрибуті `PAM_AUTHTOK` та повертає вказівник у змінній `authtok`.

```c
int pam_get_authtok(
    pam_handle_t *pamh,
    int item_type,
    const char **authtok,
    const char *prompt
);
```

## Управління змінними оточення (Environment API)

Бібліотека PAM дозволяє модулям формувати списки змінних оточення, які надалі передаються командній оболонці користувача (наприклад, `PATH`, `XDG_RUNTIME_DIR`, `KRB5CCNAME`).

```c
int pam_putenv(pam_handle_t *pamh, const char *name_value);
const char *pam_getenv(pam_handle_t *pamh, const char *name);
char **pam_getenvlist(pam_handle_t *pamh);
```

- `pam_putenv()` долучає змінну у форматі `"NAME=VALUE"`. Якщо передати `"NAME"`, змінну буде видалено з оточення PAM.
- `pam_getenvlist()` повертає масив рядків, заповнений усіма встановленими модулями змінними. Застосунок зобов'язаний самостійно вивільнити пам'ять масиву та кожного рядка після використання.

## Розмовник: структури, якими модуль питає людину

Розмовника застосунок передає у `pam_start()` для надання модулям можливості запитувати інтерактивне введення у користувача через GUI чи CLI.

```c
struct pam_message {
    int msg_style;
    const char *msg;
};

struct pam_response {
    char *resp;
    int resp_retcode;
};

struct pam_conv {
    int (*conv)(int num_msg, const struct pam_message **msg,
                struct pam_response **resp, void *appdata_ptr);
    void *appdata_ptr;
};
```

### Хто виділяє й хто звільняє пам'ять розмови
1. Модуль формує масив вказівників на `struct pam_message` розміром `num_msg` і передає його у функцію `conv()`.
2. Застосунок виділяє масив структур `struct pam_response` розміром `num_msg` за допомогою `calloc()` або `malloc()`.
3. Для кожного запиту стилю `PAM_PROMPT_ECHO_OFF` або `PAM_PROMPT_ECHO_ON` застосунок виділяє динамічний рядок `strdup()` і записує його в `resp[i].resp`.
4. Модуль отримує відповіді, зчитує дані, після чого **зобов'язаний очистити чутливі рядки в пам'яті** (`explicit_bzero`) та вивільнити пам'ять масиву й кожного рядка через `free()`.

Стилі повідомлень (`msg_style`):
- `PAM_PROMPT_ECHO_OFF` (1): Запит введення без відображення символів (для паролів та PIN-кодів).
- `PAM_PROMPT_ECHO_ON` (2): Запит введення з відображенням (для імені користувача чи одноразового коду).
- `PAM_ERROR_MSG` (3): Вивід текстового повідомлення про помилку.
- `PAM_TEXT_INFO` (4): Вивід інформаційного повідомлення чи інструкції.

## Приклад виклику API PAM: C та C++

У разі роботи з PAM у мові C++ виклики функцій `pam_start()` та `pam_end()` огортаються в RAII-контейнер для гарантованого звільнення ресурсів при виникненні винятків.

:::tabs
```c
/* Приклад автентифікації консольної програми мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <security/pam_appl.h>

static int sample_conv(int num_msg, const struct pam_message **msg,
                       struct pam_response **resp, void *appdata_ptr) {
    if (num_msg <= 0 || num_msg > PAM_MAX_NUM_MSG) return PAM_CONV_ERR;
    
    struct pam_response *reply = calloc(num_msg, sizeof(struct pam_response));
    if (!reply) return PAM_BUF_ERR;

    for (int i = 0; i < num_msg; ++i) {
        if (msg[i]->msg_style == PAM_PROMPT_ECHO_OFF) {
            printf("%s", msg[i]->msg);
            char buffer[256];
            if (fgets(buffer, sizeof(buffer), stdin)) {
                buffer[strcspn(buffer, "\n")] = '\0';
                reply[i].resp = strdup(buffer);
            }
        }
    }
    *resp = reply;
    return PAM_SUCCESS;
}

int authenticate_user(const char *username) {
    pam_handle_t *pamh = NULL;
    struct pam_conv conv = { sample_conv, NULL };

    int retval = pam_start("check_service", username, &conv, &pamh);
    if (retval != PAM_SUCCESS) return retval;

    retval = pam_authenticate(pamh, 0);
    if (retval == PAM_SUCCESS) {
        retval = pam_acct_mgmt(pamh, 0);
    }

    pam_end(pamh, retval);
    return retval;
}
```
```cpp
// Ідіоматичний RAII-обгортка PAM мовою C++20
#include <iostream>
#include <memory>
#include <string>
#include <cstring>
#include <expected>
#include <vector>
#include <utility>
#include <security/pam_appl.h>

class PamSession {
public:
    static std::expected<PamSession, int> create(const std::string& service, const std::string& user, const struct pam_conv* conv) {
        pam_handle_t* handle = nullptr;
        int rc = pam_start(service.c_str(), user.c_str(), conv, &handle);
        if (rc != PAM_SUCCESS) return std::unexpected(rc);
        return PamSession(handle);
    }

    ~PamSession() {
        if (handle_) {
            pam_end(handle_, last_status_);
        }
    }

    PamSession(const PamSession&) = delete;
    PamSession& operator=(const PamSession&) = delete;
    PamSession(PamSession&& other) noexcept : handle_(std::exchange(other.handle_, nullptr)), last_status_(other.last_status_) {}

    int authenticate(int flags = 0) {
        last_status_ = pam_authenticate(handle_, flags);
        return last_status_;
    }

    int check_account(int flags = 0) {
        last_status_ = pam_acct_mgmt(handle_, flags);
        return last_status_;
    }

private:
    explicit PamSession(pam_handle_t* handle) : handle_(handle), last_status_(PAM_SUCCESS) {}
    pam_handle_t* handle_{nullptr};
    int last_status_{PAM_SUCCESS};
};

static int cpp_conv(int num_msg, const struct pam_message **msg,
                    struct pam_response **resp, void *appdata_ptr) {
    if (num_msg <= 0) return PAM_CONV_ERR;
    auto* reply = static_cast<struct pam_response*>(calloc(num_msg, sizeof(struct pam_response)));
    if (!reply) return PAM_BUF_ERR;

    for (int i = 0; i < num_msg; ++i) {
        if (msg[i]->msg_style == PAM_PROMPT_ECHO_OFF) {
            std::cout << msg[i]->msg;
            std::string pass;
            std::cin >> pass;
            reply[i].resp = strdup(pass.c_str());
        }
    }
    *resp = reply;
    return PAM_SUCCESS;
}

std::expected<void, int> verify_credentials(const std::string& username) {
    struct pam_conv conv = { cpp_conv, nullptr };
    auto session = PamSession::create("check_service", username, &conv);
    if (!session) return std::unexpected(session.error());

    if (int rc = session->authenticate(); rc != PAM_SUCCESS) return std::unexpected(rc);
    if (int rc = session->check_account(); rc != PAM_SUCCESS) return std::unexpected(rc);

    return {};
}
```
:::

## Таблиця стандартних кодів повернення PAM

Кожна функція бібліотеки PAM повертає цілочисельний код стану. Отримане значення можна перетворити на локалізований текстовий опис за допомогою функції `pam_strerror(pamh, errnum)`. Ті самі коди мають ще й короткі імена-токени — ними їх називають у квадратних дужках рядка налаштувань (`success`, `auth_err`, `authinfo_unavail`), і повний перелік разом із діями лежить у [довідці з формату](topic:sys-unix/pam-stack/api-pam-config.md).

| Символьна константа | Числовий код | Опис значення |
| :--- | :--- | :--- |
| `PAM_SUCCESS` | 0 | Успішне виконання операції |
| `PAM_OPEN_ERR` | 1 | Помилка завантаження динамічного модуля (`dlopen`) |
| `PAM_SYMBOL_ERR` | 2 | Не знайдено необхідний символ у модулі (`dlsym`) |
| `PAM_SERVICE_ERR` | 3 | Помилка в конфігураційному файлі сервісу |
| `PAM_SYSTEM_ERR` | 4 | Збій у системних ресурсах (наприклад, брак пам'яті) |
| `PAM_BUF_ERR` | 5 | Помилка виділення буфера пам'яті |
| `PAM_PERM_DENIED` | 6 | Доступ заборонено системною політикою |
| `PAM_AUTH_ERR` | 7 | Невірна автентифікаційна інформація (невірний пароль) |
| `PAM_CRED_INSUFFICIENT` | 8 | Недостатньо облікових даних для підтвердження особи |
| `PAM_AUTHINFO_UNAVAIL` | 9 | Сервер автентифікації недоступний (наприклад, LDAP/Kerberos) |
| `PAM_USER_UNKNOWN` | 10 | Запитаний користувач відсутній у базі даних |
| `PAM_MAXTRIES` | 11 | Перевищено максимальну кількість спроб входу |
| `PAM_NEW_AUTHTOK_REQD` | 12 | Необхідна обов'язкова зміна пароля (термін дії вичерпано) |
| `PAM_ACCT_EXPIRED` | 13 | Термін дії облікового запису користувача вичерпано |
| `PAM_SESSION_ERR` | 14 | Збій при відкритті або закритті сесії |
| `PAM_CONV_ERR` | 19 | Помилка у функції розмови (повернуто некоректні відповіді) |
