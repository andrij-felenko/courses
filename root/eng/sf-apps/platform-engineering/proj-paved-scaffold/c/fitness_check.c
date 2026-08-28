// fitness_check.c — сторож на в'їзді. Проганяється в конвеєрі
// складання над КОЖНОЮ зібраною прошивкою лінійки. Не запускає
// пристрій — лише читає символи готового .elf.
//
// Правило (архітектурний інваріант лінійки):
//   прошивка ЛІБО кличе platform_boot, ЛІБО явно позначена OFF_ROAD.
//   «Ні того, ні того» = тиха помилка = складання падає.
#include <stdbool.h>
#include <stdio.h>

// Обидва факти дістаємо з готового .elf (тут — через nm/readelf,
// схований за двома помічниками; суть не в інструменті).
extern bool elf_references_symbol(const char *elf, const char *sym);
extern bool elf_has_section(const char *elf, const char *section);
extern bool elf_read_offroad_reason(const char *elf, char *buf, int n);

int check_firmware(const char *elf_path) {
    bool on_road  = elf_references_symbol(elf_path, "platform_boot");
    bool off_road = elf_has_section(elf_path, ".platform.offroad");

    if (on_road) {
        // Пройшла дорогою — усе гаразд, це очікуваний, здоровий шлях.
        printf("OK  %s: іде вимощеною дорогою (platform_boot)\n", elf_path);
        return 0;
    }

    if (off_road) {
        // Свідомий з'їзд із причиною — теж гаразд, але лишаємо в лог,
        // щоб з'їзди були ВИДИМІ й хтось їх час від часу переглядав.
        char reason[128] = {0};
        elf_read_offroad_reason(elf_path, reason, sizeof reason);
        printf("OK  %s: свідомий з'їзд з дороги — «%s»\n", elf_path, reason);
        return 0;
    }

    // Ні дороги, ні позначки. Це те, заради чого сторож і стоїть:
    // прошивка обійшла платформу МОВЧКИ. Майже завжди — не намір,
    // а помилка: хтось не знав про platform_boot. Складання падає.
    fprintf(stderr,
        "FAIL %s: платформу обійдено без позначки OFF_ROAD.\n"
        "     Кличте platform_boot() або, якщо старт свідомо свій,\n"
        "     поставте PLATFORM_OFF_ROAD(\"причина\").\n", elf_path);
    return 1;   // ненульовий код зупиняє конвеєр
}
