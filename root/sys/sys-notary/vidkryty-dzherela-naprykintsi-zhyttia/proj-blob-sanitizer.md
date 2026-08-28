# ⚙️ Валідатор кодової бази перед EOL-публікацією: виявлення блобів та секретів

Коли компанія ухвалює рішення відкрити вихідний код пристрою після завершення життєвого циклу, публікація сирого репозиторію без попереднього глибокого аудиту створює прямі юридичні та безпекові ризики. Усередині дерева коду залишаються сторонні двійкові бібліотеки чипмейкерів під NDA, зашиті приватні ключі підпису та сертифікати виробничих серверів, а також зашифровані радіокалібрувальні таблиці, представлені у вигляді шістнадцяткових масивів у C-заголовках. Якщо такий архів потрапляє у відкритий доступ, юридичний відділ стикається з судовими позовами від постачальників кремнію за порушення угод про нерозголошення, а виробнича криптографія компанії виявляється скомпрометованою.

Для запобігання цим загрозам інженерний процес підготовки EOL-релізу вимагає автоматизованого сканування всіх файлів репозиторію. Валідатор санітизації вирішує чотири критичні завдання:
1. **Виявлення двійкових сигнатур:** розпізнавання заголовків виконуваних форматів (ELF, Mach-O, Windows PE/COFF, U-Boot `uImage`, Flattened Device Tree `DTB` та Java байткод) незалежно від розширення файлу.
2. **Аналіз ентропії Шеннона:** математичний розрахунок рівномірності розподілу байтів для виявлення зашифрованих або стиснених мікрокодів, схованих всередині масивів `const uint8_t firmware_blob[]`.
3. **Пошук маркерів конфіденційності (NDA keywords):** детекція рядків «PROPRIETARY», «CONFIDENTIAL», «DO NOT DISTRIBUTE» та назв закритих SDK чипмейкерів у коментарях і строкових літералах.
4. **Виявлення зашитих криптографічних секретів:** сканування блоків `BEGIN PRIVATE KEY`, шістнадцяткових ключів шифрування AES та паролів доступу до сервісних облікових записів.

## Математична основа: ентропія Шеннона для бінарного аналізу

Прихований мікрокод чи зашифрований бінарний блоб, вбудований у вихідний файл у вигляді масиву чисел, візуально нагадує звичайні константні таблиці. Відрізнити його дозволяє розрахунок інформаційної ентропії Шеннона (англ. *Shannon entropy*). Для потоку з 256 можливих значень байтів ентропія обчислюється за формулою:

```
H = - ∑ (p[i] · log₂(p[i]))
```
де `p[i]` — емпірична ймовірність появи байта зі значенням `i` в аналізованому блоці даних (`p[i] = count[i] / total_bytes`).

Звичайний текстовий вихідний код мовами C або C++ має типову ентропію в діапазоні від 3.5 до 5.0 біт на байт через високу частоту пробілів, службових слів та повторюваних символів синтаксису. Натомість скомпільований машинний код, стиснені архіви (gzip, lzma) та зашифровані бінарні блоби мають майже рівномірний розподіл байтів, що дає ентропію від 7.2 до 8.0 біт на байт. Перевищення порогу `H ≥ 7.2` для блоків даних розміром понад 512 байтів слугує надійним тригером наявності прихованого двійкового вмісту.

Під час аналізу великих файлів розрахунок середньої ентропії по всьому об'єму може згладжувати локальні двійкові вставки (наприклад, невеликий двійковий блоб на 2 КБ усередині текстового драйвера на 50 КБ). Щоб виявити локалізовані артефакти, валідатор розбиває буфер на ковзні вікна (англ. *sliding window*) фіксованого розміру (зазвичай 512 або 1024 байти) з перекриттям у 50%. Розрахунок ентропії для кожного вікна дає часовий профіль розподілу інформації: будь-який різкий стрибок графіка вище рівня 7.2 біт/байт позначає точні межі вбудованого двійкового образу.

## Архітектура перевірки двійкових сигнатур та маркерів

Окрім статистичного аналізу ентропії, валідатор проводить детерміновану перевірку сигнатур на перших байтах кожного файлу та в точках зсуву ковзного вікна. Двійкові виконувані файли містять унікальні сигнатури (магічні байти):
- **ELF (Executable and Linkable Format):** байти `\x7fELF` (0x7F 0x45 0x4C 0x46), що передують виконуваним файлам Linux/Unix, об'єктним файлам драйверів (`.o`) та динамічним бібліотекам (`.so`).
- **PE/COFF (Portable Executable):** двобайтова сигнатура `MZ` (0x4D 0x5A), яка вказує на виконувані файли Windows або закриті утиліти для прошивки.
- **Mach-O / Fat Binary:** магічні числа `0xCAFEBABE`, `0xFEEDFACE` або `0xFEEDFACF`, що ідентифікують бінарники платформ Apple/BSD.
- **U-Boot uImage:** заголовок спадщини U-Boot `0x27051956`, що містить контрольні суми та метадані завантаження ядра Linux.
- **Flattened Device Tree (DTB):** двійковий заголовок дерева пристроїв `0xD00DFEED`, необхідний ядру Linux для ініціалізації апаратури.

Пошук текстових маркерів здійснюється без урахування регістру символів і фокусується на юридичних застереженнях чипмейкерів (Qualcomm, Broadcom, MediaTek, Nordic, Realtek), наявність яких свідчить про порушення прав інтелектуальної власності. Перевірка на приватні криптографічні ключі фіксує текстові маркери заголовків OpenSSL і OpenSSH, що запобігає випадковому розкриттю виробничих сертифікатів CA та закритих RSA/ECDSA ключів.

## Реалізація валідатора санітизації

Нижче наведено повнофункціональну реалізацію сканера-валідатора. Програма аналізує вхідний буфер файлу, перевіряє чарівні числа двійкових форматів, обчислює ентропію розподілу байтів і здійснює контекстний пошук юридичних маркерів та приватних ключів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define MAX_FINDINGS 64
#define ENTROPY_THRESHOLD 7.2
#define MIN_BUFFER_FOR_ENTROPY 256

typedef enum {
    SEV_INFO,
    SEV_WARNING,
    SEV_CRITICAL
} severity_t;

typedef enum {
    FINDING_NONE,
    FINDING_BINARY_MAGIC,
    FINDING_HIGH_ENTROPY,
    FINDING_NDA_MARKER,
    FINDING_PRIVATE_KEY
} finding_type_t;

typedef struct {
    finding_type_t type;
    severity_t severity;
    const char *rule_name;
    char description[128];
    size_t offset;
} finding_t;

typedef struct {
    size_t file_size;
    double entropy;
    size_t total_findings;
    finding_t findings[MAX_FINDINGS];
} scan_report_t;

typedef struct {
    const uint8_t magic[8];
    size_t length;
    const char *format_name;
} binary_signature_t;

static const binary_signature_t SIGNATURES[] = {
    {{0x7F, 'E', 'L', 'F'}, 4, "Executable and Linkable Format (ELF)"},
    {{'M', 'Z'}, 2, "DOS/PE Executable (MZ)"},
    {{0xCA, 0xFE, 0xBA, 0xBE}, 4, "Mach-O / Java Class (Fat Binary)"},
    {{0xFE, 0xED, 0xFA, 0xCE}, 4, "Mach-O 32-bit"},
    {{0xFE, 0xED, 0xFA, 0xCF}, 4, "Mach-O 64-bit"},
    {{0x27, 0x05, 0x19, 0x56}, 4, "U-Boot Legacy Image (uImage)"},
    {{0xD0, 0x0D, 0xFE, 0xED}, 4, "Flattened Device Tree (DTB)"}
};
static const size_t NUM_SIGNATURES = sizeof(SIGNATURES) / sizeof(SIGNATURES[0]);

static const char *NDA_PATTERNS[] = {
    "CONFIDENTIAL AND PROPRIETARY",
    "DO NOT DISTRIBUTE",
    "QUALCOMM PROPRIETARY",
    "BROADCOM PROPRIETARY",
    "MEDIATEK STRICT NDA",
    "INTERNAL USE ONLY",
    "UNDER NON-DISCLOSURE AGREEMENT"
};
static const size_t NUM_NDA_PATTERNS = sizeof(NDA_PATTERNS) / sizeof(NDA_PATTERNS[0]);

static const char *KEY_PATTERNS[] = {
    "-----BEGIN RSA PRIVATE KEY-----",
    "-----BEGIN EC PRIVATE KEY-----",
    "-----BEGIN PRIVATE KEY-----",
    "-----BEGIN OPENSSH PRIVATE KEY-----",
    "PRIVATE_KEY_SECRET"
};
static const size_t NUM_KEY_PATTERNS = sizeof(KEY_PATTERNS) / sizeof(KEY_PATTERNS[0]);

static void add_finding(scan_report_t *report, finding_type_t type,
                        severity_t sev, const char *rule, const char *desc, size_t off) {
    if (report->total_findings >= MAX_FINDINGS) {
        return;
    }
    finding_t *f = &report->findings[report->total_findings++];
    f->type = type;
    f->severity = sev;
    f->rule_name = rule;
    f->offset = off;
    strncpy(f->description, desc, sizeof(f->description) - 1);
    f->description[sizeof(f->description) - 1] = '\0';
}

double calculate_shannon_entropy(const uint8_t *data, size_t len) {
    if (len == 0) return 0.0;
    
    size_t byte_counts[256] = {0};
    for (size_t i = 0; i < len; ++i) {
        byte_counts[data[i]]++;
    }

    double entropy = 0.0;
    for (int i = 0; i < 256; ++i) {
        if (byte_counts[i] > 0) {
            double p = (double)byte_counts[i] / (double)len;
            entropy -= p * (log(p) / log(2.0));
        }
    }
    return entropy;
}

void scan_buffer(const uint8_t *data, size_t len, scan_report_t *report) {
    report->file_size = len;
    report->total_findings = 0;
    report->entropy = calculate_shannon_entropy(data, len);

    /* 1. Перевірка бінарних сигнатур у заголовку */
    for (size_t s = 0; s < NUM_SIGNATURES; ++s) {
        if (len >= SIGNATURES[s].length &&
            memcmp(data, SIGNATURES[s].magic, SIGNATURES[s].length) == 0) {
            add_finding(report, FINDING_BINARY_MAGIC, SEV_CRITICAL,
                        "BIN_HEADER", SIGNATURES[s].format_name, 0);
        }
    }

    /* 2. Перевірка ентропії */
    if (len >= MIN_BUFFER_FOR_ENTROPY && report->entropy >= ENTROPY_THRESHOLD) {
        char buf[64];
        snprintf(buf, sizeof(buf), "Висока ентропія (%.2f біт/байт): підозра на зашитий блоб", report->entropy);
        add_finding(report, FINDING_HIGH_ENTROPY, SEV_WARNING, "HIGH_ENTROPY", buf, 0);
    }

    /* 3. Сканування текстових шаблонів (NDA та ключі) */
    const char *text = (const char *)data;
    for (size_t p = 0; p < NUM_NDA_PATTERNS; ++p) {
        const char *pat = NDA_PATTERNS[p];
        size_t pat_len = strlen(pat);
        if (len < pat_len) continue;
        for (size_t i = 0; i <= len - pat_len; ++i) {
            if (strncasecmp(&text[i], pat, pat_len) == 0) {
                add_finding(report, FINDING_NDA_MARKER, SEV_CRITICAL,
                            "NDA_POLICY", pat, i);
                break;
            }
        }
    }

    for (size_t k = 0; k < NUM_KEY_PATTERNS; ++k) {
        const char *pat = KEY_PATTERNS[k];
        size_t pat_len = strlen(pat);
        if (len < pat_len) continue;
        for (size_t i = 0; i <= len - pat_len; ++i) {
            if (strncmp(&text[i], pat, pat_len) == 0) {
                add_finding(report, FINDING_PRIVATE_KEY, SEV_CRITICAL,
                            "LEAKED_SECRET", pat, i);
                break;
            }
        }
    }
}

void print_scan_report(const char *filename, const scan_report_t *report) {
    const char *sev_str[] = {"INFO", "WARNING", "CRITICAL"};
    printf("=================================================================\n");
    printf("Звіт санітизації: %s (Розмір: %zu байт, Ентропія: %.2f біт/байт)\n",
           filename, report->file_size, report->entropy);
    printf("=================================================================\n");
    if (report->total_findings == 0) {
        printf(" [OK] Жодних закритих блобів або секретів не виявлено.\n");
        return;
    }

    for (size_t i = 0; i < report->total_findings; ++i) {
        const finding_t *f = &report->findings[i];
        printf(" [%-8s] Правило: %-14s | Зсув: 0x%06zx | %s\n",
               sev_str[f->severity], f->rule_name, f->offset, f->description);
    }
    printf("-----------------------------------------------------------------\n");
    printf(" Загалом зауважень: %zu\n\n", report->total_findings);
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <array>
#include <cmath>
#include <cstdint>
#include <algorithm>
#include <iomanip>

namespace eol::sanitizer {

enum class Severity {
    Info,
    Warning,
    Critical
};

enum class FindingType {
    BinaryMagic,
    HighEntropy,
    NdaMarker,
    PrivateKey
};

struct Finding {
    FindingType type;
    Severity severity;
    std::string_view rule_name;
    std::string description;
    std::size_t offset;
};

struct ScanReport {
    std::size_t file_size{0};
    double entropy{0.0};
    std::vector<Finding> findings;

    [[nodiscard]] bool has_critical_findings() const noexcept {
        return std::any_of(findings.begin(), findings.end(), [](const Finding& f) {
            return f.severity == Severity::Critical;
        });
    }
};

struct BinarySignature {
    std::span<const uint8_t> magic;
    std::string_view format_name;
};

class RepositorySanitizer {
public:
    static constexpr double ENTROPY_THRESHOLD = 7.2;
    static constexpr std::size_t MIN_BUFFER_FOR_ENTROPY = 256;

    static double calculate_shannon_entropy(std::span<const uint8_t> data) noexcept {
        if (data.empty()) return 0.0;

        std::array<std::size_t, 256> byte_counts{};
        for (uint8_t byte : data) {
            byte_counts[byte]++;
        }

        double entropy = 0.0;
        const double total = static_cast<double>(data.size());
        for (std::size_t count : byte_counts) {
            if (count > 0) {
                const double p = static_cast<double>(count) / total;
                entropy -= p * (std::log(p) / std::log(2.0));
            }
        }
        return entropy;
    }

    [[nodiscard]] ScanReport scan(std::span<const uint8_t> buffer) const {
        ScanReport report;
        report.file_size = buffer.size();
        report.entropy = calculate_shannon_entropy(buffer);

        check_binary_signatures(buffer, report);
        check_entropy_anomaly(buffer, report);
        check_text_patterns(buffer, report);

        return report;
    }

private:
    static void check_binary_signatures(std::span<const uint8_t> buffer, ScanReport& report) {
        static constexpr uint8_t ELF_M[] = {0x7F, 'E', 'L', 'F'};
        static constexpr uint8_t PE_M[]  = {'M', 'Z'};
        static constexpr uint8_t JAVA_M[]= {0xCA, 0xFE, 0xBA, 0xBE};
        static constexpr uint8_t UIMG_M[]= {0x27, 0x05, 0x19, 0x56};
        static constexpr uint8_t DTB_M[] = {0xD0, 0x0D, 0xFE, 0xED};

        static const std::array<BinarySignature, 5> signatures = {{
            {ELF_M, "Executable and Linkable Format (ELF)"},
            {PE_M, "DOS/PE Executable (MZ)"},
            {JAVA_M, "Mach-O / Java Class (Fat Binary)"},
            {UIMG_M, "U-Boot Legacy Image (uImage)"},
            {DTB_M, "Flattened Device Tree (DTB)"}
        }};

        for (const auto& sig : signatures) {
            if (buffer.size() >= sig.magic.size() &&
                std::equal(sig.magic.begin(), sig.magic.end(), buffer.begin())) {
                report.findings.push_back(Finding{
                    FindingType::BinaryMagic,
                    Severity::Critical,
                    "BIN_HEADER",
                    std::string(sig.format_name),
                    0
                });
            }
        }
    }

    static void check_entropy_anomaly(std::span<const uint8_t> buffer, ScanReport& report) {
        if (buffer.size() >= MIN_BUFFER_FOR_ENTROPY && report.entropy >= ENTROPY_THRESHOLD) {
            report.findings.push_back(Finding{
                FindingType::HighEntropy,
                Severity::Warning,
                "HIGH_ENTROPY",
                "Висока ентропія (" + std::to_string(report.entropy).substr(0, 4) + " біт/байт): зашитий блоб",
                0
            });
        }
    }

    static void check_text_patterns(std::span<const uint8_t> buffer, ScanReport& report) {
        const std::string_view text(reinterpret_cast<const char*>(buffer.data()), buffer.size());

        static constexpr std::array<std::string_view, 5> nda_rules = {
            "CONFIDENTIAL AND PROPRIETARY",
            "DO NOT DISTRIBUTE",
            "QUALCOMM PROPRIETARY",
            "BROADCOM PROPRIETARY",
            "MEDIATEK STRICT NDA"
        };

        for (std::string_view rule : nda_rules) {
            const auto pos = text.find(rule);
            if (pos != std::string_view::npos) {
                report.findings.push_back(Finding{
                    FindingType::NdaMarker,
                    Severity::Critical,
                    "NDA_POLICY",
                    std::string(rule),
                    pos
                });
            }
        }

        static constexpr std::array<std::string_view, 3> key_rules = {
            "-----BEGIN RSA PRIVATE KEY-----",
            "-----BEGIN EC PRIVATE KEY-----",
            "-----BEGIN PRIVATE KEY-----"
        };

        for (std::string_view rule : key_rules) {
            const auto pos = text.find(rule);
            if (pos != std::string_view::npos) {
                report.findings.push_back(Finding{
                    FindingType::PrivateKey,
                    Severity::Critical,
                    "LEAKED_SECRET",
                    std::string(rule),
                    pos
                });
            }
        }
    }
};

void print_report(std::string_view filename, const ScanReport& report) {
    std::cout << "=================================================================\n";
    std::cout << "Звіт санітизації: " << filename << " (Розмір: " << report.file_size
              << " байт, Ентропія: " << std::fixed << std::setprecision(2) << report.entropy << " біт/байт)\n";
    std::cout << "=================================================================\n";

    if (report.findings.empty()) {
        std::cout << " [OK] Жодних закритих блобів або секретів не виявлено.\n\n";
        return;
    }

    for (const auto& f : report.findings) {
        const char* sev = (f.severity == Severity::Critical) ? "CRITICAL" :
                          (f.severity == Severity::Warning)  ? "WARNING" : "INFO";
        std::cout << " [" << std::left << std::setw(8) << sev << "] Правило: "
                  << std::setw(14) << f.rule_name << " | Зсув: 0x" << std::hex << std::setw(6)
                  << std::setfill('0') << f.offset << std::setfill(' ') << std::dec
                  << " | " << f.description << "\n";
    }
    std::cout << "-----------------------------------------------------------------\n";
    std::cout << " Загалом зауважень: " << report.findings.size() << "\n\n";
}

} // namespace eol::sanitizer
```
:::

## Інженерні пастки при санітизації кодової бази

Під час застосування санітизатора в процесі підготовки відкритих EOL-архівів інженери стикаються з декількома типовими крайовими випадками, що вимагають тонкого налаштування правил:

1. **Фальшиві спрацьовування на мультимедійних асетах (Asset False Positives):** стиснені растрові зображення PNG/JPEG, стиснені аудіофайли WAV чи стиснені шрифти TTF, що входять до складу вебінтерфейсу пристрою, мають природну високу ентропію (`H > 7.6`). Якщо валідатор аналізує всі файли підряд, графічні файли позначаються як підозрілі бінарні блоби. Для запобігання цьому сканер повинен попередньо перевіряти MIME-тип або розширення файлу і пропускати відомі формати відкритих мультимедійних ресурсів, якщо їхні сигнатури збігаються з легальними стандартами.
2. **Ілюзія юридичної безпеки від очищення коментарів (Cosmetic Scrubbing Fallacy):** просте текстове видалення рядків `QUALCOMM PROPRIETARY` або заміна імен авторів у файлах не робить закритий драйвер відкритим кодом. Якщо алгоритм керування радіомодулем, структура взаємодії з шиною чи математичний фільтр запатентовані постачальником, публікація репозиторію без прямої ліцензійної згоди власника є порушенням прав інтелектуальної власності. Санітизатор вказує на наявність пропрієтарного коду, який необхідно або отримати за офіційним дозволом, або повністю замінити чистою відкритою реалізацією (англ. *Clean-Room Engineering*).
3. **Руйнування структури збирання проєкту (Broken Build Tree):** механічне видалення знайдених бінарних об'єктних файлів `.o` чи бібліотек `.a` призводить до того, що проєкт перестає збиратися через помилки невизначених символів компонувальника (англ. *undefined reference*). Щоб відкриття коду не перетворилося на створення нездійсненного завдання для спільноти, інженерна команда зобов'язана створити інтерфейсні бібліотеки-заглушки (англ. *stub/mock libraries*), які емулюють функціонал видалених блобів або повертають коди помилок для закритих апаратних модулів.
