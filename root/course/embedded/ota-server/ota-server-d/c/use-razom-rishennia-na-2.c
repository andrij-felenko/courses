// running — наша чинна версія (із заголовка ВЛАСНОГО образу);
// manifest — версія, яку оголосив сервер у маніфесті.
bool should_update(const char *running_ver, const char *manifest_ver,
                   const char *manifest_hw, const char *my_hw) {

    // 1. Залізо мусить збігтися — інакше образ нас перетворить на цеглу.
    if (strcmp(manifest_hw, my_hw) != 0) {
        printf("OTA: образ під чуже залізо (%s != %s) — пропускаємо\n",
               manifest_hw, my_hw);
        return false;
    }

    // 2. Качаємо, лише якщо маніфест НОВІШИЙ за нас.
    version_t mine = parse_version(running_ver);
    version_t want = parse_version(manifest_ver);
    if (version_cmp(want, mine) <= 0) {
        printf("OTA: %s не новіше за %s — лишаємось\n", manifest_ver, running_ver);
        return false;   // та сама або старіша версія — нічого не робимо
    }

    printf("OTA: є новіше: %s > %s — починаємо завантаження\n",
           manifest_ver, running_ver);
    return true;
}
