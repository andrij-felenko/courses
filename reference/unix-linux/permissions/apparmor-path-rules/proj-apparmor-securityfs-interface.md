# ⚙️ Взаємодія з AppArmor через procfs та securityfs

Для програмного визначення стану обмеження поточного процесу або динамічного завантаження профілів у пам'ять ядро Linux використовує две віртуальні файлові системи: `procfs` (доступ до атрибутів процесу через `/proc/self/attr/current` або `/proc/self/attr/apparmor/current`) та `securityfs` (інтерфейс управління политиками ядра під `/sys/kernel/security/apparmor/.load`).

Розробники системних служб та демонів безпеки нерідко мають потребу автономно перевірити, чи перебуває поточна програма під захистом профілю AppArmor, у якому саме режимі працює політика (примусовий `enforce` чи режим скарг `complain`), та вжити відповідних заходів у разі спроби запуск у незахищеному оточенні.

## Зчитування стану з файлу procfs

Усі процеси у Linux мають доступ до власних атрибутів безпеки LSM через спеціальний каталог у віртуальній файловій системі `/proc/self/attr/`. Для систем із активним AppArmor шлях `/proc/self/attr/apparmor/current` повертає один із наступних форматів рядка:

1. `unconfined` — процес виконується без обмежень AppArmor (профіль не призначено).
2. `profile_name (enforce)` — процес перебуває під захистом профілю `profile_name` у примусовому режимі.
3. `profile_name (complain)` — профіль `profile_name` працює у режимі фіксації скарг без блокування дій.

Під час зчитування вмісту цього файлу ядро динамічно формує текстовий рядок, звертаючись до структури `aa_label` у сесії поточного процесу. Якщо файл відсутній або зчитаний рядок містить статус `unconfined`, програма може самостійно повідомити адміністратора про відсутність ізоляції або завершити роботу з помилкою.

Нижче наведено робочий приклад програми двома мовами (C та ідіоматичний C++23), яка зчитує поточний профіль безпеки процесу, перевіряє стан обмеження та розпізнає режим роботи.

:::tabs
```c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

#define ATTR_CURRENT_PATH "/proc/self/attr/apparmor/current"
#define FALLBACK_PATH     "/proc/self/attr/current"
#define BUFFER_SIZE       256

int check_apparmor_status(char *profile_out, size_t out_len, int *is_complain) {
    int fd = open(ATTR_CURRENT_PATH, O_RDONLY);
    if (fd < 0 && errno == ENOENT) {
        fd = open(FALLBACK_PATH, O_RDONLY);
    }
    if (fd < 0) {
        return -errno;
    }

    ssize_t bytes_read = read(fd, profile_out, out_len - 1);
    close(fd);

    if (bytes_read < 0) {
        return -errno;
    }

    profile_out[bytes_read] = '\0';
    if (bytes_read > 0 && profile_out[bytes_read - 1] == '\n') {
        profile_out[bytes_read - 1] = '\0';
    }

    if (strcmp(profile_out, "unconfined") == 0) {
        *is_complain = 0;
        return 0; // Активний, але неупорядкований
    }

    char *mode_ptr = strstr(profile_out, " (complain)");
    if (mode_ptr != NULL) {
        *is_complain = 1;
        *mode_ptr = '\0';
    } else {
        mode_ptr = strstr(profile_out, " (enforce)");
        if (mode_ptr != NULL) {
            *is_complain = 0;
            *mode_ptr = '\0';
        } else {
            *is_complain = 0;
        }
    }

    return 1; // Профіль активний
}

int main(void) {
    char profile[BUFFER_SIZE];
    int complain_mode = 0;

    int res = check_apparmor_status(profile, sizeof(profile), &complain_mode);
    if (res < 0) {
        fprintf(stderr, "Помилка доступу до procfs: %s\n", strerror(-res));
        return EXIT_FAILURE;
    }

    if (res == 0) {
        printf("Процес працює в режимі unconfined (поза контролем AppArmor).\n");
    } else {
        printf("Активний профіль AppArmor: '%s' [%s]\n",
               profile, complain_mode ? "COMPLAIN" : "ENFORCE");
    }

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <string>
#include <string_view>
#include <expected>
#include <system_error>
#include <filesystem>

namespace fs = std::filesystem;

enum class AppArmorMode {
    Unconfined,
    Enforce,
    Complain
};

struct ProfileInfo {
    std::string profile_name;
    AppArmorMode mode;
};

std::expected<ProfileInfo, std::error_code> get_current_apparmor_profile() {
    const fs::path primary_path{"/proc/self/attr/apparmor/current"};
    const fs::path fallback_path{"/proc/self/attr/current"};

    fs::path target_path = fs::exists(primary_path) ? primary_path : fallback_path;

    std::ifstream attr_file(target_path);
    if (!attr_file.is_open()) {
        return std::unexpected(std::make_error_code(std::errc::no_such_file_or_directory));
    }

    std::string raw_content;
    std::getline(attr_file, raw_content);

    if (raw_content.empty() || raw_content == "unconfined") {
        return ProfileInfo{.profile_name = "unconfined", .mode = AppArmorMode::Unconfined};
    }

    constexpr std::string_view complain_suffix = " (complain)";
    constexpr std::string_view enforce_suffix = " (enforce)";

    if (auto pos = raw_content.find(complain_suffix); pos != std::string::npos) {
        return ProfileInfo{
            .profile_name = raw_content.substr(0, pos),
            .mode = AppArmorMode::Complain
        };
    }

    if (auto pos = raw_content.find(enforce_suffix); pos != std::string::npos) {
        return ProfileInfo{
            .profile_name = raw_content.substr(0, pos),
            .mode = AppArmorMode::Enforce
        };
    }

    return ProfileInfo{.profile_name = raw_content, .mode = AppArmorMode::Enforce};
}

int main() {
    auto result = get_current_apparmor_profile();
    if (!result) {
        std::cerr << "Не вдалося зчитати профіль AppArmor: " 
                  << result.error().message() << '\n';
        return 1;
    }

    const auto& [name, mode] = *result;
    switch (mode) {
        case AppArmorMode::Unconfined:
            std::cout << "Процес працює поза контролем AppArmor (unconfined).\n";
            break;
        case AppArmorMode::Complain:
            std::cout << "Активний профіль: '" << name << "' [COMPLAIN]\n";
            break;
        case AppArmorMode::Enforce:
            std::cout << "Активний профіль: '" << name << "' [ENFORCE]\n";
            break;
    }

    return 0;
}
```
:::

## Динамічна зміна профілю та підпрофілі (ChangeHat API)

Окрім прямого зчитування статусу з procfs, складні багатопотокові серверні додатки (такі як Apache HTTP Server, Nginx або рішення на базі libapparmor) можуть динамічно змінювати свій політичний контекст для обробки конкретного HTTP-запиту за допомогою механізму **ChangeHat**.

Функція системного API `aa_change_hat(const char *hat_name, unsigned long magic_token)` дозволяє головному процесу сервера після прийому з'єднання перейти у звужений підпрофіль (hat), створений спеціально для конкретного віртуального хосту або користувацького скрипту. Після завершення обробки запиту демон викликає `aa_change_hat(NULL, magic_token)`, повертаючись у початковий батьківський профіль.

Використання випадково згенерованого токена `magic_token` гарантує безпеку: якщо вразливий обробник запитів буде компрометовано під час роботи у підпрофілі, зловмисник не зможе самостійно здійснити вихід назад у привілейований батьківський профіль, не знаючи точного секретного значення токена.

## Завантаження та оновлення профілів через securityfs

Управління профілями з простору користувача виконується за допомогою запису скомпільованого бінарного блоба DFA у спеціальні файли `securityfs`. Цей процес реалізується наступним чином:

1. Парсер `apparmor_parser` розгортає правила й створює бінарний блоб політики.
2. Програми системного адміністрування відкривають файл `/sys/kernel/security/apparmor/.load` (для додавання нового профілю) або `/sys/kernel/security/apparmor/.replace` (для оновлення існуючого).
3. Процес пише блоб у відкритий дескриптор. Ядро валідує заголовки `SD_ID` і розгортає нові автомати в пам'яті.

Цей механізм дозволяє реалізувати атомарну заміну конфігурації без переривання обробки мережевих з'єднань і без перезапуску демонів. Утиліти автоматизації CI/CD використовують файл `.replace` для безпечного оновлення правил на працюючих серверах.

## Пастки та крайові випадки взаємодії з securityfs

Під час практичної розробки утиліт управління профілями необхідно враховувати кілька важливих особливостей:

1. **Кешування файлових дескрипторів**: Якщо процес відкрив файловий дескриптор до переходу у новий профіль або до оновлення правил через `/sys/kernel/security/apparmor/.replace`, вже відкритий файловий дескриптор залишається дійсним для операцій `read()` та `write()`. AppArmor авторизує доступ під час системного виклику `open()`, а не на кожну послідуючу операцію зчитування байтів.
2. **Обмеження прав доступу в procfs**: Файл `/proc/self/attr/current` доступний для зчитування поточним процесом. Проте спроба змінити власний профіль через запис у цей файл регулюється спеціальними масками `change_profile` або `setprofile`, які мають бути явно дозволені в початковому профілі.
3. **Права доступу до керуючих файлів securityfs**: Файли `.load`, `.replace` та `.remove` у `/sys/kernel/security/apparmor/` зазвичай мають файлові права `0200` або `0600` і вимагають привілею `CAP_MAC_ADMIN`. Будь-які спроби запису від імені звичайного користувача без належних capabilities повертають помилку `-EPERM`.
4. **Багатопотоковість та контекст потоку**: Кожен потік в межах одного процесу Linux може мати власний контекст безпеки AppArmor. При написанні багатопотокового коду слід переконуватися, що зміна профілю виконується для цільового потоку обробки, а не лише для головного потоку.
5. **Обробка помилок при зчитуванні статусів**: Якщо AppArmor вимкнений на рівні параметрів завантаження ядра (`apparmor=0` або `lsm=capability`), спроба відкриття файлів у `/sys/kernel/security/apparmor/` поверне помилку `ENOENT`. Програми повинні коректно обробляти відсутність файлової системи `securityfs`.
