#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <openssl/evp.h>
#include <openssl/crypto.h>

#if defined(_WIN32)
#include <winsock2.h>
#else
#include <arpa/inet.h>
#endif

#define MAGIC_HEADER        0x5345
#define PROTOCOL_VERSION    0x0100
#define AEAD_KEY_SIZE       32   /* 256 бітів AES-GCM */
#define AEAD_IV_SIZE        12   /* 96 бітів Nonce */
#define AEAD_TAG_SIZE       16   /* 128 бітів автентифікаційний тег */
#define REPLAY_WINDOW_SIZE  64   /* Розмір вікна повторів у бітах */

#pragma pack(push, 1)
typedef struct {
    uint16_t magic;
    uint16_t version;
    uint16_t msg_type;
    uint16_t reserved;
    uint64_t seq_num;
} PacketHeader;
#pragma pack(pop)

typedef struct {
    uint8_t key[AEAD_KEY_SIZE];
    uint8_t iv_base[AEAD_IV_SIZE];
    uint64_t tx_seq;
    uint64_t rx_max_seq;
    uint64_t replay_bitmap;
} SecureChannel;

/* Ініціалізація захищеного каналу */
void secure_channel_init(SecureChannel *chan, const uint8_t key[AEAD_KEY_SIZE], const uint8_t iv_base[AEAD_IV_SIZE]) {
    memcpy(chan->key, key, AEAD_KEY_SIZE);
    memcpy(chan->iv_base, iv_base, AEAD_IV_SIZE);
    chan->tx_seq = 0;
    chan->rx_max_seq = 0;
    chan->replay_bitmap = 0;
}

/* Формування 96-бітного Nonce шляхом XOR seq_num з IV_base */
static void derive_nonce(const uint8_t iv_base[AEAD_IV_SIZE], uint64_t seq, uint8_t out_nonce[AEAD_IV_SIZE]) {
    memcpy(out_nonce, iv_base, AEAD_IV_SIZE);
    for (int i = 0; i < 8; ++i) {
        out_nonce[AEAD_IV_SIZE - 1 - i] ^= (uint8_t)((seq >> (i * 8)) & 0xFF);
    }
}

/* Перевірка номера послідовності через ковзне вікно (RFC 6479) */
static bool check_replay_window(const SecureChannel *chan, uint64_t seq) {
    if (seq == 0 && chan->rx_max_seq == 0 && chan->replay_bitmap == 0) return true;
    if (seq > chan->rx_max_seq) return true; /* Новий пакет попереду вікна */
    uint64_t diff = chan->rx_max_seq - seq;
    if (diff >= REPLAY_WINDOW_SIZE) return false; /* Пакет занадто старий */
    if (chan->replay_bitmap & (1ULL << diff)) return false; /* Пакет уже був отриманий */
    return true;
}

/* Оновлення стану вікна після успішної верифікації тегу */
static void update_replay_window(SecureChannel *chan, uint64_t seq) {
    if (seq > chan->rx_max_seq) {
        uint64_t diff = seq - chan->rx_max_seq;
        if (diff < REPLAY_WINDOW_SIZE) {
            chan->replay_bitmap = (chan->replay_bitmap << diff) | 1ULL;
        } else {
            chan->replay_bitmap = 1ULL;
        }
        chan->rx_max_seq = seq;
    } else {
        uint64_t diff = chan->rx_max_seq - seq;
        if (diff < REPLAY_WINDOW_SIZE) {
            chan->replay_bitmap |= (1ULL << diff);
        }
    }
}

/* Шифрування кадру (AEAD Encrypt) */
int secure_channel_encrypt_packet(
    SecureChannel *chan,
    uint16_t msg_type,
    const uint8_t *plaintext,
    size_t plaintext_len,
    uint8_t *out_frame,
    size_t *out_frame_len
) {
    if (!chan || !plaintext || !out_frame || !out_frame_len) return -1;

    PacketHeader hdr;
    hdr.magic = htons(MAGIC_HEADER);
    hdr.version = htons(PROTOCOL_VERSION);
    hdr.msg_type = htons(msg_type);
    hdr.reserved = 0;
    hdr.seq_num = htobe64(chan->tx_seq);

    uint8_t nonce[AEAD_IV_SIZE];
    derive_nonce(chan->iv_base, chan->tx_seq, nonce);
    chan->tx_seq++; /* Суворо монотонний інкремент */

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) return -1;

    int ret = -1;
    int len = 0;

    /* 1. Ініціалізація шифру AES-256-GCM */
    if (EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL) != 1) goto cleanup;
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_AEAD_SET_IVLEN, AEAD_IV_SIZE, NULL) != 1) goto cleanup;
    if (EVP_EncryptInit_ex(ctx, NULL, NULL, chan->key, nonce) != 1) goto cleanup;

    /* 2. Подання асоційованих даних AAD (Заголовок кадру) */
    if (EVP_EncryptUpdate(ctx, NULL, &len, (const uint8_t *)&hdr, sizeof(hdr)) != 1) goto cleanup;

    /* 3. Шифрування корисного навантаження (Plaintext -> Ciphertext) */
    uint8_t *ciphertext_dest = out_frame + sizeof(PacketHeader);
    if (EVP_EncryptUpdate(ctx, ciphertext_dest, &len, plaintext, (int)plaintext_len) != 1) goto cleanup;

    /* 4. Завершення шифрування */
    if (EVP_EncryptFinal_ex(ctx, ciphertext_dest + len, &len) != 1) goto cleanup;

    /* 5. Отримання 128-бітного автентифікаційного тегу */
    uint8_t *tag_dest = ciphertext_dest + plaintext_len;
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_AEAD_GET_TAG, AEAD_TAG_SIZE, tag_dest) != 1) goto cleanup;

    /* Запис відкритого заголовка в початок кадру */
    memcpy(out_frame, &hdr, sizeof(hdr));
    *out_frame_len = sizeof(PacketHeader) + plaintext_len + AEAD_TAG_SIZE;
    ret = 0;

cleanup:
    EVP_CIPHER_CTX_free(ctx);
    OPENSSL_cleanse(nonce, sizeof(nonce));
    return ret;
}

/* Дешифрування та верифікація кадру (AEAD Decrypt & Verify) */
int secure_channel_decrypt_packet(
    SecureChannel *chan,
    const uint8_t *in_frame,
    size_t frame_len,
    uint8_t *out_plaintext,
    size_t *out_plaintext_len,
    uint16_t *out_msg_type
) {
    if (!chan || !in_frame || !out_plaintext || !out_plaintext_len || !out_msg_type) return -1;
    if (frame_len < sizeof(PacketHeader) + AEAD_TAG_SIZE) return -2; /* Пакет надто короткий */

    const PacketHeader *hdr = (const PacketHeader *)in_frame;
    if (ntohs(hdr->magic) != MAGIC_HEADER || ntohs(hdr->version) != PROTOCOL_VERSION) return -3;

    uint64_t seq = be64toh(hdr->seq_num);
    /* Перевірка вікна повторів перед початком дорогих криптографічних розрахунків */
    if (!check_replay_window(chan, seq)) return -4;

    size_t ciphertext_len = frame_len - sizeof(PacketHeader) - AEAD_TAG_SIZE;
    const uint8_t *ciphertext = in_frame + sizeof(PacketHeader);
    const uint8_t *tag = in_frame + sizeof(PacketHeader) + ciphertext_len;

    uint8_t nonce[AEAD_IV_SIZE];
    derive_nonce(chan->iv_base, seq, nonce);

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) return -1;

    int ret = -5; /* Код помилки: автентифікація не пройдена */
    int len = 0;

    /* 1. Ініціалізація дешифрування AES-256-GCM */
    if (EVP_DecryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL) != 1) goto cleanup;
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_AEAD_SET_IVLEN, AEAD_IV_SIZE, NULL) != 1) goto cleanup;
    if (EVP_DecryptInit_ex(ctx, NULL, NULL, chan->key, nonce) != 1) goto cleanup;

    /* 2. Подання асоційованих даних AAD (Заголовок) */
    if (EVP_DecryptUpdate(ctx, NULL, &len, (const uint8_t *)hdr, sizeof(PacketHeader)) != 1) goto cleanup;

    /* 3. Дешифрування корисного навантаження у буфер отримувача */
    if (EVP_DecryptUpdate(ctx, out_plaintext, &len, ciphertext, (int)ciphertext_len) != 1) goto cleanup;

    /* 4. Встановлення очікуваного автентифікаційного тегу */
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_AEAD_SET_TAG, AEAD_TAG_SIZE, (void *)tag) != 1) goto cleanup;

    /* 5. БАР'ЄР ВЕРИФІКАЦІЇ: якщо тег не зійшовся, EVP_DecryptFinal_ex повертає <= 0 */
    if (EVP_DecryptFinal_ex(ctx, out_plaintext + len, &len) <= 0) {
        /* Очищення буфера у разі провалу верифікації */
        OPENSSL_cleanse(out_plaintext, ciphertext_len);
        goto cleanup;
    }

    /* Успішна верифікація: оновлюємо вікно повторів і повертаємо дані */
    update_replay_window(chan, seq);
    *out_plaintext_len = ciphertext_len;
    *out_msg_type = ntohs(hdr->msg_type);
    ret = 0;

cleanup:
    EVP_CIPHER_CTX_free(ctx);
    OPENSSL_cleanse(nonce, sizeof(nonce));
    return ret;
}
