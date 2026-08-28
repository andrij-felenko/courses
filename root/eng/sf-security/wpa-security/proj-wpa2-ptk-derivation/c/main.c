#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <openssl/evp.h>
#include <openssl/hmac.h>
#include <openssl/crypto.h>

#define PMK_LEN 32
#define PTK_LEN 64
#define MAC_LEN 6
#define NONCE_LEN 32
#define MIC_LEN 16
#define EAPOL_MIC_OFFSET 81

typedef struct {
    uint8_t kck[16]; /* Key Confirmation Key (перевірка MIC) */
    uint8_t kek[16]; /* Key Encryption Key (шифрування ключів) */
    uint8_t tk[16];  /* Temporal Key (шифрування трафіку CCMP) */
} wpa2_ptk_t;

/* Генерація PMK через PBKDF2(HMAC-SHA1, Passphrase, SSID, 4096, 32) */
bool wpa2_derive_pmk(const char *passphrase, const char *ssid, uint8_t pmk_out[PMK_LEN]) {
    if (!passphrase || !ssid || !pmk_out) return false;
    return PKCS5_PBKDF2_HMAC(passphrase, (int)strlen(passphrase),
                             (const uint8_t *)ssid, (int)strlen(ssid),
                             4096, EVP_sha1(), PMK_LEN, pmk_out) == 1;
}

/* Псевдовипадкова функція PRF-512 для генерації 64 байтів PTK */
bool wpa2_derive_ptk(const uint8_t pmk[PMK_LEN],
                     const uint8_t ap_mac[MAC_LEN], const uint8_t sta_mac[MAC_LEN],
                     const uint8_t anonce[NONCE_LEN], const uint8_t snonce[NONCE_LEN],
                     wpa2_ptk_t *ptk_out) {
    if (!pmk || !ap_mac || !sta_mac || !anonce || !snonce || !ptk_out) return false;

    /* 1. Префікс мітки стандарту IEEE 802.11i */
    const char *label = "Pairwise key expansion";
    size_t label_len = strlen(label) + 1; /* Включаючи нуль-термінатор */

    /* 2. Канонічне впорядкування MAC-адрес та Nonce */
    uint8_t mac_block[12];
    if (memcmp(ap_mac, sta_mac, MAC_LEN) < 0) {
        memcpy(mac_block, ap_mac, MAC_LEN);
        memcpy(mac_block + MAC_LEN, sta_mac, MAC_LEN);
    } else {
        memcpy(mac_block, sta_mac, MAC_LEN);
        memcpy(mac_block + MAC_LEN, ap_mac, MAC_LEN);
    }

    uint8_t nonce_block[64];
    if (memcmp(anonce, snonce, NONCE_LEN) < 0) {
        memcpy(nonce_block, anonce, NONCE_LEN);
        memcpy(nonce_block + NONCE_LEN, snonce, NONCE_LEN);
    } else {
        memcpy(nonce_block, snonce, NONCE_LEN);
        memcpy(nonce_block + NONCE_LEN, anonce, NONCE_LEN);
    }

    /* 3. Збирання префікса даних для PRF: Label || 0x00 || MACs || Nonces */
    uint8_t data_prefix[128];
    size_t offset = 0;
    memcpy(data_prefix + offset, label, label_len);
    offset += label_len;
    memcpy(data_prefix + offset, mac_block, sizeof(mac_block));
    offset += sizeof(mac_block);
    memcpy(data_prefix + offset, nonce_block, sizeof(nonce_block));
    offset += sizeof(nonce_block);

    /* 4. Ітеративне розширення через HMAC-SHA1 (4 блоки по 20 байтів для отримання 64 байтів) */
    uint8_t ptk_raw[80];
    for (uint8_t i = 0; i < 4; i++) {
        data_prefix[offset] = i; /* Додавання лічильника наприкінці */
        unsigned int md_len = 20;
        HMAC(EVP_sha1(), pmk, PMK_LEN, data_prefix, offset + 1, ptk_raw + (i * 20), &md_len);
    }

    /* 5. Розподіл ключів PTK */
    memcpy(ptk_out->kck, ptk_raw, 16);
    memcpy(ptk_out->kek, ptk_raw + 16, 16);
    memcpy(ptk_out->tk,  ptk_raw + 32, 16);

    /* Очищення чутливих тимчасових буферів у пам'яті */
    OPENSSL_cleanse(ptk_raw, sizeof(ptk_raw));
    OPENSSL_cleanse(data_prefix, sizeof(data_prefix));
    return true;
}

/* Верифікація EAPOL-Key Message 2 MIC */
bool wpa2_verify_eapol_mic(const uint8_t kck[16], const uint8_t *eapol_frame, size_t frame_len) {
    if (!kck || !eapol_frame || frame_len < EAPOL_MIC_OFFSET + MIC_LEN) return false;

    /* 1. Зчитування оригінального MIC із кадру */
    uint8_t original_mic[MIC_LEN];
    memcpy(original_mic, eapol_frame + EAPOL_MIC_OFFSET, MIC_LEN);

    /* 2. Копіювання кадру та обнулення поля MIC */
    uint8_t frame_copy[1024];
    if (frame_len > sizeof(frame_copy)) return false;
    memcpy(frame_copy, eapol_frame, frame_len);
    memset(frame_copy + EAPOL_MIC_OFFSET, 0, MIC_LEN);

    /* 3. Розрахунок HMAC-SHA1 над модифікованим кадром (WPA2 Key Descriptor v2) */
    uint8_t calculated_digest[20];
    unsigned int digest_len = sizeof(calculated_digest);
    HMAC(EVP_sha1(), kck, 16, frame_copy, frame_len, calculated_digest, &digest_len);

    /* 4. Порівняння перших 16 байтів у константному часі */
    bool match = (CRYPTO_memcmp(original_mic, calculated_digest, MIC_LEN) == 0);

    OPENSSL_cleanse(frame_copy, sizeof(frame_copy));
    OPENSSL_cleanse(calculated_digest, sizeof(calculated_digest));
    return match;
}

int main(void) {
    const char *ssid = "Office_Secure_WiFi";
    const char *passphrase = "CorrectHorseBatteryStaple99";

    uint8_t ap_mac[6]  = {0x00, 0x14, 0x6C, 0x7E, 0x40, 0x80};
    uint8_t sta_mac[6] = {0x00, 0x25, 0xD3, 0x11, 0x22, 0x33};

    uint8_t anonce[32] = {
        0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
        0x18, 0x19, 0x1A, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F,
        0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27,
        0x28, 0x29, 0x2A, 0x2B, 0x2C, 0x2D, 0x2E, 0x2F
    };

    uint8_t snonce[32] = {
        0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5, 0xA6, 0xA7,
        0xA8, 0xA9, 0xAA, 0xAB, 0xAC, 0xAD, 0xAE, 0xAF,
        0xB0, 0xB1, 0xB2, 0xB3, 0xB4, 0xB5, 0xB6, 0xB7,
        0xB8, 0xB9, 0xBA, 0xBB, 0xBC, 0xBD, 0xBE, 0xBF
    };

    uint8_t pmk[PMK_LEN];
    wpa2_derive_pmk(passphrase, ssid, pmk);

    wpa2_ptk_t ptk;
    wpa2_derive_ptk(pmk, ap_mac, sta_mac, anonce, snonce, &ptk);

    printf("=== WPA2 РОЗРАХУНОК КЛЮЧІВ ===\n");
    printf("SSID:       %s\n", ssid);
    printf("Passphrase: %s\n", passphrase);
    printf("KCK (Key Confirmation Key): ");
    for (int i = 0; i < 16; i++) printf("%02X", ptk.kck[i]);
    printf("\nKEK (Key Encryption Key):   ");
    for (int i = 0; i < 16; i++) printf("%02X", ptk.kek[i]);
    printf("\nTK  (Temporal CCMP Key):    ");
    for (int i = 0; i < 16; i++) printf("%02X", ptk.tk[i]);
    printf("\n\n");

    /* Тестовий кадр EAPOL-Key Message 2 (довжина 121 байт) */
    uint8_t test_eapol[121] = {0};
    test_eapol[0] = 0x02; /* EAPOL Version 2 */
    test_eapol[1] = 0x03; /* EAPOL-Key Type */
    test_eapol[4] = 0x02; /* Key Descriptor Type: RSN / WPA2 */
    test_eapol[6] = 0x01; /* Key Info: Pairwise + MIC встановлено */
    test_eapol[7] = 0x0A;

    /* Обчислення еталонного MIC */
    unsigned int len = 20;
    uint8_t full_digest[20];
    HMAC(EVP_sha1(), ptk.kck, 16, test_eapol, sizeof(test_eapol), full_digest, &len);
    memcpy(test_eapol + EAPOL_MIC_OFFSET, full_digest, 16);

    /* Перевірка верифікатора */
    bool valid = wpa2_verify_eapol_mic(ptk.kck, test_eapol, sizeof(test_eapol));
    printf("Результат верифікації EAPOL MIC: %s\n", valid ? "ПРАВИЛЬНИЙ (УСПІХ)" : "НЕПРАВИЛЬНИЙ (ПОМИЛКА)");

    OPENSSL_cleanse(pmk, sizeof(pmk));
    OPENSSL_cleanse(&ptk, sizeof(ptk));
    return 0;
}
