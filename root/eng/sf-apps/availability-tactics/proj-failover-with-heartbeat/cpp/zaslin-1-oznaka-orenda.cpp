// Оренда: право на роль, дійсне до expiry_ms; треба продовжувати.
typedef struct {
    uint64_t token;        // монотонний токен цього періоду оренди
    uint32_t expiry_ms;    // до якого моменту оренда дійсна
} Lease;

extern bool  lease_renew(Lease *l, uint32_t now_ms);   // продовжити в арбітра
extern void  demote_self(void);                        // розжалувати себе в резерв

// Головний зобов'язаний звати це часто. Якщо оренда згасла — НЕГАЙНО
// припинити виконувати роль, ще ДО спроби писати.
void primary_guard(Failover *f, Lease *l, uint32_t now_ms) {
    if (!lease_renew(l, now_ms) || now_ms >= l->expiry_ms) {
        // ми більше не маємо права бути головним — можливо, нас уже
        // замінили, поки ми висіли. Складаємо роль самі.
        stop_serving();
        demote_self();
        f->role = ROLE_STANDBY;
    }
}
