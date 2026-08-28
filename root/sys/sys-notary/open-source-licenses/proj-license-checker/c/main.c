#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

/* Бітові маски ліцензійних родин для швидкої алгебраїчної перевірки */
typedef enum {
    LIC_UNKNOWN      = 0,
    LIC_PERMISSIVE   = 1 << 0,  /* MIT, BSD, ISC */
    LIC_APACHE2      = 1 << 1,  /* Apache 2.0 (патентний грант) */
    LIC_WEAK_COPYLEFT= 1 << 2,  /* LGPL, MPL */
    LIC_GPL2_ONLY    = 1 << 3,  /* GPL-2.0-only */
    LIC_GPL3_PLUS    = 1 << 4,  /* GPL-3.0+, LGPL-3.0+ */
    LIC_AGPL3        = 1 << 5,  /* AGPL-3.0 (мережевий копілефт) */
    LIC_PROPRIETARY  = 1 << 6   /* Закритий комерційний код */
} LicenseType;

typedef enum {
    LINK_STATIC,
    LINK_DYNAMIC,
    LINK_IPC_BOUNDARY
} LinkageType;

typedef struct {
    const char *name;
    const char *spdx_id;
    LicenseType type;
    LinkageType linkage;
} Dependency;

typedef struct {
    const char *project_name;
    LicenseType target_license;
    Dependency *deps;
    size_t dep_count;
} ProjectContext;

/* Перевірка сумісності пари ліцензій за способом зв'язування */
static bool is_pair_compatible(LicenseType target, LicenseType dep_lic, LinkageType link) {
    /* Міжпроцесна ізоляція (IPC) знімає обмеження ліцензійного зараження */
    if (link == LINK_IPC_BOUNDARY) {
        return true;
    }

    /* Пропрієтарний цільовий продукт */
    if (target == LIC_PROPRIETARY) {
        if (dep_lic == LIC_PERMISSIVE || dep_lic == LIC_APACHE2) {
            return true;
        }
        /* Слабкий копілефт (LGPL) дозволений ТІЛЬКИ при динамічному лінкуванні */
        if (dep_lic == LIC_WEAK_COPYLEFT) {
            return (link == LINK_DYNAMIC);
        }
        /* Сильний або мережевий копілефт категорично заборонений */
        return false;
    }

    /* Цільовий проєкт під GPL-2.0-only */
    if (target == LIC_GPL2_ONLY) {
        if (dep_lic == LIC_PERMISSIVE || dep_lic == LIC_GPL2_ONLY) {
            return true;
        }
        /* Конфлікт століття: Apache 2.0 несумісна з GPL-2.0-only */
        if (dep_lic == LIC_APACHE2) {
            return false;
        }
        if (dep_lic == LIC_GPL3_PLUS || dep_lic == LIC_AGPL3) {
            return false;
        }
        return true;
    }

    /* Цільовий проєкт під GPL-3.0+ */
    if (target == LIC_GPL3_PLUS) {
        /* GPLv3 сумісна з Apache 2.0 та Permissive */
        if (dep_lic == LIC_PERMISSIVE || dep_lic == LIC_APACHE2 ||
            dep_lic == LIC_GPL3_PLUS || dep_lic == LIC_WEAK_COPYLEFT) {
            return true;
        }
        /* GPL-2.0-only несумісна з GPLv3, якщо немає застереження 'or later' */
        if (dep_lic == LIC_GPL2_ONLY) {
            return false;
        }
        return true;
    }

    return false;
}

/* Запуск повного аудиту графа залежностей */
static int audit_project(const ProjectContext *ctx) {
    int violations = 0;
    printf("[AUDIT] Перевірка проєкту: %s\n", ctx->project_name);
    printf("------------------------------------------------------------\n");

    for (size_t i = 0; i < ctx->dep_count; ++i) {
        const Dependency *d = &ctx->deps[i];
        bool ok = is_pair_compatible(ctx->target_license, d->type, d->linkage);

        const char *link_str = (d->linkage == LINK_STATIC) ? "STATIC" :
                               (d->linkage == LINK_DYNAMIC) ? "DYNAMIC (.so)" : "IPC";

        if (ok) {
            printf("  [PASS] %-15s | SPDX: %-15s | Link: %-12s\n", d->name, d->spdx_id, link_str);
        } else {
            printf("  [FAIL] %-15s | SPDX: %-15s | Link: %-12s  <-- ЮРИДИЧНИЙ КОНФЛІКТ!\n",
                   d->name, d->spdx_id, link_str);
            violations++;
        }
    }

    printf("------------------------------------------------------------\n");
    if (violations > 0) {
        printf("[ВИСНОВОК] Збірку заблоковано! Знайдено %d несумісних ліцензій.\n", violations);
        return 1;
    } else {
        printf("[ВИСНОВОК] Аудит пройдено успішно. Всі компоненти сумісні.\n");
        return 0;
    }
}

int main(void) {
    /* Тестовий стек компонентів вбудованого контролера */
    Dependency deps[] = {
        {"cJSON",       "MIT",                 LIC_PERMISSIVE,    LINK_STATIC},
        {"mbedTLS",     "Apache-2.0",          LIC_APACHE2,       LINK_STATIC},
        {"libmodbus",   "LGPL-2.1-or-later",   LIC_WEAK_COPYLEFT, LINK_DYNAMIC},
        {"busybox",     "GPL-2.0-only",        LIC_GPL2_ONLY,     LINK_IPC_BOUNDARY},
        {"libgpl_math", "GPL-2.0-only",        LIC_GPL2_ONLY,     LINK_STATIC} /* Порушення! */
    };

    ProjectContext proprietary_app = {
        .project_name = "EdgeGateway-Daemon (Proprietary)",
        .target_license = LIC_PROPRIETARY,
        .deps = deps,
        .dep_count = sizeof(deps) / sizeof(deps[0])
    };

    return audit_project(&proprietary_app);
}
