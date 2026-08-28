#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define CHALLENGE_NONCE_LEN   32
#define CHIP_UUID_LEN         16
#define SIGNATURE_LEN         64
#define PUBLIC_KEY_LEN        32
#define NVS_FLASH_SECTOR_SIZE 4096
#define NVS_FLASH_SECTORS_NUM 8

/* Коди результатів виконання операцій */
typedef enum {
    UNLOCK_OK                 = 0,
    UNLOCK_ERR_INVALID_NONCE  = 1,
    UNLOCK_ERR_SIGNATURE_FAIL = 2,
    UNLOCK_ERR_TIMEOUT        = 3,
    UNLOCK_ERR_FLASH_FAILURE  = 4
} unlock_status_t;

/* Структура запиту на розблокування */
typedef struct {
    uint8_t nonce[CHALLENGE_NONCE_LEN];
    uint8_t chip_uuid[CHIP_UUID_LEN];
    uint32_t timestamp_ms;
    bool     is_active;
} challenge_state_t;

/* Відкритий кореневий ключ розблокування виробника (зашитий у ROM) */
static const uint8_t EOL_ROOT_PUBLIC_KEY[PUBLIC_KEY_LEN] = {
    0x3b, 0x6a, 0x27, 0xbc, 0xce, 0xb6, 0xa4, 0x2d,
    0x68, 0x7a, 0xa5, 0x65, 0x84, 0x88, 0xdd, 0x4d,
    0x9c, 0x86, 0x45, 0x40, 0x07, 0x69, 0x66, 0x04,
    0x69, 0x62, 0x0d, 0xa4, 0x63, 0xa5, 0x72, 0x8b
};

static challenge_state_t g_challenge_state;

/* Прототипи апаратних функцій HAL */
extern void hal_trng_fill(uint8_t *dest, size_t len);
extern void hal_get_chip_uuid(uint8_t *dest);
extern uint32_t hal_get_tick_ms(void);
extern bool hal_flash_erase_sector(uint32_t sector_addr);
extern bool hal_flash_write(uint32_t addr, const uint8_t *data, size_t len);
extern bool hal_efuse_burn_unlocked_flag(void);
extern bool crypto_ed25519_verify(const uint8_t *sig, const uint8_t *msg, 
                                  size_t msg_len, const uint8_t *pub_key);

/* Безпечне очищення буфера (гарантоване компілятором без оптимізації) */
static void secure_memzero(void *v, size_t n) {
    volatile uint8_t *p = (volatile uint8_t *)v;
    while (n--) {
        *p++ = 0x00;
    }
}

/* Генерація одноразового виклику (Challenge) */
void bootloader_create_challenge(uint8_t *out_nonce, uint8_t *out_uuid) {
    hal_trng_fill(g_challenge_state.nonce, CHALLENGE_NONCE_LEN);
    hal_get_chip_uuid(g_challenge_state.chip_uuid);
    
    g_challenge_state.timestamp_ms = hal_get_tick_ms();
    g_challenge_state.is_active = true;
    
    memcpy(out_nonce, g_challenge_state.nonce, CHALLENGE_NONCE_LEN);
    memcpy(out_uuid, g_challenge_state.chip_uuid, CHIP_UUID_LEN);
}

/* Безпечне знищення даних користувача у Flash (Secure Zeroization) */
static bool bootloader_zeroize_user_data(void) {
    uint8_t zero_buf[256];
    secure_memzero(zero_buf, sizeof(zero_buf));

    /* Сектори NVS сховища параметрів (Wi-Fi паролі, сертифікати, токени) */
    const uint32_t nvs_base_addr = 0x08040000;
    
    for (uint32_t i = 0; i < NVS_FLASH_SECTORS_NUM; i++) {
        uint32_t addr = nvs_base_addr + (i * NVS_FLASH_SECTOR_SIZE);
        
        /* 1. Стираємо сектор (переведення всіх бітів у 0xFF) */
        if (!hal_flash_erase_sector(addr)) {
            return false;
        }
        
        /* 2. Записуємо нулі для запобігання відновленню залишків заряду */
        for (uint32_t offset = 0; offset < NVS_FLASH_SECTOR_SIZE; offset += sizeof(zero_buf)) {
            if (!hal_flash_write(addr + offset, zero_buf, sizeof(zero_buf))) {
                return false;
            }
        }
    }
    return true;
}

/* Обробка та верифікація токена розблокування */
unlock_status_t bootloader_process_unlock(const uint8_t *signature, uint32_t current_time_ms) {
    if (!g_challenge_state.is_active) {
        return UNLOCK_ERR_TIMEOUT;
    }
    
    /* Перевірка тайм-ауту активності виклику (120 секунд) */
    if ((current_time_ms - g_challenge_state.timestamp_ms) > 120000) {
        secure_memzero(&g_challenge_state, sizeof(g_challenge_state));
        return UNLOCK_ERR_TIMEOUT;
    }
    
    /* Формуємо повідомлення: Nonce || Chip_UUID */
    uint8_t message[CHALLENGE_NONCE_LEN + CHIP_UUID_LEN];
    memcpy(message, g_challenge_state.nonce, CHALLENGE_NONCE_LEN);
    memcpy(message + CHALLENGE_NONCE_LEN, g_challenge_state.chip_uuid, CHIP_UUID_LEN);
    
    /* Верифікація криптографічного підпису */
    bool valid = crypto_ed25519_verify(signature, message, sizeof(message), EOL_ROOT_PUBLIC_KEY);
    
    /* Негайне стирання повідомлення та виклику з оперативної пам'яті */
    secure_memzero(message, sizeof(message));
    secure_memzero(&g_challenge_state, sizeof(g_challenge_state));
    
    if (!valid) {
        return UNLOCK_ERR_SIGNATURE_FAIL;
    }
    
    /* Підпис валідний -> виконуємо стирання конфіденційних даних */
    if (!bootloader_zeroize_user_data()) {
        return UNLOCK_ERR_FLASH_FAILURE;
    }
    
    /* Перепалюємо апаратний біт статусу розблокування */
    if (!hal_efuse_burn_unlocked_flag()) {
        return UNLOCK_ERR_FLASH_FAILURE;
    }
    
    return UNLOCK_OK;
}
