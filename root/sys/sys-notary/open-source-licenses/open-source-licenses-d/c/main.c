#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

/* Бітові класифікатори ліцензій */
typedef enum {
    LIC_PERMISSIVE = 1 << 0,  /* MIT, BSD, ISC */
    LIC_APACHE2    = 1 << 1,  /* Apache 2.0 */
    LIC_LGPL       = 1 << 2,  /* LGPL v2.1/v3.0 */
    LIC_GPL2       = 1 << 3,  /* GPL-2.0-only */
    LIC_GPL3       = 1 << 4,  /* GPL-3.0-or-later */
    LIC_PROPRIETARY= 1 << 5   /* Комерційний закритий код */
} LicenseClass;

typedef enum {
    LINK_STATIC,
    LINK_DYNAMIC,
    LINK_IPC
} LinkType;

typedef struct {
    const char *module_name;
    const char *spdx;
    LicenseClass lic;
    LinkType link;
} ModuleDep;

/* Перевірка сумісності за матрицею ліцензійних правил */
static bool check_compatibility(LicenseClass target, LicenseClass dep, LinkType link) {
    /* Міжпроцесний бар'єр (IPC) повністю знімає ліцензійні вимоги */
    if (link == LINK_IPC) return true;

    /* Правила для закритого пропрієтарного продукту */
    if (target == LIC_PROPRIETARY) {
        if (dep == LIC_PERMISSIVE || dep == LIC_APACHE2) return true;
        if (dep == LIC_LGPL) return (link == LINK_DYNAMIC);
        return false; /* GPL/AGPL блокують реліз */
    }

    /* Правила для продукту під GPL-2.0-only */
    if (target == LIC_GPL2) {
        if (dep == LIC_PERMISSIVE || dep == LIC_GPL2) return true;
        if (dep == LIC_APACHE2) return false; /* Патентний конфлікт */
        if (dep == LIC_GPL3) return false;    /* Конфлікт версій */
        return true;
    }

    /* Правила для продукту під GPL-3.0 */
    if (target == LIC_GPL3) {
        if (dep == LIC_GPL2) return false;   /* GPL-2.0-only несумісна з v3 */
        return true;                          /* MIT, Apache-2.0, LGPL сумісні */
    }

    return false;
}

int main(void) {
    ModuleDep deps[] = {
        {"libjson-c",    "MIT",        LIC_PERMISSIVE, LINK_STATIC},
        {"libcrypto",    "Apache-2.0", LIC_APACHE2,    LINK_STATIC},
        {"libprotocols", "LGPL-2.1",   LIC_LGPL,       LINK_DYNAMIC},
        {"system-core",  "GPL-2.0",    LIC_GPL2,       LINK_IPC},
        {"libdsp_filter","GPL-2.0",    LIC_GPL2,       LINK_STATIC} /* Порушення! */
    };
    size_t count = sizeof(deps) / sizeof(deps[0]);

    printf("=== АУДИТ ЛІЦЕНЗІЙНОЇ ВІДПОВІДНОСТІ (PROPRIETARY) ===\n");
    int failed = 0;
    for (size_t i = 0; i < count; ++i) {
        bool ok = check_compatibility(LIC_PROPRIETARY, deps[i].lic, deps[i].link);
        const char *link_name = (deps[i].link == LINK_STATIC) ? "STATIC" :
                                (deps[i].link == LINK_DYNAMIC) ? "DYNAMIC" : "IPC";

        if (ok) {
            printf("[OK]   %-15s (%-10s) Link: %-8s\n", deps[i].module_name, deps[i].spdx, link_name);
        } else {
            printf("[FAIL] %-15s (%-10s) Link: %-8s <-- БЛОКУВАННЯ ЗБІРКИ!\n",
                   deps[i].module_name, deps[i].spdx, link_name);
            failed++;
        }
    }

    printf("----------------------------------------------------\n");
    if (failed > 0) {
        printf("РЕЗУЛЬТАТ: Виявлено %d порушень. Збірку зупинено.\n", failed);
        return 1;
    }
    printf("РЕЗУЛЬТАТ: Всі залежності юридично сумісні.\n");
    return 0;
}
