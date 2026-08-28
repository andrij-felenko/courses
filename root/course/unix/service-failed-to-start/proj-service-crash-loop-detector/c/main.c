#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <systemd/sd-bus.h>
#include <signal.h>
#include <stdbool.h>

typedef struct {
    char active_state[64];
    char sub_state[64];
    char result[64];
    uint32_t n_restarts;
    uint64_t restart_usec;
    uint32_t main_pid;
    int32_t main_code;
    int32_t main_status;
} unit_diagnostics_t;

static int query_unit_properties(sd_bus *bus, const char *unit_name, unit_diagnostics_t *diag) {
    char *path = NULL;
    int r = sd_bus_path_encode("/org/freedesktop/systemd1/unit", unit_name, &path);
    if (r < 0) {
        fprintf(stderr, "Помилка кодування об'єктного шляху D-Bus: %s\n", strerror(-r));
        return r;
    }

    char *active = NULL, *sub = NULL, *res = NULL;

    r = sd_bus_get_property_string(bus, "org.freedesktop.systemd1", path,
                                   "org.freedesktop.systemd1.Unit", "ActiveState",
                                   NULL, &active);
    if (r >= 0 && active) {
        strncpy(diag->active_state, active, sizeof(diag->active_state) - 1);
        free(active);
    }

    r = sd_bus_get_property_string(bus, "org.freedesktop.systemd1", path,
                                   "org.freedesktop.systemd1.Unit", "SubState",
                                   NULL, &sub);
    if (r >= 0 && sub) {
        strncpy(diag->sub_state, sub, sizeof(diag->sub_state) - 1);
        free(sub);
    }

    r = sd_bus_get_property_string(bus, "org.freedesktop.systemd1", path,
                                   "org.freedesktop.systemd1.Unit", "Result",
                                   NULL, &res);
    if (r >= 0 && res) {
        strncpy(diag->result, res, sizeof(diag->result) - 1);
        free(res);
    }

    sd_bus_get_property_trivial(bus, "org.freedesktop.systemd1", path,
                                "org.freedesktop.systemd1.Service", "NRestarts",
                                NULL, 'u', &diag->n_restarts);

    sd_bus_get_property_trivial(bus, "org.freedesktop.systemd1", path,
                                "org.freedesktop.systemd1.Service", "RestartUSec",
                                NULL, 't', &diag->restart_usec);

    sd_bus_get_property_trivial(bus, "org.freedesktop.systemd1", path,
                                "org.freedesktop.systemd1.Service", "ExecMainPID",
                                NULL, 'u', &diag->main_pid);

    sd_bus_get_property_trivial(bus, "org.freedesktop.systemd1", path,
                                "org.freedesktop.systemd1.Service", "ExecMainCode",
                                NULL, 'i', &diag->main_code);

    sd_bus_get_property_trivial(bus, "org.freedesktop.systemd1", path,
                                "org.freedesktop.systemd1.Service", "ExecMainStatus",
                                NULL, 'i', &diag->main_status);

    free(path);
    return 0;
}

static void print_verdict(const char *unit_name, const unit_diagnostics_t *diag) {
    printf("=================================================================\n");
    printf("ДІАГНОСТИЧНИЙ ПАСПОРТ ЮНІТА: %s\n", unit_name);
    printf("=================================================================\n");
    printf("Стан (Active/Sub):    %s / %s\n", diag->active_state, diag->sub_state);
    printf("Результат менеджера:  %s\n", diag->result);
    printf("Кількість перезапусків: %u (інтервал: %.1f c)\n",
           diag->n_restarts, (double)diag->restart_usec / 1000000.0);
    printf("Останній PID:          %u (код: %d, статус: %d)\n",
           diag->main_pid, diag->main_code, diag->main_status);
    printf("-----------------------------------------------------------------\n");

    printf("АНАЛІЗ ТА РЕКОМЕНДАЦІЇ:\n");

    if (strcmp(diag->result, "start-limit-hit") == 0) {
        printf("⚠️  КРИТИЧНО: Служба потрапила в CrashLoop і заблокована менеджером!\n");
        printf("    Перевищено ліміт StartLimitBurst у межах StartLimitIntervalSec.\n");
        printf("    Щоб відновити спроби запуску після виправлення причини, виконайте:\n");
        printf("    --> systemctl reset-failed %s\n", unit_name);
    } else if (strcmp(diag->sub_state, "auto-restart") == 0) {
        printf("⚠️  УВАГА: Служба перебуває в активній рестарт-петлі (стан очікування).\n");
        printf("    Зафіксовано вже %u невдалих перезапусків.\n", diag->n_restarts);
        printf("    Зупиніть службу для запобігання спаму в логах:\n");
        printf("    --> systemctl stop %s\n", unit_name);
    }

    if (diag->main_code == CLD_EXITED) {
        if (diag->main_status == 203) {
            printf("❌ ПОМИЛКА 203/EXEC: Ядро не змогло виконати бінарник.\n");
            printf("   1. Перевірте існування файлу ExecStart= та права chmod +x.\n");
            printf("   2. Якщо це скрипт — перевірте шлях до інтерпретатора у першому рядку (шебанг).\n");
            printf("   3. Перевірте наявність динамічного лінкера (ldd <binary>).\n");
        } else if (diag->main_status == 217) {
            printf("❌ ПОМИЛКА 217/USER: Неможливо перемкнутися на користувача в User=.\n");
            printf("   Користувач відсутній у /etc/passwd або мережевий NSS (SSSD/LDAP) ще не готовий.\n");
        } else if (diag->main_status == 226) {
            printf("❌ ПОМИЛКА 226/NAMESPACE: Збій налаштування пісочниці монтування.\n");
            printf("   Перевірте сумісність директив ProtectSystem=, PrivateTmp= з файловою системою.\n");
        } else if (diag->main_status != 0) {
            printf("❌ ПРИКЛАДНИЙ ЗБІЙ (код %d): Застосунок вийшов із власною помилкою.\n", diag->main_status);
            printf("   Перегляньте точний лог падіння:\n");
            printf("   --> journalctl -u %s -b -e --no-pager\n", unit_name);
        }
    } else if (diag->main_code == CLD_KILLED) {
        if (diag->main_status == SIGKILL) {
            printf("❌ ЗНИЩЕНО СИГНАЛОМ SIGKILL (9):\n");
            printf("   1. Спрацював ядерний cgroup OOM-killer через перевищення MemoryMax=.\n");
            printf("   2. Вичерпано таймаут запуску TimeoutStartSec= (Type=notify не надіслав READY=1).\n");
            printf("   Перевірте dmesg: dmesg -T | grep -i oom\n");
        } else if (diag->main_status == SIGABRT) {
            printf("❌ ЗНИЩЕНО СИГНАЛОМ SIGABRT (6): Програма викликала abort() або впав assert.\n");
        } else if (diag->main_status == SIGSEGV) {
            printf("❌ ЗНИЩЕНО СИГНАЛОМ SIGSEGV (11): Порушення адресації пам'яті (Segfault).\n");
        }
    }

    printf("=================================================================\n");
}

int main(int argc, char *argv[]) {
    if (argc < 2) {
        fprintf(stderr, "Використання: %s <назва_юніта.service>\n", argv[0]);
        return 1;
    }

    const char *unit_name = argv[1];
    sd_bus *bus = NULL;

    int r = sd_bus_open_system(&bus);
    if (r < 0) {
        fprintf(stderr, "Не вдалося підключитися до системної шини D-Bus: %s\n", strerror(-r));
        return 1;
    }

    unit_diagnostics_t diag;
    memset(&diag, 0, sizeof(diag));

    r = query_unit_properties(bus, unit_name, &diag);
    if (r == 0) {
        print_verdict(unit_name, &diag);
    }

    sd_bus_unref(bus);
    return (r < 0) ? 1 : 0;
}
