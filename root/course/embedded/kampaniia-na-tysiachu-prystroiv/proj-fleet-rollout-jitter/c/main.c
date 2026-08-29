/* Прогін кампанії на одному вузлі парку — від номера когорти до підтвердження
 * або відкату. Симульовані тут лише зовнішні речі: годинник, радіоканал і сам
 * CDN; уся логіка вузла — та сама, що поїде на кристал.
 *
 *   ./ota_node          — вузол проходить випробування і підтверджує образ
 *   ./ota_node crash    — новий образ падає на кожному старті; видно, як
 *                         лічильник у незалежній пам'яті доводить до відкату */
#include "boot.h"
#include "cohort.h"
#include "flash.h"
#include "jitter.h"
#include "platform.h"
#include "trial.h"

#include <stdio.h>
#include <string.h>

#define IMAGE_LEN        (96u * 1024u)
#define BLOCK_LEN        2048u
#define FLEET_SIZE       1000u
#define STAGE_PERCENT    25u
#define JITTER_WINDOW_MS (15u * 60u * 1000u)
#define TRIAL_WINDOW_S   1800u
#define TICK_S           60u

/* Маніфест кампанії, який вузол забрав із сервера. Сіль публікується разом із
 * кампанією: інша кампанія — інша сіль — інше розбиття парку. */
typedef struct {
    uint32_t    campaign_id;
    const char *salt;
    uint8_t     stage_percent;
    uint32_t    image_len;
    uint32_t    image_crc;
} manifest_t;

static uint8_t g_image[IMAGE_LEN];      /* образ, який роздає CDN (версія 2) */
static uint8_t g_factory[IMAGE_LEN];    /* заводський образ у Bank A         */

/* ---- імітація зовнішнього світу ------------------------------------------ */

static void image_fill(uint8_t *buf, size_t len, uint32_t version)
{
    /* Замість справжнього образу — детермінований візерунок: важливо лише те,
     * що дві версії різні, а CRC відтворюваний. */
    uint32_t x = 0x1234567u ^ version;
    for (size_t i = 0; i < len; ++i) {
        x = x * 1664525u + 1013904223u;
        buf[i] = (uint8_t)(x >> 24);
    }
}

/* Радіоканал у полі: приблизно кожна четверта сесія обривається. */
static bool cdn_read_block(uint32_t offset, uint8_t *dst, size_t len, rng_t *rng)
{
    if (rng_below(rng, 100u) < 25u) {
        return false;
    }
    memcpy(dst, &g_image[offset], len);
    return true;
}

/* ---- підготовка вузла ----------------------------------------------------- */

static bool provision_factory_image(void)
{
    ota_state_t st;
    ota_state_load(&st);
    if (st.bank_len[BOOT_BANK_A] != 0u) {
        return true;   /* вузол уже прошитий на конвеєрі */
    }

    image_fill(g_factory, sizeof(g_factory), 1u);
    if (!flash_bank_erase(BOOT_BANK_A) ||
        !flash_bank_write(BOOT_BANK_A, 0u, g_factory, sizeof(g_factory))) {
        return false;
    }

    st.active_bank            = BOOT_BANK_A;
    st.trial_pending          = false;
    st.boot_failures          = 0;
    st.bank_len[BOOT_BANK_A]  = IMAGE_LEN;
    st.bank_crc[BOOT_BANK_A]  = flash_bank_crc(BOOT_BANK_A, IMAGE_LEN);
    ota_state_store(&st);
    return true;
}

/* Перед кампанією розподіл перевіряють на всій множині серійних номерів парку. */
static void survey_fleet(const manifest_t *m, const uint8_t hw_id[COHORT_ID_LEN])
{
    static uint8_t ids[FLEET_SIZE * COHORT_ID_LEN];

    for (uint32_t i = 0; i < FLEET_SIZE; ++i) {
        uint8_t *id = &ids[i * COHORT_ID_LEN];
        memcpy(id, hw_id, COHORT_ID_LEN);
        id[12] = (uint8_t)(i);
        id[13] = (uint8_t)(i >> 8);
        id[14] = (uint8_t)(i >> 16);
        id[15] = (uint8_t)(i >> 24);
    }

    const size_t salt_len = strlen(m->salt);
    cohort_survey_t s;

    cohort_survey(ids, FLEET_SIZE, (const uint8_t *)m->salt, salt_len,
                  cohort_bucket_sha256, &s);
    printf("[парк] SHA-256: хі-квадрат %.1f, кошики %u..%u -> %s\n",
           s.chi_square, s.min_count, s.max_count,
           cohort_survey_acceptable(&s) ? "рівномірно" : "НЕРІВНОМІРНО");

    cohort_survey(ids, FLEET_SIZE, (const uint8_t *)m->salt, salt_len,
                  cohort_bucket_fnv1a, &s);
    printf("[парк] FNV-1a:  хі-квадрат %.1f, кошики %u..%u -> %s\n",
           s.chi_square, s.min_count, s.max_count,
           cohort_survey_acceptable(&s) ? "рівномірно" : "НЕРІВНОМІРНО");
}

/* ---- завантаження образу -------------------------------------------------- */

static bool download_image(const manifest_t *m, rng_t *rng, boot_bank_t target)
{
    backoff_t backoff;
    backoff_init(&backoff, 2000u, 5u * 60u * 1000u);

    if (!flash_bank_erase(target)) {
        printf("[ota] банк не стерся\n");
        return false;
    }

    uint8_t block[BLOCK_LEN];
    unsigned retries = 0;

    for (uint32_t off = 0; off < m->image_len; off += BLOCK_LEN) {
        const uint32_t len = (m->image_len - off < BLOCK_LEN) ? (m->image_len - off) : BLOCK_LEN;

        while (!cdn_read_block(off, block, len, rng)) {
            const uint32_t wait = backoff_next(&backoff, rng);
            retries++;
            if (retries > 200u) {
                printf("[ota] канал не тримає сесію, кампанію відкладено\n");
                return false;
            }
            plat_delay_ms(wait);
        }
        backoff_reset(&backoff);

        if (!flash_bank_write(target, off, block, len)) {
            printf("[ota] помилка запису на зсуві %u\n", off);
            return false;
        }
    }

    printf("[ota] образ завантажено, повторів через обриви: %u\n", retries);

    if (flash_bank_crc(target, m->image_len) != m->image_crc) {
        printf("[ota] CRC не збігся з маніфестом — банк не активуємо\n");
        return false;
    }
    return true;
}

/* ---- застосунок, який стартував із вибраного банку ------------------------ */

static bool app_run(const boot_decision_t *d, bool inject_crash)
{
    trial_t t;
    if (!trial_begin(&t, TRIAL_WINDOW_S)) {
        printf("[app] звичайний старт із банку %c\n", d->bank == BOOT_BANK_B ? 'B' : 'A');
        return true;
    }

    printf("[app] випробувальний термін, банк %c, аварійних стартів %u\n",
           d->bank == BOOT_BANK_B ? 'B' : 'A', d->failures);

    for (;;) {
        if (inject_crash && t.elapsed_s >= 120u) {
            /* Паніка ядра: підтвердження не сталося, стан у незалежній пам'яті
             * лишився як був. */
            printf("[app] паніка на %u с — перезавантаження\n", t.elapsed_s);
            plat_reboot();
            return false;
        }

        /* Самодіагностика: шини сенсорів, живлення, цілісність конфігурації.
         * Обмін із бекендом іде довше — він вимагає TLS і живого каналу. */
        const trial_check_t selftest = (t.elapsed_s >= 180u) ? TRIAL_CHECK_PASS : TRIAL_CHECK_PENDING;
        const trial_check_t backend  = (t.elapsed_s >= 300u) ? TRIAL_CHECK_PASS : TRIAL_CHECK_PENDING;

        const trial_result_t r = trial_step(&t, TICK_S, selftest, backend);
        plat_delay_ms(TICK_S * 1000u);

        if (r == TRIAL_COMMITTED) {
            printf("[app] образ підтверджено на %u с\n", t.elapsed_s);
            return true;
        }
        if (r == TRIAL_ROLLBACK) {
            printf("[app] відкат на попередній банк — перезавантаження\n");
            plat_reboot();
            return false;
        }
    }
}

/* ---- кампанія ------------------------------------------------------------- */

int main(int argc, char **argv)
{
    const bool inject_crash = (argc > 1 && strcmp(argv[1], "crash") == 0);

    uint8_t hw_id[COHORT_ID_LEN];
    plat_hardware_id(hw_id);

    image_fill(g_image, sizeof(g_image), 2u);

    manifest_t manifest = {
        .campaign_id   = 0x20260829u,
        .salt          = "rollout-2026-08-r3",
        .stage_percent = STAGE_PERCENT,
        .image_len     = IMAGE_LEN,
        /* На сервері цю суму рахують один раз і підписують разом із маніфестом. */
        .image_crc     = crc32_update(0u, g_image, IMAGE_LEN)
    };

    if (!provision_factory_image()) {
        printf("[вузол] заводський образ не записався\n");
        return 1;
    }

    survey_fleet(&manifest, hw_id);

    const uint8_t bucket = cohort_bucket_sha256(hw_id, (const uint8_t *)manifest.salt,
                                                strlen(manifest.salt));
    printf("[вузол] когорта %u, поточна фаза %u%%\n", bucket, manifest.stage_percent);

    if (!cohort_eligible(bucket, manifest.stage_percent)) {
        printf("[вузол] фаза цього вузла ще не настала — чекаємо\n");
        return 0;
    }

    rng_t rng;
    rng_seed_from_hardware(&rng, hw_id);

    const uint32_t delay_ms = jitter_initial_ms(&rng, JITTER_WINDOW_MS);
    printf("[вузол] початковий джитер %u.%03u с у вікні %u с\n",
           delay_ms / 1000u, delay_ms % 1000u, JITTER_WINDOW_MS / 1000u);
    plat_delay_ms(delay_ms);

    ota_state_t st;
    ota_state_load(&st);
    const boot_bank_t target = flash_other_bank(st.active_bank);

    if (!download_image(&manifest, &rng, target)) {
        return 1;
    }
    if (!trial_arm(target, manifest.campaign_id, manifest.image_len, manifest.image_crc)) {
        printf("[ota] покажчик завантаження не переставлено\n");
        return 1;
    }
    printf("[ota] банк %c озброєно, перезавантаження\n", target == BOOT_BANK_B ? 'B' : 'A');
    plat_reboot();

    /* Далі — цикли скидання. На кристалі кожен виток це справжній reset. */
    for (unsigned cycle = 1; plat_sim_take_reboot() && cycle <= 8u; ++cycle) {
        printf("\n--- скидання #%u ---\n", cycle);

        const boot_decision_t d = boot_select();
        if (d.kind == BOOT_NO_IMAGE) {
            printf("[boot] цілого образу немає — лишаємось у завантажувачі\n");
            return 2;
        }
        if (d.kind == BOOT_ROLLED_BACK) {
            printf("[boot] лічильник збоїв вичерпано, повернулись на банк %c\n",
                   d.bank == BOOT_BANK_B ? 'B' : 'A');
        }
        boot_jump(d.entry);

        if (app_run(&d, inject_crash && d.bank == BOOT_BANK_B)) {
            ota_state_load(&st);
            printf("\n[підсумок] банк %c, випробування %s, аварійних стартів %u\n",
                   st.active_bank == BOOT_BANK_B ? 'B' : 'A',
                   st.trial_pending ? "триває" : "завершено", st.boot_failures);
            return 0;
        }
    }

    printf("[вузол] вичерпано ліміт скидань симуляції\n");
    return 3;
}
