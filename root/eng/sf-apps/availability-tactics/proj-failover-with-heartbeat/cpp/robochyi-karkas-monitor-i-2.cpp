typedef enum {
    ROLE_STANDBY,     // ми резерв, чекаємо
    ROLE_PRIMARY,     // ми головний, виконуємо роль
    ROLE_PROMOTING,   // ми в процесі підняття (тут беремо оренду/кворум)
    ROLE_REJOINING    // ми колишній головний, доганяємо стан після оживлення
} role_t;

typedef struct {
    role_t   role;
    NodeHealth peer;        // монітор ЧУЖОГО серцебиття (за ким стежимо)
    uint64_t fence_token;   // наш поточний токен огорожі (див. нижче)
    uint32_t promoting_since_ms;  // коли почали підніматися (щоб не зависнути в PROMOTING)
} Failover;

// Реакції на події, які реалізує конкретна система (заглушки-приклади):
extern bool     acquire_lease_or_quorum(uint64_t *out_token); // взяти оренду, видати токен
extern void     start_serving(uint64_t token);   // почати виконувати роль
extern void     stop_serving(void);              // припинити виконувати роль
extern uint64_t storage_current_token(void);     // найбільший токен, що бачило сховище

void failover_init(Failover *f, role_t start, uint32_t now_ms) {
    f->role = start;
    f->fence_token = 0;
    f->promoting_since_ms = 0;
    health_init(&f->peer, now_ms);
}

// Головний тик автомата: викликається періодично на РЕЗЕРВНОМУ вузлі.
// now_ms — монотонний час; peer_beat=true, якщо цим тиком прийшов удар
// від головного.
void failover_tick(Failover *f, uint32_t now_ms, bool peer_beat) {
    if (peer_beat)
        health_on_beat(&f->peer, now_ms);
    health_tick(&f->peer, now_ms);

    switch (f->role) {
    case ROLE_STANDBY:
        // головний мовчить достатньо довго -> пробуємо піднятися
        if (f->peer.health == NODE_DOWN) {
            f->role = ROLE_PROMOTING;
            f->promoting_since_ms = now_ms;
        }
        break;

    case ROLE_PROMOTING: {
        // КЛЮЧОВА межа: піднятися можна ЛИШЕ взявши оренду/кворум.
        // Це і є заслін розколу мозку — без цього кроку два вузли
        // спокійно піднялися б удвох.
        uint64_t token;
        if (acquire_lease_or_quorum(&token)) {
            f->fence_token = token;
            start_serving(token);
            f->role = ROLE_PRIMARY;
        }
        // не взяли оренду -> лишаємось PROMOTING і пробуємо наступним тиком;
        // якщо головний насправді живий і тримає оренду, ми НІКОЛИ не піднімемось
        break;
    }

    case ROLE_PRIMARY:
        // ми головний; окремо стежимо, чи не втратили оренду (нижче)
        break;

    case ROLE_REJOINING:
        // ми колись були головним, впали, ожили. Роль уже в іншого.
        // Не рвемось назад — доганяємо стан і чекаємо (див. пастку ляпання).
        break;
    }
}
