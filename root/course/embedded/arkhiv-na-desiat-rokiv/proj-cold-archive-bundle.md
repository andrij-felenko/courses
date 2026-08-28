# Автоматизоване пакування та перевірка холодного архіву

Створення десятирічного холодного архіву не може бути ручною операцією, де інженер копіює випадкові папки на диск. Людський фактор неминуче призведе до забутого субмодуля, втраченого файла конфігурації компілятора або неправильної ревізії схеми.

У цьому практичному проекті ми реалізуємо повний двохетапний конвеєр:
1. **Скрипт пакування та консервації (`archive_seal.py`):** збирає автономні `git bundle`, експортує OCI-образ контейнера збірки, збирає апаратні PDF/BOM-файли, генерує криптографічний маніфест за [специфікацією LTS-Manifest](root:embedded/arkhiv-na-desiat-rokiv/api-archive-manifest-spec.md) і підписує його цифровим ключем.
2. **Автономна утиліта верифікації (`verify_archive`):** швидка програма мовами C та C++, яка працює на ізольованій станції без інтернету, розраховує контрольні суми SHA-256 усіх файлів, перевіряє цілісність маніфесту та звітує про стан архіву.

## Архітектура процесу пакування та консервації

Процес формування архіву відбувається на захищеному релізному сервері автоматичної збірки після успішного проходження повного набору модульних, інтеграційних та апаратно-програмних (HIL) тестів. Головна мета консервації — створити монолітний пакет, який можна скопіювати на фізичний носій і розгорнути на будь-якому комп'ютері без доступу до локальної мережі чи інтернету.

Етапи роботи скрипта консервації:
1. **Ізоляція Git-історії:** Замість копіювання робочого каталогу з файлами `.git` виконується команда `git bundle create --all`. Це пакує всі гілки, релізні теги, підписи комітів та історію змін в один герметичний файл. Субмодулі обробляються рекурсивно й зберігаються в окремих бандлах.
2. **Фіксація OCI-образу контейнера:** Виконується експорт шарів Docker/Podman у монолітний архів `.tar.gz`. Це гарантує, що версія операційної системи хоста, пакетний менеджер, компілятор і бібліотека C будуть зафіксовані в незмінному стані.
3. **Збір апаратної документації:** Скрипт копіює векторні схеми PDF/A, файли шарів Gerber, перелік компонентів (BOM) у форматі CSV та архів збережених даташитів із кремнієвими листами помилок (*silicon errata*).
4. **Розрахунок хешів і генерація маніфесту:** Скрипт побайтово обчислює контрольні суми SHA-256 для кожного артефакту, формує документ `archive-manifest.json` та створює відокремлений цифровий підпис.

```python
#!/usr/bin/env python3
import os
import sys
import json
import hashlib
import subprocess
import shutil
from datetime import datetime, timezone

def sha256_file(filepath):
    """Обчислення SHA-256 для файлу блоками по 64 КБ."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def create_git_bundle(repo_path, output_bundle):
    """Створення автономного git bundle з усіма гілками та тегами."""
    cmd = ["git", "-C", repo_path, "bundle", "create", output_bundle, "--all"]
    subprocess.run(cmd, check=True)

def seal_archive(project_dir, output_archive_dir):
    os.makedirs(output_archive_dir, exist_ok=True)
    os.makedirs(os.path.join(output_archive_dir, "src"), exist_ok=True)
    os.makedirs(os.path.join(output_archive_dir, "bin"), exist_ok=True)
    os.makedirs(os.path.join(output_archive_dir, "env"), exist_ok=True)
    os.makedirs(os.path.join(output_archive_dir, "hw"), exist_ok=True)
    os.makedirs(os.path.join(output_archive_dir, "docs"), exist_ok=True)

    # 1. Експорт вихідного коду в автономний bundle
    main_bundle = os.path.join(output_archive_dir, "src", "main_firmware.bundle")
    create_git_bundle(project_dir, main_bundle)

    # 2. Отримання SHA коміту та дерева
    commit_sha = subprocess.check_output(
        ["git", "-C", project_dir, "rev-parse", "HEAD"], text=True
    ).strip()

    # 3. Експорт образу контейнера тулчейну (якщо використовується Docker/Podman)
    container_tar = os.path.join(output_archive_dir, "env", "builder_env.tar.gz")
    # subprocess.run(["docker", "save", "firmware-builder:v1.0", "-o", container_tar], check=True)

    # 4. Формування маніфесту
    manifest = {
        "schema_version": "1.2.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "epoch_timestamp": int(datetime.now(timezone.utc).timestamp()),
        "commit_sha": commit_sha,
        "files": []
    }

    # Обхід усіх файлів у структурі та збір хешів
    for root, _, files in os.walk(output_archive_dir):
        for f in files:
            if f in ["archive-manifest.json", "archive-manifest.sig"]:
                continue
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, output_archive_dir).replace("\\", "/")
            manifest["files"].append({
                "path": rel_path,
                "size_bytes": os.path.getsize(full_path),
                "sha256": sha256_file(full_path)
            })

    manifest_path = os.path.join(output_archive_dir, "archive-manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"[OK] Архів успішно сформовано: {output_archive_dir}")
    print(f"[OK] Маніфест містить {len(manifest['files'])} артефактів.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Використання: archive_seal.py <каталог_проєкту> <каталог_архіву>")
        sys.exit(1)
    seal_archive(sys.argv[1], sys.argv[2])
```

## Автономна утиліта верифікації (C та C++)

Для перевірки архіву під час щорічного регламентного скрабінгу використовується автономна утиліта `verify_archive`. Вона працює без динамічних зовнішніх залежностей (OpenSSL, cURL тощо), містить власну вбудовану реалізацію алгоритму SHA-256 і може бути запущена навіть під мінімальним середовищем завантажувального накопичувача LiveUSB або на вбудованому стенді перевірки.

Програма відкриває вказаний каталог архіву, зчитує кожен файл блоками фіксованого розміру (64 КБ для оптимізації дискового кешування), покроково оновлює внутрішній стан криптографічного перетворення SHA-256 та звіряє фінальний 64-символьний шістнадцятковий дайджест з еталонним значенням.

Нижче наведено дві ідіоматичні реалізації утиліти верифікації: мовою C (з ручним керуванням пам'яттю та файловими дескрипторами) та мовою C++ (з використанням стандартних бібліотек C++20/C++23: `std::span`, `std::string_view`, `std::filesystem` та `std::expected`).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define SHA256_BLOCK_SIZE 64
#define BUFFER_SIZE 65536

/* Структура контексту для обчислення SHA-256 */
typedef struct {
    uint32_t state[8];
    uint64_t count;
    uint8_t buffer[SHA256_BLOCK_SIZE];
} sha256_ctx_t;

/* Оголошення функцій SHA-256 */
void sha256_init(sha256_ctx_t *ctx);
void sha256_update(sha256_ctx_t *ctx, const uint8_t *data, size_t len);
void sha256_final(sha256_ctx_t *ctx, uint8_t hash[32]);

static const uint32_t k256[64] = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
};

#define ROR(x, n) (((x) >> (n)) | ((x) << (32 - (n))))
#define CH(x, y, z) (((x) & (y)) ^ (~(x) & (z)))
#define MAJ(x, y, z) (((x) & (y)) ^ ((x) & (z)) ^ ((y) & (z)))
#define SIGMA0(x) (ROR(x, 2) ^ ROR(x, 13) ^ ROR(x, 22))
#define SIGMA1(x) (ROR(x, 6) ^ ROR(x, 11) ^ ROR(x, 25))
#define SIG0(x) (ROR(x, 7) ^ ROR(x, 18) ^ ((x) >> 3))
#define SIG1(x) (ROR(x, 17) ^ ROR(x, 19) ^ ((x) >> 10))

static void sha256_transform(uint32_t state[8], const uint8_t block[64]) {
    uint32_t w[64], a, b, c, d, e, f, g, h;
    for (int i = 0; i < 16; i++) {
        w[i] = ((uint32_t)block[i * 4] << 24) | ((uint32_t)block[i * 4 + 1] << 16) |
               ((uint32_t)block[i * 4 + 2] << 8) | ((uint32_t)block[i * 4 + 3]);
    }
    for (int i = 16; i < 64; i++) {
        w[i] = SIG1(w[i - 2]) + w[i - 7] + SIG0(w[i - 15]) + w[i - 16];
    }
    a = state[0]; b = state[1]; c = state[2]; d = state[3];
    e = state[4]; f = state[5]; g = state[6]; h = state[7];
    for (int i = 0; i < 64; i++) {
        uint32_t t1 = h + SIGMA1(e) + CH(e, f, g) + k256[i] + w[i];
        uint32_t t2 = SIGMA0(a) + MAJ(a, b, c);
        h = g; g = f; f = e; e = d + t1;
        d = c; c = b; b = a; a = t1 + t2;
    }
    state[0] += a; state[1] += b; state[2] += c; state[3] += d;
    state[4] += e; state[5] += f; state[6] += g; state[7] += h;
}

void sha256_init(sha256_ctx_t *ctx) {
    ctx->state[0] = 0x6a09e667; ctx->state[1] = 0xbb67ae85;
    ctx->state[2] = 0x3c6ef372; ctx->state[3] = 0xa54ff53a;
    ctx->state[4] = 0x510e527f; ctx->state[5] = 0x9b05688c;
    ctx->state[6] = 0x1f83d9ab; ctx->state[7] = 0x5be0cd19;
    ctx->count = 0;
}

void sha256_update(sha256_ctx_t *ctx, const uint8_t *data, size_t len) {
    size_t index = (size_t)(ctx->count & 0x3f);
    ctx->count += len;
    size_t part_len = 64 - index;
    size_t i = 0;
    if (len >= part_len) {
        memcpy(&ctx->buffer[index], data, part_len);
        sha256_transform(ctx->state, ctx->buffer);
        for (i = part_len; i + 63 < len; i += 64) {
            sha256_transform(ctx->state, &data[i]);
        }
        index = 0;
    }
    memcpy(&ctx->buffer[index], &data[i], len - i);
}

void sha256_final(sha256_ctx_t *ctx, uint8_t hash[32]) {
    uint8_t bits[8];
    uint64_t total_bits = ctx->count * 8;
    for (int i = 0; i < 8; i++) {
        bits[i] = (uint8_t)(total_bits >> ((7 - i) * 8));
    }
    size_t index = (size_t)(ctx->count & 0x3f);
    size_t pad_len = (index < 56) ? (56 - index) : (120 - index);
    static const uint8_t padding[64] = { 0x80 };
    sha256_update(ctx, padding, pad_len);
    sha256_update(ctx, bits, 8);
    for (int i = 0; i < 8; i++) {
        hash[i * 4] = (uint8_t)(ctx->state[i] >> 24);
        hash[i * 4 + 1] = (uint8_t)(ctx->state[i] >> 16);
        hash[i * 4 + 2] = (uint8_t)(ctx->state[i] >> 8);
        hash[i * 4 + 3] = (uint8_t)(ctx->state[i]);
    }
}

/* Перевірка одного файлу за контрольною сумою */
int verify_single_file(const char *base_dir, const char *rel_path, const char *expected_hex) {
    char full_path[1024];
    snprintf(full_path, sizeof(full_path), "%s/%s", base_dir, rel_path);

    FILE *f = fopen(full_path, "rb");
    if (!f) {
        fprintf(stderr, "[ПОМИЛКА] Файл не знайдено: %s\n", full_path);
        return -1;
    }

    sha256_ctx_t ctx;
    sha256_init(&ctx);

    uint8_t *buf = (uint8_t *)malloc(BUFFER_SIZE);
    if (!buf) {
        fclose(f);
        return -1;
    }

    size_t read_bytes;
    while ((read_bytes = fread(buf, 1, BUFFER_SIZE, f)) > 0) {
        sha256_update(&ctx, buf, read_bytes);
    }
    free(buf);
    fclose(f);

    uint8_t hash[32];
    sha256_final(&ctx, hash);

    char calc_hex[65];
    for (int i = 0; i < 32; i++) {
        sprintf(&calc_hex[i * 2], "%02x", hash[i]);
    }
    calc_hex[64] = '\0';

    if (strcmp(calc_hex, expected_hex) != 0) {
        fprintf(stderr, "[ХЕШ НЕ ЗБІГСЯ] %s\n  Очікувався: %s\n  Отримано:    %s\n",
                rel_path, expected_hex, calc_hex);
        return -2;
    }

    printf("[OK] %s\n", rel_path);
    return 0;
}
```
```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <filesystem>
#include <iomanip>
#include <sstream>
#include <memory>
#include <expected>
#include <array>
#include <cstdint>

namespace fs = std::filesystem;

class Sha256Calculator {
public:
    Sha256Calculator() { reset(); }

    void reset() {
        m_state = {0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
                   0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19};
        m_count = 0;
        m_buffer.fill(0);
    }

    void update(std::span<const uint8_t> data) {
        size_t index = static_cast<size_t>(m_count & 0x3f);
        m_count += data.size();
        size_t part_len = 64 - index;
        size_t i = 0;

        if (data.size() >= part_len) {
            std::copy_n(data.data(), part_len, m_buffer.begin() + index);
            transform(m_buffer.data());
            for (i = part_len; i + 63 < data.size(); i += 64) {
                transform(data.data() + i);
            }
            index = 0;
        }
        std::copy_n(data.data() + i, data.size() - i, m_buffer.begin() + index);
    }

    [[nodiscard]] std::string finalize() {
        std::array<uint8_t, 8> bits{};
        uint64_t total_bits = m_count * 8;
        for (size_t i = 0; i < 8; ++i) {
            bits[i] = static_cast<uint8_t>(total_bits >> ((7 - i) * 8));
        }

        size_t index = static_cast<size_t>(m_count & 0x3f);
        size_t pad_len = (index < 56) ? (56 - index) : (120 - index);
        std::vector<uint8_t> padding(pad_len, 0);
        padding[0] = 0x80;

        update(padding);
        update(bits);

        std::ostringstream ss;
        ss << std::hex << std::setfill('0');
        for (uint32_t val : m_state) {
            ss << std::setw(8) << val;
        }
        return ss.str();
    }

private:
    static constexpr uint32_t ror(uint32_t x, uint32_t n) noexcept {
        return (x >> n) | (x << (32 - n));
    }
    static constexpr uint32_t ch(uint32_t x, uint32_t y, uint32_t z) noexcept {
        return (x & y) ^ (~x & z);
    }
    static constexpr uint32_t maj(uint32_t x, uint32_t y, uint32_t z) noexcept {
        return (x & y) ^ (x & z) ^ (y & z);
    }
    static constexpr uint32_t sigma0(uint32_t x) noexcept {
        return ror(x, 2) ^ ror(x, 13) ^ ror(x, 22);
    }
    static constexpr uint32_t sigma1(uint32_t x) noexcept {
        return ror(x, 6) ^ ror(x, 11) ^ ror(x, 25);
    }
    static constexpr uint32_t sig0(uint32_t x) noexcept {
        return ror(x, 7) ^ ror(x, 18) ^ (x >> 3);
    }
    static constexpr uint32_t sig1(uint32_t x) noexcept {
        return ror(x, 17) ^ ror(x, 19) ^ (x >> 10);
    }

    void transform(const uint8_t* block) {
        static constexpr std::array<uint32_t, 64> k = {
            0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
            0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
            0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
            0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
            0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
            0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
            0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
            0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
        };

        std::array<uint32_t, 64> w{};
        for (size_t i = 0; i < 16; ++i) {
            w[i] = (static_cast<uint32_t>(block[i * 4]) << 24) |
                   (static_cast<uint32_t>(block[i * 4 + 1]) << 16) |
                   (static_cast<uint32_t>(block[i * 4 + 2]) << 8) |
                   (static_cast<uint32_t>(block[i * 4 + 3]));
        }
        for (size_t i = 16; i < 64; ++i) {
            w[i] = sig1(w[i - 2]) + w[i - 7] + sig0(w[i - 15]) + w[i - 16];
        }

        uint32_t a = m_state[0], b = m_state[1], c = m_state[2], d = m_state[3];
        uint32_t e = m_state[4], f = m_state[5], g = m_state[6], h = m_state[7];

        for (size_t i = 0; i < 64; ++i) {
            uint32_t t1 = h + sigma1(e) + ch(e, f, g) + k[i] + w[i];
            uint32_t t2 = sigma0(a) + maj(a, b, c);
            h = g; g = f; f = e; e = d + t1;
            d = c; c = b; b = a; a = t1 + t2;
        }

        m_state[0] += a; m_state[1] += b; m_state[2] += c; m_state[3] += d;
        m_state[4] += e; m_state[5] += f; m_state[6] += g; m_state[7] += h;
    }

    std::array<uint32_t, 8> m_state{};
    uint64_t m_count{0};
    std::array<uint8_t, 64> m_buffer{};
};

enum class VerificationError {
    FileNotFound,
    ReadError,
    ChecksumMismatch
};

struct ArchiveValidator {
    static std::expected<void, VerificationError> verifyFile(
        const fs::path& basePath,
        std::string_view relPath,
        std::string_view expectedHash
    ) {
        fs::path fullPath = basePath / relPath;
        std::ifstream file(fullPath, std::ios::binary);
        if (!file) {
            std::cerr << "[ПОМИЛКА] Файл відсутній: " << fullPath << '\n';
            return std::unexpected(VerificationError::FileNotFound);
        }

        Sha256Calculator calc;
        std::vector<uint8_t> buffer(65536);

        while (file.read(reinterpret_cast<char*>(buffer.data()), buffer.size()) || file.gcount() > 0) {
            calc.update(std::span(buffer.data(), static_cast<size_t>(file.gcount())));
        }

        std::string calculated = calc.finalize();
        if (calculated != expectedHash) {
            std::cerr << "[ХЕШ НЕ ЗБІГСЯ] " << relPath
                      << "\n  Очікувано:  " << expectedHash
                      << "\n  Обчислено:  " << calculated << '\n';
            return std::unexpected(VerificationError::ChecksumMismatch);
        }

        std::cout << "[OK] " << relPath << '\n';
        return {};
    }
};
```
:::

## Інженерні пастки під час консервації та перевірки

Практика довготривалого супроводу показує, що навіть за наявності автоматизованих скриптів під час консервації та верифікації виникають типові підводні камені:

1. **Недетерміновані часові мітки в tar-архівах:**
   Утиліта `tar` за замовчуванням записує поточний час створення архіву в заголовок кожного файлу. Два архіви, створені з однакових джерел з різницею в 5 секунд, матимуть різні контрольні суми SHA-256. Для усунення використовуйте прапорці `--mtime='@1787911200'`, `--sort=name`, `--owner=0`, `--group=0`.
2. **Плаваючий хеш шарів Docker/OCI:**
   Якщо образ контейнера тулчейну не експортовано в статичний `.tar` файл, а залишено як тег у реєстрі, зміна базового образу (наприклад, `debian:stable`) з часом підмінить компілятор або версію `glibc`, зруйнувавши відтворюваність збірки.
3. **Розрив зв'язків Git Submodules:**
   Якщо субмодулі додані через зовнішні URL (`https://github.com/...`), а не заморожені у локальні `git bundle`, через 5 років збірка впаде через помилку мережевого з'єднання на віддаленому сервері.
4. **Символічні посилання та права доступу:**
   Під час копіювання між файловими системами (NTFS, EXT4, FAT32, UDF) можуть втрачатися біти виконання (`chmod +x`) для скриптів збірки та цілісність символічних посилань. Зберігайте файли виключно у стандартизованих контейнерах або tar/iso образах із фіксацією прав доступу.
5. **Втрата ключів розшифрування під час пожежного тренування:**
   Якщо частки секрету Шаміра не перевірялися на процедуру складання, під час реальної аварії може виявитися, що одна з часток записана з помилкою у шістнадцятковому символі. Проводьте тестове складання секрету під час кожного планового тренування.
6. **Різниця переведення рядків (CRLF проти LF):**
   Якщо вихідні тексти відкривалися або пакувалися у середовищі Windows без суворого контролю `core.autocrlf = input`, символи повернення каретки `\r` змінять контрольні суми текстових файлів конфігурацій та лінкерних скриптів. Фіксуйте конфігурацію `.gitattributes` у корені репозиторію.
7. **Зміна порядку сканування каталогів операційною системою:**
   Функції `os.walk` у Python або `readdir` у C не гарантують однакового порядку обходу файлів на різних файлових системах. Перед додаванням записів до маніфесту список шляхів завжди обов'язково сортується за зростанням байтових значень UTF-8.
