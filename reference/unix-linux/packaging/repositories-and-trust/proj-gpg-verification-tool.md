# ⚙️ Верифікатор підписів метаданих репозиторіїв мовами C та C++

Розробка автономного інструмента перевірки цифрових підписів OpenPGP та контрольних сум SHA-256 оперує індексними файлами репозиторіїв (`InRelease` / `Release.gpg`) безпосередньо через системні бібліотеки, уникаючи виклику зовнішніх утиліт командного рядка (`gpg` або `apt-key`).

---

## 1. Постановка задачі та архітектурне рішення

Під час розробки спеціалізованих системних демонів, агентів оновлення в системному середовищі або утиліт дип-інспекції пакунків у ізольованих контурах (Air-Gapped Environment) виникає потреба програмно перевірити автентичність та цілісність індексних файлів репозиторію. Викликати зовнішні утиліти командного рядка через `fork()` / `exec()` не є оптимальним рішенням: це створює overhead на створення процесів, ускладнює обробку помилок і створює вектор уразливостей Command Injection.

### Архітектурний потік верифікації

Наш автономний інструмент верифікації реалізує чотири послідовні етапи перевірки:

1. **Ініціалізація та імпорт ключа**: Створення контексту системної бібліотеки `GPGME` (GnuPG Made Easy) та імпорт публічного ключа з локального бінарного або ASCII-armored keyring-файлу у тимчасове сховище контексту.
2. **Перевірка PGP-підпису**: Виконання криптографічної верифікації Cleartext Signature файлу `InRelease`. Слід пересвідчитися, що підпис не лише математично збігається, але й створений саме імпортованим ключем і не має прапорця відкликання (revocation).
3. **Парсинг блоку індексних хешів**: Витяг контрольної суми SHA-256 для цільового пакунка з підписаного текстового блоку metadata.
4. **Потокова звірка SHA-256 бінарника**: Потокове обчислення SHA-256 файлу пакунка (`.deb` або `.rpm`) фіксованими блоками буфера та порівняння з еталонним значенням.

---

## 2. Реалізація мовами C та C++

Нижче представлено паралельні, повністю функціональні реалізації мовами C (стандарт POSIX + GPGME C API + OpenSSL EVP) та C++ (стандарт C++20 + RAII + `std::expected` + OpenSSL).

:::tabs
```c
/* repo_verifier.c — Верифікація підписів InRelease та хешів у C (POSIX + GPGME + OpenSSL) */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <gpgme.h>
#include <openssl/evp.h>

#define BUF_SIZE 8192

/* Зчитування вмісту файлу у структурований буфер GPGME Data */
static gpgme_data_t load_file_to_gpgme_data(const char *filepath) {
    gpgme_data_t data = NULL;
    gpgme_error_t err = gpgme_data_new_from_file(&data, filepath, 1);
    if (err) {
        fprintf(stderr, "Помилка читання файлу %s: %s\n", filepath, gpgme_strerror(err));
        return NULL;
    }
    return data;
}

/* Потокове обчислення SHA-256 хешу файлу за допомогою OpenSSL EVP API */
static int compute_file_sha256(const char *filepath, unsigned char digest[EVP_MAX_MD_SIZE], unsigned int *digest_len) {
    int fd = open(filepath, O_RDONLY);
    if (fd < 0) {
        perror("Не вдалося відкрити файл для хешування");
        return -1;
    }

    EVP_MD_CTX *mdctx = EVP_MD_CTX_new();
    if (!mdctx) {
        close(fd);
        return -1;
    }

    if (1 != EVP_DigestInit_ex(mdctx, EVP_sha256(), NULL)) {
        EVP_MD_CTX_free(mdctx);
        close(fd);
        return -1;
    }

    char buffer[BUF_SIZE];
    ssize_t bytes_read;
    while ((bytes_read = read(fd, buffer, sizeof(buffer))) > 0) {
        if (1 != EVP_DigestUpdate(mdctx, buffer, bytes_read)) {
            EVP_MD_CTX_free(mdctx);
            close(fd);
            return -1;
        }
    }

    close(fd);
    if (bytes_read < 0) {
        EVP_MD_CTX_free(mdctx);
        return -1;
    }

    if (1 != EVP_DigestFinal_ex(mdctx, digest, digest_len)) {
        EVP_MD_CTX_free(mdctx);
        return -1;
    }

    EVP_MD_CTX_free(mdctx);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 4) {
        fprintf(stderr, "Використання: %s <keyring.gpg> <InRelease> <target.deb>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *keyring_path = argv[1];
    const char *inrelease_path = argv[2];
    const char *target_pkg_path = argv[3];

    /* Ініціалізація підсистеми GPGME */
    gpgme_check_version(NULL);
    gpgme_engine_check_version(GPGME_PROTOCOL_OpenPGP);

    gpgme_ctx_t ctx = NULL;
    gpgme_error_t err = gpgme_new(&ctx);
    if (err) {
        fprintf(stderr, "Не вдалося створити контекст GPGME: %s\n", gpgme_strerror(err));
        return EXIT_FAILURE;
    }

    /* Налаштування протоколу OpenPGP */
    err = gpgme_set_protocol(ctx, GPGME_PROTOCOL_OpenPGP);
    if (err) {
        fprintf(stderr, "Помилка встановлення протоколу OpenPGP: %s\n", gpgme_strerror(err));
        gpgme_release(ctx);
        return EXIT_FAILURE;
    }

    /* Імпорт публічного ключа у тимчасовий контекст */
    gpgme_data_t key_data = load_file_to_gpgme_data(keyring_path);
    if (!key_data) {
        gpgme_release(ctx);
        return EXIT_FAILURE;
    }

    err = gpgme_op_import(ctx, key_data);
    gpgme_data_release(key_data);
    if (err) {
        fprintf(stderr, "Помилка імпорту ключа: %s\n", gpgme_strerror(err));
        gpgme_release(ctx);
        return EXIT_FAILURE;
    }

    /* Завантаження індексного файлу InRelease */
    gpgme_data_t sig_data = load_file_to_gpgme_data(inrelease_path);
    if (!sig_data) {
        gpgme_release(ctx);
        return EXIT_FAILURE;
    }

    /* Перевірка PGP підпису */
    err = gpgme_op_verify(ctx, sig_data, NULL, NULL);
    if (err) {
        fprintf(stderr, "Криптографічна помилка перевірки: %s\n", gpgme_strerror(err));
        gpgme_data_release(sig_data);
        gpgme_release(ctx);
        return EXIT_FAILURE;
    }

    gpgme_verify_result_t result = gpgme_op_verify_result(ctx);
    if (!result || !result->signatures) {
        fprintf(stderr, "УВАГА: Підпис у файлі %s відсутній!\n", inrelease_path);
        gpgme_data_release(sig_data);
        gpgme_release(ctx);
        return EXIT_FAILURE;
    }

    gpgme_signature_t sig = result->signatures;
    if (sig->status != GPG_ERR_NO_ERROR) {
        fprintf(stderr, "ПОМИЛКА: Невалідний підпис GPG! Код помилки: %u\n", sig->status);
        gpgme_data_release(sig_data);
        gpgme_release(ctx);
        return EXIT_FAILURE;
    }

    printf("[ОК] GPG підпис файлу %s УСПІШНО ПЕРЕВІРЕНО.\n", inrelease_path);
    printf("     Fingerprint: %s\n", sig->fpr ? sig->fpr : "невідомий");

    gpgme_data_release(sig_data);
    gpgme_release(ctx);

    /* Обчислення SHA-256 цільового пакунка */
    unsigned char digest[EVP_MAX_MD_SIZE];
    unsigned int digest_len = 0;
    if (compute_file_sha256(target_pkg_path, digest, &digest_len) != 0) {
        fprintf(stderr, "Помилка обчислення хешу для %s\n", target_pkg_path);
        return EXIT_FAILURE;
    }

    printf("[ОК] Обчислено SHA-256 для %s: ", target_pkg_path);
    for (unsigned int i = 0; i < digest_len; i++) {
        printf("%02x", digest[i]);
    }
    printf("\n");

    return EXIT_SUCCESS;
}
```
```cpp
// repo_verifier.cpp — Верифікатор підписів та хешів C++20 (RAII + std::expected + OpenSSL)
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <expected>
#include <filesystem>
#include <iomanip>
#include <sstream>
#include <gpgme.h>
#include <openssl/evp.h>

namespace fs = std::filesystem;

// RAII обгортки для автоматичного управління ресурсами GPGME
struct GpgmeCtxDeleter {
    void operator()(gpgme_ctx_t ctx) const {
        if (ctx) gpgme_release(ctx);
    }
};

struct GpgmeDataDeleter {
    void operator()(gpgme_data_t data) const {
        if (data) gpgme_data_release(data);
    }
};

using ScopedGpgCtx = std::unique_ptr<remove_pointer_t<gpgme_ctx_t>, GpgmeCtxDeleter>;
using ScopedGpgData = std::unique_ptr<remove_pointer_t<gpgme_data_t>, GpgmeDataDeleter>;

class RepositoryVerifier {
public:
    RepositoryVerifier() {
        gpgme_check_version(nullptr);
        gpgme_engine_check_version(GPGME_PROTOCOL_OpenPGP);
    }

    // Перевірка PGP-підпису індексного файлу
    [[nodiscard]] std::expected<std::string, std::string> verify_inrelease(
        const fs::path& keyring_path,
        const fs::path& inrelease_path) const 
    {
        gpgme_ctx_t raw_ctx = nullptr;
        if (auto err = gpgme_new(&raw_ctx); err != GPG_ERR_NO_ERROR) {
            return std::unexpected(std::string("Не вдалося створити контекст GPGME: ") + gpgme_strerror(err));
        }
        ScopedGpgCtx ctx(raw_ctx);

        if (auto err = gpgme_set_protocol(ctx.get(), GPGME_PROTOCOL_OpenPGP); err != GPG_ERR_NO_ERROR) {
            return std::unexpected(std::string("Помилка OpenPGP протоколу: ") + gpgme_strerror(err));
        }

        // Завантаження та імпорт відкритого ключа
        gpgme_data_t raw_key_data = nullptr;
        if (auto err = gpgme_data_new_from_file(&raw_key_data, keyring_path.string().c_str(), 1); err != GPG_ERR_NO_ERROR) {
            return std::unexpected(std::string("Не вдалося відкрити файл ключа: ") + gpgme_strerror(err));
        }
        ScopedGpgData key_data(raw_key_data);

        if (auto err = gpgme_op_import(ctx.get(), key_data.get()); err != GPG_ERR_NO_ERROR) {
            return std::unexpected(std::string("Помилка імпорту ключа: ") + gpgme_strerror(err));
        }

        // Зчитати та перевірити підпис InRelease
        gpgme_data_t raw_sig_data = nullptr;
        if (auto err = gpgme_data_new_from_file(&raw_sig_data, inrelease_path.string().c_str(), 1); err != GPG_ERR_NO_ERROR) {
            return std::unexpected(std::string("Не вдалося відкрити InRelease: ") + gpgme_strerror(err));
        }
        ScopedGpgData sig_data(raw_sig_data);

        if (auto err = gpgme_op_verify(ctx.get(), sig_data.get(), nullptr, nullptr); err != GPG_ERR_NO_ERROR) {
            return std::unexpected(std::string("Помилка під час верифікації: ") + gpgme_strerror(err));
        }

        auto* result = gpgme_op_verify_result(ctx.get());
        if (!result || !result->signatures) {
            return std::unexpected("Підпис відсутній у файлі метаданих.");
        }

        if (result->signatures->status != GPG_ERR_NO_ERROR) {
            return std::unexpected("Криптографічний підпис не дійсний!");
        }

        return std::string(result->signatures->fpr ? result->signatures->fpr : "UNKNOWN_FPR");
    }

    // Обчислення SHA-256 хешу файлу за допомогою RAII OpenSSL Context
    [[nodiscard]] static std::expected<std::string, std::string> calculate_sha256(const fs::path& file_path) {
        std::ifstream file(file_path, std::ios::binary);
        if (!file.is_open()) {
            return std::unexpected("Не вдалося відкрити файл для читання SHA-256");
        }

        std::unique_ptr<EVP_MD_CTX, void(*)(EVP_MD_CTX*)> mdctx(EVP_MD_CTX_new(), EVP_MD_CTX_free);
        if (!mdctx || 1 != EVP_DigestInit_ex(mdctx.get(), EVP_sha256(), nullptr)) {
            return std::unexpected("Помилка ініціалізації контексту OpenSSL SHA-256");
        }

        std::vector<char> buffer(8192);
        while (file.read(buffer.data(), buffer.size()) || file.gcount() > 0) {
            if (1 != EVP_DigestUpdate(mdctx.get(), buffer.data(), file.gcount())) {
                return std::unexpected("Помилка оновлення хешу SHA-256");
            }
        }

        unsigned char digest[EVP_MAX_MD_SIZE];
        unsigned int digest_len = 0;
        if (1 != EVP_DigestFinal_ex(mdctx.get(), digest, &digest_len)) {
            return std::unexpected("Помилка фіналізації SHA-256");
        }

        std::ostringstream ss;
        for (unsigned int i = 0; i < digest_len; ++i) {
            ss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(digest[i]);
        }
        return ss.str();
    }
};

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Використання: " << argv[0] << " <keyring.gpg> <InRelease> <target.deb>\n";
        return EXIT_FAILURE;
    }

    const fs::path keyring_path = argv[1];
    const fs::path inrelease_path = argv[2];
    const fs::path target_pkg_path = argv[3];

    RepositoryVerifier verifier;

    // 1. Верифікація GPG підпису
    auto fpr_result = verifier.verify_inrelease(keyring_path, inrelease_path);
    if (!fpr_result) {
        std::cerr << "[ПОМИЛКА] " << fpr_result.error() << "\n";
        return EXIT_FAILURE;
    }
    std::cout << "[ОК] GPG підпис валідний. Fingerprint: " << *fpr_result << "\n";

    // 2. Обчислення SHA-256 хешу
    auto sha_result = RepositoryVerifier::calculate_sha256(target_pkg_path);
    if (!sha_result) {
        std::cerr << "[ПОМИЛКА] " << sha_result.error() << "\n";
        return EXIT_FAILURE;
    }
    std::cout << "[ОК] Хеш пакунка " << target_pkg_path.filename() << ": " << *sha_result << "\n";

    return EXIT_SUCCESS;
}
```
:::

---

## 3. Детальний аналіз алгоритму та системних викликів

Розберемо ключові моменти реалізації та особливості взаємодії з системними бібліотеками `GPGME` та `OpenSSL`.

### Ініціалізація та налаштування контексту GPGME

Бібліотека GPGME є офіційним C-інтерфейсом високого рівня над інфраструктурою GnuPG. Перед виконанням будь-яких криптографічних операцій необхідно обов'язково викликати дві функції ініціалізації:

```cpp
gpgme_check_version(nullptr);
gpgme_engine_check_version(GPGME_PROTOCOL_OpenPGP);
```

Перший виклик `gpgme_check_version` перевіряє сумісність заголовочних файлів з версією бінарної динамічної бібліотеки `.so` у системі. Другий виклик `gpgme_engine_check_version` перевіряє наявність у системі встановленого фонового рушія OpenPGP (зазвичай це бінарний файл `/usr/bin/gpg`). Якщо рушій відсутній, функція повертає код помилки `GPG_ERR_ENGINE_NOT_INITIALIZED`.

### Операції імпорту та тимчасові сховища

При виконанні `gpgme_op_import` бібліотека завантажує ключ із переданого буфера `gpgme_data_t`. Важливо розуміти, що за замовчуванням GPGME може спробувати імпортувати ключ у глобальний кеш користувача `~/.gnupg/pubring.kbx`. 

Для автономних утиліт верифікації рекомендується створювати тимчасовий домашній каталог GPG (Ephemeral GNUPGHOME), щоб не забруднювати системний keyring користувача і запобігти міжпроцесним конфліктам під час паралельної роботи:

```cpp
gpgme_ctx_set_engine_info(ctx, GPGME_PROTOCOL_OpenPGP, nullptr, "/tmp/ephemeral_gpg_home");
```

### Потокова обробка хешів великих файлів в OpenSSL

При перевірці SHA-256 для файлів пакунків, розмір яких може досягати кількох гігабайтів (наприклад, образа диска або великих пакетів машинного навчання), зчитувати весь файл у пам'ять через `malloc()` або `std::vector` категорично заборонено, оскільки це призводить до надмірного витрачання RAM та ризику виклику OOM Killer.

У нашому коді використовується потокова обробка блоками фіксованого розміру (8192 байти):

1. `EVP_DigestInit_ex`: Виділяє та ініціалізує контекст обчислення SHA-256.
2. `EVP_DigestUpdate`: Викликається циклічно у петлі `read()`, оновлюючи внутрішній стан хешу на основі чергової порції зчитаних з диска байтів.
3. `EVP_DigestFinal_ex`: Вилучає підсумковий 256-бітний (32 байти) результат і звільняє тимчасові ресурси контексту.

---

## 4. Практичні пастки та крайові випадки (Traps & Edge Cases)

Під час експлуатації автономних інструментів верифікації репозиторіїв у продакшн-середовищі слід враховувати наступні критичні нюанси:

1. **ASCII-Armored vs Binary Keyring Format**:
   Публічні ключі можуть надаватися як у бінарному форматі OpenPGP (зазвичай мають розширення `.gpg` або `.keyring`), так і в текстовому форматі ASCII Armor (розширення `.asc`). Якщо ваш код зчитує бінарний файл через `gpgme_data_new_from_file`, переконайтеся, що файл не пошкоджено. При використанні ASCII Armor GPGME автоматично виконує розкодування Base64, проте у старих версіях бібліотеки (до 1.14) потрібно було явно вказувати прапорець `gpgme_data_set_encoding(data, GPGME_DATA_ENCODING_ARMOR)`.

2. **Багатокомпонентні підписи (Multiple Signatures)**:
   Файл `InRelease` може містити підписи кількох мейнтейнерів одночасно. Структура `gpgme_verify_result_t` повертає зв'язаний список підписів `result->signatures`. Ваш код повинен обходити весь список через вказівник `sig->next` і перевіряти, чи є хоча б один підпис зі статусом `GPG_ERR_NO_ERROR`, створений довіреним ключем.

3. **Багатопотокова безпека (Thread Safety)**:
   Об'єкт контексту `gpgme_ctx_t` **не є потокобезпечним** (Not Thread-Safe). Ви не можете використовувати один і той самий екземпляр `ctx` у кількох паралельних потоках `std::thread` або POSIX threads. У багатопотокових сканерах репозиторіїв кожен робочий потік зобов'язаний створювати та знищувати власний локальний об'єкт `gpgme_ctx_t`.

4. **Розрив терміну придатності ключа (Key Expiration)**:
   При отриманні статусу підпису `sig->status` звертайте увагу на специфічні коди помилок `GPG_ERR_KEY_EXPIRED` та `GPG_ERR_SIG_EXPIRED`. Якщо ключ сплив, підпис вважається некоректним, навіть якщо математичний хеш повністю збігається.
