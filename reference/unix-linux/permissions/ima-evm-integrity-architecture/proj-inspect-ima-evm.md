# ⚙️ Практичний аналізатор атрибутів цілісності IMA/EVM та вимірювань sysfs

Для перевірки та діагностики роботи підсистеми цілісності в системному програмуванні Linux використовується зчитування розширених атрибутів файлів `security.ima` та `security.evm` за допомогою системних викликів родини `getxattr(2)`, а також аналіз системного журналу вимірювань ядра через інтерфейс `securityfs` за шляхом `/sys/kernel/security/ima/ascii_runtime_measurements`.

Нижче наведено практичну утиліту аналізу, яка виконує бінарний розбір розширеного атрибута вказаного файлу, витягує алгоритм хешування, тип заголовка, Key ID відкритого ключа та перевіряє стан атрибута EVM.

## Архітектура та логіка роботи аналізатора

Програма приймає як аргумент шлях до будь-якого бінарного файлу чи бібліотеки на диску. Вона здійснює низку послідовних перевірок та бінарного розпарсингу даних розширених атрибутів:

1. **Запит розміру та зчитування вмісту**: Програма викликає системний виклик `getxattr(filepath, "security.ima", buffer, sizeof(buffer))`. Якщо атрибут відсутній у структурі файлової системи, функція повертає від'ємне значення із кодом помилки `ENODATA` (`No data available`). Це сигналізує про те, що файл не має розширеного атрибута цілісності і при ввімкненому режимі `ima_appraise=enforce` його виконання буде відхилено ядром.
2. **Аналіз першого заголовочного байта**: Перший байт буфера дає тип упакованих даних. Якщо перший байт дорівнює `0x02` (`EVM_IMA_XATTR_DIGEST_NG`), програма розбирає другий байт як ідентифікатор криптографічного алгоритму хешування (enum `hash_algo`: 4 = SHA-256, 5 = SHA-384, 6 = SHA-512) і форматує решту необроблених байтів у шістнадцятковий (hex) рядок.
3. **Розбір цифрового підпису**: Якщо перший байт дорівнює `0x04` (`EVMSIG_XATTR_DIGEST`) або `0x05` (`IMA_ASYM_DIGSIG`), програма інтерпретує початок буфера як заголовок `signature_v2_hdr`. Поля `keyid` (4 байти) та `sig_size` (2 байти) перетворюються з мережевого Big-Endian порядку байтів у хостовий порядок за допомогою компіляторних вбудованих функцій `bswap`. Значення `keyid` виводиться у форматі шістнадцяткового 32-бітного ідентифікатора, який дозволяє відшукати відповідний X.509 сертифікат у системному брелоку ядра `%keyring:.ima` за допомогою командної утиліти `keyctl`.
4. **Інспекція атрибута EVM**: Програма повторює системний виклик для атрибута `security.evm`. Значення першого байта `0x03` відповідає симетричному HMAC, обчисленому з використанням майстер-ключа EVM, а тип `0x04` означає використання асиметричного підпису Portable EVM.

## Вихідний код аналізатора розширених атрибутів

Нижче наведено ідентичні реалізації утиліти мовами C та C++. У версії для C++ використовуються ідіоматичні концепції C++20: концепція строго типізованих `enum class`, безперервні зрізи пам'яті `std::span`, строкова типізація `std::string_view` та обробка системних помилок через `std::generic_category`. При компіляції додається прапорець `-lkeyutils` для зв'язування з бібліотекою управління ключами.

:::tabs
```c
/* inspect_integrity.c - Інспекція атрибутів IMA/EVM мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <errno.h>
#include <sys/xattr.h>

#define IMA_XATTR_DIGEST_NG 0x02
#define EVMSIG_XATTR_DIGEST 0x04
#define IMA_ASYM_DIGSIG     0x05

struct signature_v2_hdr {
    uint8_t type;
    uint8_t version;
    uint8_t hash_algo;
    uint32_t keyid;
    uint16_t sig_size;
} __attribute__((packed));

static const char* algo_name(uint8_t algo) {
    switch (algo) {
        case 1: return "SHA-1";
        case 2: return "RIPEMD160";
        case 4: return "SHA-256";
        case 5: return "SHA-384";
        case 6: return "SHA-512";
        default: return "Невідомий";
    }
}

static void inspect_ima_xattr(const char *filepath) {
    uint8_t buffer[1024];
    ssize_t res = getxattr(filepath, "security.ima", buffer, sizeof(buffer));
    
    if (res < 0) {
        if (errno == ENODATA) {
            printf("[IMA] Атрибут security.ima відсутній у файлі\n");
        } else {
            perror("[IMA] Помилка системного виклику getxattr");
        }
        return;
    }

    if (res == 0) {
        printf("[IMA] Атрибут security.ima існує, але має порожній вміст\n");
        return;
    }

    uint8_t type = buffer[0];
    printf("[IMA] Зчитано %zd байт. Заголовочний тип атрибута: 0x%02x\n", res, type);

    if (type == IMA_XATTR_DIGEST_NG && res >= 2) {
        uint8_t algo = buffer[1];
        printf("  -> Формат: DIGEST_NG (необроблений криптографічний хеш)\n");
        printf("  -> Алгоритм хешування: %s (id: %d)\n", algo_name(algo), algo);
        printf("  -> Хеш вмісту (hex): ");
        for (ssize_t i = 2; i < res; i++) {
            printf("%02x", buffer[i]);
        }
        printf("\n");
    } else if ((type == EVMSIG_XATTR_DIGEST || type == IMA_ASYM_DIGSIG) &&
               res >= (ssize_t)sizeof(struct signature_v2_hdr)) {
        struct signature_v2_hdr *hdr = (struct signature_v2_hdr*)buffer;
        uint32_t keyid = __builtin_bswap32(hdr->keyid);
        uint16_t sig_len = __builtin_bswap16(hdr->sig_size);
        printf("  -> Формат: Асиметричний цифровий підпис (версія %d)\n", hdr->version);
        printf("  -> Алгоритм хешування: %s\n", algo_name(hdr->hash_algo));
        printf("  -> Key ID відкритого ключа у брелоку .ima: 0x%08x\n", keyid);
        printf("  -> Розмір цифрового підпису: %u байт\n", sig_len);
    } else {
        printf("  -> Формат: Невідомий або застарілий тип заголовка атрибута\n");
    }
}

static void inspect_evm_xattr(const char *filepath) {
    uint8_t buffer[512];
    ssize_t res = getxattr(filepath, "security.evm", buffer, sizeof(buffer));

    if (res < 0) {
        if (errno == ENODATA) {
            printf("[EVM] Атрибут security.evm відсутній\n");
        } else {
            perror("[EVM] Помилка системного виклику getxattr для security.evm");
        }
        return;
    }

    uint8_t type = buffer[0];
    printf("[EVM] Зчитано %zd байт. Тип метаданих: 0x%02x ", res, type);
    if (type == 0x03) {
        printf("(Симетричний HMAC над inode та xattrs)\n");
    } else if (type == 0x04) {
        printf("(Асиметричний Portable підпис метаданих)\n");
    } else {
        printf("(Невідомий тип атрибута EVM)\n");
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях_до_файлу>\n", argv[0]);
        return EXIT_FAILURE;
    }

    printf("=== Аналіз цілісності файлу: %s ===\n", argv[1]);
    inspect_ima_xattr(argv[1]);
    inspect_evm_xattr(argv[1]);

    return EXIT_SUCCESS;
}
```
```cpp
// inspect_integrity.cpp - Інспекція атрибутів IMA/EVM мовою C++ (C++20, RAII, std::span)
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span >
#include <iomanip>
#include <cstdint>
#include <system_error>
#include <byteswap.h>
#include <sys/xattr.h>

enum class ImaXattrType : uint8_t {
    DigestNg = 0x02,
    EvmSig = 0x04,
    AsymSig = 0x05
};

#pragma pack(push, 1)
struct SignatureV2Hdr {
    uint8_t type;
    uint8_t version;
    uint8_t hash_algo;
    uint32_t keyid;
    uint16_t sig_size;
};
#pragma pack(pop)

std::string_view algoToName(uint8_t algo) noexcept {
    switch (algo) {
        case 1: return "SHA-1";
        case 2: return "RIPEMD160";
        case 4: return "SHA-256";
        case 5: return "SHA-384";
        case 6: return "SHA-512";
        default: return "Невідомий";
    }
}

void inspectImaXattr(std::string_view path) {
    std::vector<uint8_t> buffer(1024);
    ssize_t res = ::getxattr(path.data(), "security.ima", buffer.data(), buffer.size());

    if (res < 0) {
        if (errno == ENODATA) {
            std::cout << "[IMA] Атрибут security.ima відсутній у файлі\n";
        } else {
            std::cout << "[IMA] Помилка getxattr: " << std::generic_category().message(errno) << "\n";
        }
        return;
    }

    std::span<const uint8_t> data(buffer.data(), static_cast<size_t>(res));
    if (data.empty()) {
        std::cout << "[IMA] Атрибут security.ima порожній\n";
        return;
    }

    const auto type = static_cast<ImaXattrType>(data[0]);
    std::cout << "[IMA] Зчитано " << data.size() << " байт. Тип: 0x"
              << std::hex << std::setfill('0') << std::setw(2) << static_cast<int>(data[0])
              << std::dec << "\n";

    if (type == ImaXattrType::DigestNg && data.size() >= 2) {
        const uint8_t algo = data[1];
        std::cout << "  -> Формат: DIGEST_NG (необроблений хеш)\n";
        std::cout << "  -> Алгоритм: " << algoToName(algo) << "\n";
        std::cout << "  -> Хеш вмісту (hex): ";
        for (size_t i = 2; i < data.size(); ++i) {
            std::cout << std::hex << std::setfill('0') << std::setw(2) << static_cast<int>(data[i]);
        }
        std::cout << std::dec << "\n";
    } else if ((type == ImaXattrType::EvmSig || type == ImaXattrType::AsymSig) &&
               data.size() >= sizeof(SignatureV2Hdr)) {
        const auto* hdr = reinterpret_cast<const SignatureV2Hdr*>(data.data());
        const uint32_t keyid = __builtin_bswap32(hdr->keyid);
        const uint16_t sigLen = __builtin_bswap16(hdr->sig_size);

        std::cout << "  -> Формат: Асиметричний цифровий підпис (v" << static_cast<int>(hdr->version) << ")\n";
        std::cout << "  -> Алгоритм хешування: " << algoToName(hdr->hash_algo);
        std::cout << "  -> Key ID у брелоку .ima: 0x" << std::hex << std::setfill('0') << std::setw(8) << keyid << std::dec << "\n";
        std::cout << "  -> Розмір цифрового підпису: " << sigLen << " байт\n";
    }
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <шлях_до_файлу>\n";
        return EXIT_FAILURE;
    }

    std::cout << "=== Аналіз цілісності файлу (C++20): " << argv[1] << " ===\n";
    inspectImaXattr(argv[1]);
    return EXIT_SUCCESS;
}
```
:::

## Моніторинг та розбір журналу вимірювань securityfs

Окрім аналізу індивідуальних файлів на диску, адміністратори та розробники захищених систем можуть перевірити весь журнал виконаних вимірювань IMA, що зберігається в операційній пам'яті ядра. Інтерфейс доступний через віртуальний файл `/sys/kernel/security/ima/ascii_runtime_measurements`.

Кожен рядок журналу описує однакові операції розширення регістра PCR і має структуру з чотирьох основних колонок:

`PCR_NUM  TEMPLATE_HASH  TEMPLATE_NAME  CONTENT_DATA`

Розглянемо типовий запис із системного журналу:
`10 4f3a2b1c8e9f... ima-ng sha256:8f3c4d2e... /usr/bin/sudo`

1. **`PCR_NUM` (`10`)**: Номер Platform Configuration Register регістра апаратного модуля TPM 2.0, в який було відправлено вимірювання. Для підсистеми IMA за замовчуванням виділено PCR 10.
2. **`TEMPLATE_HASH`**: Криптографічний хеш самого запису журналу, обчислений над розгорнутою структурою шаблону IMA.
3. **`TEMPLATE_NAME` (`ima-ng`)**: Назва шаблону вимірювання ядра. Сучасне ядро використовує шаблон `ima-ng` (Next Generation) або `ima-sig` (якщо записується цифровий підпис).
4. **`CONTENT_DATA` (`sha256:8f3c... /usr/bin/sudo`)**: Ідентифікатор криптографічного алгоритму, обчислений дайджест вмісту файлу та абсолютний шлях до файлу у Virtual File System.

## Крайові випадки та обробка системних помилок

При розробці системних інструментів верифікації розробник повинен зважати на декілька крайових ситуацій під час роботи з IMA/EVM:

- **Відсутність змонтованого securityfs**: Якщо віртуальна файлова система `securityfs` не змонтована у `/sys/kernel/security`, утиліта не зможе прочитати ані список вимірювань, ані завантажити нові правила політики. Для монтажу використовується команда `mount -t securityfs securityfs /sys/kernel/security`.
- **Помилки `EACCES` проти `EPERM`**: При ввімкненому `ima_appraise=enforce` спроба виконання підробленого бінарника повертає `EACCES` (Permission Denied). Проте спроба модифікації захищеного розширеного атрибута без привілеїв `CAP_SYS_ADMIN` повернути помилку `EPERM` (Operation Not Permitted).
- **Спеціальні файлові системи**: Політики за замовчуванням виключають псевдо-файлові системи `proc`, `sysfs`, `tmpfs`, `devtmpfs` з обробки Appraisal, оскільки вміст у них генерується динамічно у пам'яті і не має фізичного носія на диску.
- **Взаємодія з обмеженнями SELinux та AppArmor**: Якщо локальна політика MAC забороняє домену процесу доступ до читання розширених атрибутів простору `security.*`, системний виклик `getxattr()` поверне помилку `EACCES` незалежно від стану атрибута на диску.

При розробці систем розгортання для накладання підписів у просторі користувача застосовується утиліта `evmctl` з пакета `ima-evm-utils`. Команда `evmctl ima_sign --key /etc/keys/x509_ima.der /usr/bin/sudo` автоматично обчислює SHA-256 хеш файлу, підписує його закритим ключем і записує бінарну структуру `signature_v2_hdr` безпосередньо в розширений атрибут `security.ima`. Перевірити стан накладеного підпису можна також утилітою `evmctl ima_verify --key /etc/keys/x509_ima.der /usr/bin/sudo`, яка поверне статуси `VERIFY_SUCCESS` або `VERIFY_FAIL`.
