# ⚙️ Програмування та управління LUKS/DM-Crypt

Управління зашифрованими пристроями у системному програмному забезпеченні Linux можна виконувати двома основними шляхами: через прямі системні виклики `ioctl` до символьного вузла `/dev/mapper/control` або через високорівневу офіційну бібліотеку `libcryptsetup`. 

Прямий виклик `ioctl` вимагає від розробника ручного зчитування заголовків з диска, самостійної реалізації алгоритмів підсилення пароля (Argon2id або PBKDF2) та формування сирих текстових рядків параметрів для `dm-crypt`. Бібліотека `libcryptsetup` повністю абстрагує цю складність: вона бере на себе весь цикл роботи з метаданими LUKS1/LUKS2, безпечне управління пам'яттю з мастер-ключами та автоматичне завантаження конфігурації у ядро Device Mapper.

Далі — робоча програма, що відкриває та активує зашифрований том LUKS2 у просторі користувача: від ініціалізації контексту пристрою та перевірки заголовка до аутентифікації парольною фразою й створення нового відображеного пристрою у `/dev/mapper/`.

## Архітектура взаємодії з libcryptsetup

Процес активації зашифрованого тома за допомогою `libcryptsetup` складається з чотирьох послідовних етапів:

1. **Ініціалізація контексту (`crypt_init`):** бібліотека створює непрозору структуру `struct crypt_device`, яка пов'язує файловий дескриптор базового блокового пристрою (наприклад `/dev/nvme0n1p2`) із криптографічним контекстом програми.
2. **Завантаження та валідація заголовка (`crypt_load`):** бібліотека зчитує з початку диска магічне число `LUKS\xba\xbe`, перевіряє цілісність JSON-метаданих LUKS2 та витягує з них параметри тома (назву алгоритму шифрування, розмір ключа, зсув payload) і окремо параметри KDF (кількість ітерацій Argon2id, сіль, обсяг потрібної пам'яті).
3. **Аутентифікація та розшифрування Master Key (`crypt_activate_by_passphrase`):** введена користувачем парольна фраза передається до функції KDF. Якщо розрахований KEK успішно відкриває один із Key Slots, розшифрований матеріал слота проходить зворотне перетворення AF-merge, збирається назад у Master Key й лягає в захищену пам'ять.
4. **Конфігурація Device Mapper:** `libcryptsetup` будує рядок відображення `dm-crypt`, відкриває `/dev/mapper/control` і виконує `DM_DEV_CREATE`, потім `DM_TABLE_LOAD` — а вмикає завантажену таблицю завершальний `DM_DEV_SUSPEND` зі знятим прапорцем `DM_SUSPEND_FLAG` (окремої команди «resume» в інтерфейсі немає). Аж після цього пристрій `/dev/mapper/target_name` приймає I/O.

## Управління слотами ключів, резервування та статус пристрою

Окрім базової активації, `libcryptsetup` забезпечує повний цикл керування життєвим циклом ключового матеріалу та резервним копіюванням метаданих:

- `crypt_keyslot_status(cd, keyslot)` — перевіряє стан конкретного слота (повертає `CRYPT_SLOT_ACTIVE`, `CRYPT_SLOT_INACTIVE` або `CRYPT_SLOT_INVALID`).
- `crypt_keyslot_add_by_passphrase(cd, new_slot, old_passphrase, old_len, new_passphrase, new_len)` — додає нову парольну фразу в інший слот ключа без перешифрування основного вмісту диска.
- `crypt_keyslot_destroy(cd, slot)` — робить слот ключа недійсним, затираючи його вміст на диску.
- `crypt_header_backup(cd, CRYPT_LUKS2, backup_file)` — зберігає бінарну копію заголовка LUKS2 у зовнішній файл для захисту від випадкового перезапису початкових секторів пристрою.
- `crypt_header_restore(cd, CRYPT_LUKS2, backup_file)` — відновлює пошкоджені JSON-метадані та слоти ключів із резервного файлу.
- `crypt_deactivate(cd, name)` — надсилає виклик `DM_DEV_REMOVE` в Device Mapper, вилучаючи пристрій із `/dev/mapper/` і затираючи ключ у пам'яті ядра.

Порядок дій при зміні пароля важить більше, ніж здається. Утиліта спершу додає новий запис у **вільний** слот, перевіряє, що з нього справді збирається Master Key, і лише після цього затирає старий слот. Атомарною ця пара записів не є — і саме тому порядок такий: якщо живлення зникне посередині, на диску залишиться або старий робочий слот, або вже обидва, але ніколи не «жодного».

Збереження резервної копії заголовка критично важливе для промислових систем: у разі збою файлової системи чи випадкового перезапису перших секторів диска відновлення метаданих через `crypt_header_restore()` є єдиним способом врятувати зашифровані терабайти даних від повної втрати.

## Практична реалізація мовами C та C++

Обидві вкладки роблять те саме — відкривають том і активують відображення, — але різними засобами: у C кожна гілка помилки сама згадує про `crypt_free()`, а C++ віддає це RAII й повертає результат через `std::expected`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <libcryptsetup.h>

int main(int argc, char *argv[]) {
    if (argc < 4) {
        fprintf(stderr, "Використання: %s <пристрій> <ім'я_відображення> <пароль>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *device_path = argv[1];
    const char *target_name = argv[2];
    const char *passphrase = argv[3];

    struct crypt_device *cd = NULL;
    int r;

    /* 1. Ініціалізація контексту для блокового пристрою */
    r = crypt_init(&cd, device_path);
    if (r < 0) {
        fprintf(stderr, "Помилка crypt_init для %s: %s\n", device_path, strerror(-r));
        return EXIT_FAILURE;
    }

    /* 2. Зчитування та валідація заголовка LUKS */
    r = crypt_load(cd, CRYPT_LUKS, NULL);
    if (r < 0) {
        fprintf(stderr, "Помилка зчитування заголовка LUKS на %s: %s\n", device_path, strerror(-r));
        crypt_free(cd);
        return EXIT_FAILURE;
    }

    printf("Успішно зчитано заголовок!\n");
    printf("Тип заголовка: %s\n", crypt_get_type(cd));
    printf("UUID тома:     %s\n", crypt_get_uuid(cd));

    /* 3. Активація зашифрованого тома парольною фразою */
    r = crypt_activate_by_passphrase(cd, target_name, CRYPT_ANY_SLOT,
                                     passphrase, strlen(passphrase), 0);
    if (r < 0) {
        fprintf(stderr, "Помилка аутентифікації або активації: %s\n", strerror(-r));
        crypt_free(cd);
        return EXIT_FAILURE;
    }

    printf("Пристрій успішно активовано: /dev/mapper/%s (використано слот ключа %d)\n", target_name, r);

    /* 4. Безумовне звільнення ресурсів контексту */
    crypt_free(cd);
    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <string_view>
#include <memory>
#include <expected>
#include <system_error>
#include <cstring>
#include <cstdlib>
#include <libcryptsetup.h>

// RAII кастомний видаляч для struct crypt_device
struct CryptDeviceDeleter {
    void operator()(crypt_device* cd) const noexcept {
        if (cd) {
            crypt_free(cd);
        }
    }
};

using CryptDevicePtr = std::unique_ptr<crypt_device, CryptDeviceDeleter>;

class LuksVolume {
public:
    // Фабричний метод відкриття зашифрованого пристрою
    static std::expected<LuksVolume, std::string> open(std::string_view device_path) {
        crypt_device* raw_cd = nullptr;
        int r = crypt_init(&raw_cd, device_path.data());
        if (r < 0) {
            return std::unexpected(std::string("crypt_init failed: ") + std::strerror(-r));
        }

        CryptDevicePtr cd(raw_cd);

        r = crypt_load(cd.get(), CRYPT_LUKS, nullptr);
        if (r < 0) {
            return std::unexpected(std::string("crypt_load failed: ") + std::strerror(-r));
        }

        return LuksVolume(std::move(cd));
    }

    // Метод аутентифікації та активації відображення
    [[nodiscard]] std::expected<int, std::string> activate(std::string_view target_name, 
                                                            std::string_view passphrase) const {
        int slot = crypt_activate_by_passphrase(
            cd_.get(),
            target_name.data(),
            CRYPT_ANY_SLOT,
            passphrase.data(),
            passphrase.size(),
            0
        );

        if (slot < 0) {
            return std::unexpected(std::string("Активація відхилена: ") + std::strerror(-slot));
        }

        return slot;
    }

    [[nodiscard]] std::string_view type() const noexcept {
        const char* t = crypt_get_type(cd_.get());
        return t ? std::string_view(t) : std::string_view("unknown");
    }

    [[nodiscard]] std::string_view uuid() const noexcept {
        const char* u = crypt_get_uuid(cd_.get());
        return u ? std::string_view(u) : std::string_view("");
    }

private:
    explicit LuksVolume(CryptDevicePtr cd) : cd_(std::move(cd)) {}
    CryptDevicePtr cd_;
};

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Використання: " << argv[0] << " <пристрій> <ім'я_відображення> <пароль>\n";
        return EXIT_FAILURE;
    }

    const std::string_view device_path = argv[1];
    const std::string_view target_name = argv[2];
    const std::string_view passphrase = argv[3];

    auto volume_result = LuksVolume::open(device_path);
    if (!volume_result) {
        std::cerr << "Помилка відкриття LUKS тома: " << volume_result.error() << '\n';
        return EXIT_FAILURE;
    }

    const auto& volume = *volume_result;
    std::cout << "Успішно відкрито том LUKS!\n";
    std::cout << "Тип заголовка: " << volume.type() << "\nUUID тома:     " << volume.uuid() << '\n';

    auto activation_result = volume.activate(target_name, passphrase);
    if (!activation_result) {
        std::cerr << "Помилка активації: " << activation_result.error() << '\n';
        return EXIT_FAILURE;
    }

    std::cout << "Пристрій успішно активовано: /dev/mapper/" << target_name
              << " (слот ключа " << *activation_result << ")\n";

    return EXIT_SUCCESS;
}
```
:::

## Нюанси безпеки та обробка крайових випадків

При розробці продакшн-систем шифрування дисків необхідно враховувати чотири ключові безпекові вимоги:

1. **Захист пам'яті від скидання на диск (Memory Locking):** Буфери пам'яті у просторі користувача, які містять парольні фрази або розшифрований Master Key, можуть бути випадково записані у swap-розділ при нестачі RAM. Власні буфери з ключовим матеріалом `libcryptsetup` обнуляє примусово (`explicit_bzero`) перед звільненням — це вона робить сама. А от блокування пам'яті сама не вмикає: його вмикає програма викликом `crypt_memory_lock(cd, 1)`, і діє він на **весь** процес (під капотом `mlockall`), тому потребує прав root. Саме так робить утиліта `cryptsetup`; свій демон має робити те саме, інакше пароль може опинитися у swap.
2. **Деактивація зайнятого пристрою (`crypt_deactivate`):** При закритті зашифрованого тома програма надсилає виклик `crypt_deactivate()`. Якщо у системі лишився хоча б один процес із відкритим файловим дескриптором на пристрої `/dev/mapper/target_name` або змонтована файлова система, ядро поверне помилку `EBUSY`. Програми-демони повинні обробляти цей випадок і спочатку розмонтовувати пристрій.
3. **Режим лише для читання (`CRYPT_ACTIVATE_READONLY`):** При проведенні криміналістичного аналізу (forensics) або монтуванні пошкоджених томів активація повинна виконуватися із прапорцем `CRYPT_ACTIVATE_READONLY`. Це блокує будь-які записи на базовий дисковий пристрій на рівні самого target-драйвера `dm-crypt` у ядрі.
4. **Інтеграція з Kernel Keyring:** для LUKS2 розшифрований Master Key не вписують у таблицю відображення шістнадцятковим рядком, а кладуть у ключник ядра (Kernel Keyring) і передають у таблицю саме **посилання** на нього — у форматі `:<розмір_ключа>:logon:<опис>`. Виграш конкретний: ключ більше не видно у виводі `dmsetup table`, і він не мандрує через буфери простору користувача при кожному перезавантаженні таблиці.
