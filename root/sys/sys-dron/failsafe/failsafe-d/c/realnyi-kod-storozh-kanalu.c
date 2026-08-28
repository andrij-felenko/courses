// Таймаут: серцебиття мали б приходити раз на секунду (1000 мс).
// Дозволяємо пропустити одне-півтора, перш ніж бити тривогу:
#define LINK_TIMEOUT_MS   1500

static uint32_t last_heartbeat_ms = 0;   // коли востаннє чули борт/пульт
static bool     link_lost        = false;

// Викликається ЩОРАЗУ, коли з каналу прийшов валідний пакет серцебиття.
// Найчастіше — з обробника прийому (ISR/колбек приймача).
void on_heartbeat_received(void) {
    last_heartbeat_ms = millis();        // позначка «щойно чули життя»
    link_lost = false;                   // лінк точно живий
}

// Викликається регулярно з головного циклу — це і є детектор ВІДСУТНОСТІ.
void link_check(void) {
    uint32_t silent = millis() - last_heartbeat_ms;   // скільки мовчить канал

    if (silent > LINK_TIMEOUT_MS && !link_lost) {
        link_lost = true;                // перехід «живий → мертвий» — лише раз
        enter_failsafe(FS_LINK_LOST);    // запускаємо безпечну дію
    }
}
