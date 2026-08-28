#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_KEYS   8          // фіксовано: без malloc, усе у флеші (NVS)
#define ROLE_OP    0          // операційний: підписує дозволи на відкриття
#define ROLE_ROOT  1          // корінь: підписує ЛИШЕ оновлення ключів
#define SIG_LEN    64         // Ed25519

typedef struct {
    bool     used;
    bool     revoked;         // «надгробок»: раз відкликаний — назавжди
    uint8_t  role;            // ROLE_OP чи ROLE_ROOT
    uint32_t kid;             // номер ключа
    uint64_t not_before;      // чинний від (unix, с)
    uint64_t not_after;       // чинний до
    uint8_t  pub[32];         // відкритий ключ Ed25519
} keyslot_t;

// Звʼязка живе у флеші й переживає перезавантаження. На заводі (фаза 1)
// в неї кладуть ДВА ключі: корінь-якір і перший операційний.
static keyslot_t g_ring[MAX_KEYS];
static uint32_t  g_device_id;

// Обгортка над перевіркою підпису Ed25519 (напр., libsodium
// crypto_sign_verify_detached, що вертає 0 на успіх). 32-байтний
// відкритий ключ, 64-байтний підпис — стандарт Ed25519.
bool ed25519_verify(const uint8_t sig[SIG_LEN], const uint8_t *msg,
                    size_t len, const uint8_t pub[32]);

void nvs_save_ring(void);     // персистить g_ring у флеш

static keyslot_t *find_key(uint32_t kid, uint8_t role) {
    for (int i = 0; i < MAX_KEYS; i++)
        if (g_ring[i].used && g_ring[i].kid == kid && g_ring[i].role == role)
            return &g_ring[i];
    return NULL;
}
