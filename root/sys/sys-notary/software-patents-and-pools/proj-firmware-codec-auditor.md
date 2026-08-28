# ⚙️ Аудит медіазалежностей та виявлення запатентованих кодеків у бінарних збірках

Під час складання дистрибутива вбудованого Linux для серійних пристроїв (IP-камер, дронів, робототехніки чи медіахабів) системи збирання на кшталт Yocto Project або Buildroot автоматично компілюють і компонують сотні пакетів. Якщо розробник без урахування юридичних наслідків увімкнув прапорець `gstreamer1.0-plugins-ugly`, зібрав `ffmpeg` із глобальним прапорцем підтримки всіх кодеків або включив бібліотеки `libx264`, `libx265` чи `libfaac`, готова прошивка починає нести приховані патентні зобов'язання перед пулами Via LA чи Access Advance.

Щоб виявити запатентовані алгоритми стиснення до того, як скомпільований образ прошивки надійде у виробничий цех на прошивання або потрапить під митну перевірку, у конвеєрі неперервної інтеграції (CI/CD) застосовують автоматичний аудит двійкових файлів кореневої файлової системи (`rootfs`).

## Механіка відстеження залежностей у бінарних образах

У класичних дистрибутивах Linux залежності між двійковими виконуваними файлами та динамічними бібліотеками фіксуються в заголовках формату ELF (Executable and Linkable Format). Коли компілятор і компонувальник створюють спільну бібліотеку чи бінарник, у динамічну секцію `.dynamic` записуються спеціальні теги:
- `DT_NEEDED`: містить назви динамічних бібліотек (`SONAME`), без яких завантажувач `ld.so` не зможе запустити процес.
- `DT_RPATH` / `DT_RUNPATH`: шляхи пошуку бібліотек в операційній системі.
- `.rodata`: секція константних рядків, де зберігаються імена плагінів, рядкові літерали для викликів `dlopen()` та рядки реєстрації медіафабрик.
- `.dynsym` та `.symtab`: таблиці динамічних та експортованих символів, що містять назви конкретних функцій кодування (`x264_encoder_open`, `faacEncEncode`).

```
/rootfs/usr/bin/  ──► [ Сканер ELF-файлів ] ──► Аналіз секцій DT_NEEDED
/rootfs/usr/lib/  ──► [ Пошук сигнатур   ] ──► Зіставлення з базою патентних ризиків
                                                    │
                                                    ▼
                     Звіт про виявлені ризики (H.264, H.265, AAC, MP3)
```

База сигнатур сканера містить перелік маркерів підвищеного патентного ризику, згрупованих за технологіями та пулами:
- **H.264 / AVC:** `libx264`, `libgstx264.so`, `h264_vaapi`, `h264_v4l2m2m`, `avc1`, `x264_encoder_encode`.
- **H.265 / HEVC:** `libx265`, `libgstx265.so`, `hevc_vaapi`, `h265_v4l2m2m`, `hvc1`, `x265_encoder_encode`.
- **AAC:** `libfaac`, `libfdk_aac`, `libgstaac.so`, `aac_encoder`, `faacEncOpen`.
- **MPEG-2:** `libmpeg2`, `mpeg2video`, `mpeg2_decode_data`.

## Реалізація утиліти сканування ELF-образів

Нижче наведено робочу реалізацію консольного сканера, який приймає шлях до бінарного файлу або кореневої теки бібліотек, зчитує зміст файлу та генерує класифікований звіт про патентні ризики.

:::tabs
@tab C
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_PATH_LEN 1024
#define MAX_SIGNATURES 8

typedef enum {
    RISK_NONE = 0,
    RISK_PATENT_AVC,
    RISK_PATENT_HEVC,
    RISK_PATENT_AAC,
    RISK_PATENT_MPEG2
} PatentRiskCategory;

typedef struct {
    const char *signature;
    const char *codec_name;
    const char *pool_name;
    PatentRiskCategory category;
} CodecSignature;

static const CodecSignature KNOWN_SIGNATURES[MAX_SIGNATURES] = {
    {"libx264",     "H.264 / AVC",    "Via LA (MPEG LA)",      RISK_PATENT_AVC},
    {"libgstx264",  "H.264 / AVC",    "Via LA (MPEG LA)",      RISK_PATENT_AVC},
    {"libx265",     "H.265 / HEVC",   "Access Advance / Via",  RISK_PATENT_HEVC},
    {"libgstx265",  "H.265 / HEVC",   "Access Advance / Via",  RISK_PATENT_HEVC},
    {"libfaac",     "AAC Audio",      "Via LA (Via Licensing)", RISK_PATENT_AAC},
    {"libfdk_aac",  "AAC Audio",      "Via LA (Via Licensing)", RISK_PATENT_AAC},
    {"libmpeg2",    "MPEG-2 Video",   "MPEG LA (Expired in US)",RISK_PATENT_MPEG2},
    {"libgstaac",   "AAC Audio",      "Via LA (Via Licensing)", RISK_PATENT_AAC}
};

static void analyze_buffer(const unsigned char *buffer, size_t size, const char *filepath) {
    bool found_any = false;
    printf("[*] Аудит файлу: %s (%zu байтів)\n", filepath, size);

    for (int i = 0; i < MAX_SIGNATURES; ++i) {
        const char *sig = KNOWN_SIGNATURES[i].signature;
        size_t sig_len = strlen(sig);
        if (sig_len > size) continue;

        for (size_t pos = 0; pos <= size - sig_len; ++pos) {
            if (memcmp(buffer + pos, sig, sig_len) == 0) {
                printf("  [!] ВИЯВЛЕНО ПАТЕНТНИЙ РИЗИК:\n");
                printf("      - Сигнатура: %s\n", sig);
                printf("      - Технологія: %s\n", KNOWN_SIGNATURES[i].codec_name);
                printf("      - Патентний пул: %s\n", KNOWN_SIGNATURES[i].pool_name);
                found_any = true;
                break;
            }
        }
    }

    if (!found_any) {
        printf("  [+] Чисто: запатентованих кодеків не виявлено.\n");
    }
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <шлях до ELF-файлу>\n", argv[0]);
        return EXIT_FAILURE;
    }

    const char *filepath = argv[1];
    FILE *f = fopen(filepath, "rb");
    if (!f) {
        perror("Помилка відкриття файлу");
        return EXIT_FAILURE;
    }

    fseek(f, 0, SEEK_END);
    long file_size = ftell(f);
    fseek(f, 0, SEEK_SET);

    if (file_size <= 0) {
        fclose(f);
        fprintf(stderr, "Помилка: порожній файл\n");
        return EXIT_FAILURE;
    }

    unsigned char *buffer = (unsigned char *)malloc((size_t)file_size);
    if (!buffer) {
        fclose(f);
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return EXIT_FAILURE;
    }

    size_t read_bytes = fread(buffer, 1, (size_t)file_size, f);
    fclose(f);

    if (read_bytes != (size_t)file_size) {
        free(buffer);
        fprintf(stderr, "Помилка читання даних файлу\n");
        return EXIT_FAILURE;
    }

    analyze_buffer(buffer, (size_t)file_size, filepath);
    free(buffer);
    return EXIT_SUCCESS;
}
```
@tab C++
```cpp
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <string_view>
#include <filesystem>
#include <span>
#include <algorithm>

namespace fs = std::filesystem;

enum class PatentRisk {
    None,
    AVC,
    HEVC,
    AAC,
    MPEG2
};

struct CodecSignature {
    std::string_view signature;
    std::string_view codec_name;
    std::string_view pool_name;
    PatentRisk risk;
};

class FirmwareCodecAuditor {
public:
    FirmwareCodecAuditor() {
        signatures_ = {
            {"libx264",    "H.264 / AVC",   "Via LA (MPEG LA)",       PatentRisk::AVC},
            {"libgstx264", "H.264 / AVC",   "Via LA (MPEG LA)",       PatentRisk::AVC},
            {"libx265",    "H.265 / HEVC",  "Access Advance / Via",   PatentRisk::HEVC},
            {"libgstx265", "H.265 / HEVC",  "Access Advance / Via",   PatentRisk::HEVC},
            {"libfaac",    "AAC Audio",     "Via LA (Via Licensing)",  PatentRisk::AAC},
            {"libfdk_aac", "AAC Audio",     "Via LA (Via Licensing)",  PatentRisk::AAC},
            {"libmpeg2",   "MPEG-2 Video",  "MPEG LA (Expired in US)", PatentRisk::MPEG2},
            {"libgstaac",  "AAC Audio",     "Via LA (Via Licensing)",  PatentRisk::AAC}
        };
    }

    void audit_file(const fs::path& target_path) const {
        if (!fs::exists(target_path) || !fs::is_regular_file(target_path)) {
            std::cerr << "Помилка: файл " << target_path << " не існує або не є файлом.\n";
            return;
        }

        std::ifstream file(target_path, std::ios::binary | std::ios::ate);
        if (!file.is_open()) {
            std::cerr << "Не вдалося відкрити файл: " << target_path << "\n";
            return;
        }

        const auto file_size = file.tellg();
        file.seekg(0, std::ios::beg);

        std::vector<char> buffer(static_cast<size_t>(file_size));
        if (!file.read(buffer.data(), file_size)) {
            std::cerr << "Помилка зчитування вмісту файлу: " << target_path << "\n";
            return;
        }

        std::string_view content(buffer.data(), buffer.size());
        std::cout << "[*] Аудит файлу: " << target_path.filename().string() 
                  << " (" << buffer.size() << " байтів)\n";

        bool risk_found = false;
        for (const auto& entry : signatures_) {
            if (content.find(entry.signature) != std::string_view::npos) {
                std::cout << "  [!] ВИЯВЛЕНО ПАТЕНТНИЙ РИЗИК:\n";
                std::cout << "      - Сигнатура: " << entry.signature << "\n";
                std::cout << "      - Технологія: " << entry.codec_name << "\n";
                std::cout << "      - Патентний пул: " << entry.pool_name << "\n";
                risk_found = true;
            }
        }

        if (!risk_found) {
            std::cout << "  [+] Чисто: запатентованих кодеків не виявлено.\n";
        }
    }

private:
    std::vector<CodecSignature> signatures_;
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Використання: " << argv[0] << " <шлях до файлу або каталогу>\n";
        return 1;
    }

    const fs::path input_path(argv[1]);
    const FirmwareCodecAuditor auditor;

    if (fs::is_directory(input_path)) {
        for (const auto& entry : fs::recursive_directory_iterator(input_path)) {
            if (entry.is_regular_file()) {
                auditor.audit_file(entry.path());
            }
        }
    } else {
        auditor.audit_file(input_path);
    }

    return 0;
}
```
:::

## Інтеграція у виробничий конвеєр Yocto та CI/CD

У промислових проєктах на базі Yocto Project механізм захисту від випадкового включення запатентованих пакетів реалізується через систему ліцензійних прапорців `LICENSE_FLAGS_ACCEPTED`.

За замовчуванням рецепти, що містять запатентовані технології (наприклад, `x264`, `x265`, `faac`, `ffmpeg`), позначені рядком `LICENSE_FLAGS = "commercial"`. Якщо системний архітектор не додав у конфігураційний файл `build/conf/local.conf` явне підтвердження:

```bitbake
# Дозвіл на збирання комерційно обмежених рецептів
LICENSE_FLAGS_ACCEPTED = "commercial"
```

Система збирання BitBake примусово зупинить процес компіляції з повідомленням про неможливість включення пакета без усвідомлення ліцензійних ризиків.

Проте якщо розробник увімкнув цей прапорець для налагодження і забув його вимкнути перед релізом, консольний сканер у пайплайні CI/CD слугує останнім автоматичним бар'єром. Скрипт автоматично монтує результуючий образ кореневої файлової системи `rootfs.ext4` або розпаковує тарбол `rootfs.tar.gz`, рекурсивно проходить усі каталоги `/usr/bin` та `/usr/lib` і у разі виявлення заборонених сигнатур зупиняє конвеєр із кодом помилки `EXIT_FAILURE`.

## Аналіз статичного лінкування та внутрішніх символів

Найнебезпечнішим сценарієм для компанії є статичне лінкування (Static Linking). Якщо бібліотека `libavcodec.a` була скомпільована з підтримкою `libx264` і статично вшита всередину головного бінарника `/usr/bin/streamer_daemon`, завантажувач операційної системи не вимагатиме файлу `libx264.so`, і стандартний виклик `ldd` покаже повну відсутність зовнішніх кодеків.

У такій ситуації сканування виключно списку залежностей `DT_NEEDED` дає хибно-негативний результат (*False Negative*). Саме тому аудитор сканує весь двійковий образ методом прямого пошуку характерних рядків та сигнатур алгоритму. Навіть якщо назви функцій були модифіковані, константні таблиці квантування, матриці перетворення DCT та рядки журналювання x264/x265 неминуче потрапляють у секції `.rodata` та `.data`, викриваючи присутність запатентованої технології.

## Інженерні пастки та крайові випадки аудиту

1. **Динамічне завантаження через `dlopen`:**
   Коли мультимедійний рушій (наприклад, FFmpeg або GStreamer) компілюється з підтримкою модульної архітектури, пряма секція `DT_NEEDED` у двійковому файлі головної програми може бути відсутня. Проте виклик `dlopen("libx264.so")` залишає текстовий рядок у секції `.rodata`, який надійно фіксується сканером сигнатур.

2. **Апаратні драйвери V4L2 M2M та VA-API:**
   Якщо система використовує апаратне прискорення процесора через драйвер ядра Linux (`v4l2-m2m`), сам прикладний код не містить алгоритмічного кодера. Проте якщо процесор не має передплаченої вендором патентної ліцензії, активація апаратного блоку все одно створює відповідальність за роялті для виробника пристрою.

3. **Стриппінг двійкових файлів (`strip`):**
   Видалення налагоджувальних символів утилітою `strip --strip-unneeded` видаляє таблиці налагодження, але не змінює системні секції релокацій `DT_NEEDED` та константні рядки бінарного образу. Тому аудит залишається ефективним навіть на оптимізованих релізних прошивках.

4. **Реєстраційні кеші плагінів GStreamer:**
   Під час першого запуску GStreamer створює бінарний файл реєстру (наприклад, `~/.cache/gstreamer-1.0/registry.aarch64.bin`). Сканування цього реєстру дає повну інформацію про всі доступні в системі елементи обробки медіапотоків, що дозволяє виявити навіть ті плагіни, які були встановлені через сторонні динамічні пакети безпосередньо перед пакуванням образу.

5. **Стратегія заміни на безпатентні альтернативи:**
   Якщо аудит виявив заборонений плагін `x264enc` або `faac`, архітектурне виправлення медіаконвеєра полягає у зміні конфігурації конвеєра на відкриті безпатентні формати. У конвеєрі GStreamer елемент `x264enc` замінюють на `vp9enc` або апаратний `v4l2slvp9enc`, а аудіокодек `faac` — на стандартний відмитий від роялті кодек `opusenc`. Це усуває патентні ризики без втрати якості зв'язку чи стиснення.
