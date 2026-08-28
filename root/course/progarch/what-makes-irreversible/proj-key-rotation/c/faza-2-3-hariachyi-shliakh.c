#define GRANT_BODY 34         // 1+1 + 4 + 4 + 8 + 16

static uint8_t rd_u8 (const uint8_t *p) { return p[0]; }
static uint32_t rd_u32(const uint8_t *p) {
    return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16) |
           ((uint32_t)p[2] <<  8) |  (uint32_t)p[3];
}
static uint64_t rd_u64(const uint8_t *p) {
    uint64_t v = 0;
    for (int i = 0; i < 8; i++) v = (v << 8) | p[i];
    return v;
}

// Нонс, який замок щойно видав застосункові як виклик. Кожен новий виклик
// його перезаписує; після вдалого відкриття ми його спалюємо — тож той
// самий підписаний дозвіл не спрацює вдруге (захист від повтору-реплею).
static uint8_t g_pending_nonce[16];

// frame = тіло(34) || підпис(64). Тіло: version|type|device_id|kid|not_after|nonce.
bool handle_unlock(const uint8_t *frame, size_t len, uint64_t now) {
    if (len != GRANT_BODY + SIG_LEN) return false;

    const uint8_t *body = frame;
    const uint8_t *sig  = frame + GRANT_BODY;

    uint8_t  version   = rd_u8 (body + 0);
    uint8_t  type      = rd_u8 (body + 1);
    uint32_t device_id = rd_u32(body + 2);
    uint32_t kid       = rd_u32(body + 6);
    uint64_t not_after = rd_u64(body + 10);
    const uint8_t *nonce = body + 18;               // 16 байтів

    if (version != 1 || type != 1)              return false;  // не той формат
    if (device_id != g_device_id)               return false;  // дозвіл не для цього замка
    if (now > not_after)                        return false;  // протермінований
    if (memcmp(nonce, g_pending_nonce, 16) != 0) return false; // не на наш виклик → реплей

    // Ось де працює звʼязка: шукаємо ключ ЗА НОМЕРОМ і перевіряємо його вікно.
    keyslot_t *k = find_key(kid, ROLE_OP);
    if (!k)                                     return false;  // такого ключа не знаємо
    if (k->revoked)                             return false;  // відкликаний
    if (now < k->not_before || now > k->not_after) return false; // поза вікном чинності

    // Підпис перевіряємо САМЕ тим ключем, чий номер названо в дозволі.
    if (!ed25519_verify(sig, body, GRANT_BODY, k->pub)) return false;

    memset(g_pending_nonce, 0, 16);             // спалити нонс — дозвіл одноразовий
    return true;                                // усе зійшлося — відчинити
}
