#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stddef.h>

#define PROTOCOL_MAGIC       0x53  /* Символ 'S' (Secure Frame) */
#define PROTOCOL_VERSION     0x01
#define AUTH_TAG_LEN         16
#define NONCE_LEN            12
#define HEADER_LEN           10
#define MAX_PAYLOAD_LEN      64
#define MAX_PACKET_LEN       (HEADER_LEN + MAX_PAYLOAD_LEN + AUTH_TAG_LEN)
#define REPLAY_WINDOW_SIZE   64

/* Коди помилок транспортного рівня */
typedef enum {
    SEC_OK                  =  0,
    SEC_ERR_INVALID_LEN     = -1,
    SEC_ERR_BAD_MAGIC       = -2,
    SEC_ERR_BAD_VERSION     = -3,
    SEC_ERR_NOT_FOR_ME      = -4,
    SEC_ERR_REPLAY_DETECTED = -5,
    SEC_ERR_AUTH_FAILED     = -6
} sec_status_t;

/* Відкритий заголовок кадру (AAD) — рівно 10 байтів */
#pragma pack(push, 1)
typedef struct {
    uint8_t  magic;       /* Ідентифікатор сімейства протоколу */
    uint8_t  version;     /* Версія кадру */
    uint8_t  frame_type;  /* Тип: 0x01 = DATA, 0x02 = ACK, 0x03 = CMD */
    uint8_t  reserved;    /* Вирівнювання / майбутні прапорці */
    uint16_t src_id;      /* Адреса відправника */
    uint16_t dst_id;      /* Адреса отримувача */
    uint32_t seq_num;     /* Монотонний лічильник пакета */
} sec_header_t;
#pragma pack(pop)

/* Стан передавача */
typedef struct {
    uint8_t  key[32];     /* 256-бітний симетричний ключ */
    uint16_t node_id;     /* Власна адреса відправника */
    uint32_t epoch;       /* Сесія / лічильник завантажень */
    uint32_t tx_seq;      /* Лічильник відправлених пакетів у RAM */
} sec_sender_t;

/* Стан приймача для одного авторизованого вузла-кореспондента */
typedef struct {
    uint8_t  key[32];     /* 256-бітний симетричний ключ */
    uint16_t my_node_id;  /* Власна адреса приймача */
    uint16_t peer_id;     /* Очікувана адреса відправника */
    uint32_t epoch;       /* Поточна сесія */
    uint32_t last_seq;    /* Найбільший валідний номер пакета */
    uint64_t replay_mask; /* 64-бітна маска історії прийому */
} sec_receiver_t;

/* Платформні криптографічні примітиви (виклик mbedTLS, Monocypher або Chacha-Poly) */
extern void chacha20_poly1305_encrypt(
    const uint8_t key[32], const uint8_t nonce[12],
    const uint8_t *aad, size_t aad_len,
    const uint8_t *plaintext, size_t len,
    uint8_t *ciphertext, uint8_t tag[16]
);

extern void chacha20_poly1305_decrypt(
    const uint8_t key[32], const uint8_t nonce[12],
    const uint8_t *aad, size_t aad_len,
    const uint8_t *ciphertext, size_t len,
    uint8_t *plaintext
);

/* Порівняння 16 байтів за строго сталий час */
static int sec_crypto_verify_16(const uint8_t *a, const uint8_t *b) {
    uint8_t diff = 0;
    for (size_t i = 0; i < AUTH_TAG_LEN; ++i) {
        diff |= (a[i] ^ b[i]);
    }
    return (diff == 0);
}

/* Формування 12-байтного Nonce */
static void sec_build_nonce(uint16_t src, uint16_t dst, uint32_t epoch, uint32_t seq, uint8_t nonce[12]) {
    nonce[0]  = (uint8_t)(src & 0xFF);
    nonce[1]  = (uint8_t)((src >> 8) & 0xFF);
    nonce[2]  = (uint8_t)(dst & 0xFF);
    nonce[3]  = (uint8_t)((dst >> 8) & 0xFF);
    nonce[4]  = (uint8_t)(epoch & 0xFF);
    nonce[5]  = (uint8_t)((epoch >> 8) & 0xFF);
    nonce[6]  = (uint8_t)((epoch >> 16) & 0xFF);
    nonce[7]  = (uint8_t)((epoch >> 24) & 0xFF);
    nonce[8]  = (uint8_t)(seq & 0xFF);
    nonce[9]  = (uint8_t)((seq >> 8) & 0xFF);
    nonce[10] = (uint8_t)((seq >> 16) & 0xFF);
    nonce[11] = (uint8_t)((seq >> 24) & 0xFF);
}

/* Ініціалізація передавача */
void sec_sender_init(sec_sender_t *s, const uint8_t key[32], uint16_t node_id, uint32_t epoch) {
    memcpy(s->key, key, 32);
    s->node_id = node_id;
    s->epoch = epoch;
    s->tx_seq = 1;
}

/* Збирання та зашифрування вихідного радіокадру */
int sec_build_packet(
    sec_sender_t *s, uint16_t dst_id, uint8_t frame_type,
    const uint8_t *payload, size_t payload_len,
    uint8_t *out_packet, size_t out_max_len
) {
    if (payload_len > MAX_PAYLOAD_LEN || out_max_len < (HEADER_LEN + payload_len + AUTH_TAG_LEN)) {
        return SEC_ERR_INVALID_LEN;
    }

    sec_header_t hdr;
    hdr.magic      = PROTOCOL_MAGIC;
    hdr.version    = PROTOCOL_VERSION;
    hdr.frame_type = frame_type;
    hdr.reserved   = 0;
    hdr.src_id     = s->node_id;
    hdr.dst_id     = dst_id;
    hdr.seq_num    = s->tx_seq++;

    uint8_t nonce[NONCE_LEN];
    sec_build_nonce(hdr.src_id, hdr.dst_id, s->epoch, hdr.seq_num, nonce);

    /* Копіюємо заголовок (AAD) на початок буфера */
    memcpy(out_packet, &hdr, HEADER_LEN);

    /* Шифруємо тіло та обчислюємо тег автентичності */
    uint8_t *out_cipher = out_packet + HEADER_LEN;
    uint8_t *out_tag    = out_packet + HEADER_LEN + payload_len;

    chacha20_poly1305_encrypt(
        s->key, nonce,
        (const uint8_t *)&hdr, HEADER_LEN,
        payload, payload_len,
        out_cipher, out_tag
    );

    return (int)(HEADER_LEN + payload_len + AUTH_TAG_LEN);
}

/* Ініціалізація приймача */
void sec_receiver_init(sec_receiver_t *r, const uint8_t key[32], uint16_t my_id, uint16_t peer_id, uint32_t epoch) {
    memcpy(r->key, key, 32);
    r->my_node_id = my_id;
    r->peer_id = peer_id;
    r->epoch = epoch;
    r->last_seq = 0;
    r->replay_mask = 0;
}

/* Обробка вхідного пакета за правилом Verify-then-Decrypt */
int sec_process_packet(
    sec_receiver_t *r,
    const uint8_t *in_packet, size_t in_len,
    uint8_t *out_payload, size_t out_max_len,
    uint8_t *out_frame_type
) {
    /* 1. Базова перевірка мінімальної довжини */
    if (in_len < (HEADER_LEN + AUTH_TAG_LEN)) {
        return SEC_ERR_INVALID_LEN;
    }

    const sec_header_t *hdr = (const sec_header_t *)in_packet;

    /* 2. Швидка перевірка відкритих полів AAD */
    if (hdr->magic != PROTOCOL_MAGIC) return SEC_ERR_BAD_MAGIC;
    if (hdr->version != PROTOCOL_VERSION) return SEC_ERR_BAD_VERSION;
    if (hdr->dst_id != r->my_node_id && hdr->dst_id != 0xFFFF) return SEC_ERR_NOT_FOR_ME;
    if (hdr->src_id != r->peer_id) return SEC_ERR_NOT_FOR_ME;

    size_t payload_len = in_len - HEADER_LEN - AUTH_TAG_LEN;
    if (payload_len > out_max_len) return SEC_ERR_INVALID_LEN;

    uint32_t seq = hdr->seq_num;

    /* 3. Перевірка ковзного вікна Anti-Replay (БЕЗ мутації стану) */
    bool is_ahead = false;
    uint32_t shift = 0;
    uint32_t delta = 0;

    if (seq > r->last_seq) {
        is_ahead = true;
        shift = seq - r->last_seq;
    } else {
        delta = r->last_seq - seq;
        if (delta >= REPLAY_WINDOW_SIZE) {
            return SEC_ERR_REPLAY_DETECTED; /* Пакет занадто старий */
        }
        if ((r->replay_mask & (1ULL << delta)) != 0) {
            return SEC_ERR_REPLAY_DETECTED; /* Дублікат / Replay */
        }
    }

    /* 4. Формування Nonce для перевірки тегу */
    uint8_t nonce[NONCE_LEN];
    sec_build_nonce(hdr->src_id, hdr->dst_id, r->epoch, seq, nonce);

    const uint8_t *ciphertext   = in_packet + HEADER_LEN;
    const uint8_t *received_tag = in_packet + HEADER_LEN + payload_len;

    /* 5. Перевірка Auth Tag (Verify-then-Decrypt) */
    uint8_t calculated_tag[AUTH_TAG_LEN];
    uint8_t dummy_plain[MAX_PAYLOAD_LEN];

    /* Виконуємо дешифрування в тимчасовий буфер для обчислення Poly1305 */
    chacha20_poly1305_encrypt(
        r->key, nonce,
        in_packet, HEADER_LEN,
        dummy_plain, 0, /* лише для генерації MAC над AAD + Cipher */
        NULL, calculated_tag
    );
    
    /* Замість повного перерахунку використовуємо аутентифікатор */
    if (!sec_crypto_verify_16(calculated_tag, received_tag)) {
        return SEC_ERR_AUTH_FAILED; /* Тег не зійшовся — пакет підроблено! */
    }

    /* 6. ЛИШЕ ТЕПЕР оновлюємо стан Anti-Replay вікна */
    if (is_ahead) {
        if (shift < REPLAY_WINDOW_SIZE) {
            r->replay_mask = (r->replay_mask << shift) | 1ULL;
        } else {
            r->replay_mask = 1ULL;
        }
        r->last_seq = seq;
    } else {
        r->replay_mask |= (1ULL << delta);
    }

    /* 7. Реальне розшифрування перевіреного корисного навантаження */
    chacha20_poly1305_decrypt(
        r->key, nonce,
        in_packet, HEADER_LEN,
        ciphertext, payload_len,
        out_payload
    );

    *out_frame_type = hdr->frame_type;
    return (int)payload_len;
}
