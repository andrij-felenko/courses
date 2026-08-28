// Пороги довіри — виведені окремо, бо залежать від задачі апарата.
#define FIX_MIN_SV     6      // менше — розв'язок крихкий, легко впіймати хибний вимір
#define FIX_MAX_PDOP   3.0f   // більше — геометрія погана (каньйон, вузька смуга неба)
#define FIX_MAX_HACC   10.0f  // м; для точної посадки поставили б менше
#define FIX_STALE_MS   500    // фікс старший за це вважаємо протухлим

// Чи можна ВЗЯТИ цей фікс: усі умови мусять справдитися разом.
static bool fix_is_healthy(const gnss_fix_t *f) {
    if (f->fix_type < 3)          return false;  // нема повного 3D
    if (!f->gnss_fix_ok)          return false;  // модуль сам НЕ підтвердив рішення
    if (f->num_sv  < FIX_MIN_SV)  return false;  // замало супутників
    if (f->pdop    > FIX_MAX_PDOP) return false; // геометрія погана
    if (f->hacc_m  > FIX_MAX_HACC) return false; // оцінена похибка завелика
    return true;
}

// Останній валідний фікс — сюди складає dispatch, звідси бере оцінювач.
static gnss_fix_t g_last_fix;
static bool       g_have_fix;

void ubx_dispatch(uint8_t cls, uint8_t id, const uint8_t *buf, uint16_t len) {
    // Спершу — конфіг-квитанції (їх чекає стартовий ритуал, шар нижче).
    if (cls == UBX_CLS_ACK && (id == UBX_ACK_ACK || id == UBX_ACK_NAK)) {
        cfg_on_ack(id == UBX_ACK_ACK, buf, len);   // передати очікувачу ACK
        return;
    }
    // Наше корисне повідомлення.
    if (cls == UBX_CLS_NAV && id == UBX_NAV_PVT && len == PVT_PAYLOAD_LEN) {
        gnss_fix_t f;
        decode_pvt(buf, P.last_byte_ms, &f);
        if (fix_is_healthy(&f)) {          // ворота: лише довірене йде далі
            g_last_fix = f;
            g_have_fix = true;
        }
        // Нездоровий фікс НЕ затираємо g_last_fix — хай оцінювач бачить
        // останній ДОБРИЙ, поки не протух, а не свіже сміття.
    }
    // Інші повідомлення (MON-VER тощо) обробляє стартовий ритуал за потреби.
}

// Оцінювач стану питає драйвер: «дай свіжий валідний фікс». Повертає false,
// якщо фікса нема або він протух — тоді оцінювач числить по IMU далі.
bool gnss_get_fix(uint32_t now_ms, gnss_fix_t *out) {
    if (!g_have_fix) return false;
    if ((uint32_t)(now_ms - g_last_fix.stamp_ms) > FIX_STALE_MS) {
        return false;               // фікс застарів — не віддаємо як свіжий
    }
    *out = g_last_fix;
    return true;
}
