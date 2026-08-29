#include "upkg.h"

#include <string.h>

/* Таблиця хешів лежить одразу за заголовком і його підписом. */
#define UPKG_TABLE_OFFSET (UPKG_HEADER_SIZE + UPKG_SIG_SIZE)

static uint32_t table_bytes(const upkg_header_t *hdr) {
    return hdr->chunk_count * UPKG_HASH_SIZE;
}

static uint32_t payload_offset(const upkg_header_t *hdr) {
    return UPKG_TABLE_OFFSET + table_bytes(hdr);
}

static uint32_t chunk_len(const upkg_header_t *hdr, uint32_t idx) {
    uint32_t done = idx * UPKG_CHUNK_SIZE;
    uint32_t left = hdr->payload_size - done;
    return left < UPKG_CHUNK_SIZE ? left : UPKG_CHUNK_SIZE;
}

/* Квитанція лягає в окремий сектор одразу за навантаженням. */
static uint32_t receipt_offset(const upkg_header_t *hdr) {
    uint32_t end = payload_offset(hdr) + hdr->payload_size;
    return (end + UPKG_CHUNK_SIZE - 1u) / UPKG_CHUNK_SIZE * UPKG_CHUNK_SIZE;
}

const char *upkg_strstatus(upkg_status_t status) {
    switch (status) {
    case UPKG_OK:                       return "гаразд";
    case UPKG_ERR_IO:                   return "носій недоступний";
    case UPKG_ERR_INVALID_MAGIC:        return "це не пакет UPKG";
    case UPKG_ERR_FORMAT:               return "поля заголовка суперечливі";
    case UPKG_ERR_HW_MISMATCH:          return "образ для іншої плати";
    case UPKG_ERR_ROLLBACK_DETECTED:    return "спроба відкату версії";
    case UPKG_ERR_SIGNATURE_INVALID:    return "підпис випуску недійсний";
    case UPKG_ERR_TABLE_HASH_MISMATCH:  return "таблиця хешів підмінена";
    case UPKG_ERR_CHUNK_HASH_MISMATCH:  return "чанк не збігся з таблицею";
    case UPKG_ERR_FINAL_HASH_MISMATCH:  return "підсумковий хеш образу інший";
    case UPKG_ERR_FLASH_ERASE:          return "стирання Slot B не вдалося";
    case UPKG_ERR_FLASH_WRITE:          return "запис у Slot B не вдався";
    case UPKG_ERR_CRYPTO:               return "криптоблок відмовив";
    case UPKG_ERR_NVS_WRITE:            return "стан завантаження не збережено";
    }
    return "невідомий код";
}

upkg_status_t upkg_read_header(upkg_session_t *s, upkg_header_t *hdr,
                               uint8_t sig[UPKG_SIG_SIZE]) {
    if (!s->media.read(s->media.ctx, 0, (uint8_t *)hdr, UPKG_HEADER_SIZE)) {
        return UPKG_ERR_IO;
    }
    if (!s->media.read(s->media.ctx, UPKG_HEADER_SIZE, sig, UPKG_SIG_SIZE)) {
        return UPKG_ERR_IO;
    }
    return UPKG_OK;
}

upkg_status_t upkg_validate_header(const upkg_session_t *s,
                                   const upkg_header_t *hdr,
                                   const uint8_t sig[UPKG_SIG_SIZE]) {
    if (hdr->magic != UPKG_MAGIC) {
        return UPKG_ERR_INVALID_MAGIC;
    }
    if (hdr->format_version != UPKG_FORMAT_VER ||
        hdr->chunk_size != UPKG_CHUNK_SIZE) {
        return UPKG_ERR_FORMAT;
    }
    if (hdr->payload_size == 0u ||
        hdr->chunk_count == 0u || hdr->chunk_count > UPKG_MAX_CHUNKS) {
        return UPKG_ERR_FORMAT;
    }
    /* Кількість чанків мусить точно відповідати довжині навантаження.
     * Інакше підроблений заголовок змусить нас рахувати зміщення повз
     * кінець файла — і читати як "дані" будь-що, що лежить далі. */
    uint32_t expected_chunks =
        (hdr->payload_size + UPKG_CHUNK_SIZE - 1u) / UPKG_CHUNK_SIZE;
    if (hdr->chunk_count != expected_chunks) {
        return UPKG_ERR_FORMAT;
    }

    if (hdr->target_hw_id != s->policy.hw_id) {
        return UPKG_ERR_HW_MISMATCH;
    }
    /* Строго "менше або дорівнює": повторний випуск із тим самим номером
     * теж відкат — саме через нього повертають закриту вразливість. */
    if (hdr->version_monotonic <= s->policy.min_version) {
        return UPKG_ERR_ROLLBACK_DETECTED;
    }

    /* Підпис накладено рівно на 128 байтів заголовка. */
    if (!s->crypto.verify(sig, s->policy.root_public_key,
                          (const uint8_t *)hdr, UPKG_HEADER_SIZE)) {
        return UPKG_ERR_SIGNATURE_INVALID;
    }
    return UPKG_OK;
}

/* Фаза 2.5: таблиця хешів — це і є "дерево" пакета. Підписаний заголовок
 * ручається за її хеш, а вона — за кожен окремий сектор. Тому таблицю
 * звіряємо цілком, ще до першого стирання Flash. */
static upkg_status_t verify_hash_table(upkg_session_t *s,
                                       const upkg_header_t *hdr) {
    sha256_ctx_t h;
    sha256_init(&h);

    uint32_t offset = UPKG_TABLE_OFFSET;
    uint32_t left = table_bytes(hdr);
    while (left > 0u) {
        uint32_t n = left < UPKG_CHUNK_SIZE ? left : UPKG_CHUNK_SIZE;
        if (!s->media.read(s->media.ctx, offset, s->chunk_buf, n)) {
            return UPKG_ERR_IO;
        }
        sha256_update(&h, s->chunk_buf, n);
        offset += n;
        left -= n;
    }

    uint8_t digest[UPKG_HASH_SIZE];
    sha256_final(&h, digest);
    if (memcmp(digest, hdr->table_sha256, UPKG_HASH_SIZE) != 0) {
        return UPKG_ERR_TABLE_HASH_MISMATCH;
    }
    return UPKG_OK;
}

/* Фаза 3: потік чанків. У пам'яті одночасно живе рівно один сектор. */
static upkg_status_t stream_chunks(upkg_session_t *s,
                                   const upkg_header_t *hdr,
                                   bool resume,
                                   uint8_t image_hash[UPKG_HASH_SIZE]) {
    sha256_ctx_t image;
    sha256_init(&image);

    const uint32_t data_offset = payload_offset(hdr);

    for (uint32_t i = 0; i < hdr->chunk_count; ++i) {
        uint8_t expected[UPKG_HASH_SIZE];
        uint8_t digest[UPKG_HASH_SIZE];

        if (!s->media.read(s->media.ctx,
                           UPKG_TABLE_OFFSET + i * UPKG_HASH_SIZE,
                           expected, UPKG_HASH_SIZE)) {
            return UPKG_ERR_IO;
        }

        const uint32_t len = chunk_len(hdr, i);
        const uint32_t flash_offset = i * UPKG_CHUNK_SIZE;

        if (resume) {
            /* Продовження після знеструмлення. Сектор, що вже лежить
             * у Slot B і збігається з таблицею, не переписуємо: у нього
             * і так правильні байти, а ресурс NOR не безмежний.
             * Недописаний сектор хеш не пройде — його стираємо точково. */
            if (s->flash.read(s->flash.ctx, flash_offset, s->chunk_buf, len)) {
                sha256_once(s->chunk_buf, len, digest);
                if (memcmp(digest, expected, UPKG_HASH_SIZE) == 0) {
                    sha256_update(&image, s->chunk_buf, len);
                    continue;
                }
            }
            if (!s->flash.erase(s->flash.ctx, flash_offset, UPKG_CHUNK_SIZE)) {
                return UPKG_ERR_FLASH_ERASE;
            }
        }

        if (!s->media.read(s->media.ctx, data_offset + flash_offset,
                           s->chunk_buf, len)) {
            return UPKG_ERR_IO;
        }
        sha256_once(s->chunk_buf, len, digest);
        if (memcmp(digest, expected, UPKG_HASH_SIZE) != 0) {
            return UPKG_ERR_CHUNK_HASH_MISMATCH;
        }
        /* Спершу хеш, і лише потім програмування сектора. */
        if (!s->flash.write(s->flash.ctx, flash_offset, s->chunk_buf, len)) {
            return UPKG_ERR_FLASH_WRITE;
        }
        sha256_update(&image, s->chunk_buf, len);
    }

    sha256_final(&image, image_hash);
    if (memcmp(image_hash, hdr->final_sha256, UPKG_HASH_SIZE) != 0) {
        return UPKG_ERR_FINAL_HASH_MISMATCH;
    }
    return UPKG_OK;
}

/* Фаза 4: квитанція. Пишемо її і після невдачі — технікові потрібен
 * доказ причини, а не мовчазна відмова пристрою. */
static upkg_status_t emit_receipt(upkg_session_t *s,
                                  const upkg_header_t *hdr,
                                  upkg_status_t result,
                                  const uint8_t *image_hash,
                                  upkg_receipt_t *out) {
    memset(out, 0, sizeof(*out));
    out->body.magic = UPKG_RECEIPT_MAGIC;
    out->body.device_serial = s->policy.device_serial;
    out->body.hw_id = s->policy.hw_id;
    out->body.status = (uint16_t)result;
    out->body.version = hdr->version_monotonic;
    out->body.boot_retries = (result == UPKG_OK) ? UPKG_BOOT_RETRIES : 0u;
    if (image_hash != NULL) {
        memcpy(out->body.image_sha256, image_hash, UPKG_HASH_SIZE);
    }

    if (!s->crypto.sign_receipt((const uint8_t *)&out->body,
                                sizeof(out->body), out->signature)) {
        return UPKG_ERR_CRYPTO;
    }
    if (!s->media.write(s->media.ctx, receipt_offset(hdr),
                        (const uint8_t *)out, sizeof(*out))) {
        return UPKG_ERR_IO;
    }
    return UPKG_OK;
}

upkg_status_t upkg_install(upkg_session_t *s, bool resume,
                           upkg_receipt_t *receipt) {
    upkg_header_t hdr;
    uint8_t sig[UPKG_SIG_SIZE];

    upkg_status_t st = upkg_read_header(s, &hdr, sig);
    if (st != UPKG_OK) {
        return st;
    }
    st = upkg_validate_header(s, &hdr, sig);
    if (st != UPKG_OK) {
        /* Пакет чужий або підроблений — квитанції не буде: ми навіть
         * не знаємо, чи ці метадані взагалі стосуються нашого парку. */
        return st;
    }
    st = verify_hash_table(s, &hdr);
    if (st != UPKG_OK) {
        return st;
    }

    /* Пастка "стерли раніше, ніж перевірили". Slot B гине лише тепер,
     * коли підпис випуску і таблиця хешів уже підтверджені: інакше
     * кожен зіпсований файл коштував би плати циклу перезапису. */
    if (!resume &&
        !s->flash.erase(s->flash.ctx, 0, hdr.chunk_count * UPKG_CHUNK_SIZE)) {
        return UPKG_ERR_FLASH_ERASE;
    }

    uint8_t image_hash[UPKG_HASH_SIZE];
    upkg_status_t data_st = stream_chunks(s, &hdr, resume, image_hash);

    if (data_st == UPKG_OK) {
        /* Новій прошивці дається три спроби завантажитися й підтвердити
         * себе; не підтвердить — сторожовий таймер поверне Slot A. */
        upkg_boot_state_t state;
        state.staged_version = hdr.version_monotonic;
        state.flag = UPKG_SLOT_PENDING_VERIFY;
        state.boot_retries = UPKG_BOOT_RETRIES;
        if (!s->nvs_write_state(s->nvs_ctx, &state)) {
            data_st = UPKG_ERR_NVS_WRITE;
        }
    }

    upkg_status_t receipt_st = emit_receipt(
        s, &hdr, data_st, (data_st == UPKG_OK) ? image_hash : NULL, receipt);

    return (data_st != UPKG_OK) ? data_st : receipt_st;
}
