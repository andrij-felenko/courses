#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <unistd.h>

typedef struct {
    int log_level;
    char server_addr[64];
    int port;
} ServerConfig;

// Глобальний кеш налаштувань у процесі
static ServerConfig g_active_config;

bool save_and_apply_config_c(const char* target_path, const ServerConfig* new_cfg) {
    char tmp_path[256];
    char bak_path[256];
    snprintf(tmp_path, sizeof(tmp_path), "%s.tmp", target_path);
    snprintf(bak_path, sizeof(bak_path), "%s.bak", target_path);

    bool tmp_created = false;
    bool bak_created = false;
    ServerConfig prev_cache;

    // 1. Створення та запис у тимчасовий файл
    FILE* f = fopen(tmp_path, "wb");
    if (!f) {
        return false;
    }
    tmp_created = true;

    if (fwrite(new_cfg, sizeof(ServerConfig), 1, f) != 1) {
        fclose(f);
        goto fail;
    }

    // Примусове скидання буферів ОС на накопичувач
    fflush(f);
    fsync(fileno(f));
    fclose(f);

    // 2. Валідація параметрів конфігурації
    if (new_cfg->port <= 0 || new_cfg->port > 65535) {
        goto fail;
    }
    if (strlen(new_cfg->server_addr) == 0) {
        goto fail;
    }

    // 3. Створення резервної копії попереднього файлу
    if (access(target_path, F_OK) == 0) {
        if (rename(target_path, bak_path) != 0) {
            goto fail;
        }
        bak_created = true;
    }

    // 4. Атомарне перейменування тимчасового файлу на цільовий
    if (rename(tmp_path, target_path) != 0) {
        goto fail;
    }
    tmp_created = false; // файл зайняв цільове місце

    // 5. Оновлення стану в оперативній пам'яті
    memcpy(&prev_cache, &g_active_config, sizeof(ServerConfig));
    memcpy(&g_active_config, new_cfg, sizeof(ServerConfig));

    // Успішне завершення: видаляємо старий бекап
    if (bak_created) {
        unlink(bak_path);
    }
    return true;

fail:
    // Ручний каскад відкату у зворотному порядку створення
    if (tmp_created) {
        unlink(tmp_path);
    }
    if (bak_created) {
        rename(bak_path, target_path);
    }
    return false;
}
