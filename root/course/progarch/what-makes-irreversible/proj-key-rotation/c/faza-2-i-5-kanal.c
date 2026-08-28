#define KU_BODY 59            // 1+1 + 4 + 4 + 1 + 8 + 8 + 32

// Чи лишиться хоч один придатний операційний ключ, якщо викинути except_kid?
static bool ring_has_live_op(uint32_t except_kid, uint64_t now) {
    for (int i = 0; i < MAX_KEYS; i++) {
        keyslot_t *k = &g_ring[i];
        if (k->used && !k->revoked && k->role == ROLE_OP && k->kid != except_kid
            && now >= k->not_before && now <= k->not_after)
            return true;
    }
    return false;
}

// frame = тіло(59) || підпис(64). Тіло: version|type|signer_kid|target_kid|
//         role|not_before|not_after|pub.  type: 2 = додати, 3 = відкликати.
bool apply_key_update(const uint8_t *frame, size_t len, uint64_t now) {
    if (len != KU_BODY + SIG_LEN) return false;

    const uint8_t *body = frame;
    const uint8_t *sig  = frame + KU_BODY;

    uint8_t  version    = rd_u8 (body + 0);
    uint8_t  type       = rd_u8 (body + 1);
    uint32_t signer_kid = rd_u32(body + 2);
    uint32_t target_kid = rd_u32(body + 6);
    uint8_t  role       = rd_u8 (body + 10);
    uint64_t not_before = rd_u64(body + 11);
    uint64_t not_after  = rd_u64(body + 19);
    const uint8_t *pub  = body + 27;                // 32 байти

    if (version != 1) return false;

    // 1) ОНОВЛЕННЯ ПІДПИСУЄ ЛИШЕ КОРІНЬ — і лише той, що сам чинний і не відкликаний.
    keyslot_t *root = find_key(signer_kid, ROLE_ROOT);
    if (!root || root->revoked)                          return false;
    if (now < root->not_before || now > root->not_after) return false;
    if (!ed25519_verify(sig, body, KU_BODY, root->pub))  return false;

    if (type == 2) {                                     // ── ДОДАТИ ключ ──
        // Надгробок: якщо цей номер колись відкликали — НЕ воскрешати.
        // Інакше злодій переграв би старе «додай», щоб оживити мертвий ключ.
        for (int i = 0; i < MAX_KEYS; i++)
            if (g_ring[i].used && g_ring[i].kid == target_kid && g_ring[i].revoked)
                return false;

        keyslot_t *dst = find_key(target_kid, role);     // повторно той самий → ідемпотентно
        if (!dst)
            for (int i = 0; i < MAX_KEYS; i++)
                if (!g_ring[i].used) { dst = &g_ring[i]; break; }
        if (!dst) return false;                          // звʼязка повна — нема куди

        dst->used = true;  dst->revoked = false;
        dst->kid  = target_kid;  dst->role = role;
        dst->not_before = not_before;  dst->not_after = not_after;
        memcpy(dst->pub, pub, 32);

    } else if (type == 3) {                              // ── ВІДКЛИКАТИ ключ ──
        keyslot_t *victim = find_key(target_kid, ROLE_OP);
        if (!victim) victim = find_key(target_kid, ROLE_ROOT);
        if (!victim) return false;

        // ЗАПОБІЖНИК від замурування: не відкликати останній живий операційний
        // ключ — інакше замок осліпне й не впустить нікого, зокрема хазяїна.
        if (victim->role == ROLE_OP && !ring_has_live_op(target_kid, now))
            return false;

        victim->revoked = true;                          // надгробок лишається назавжди
    } else {
        return false;
    }

    nvs_save_ring();                                     // персистимо у флеш
    return true;
}
