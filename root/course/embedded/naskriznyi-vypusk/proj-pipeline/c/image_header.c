#include "image_header.h"

const char *release_status_text(release_status_t status)
{
    switch (status) {
    case RELEASE_OK:             return "образ прийнято";
    case RELEASE_ERR_TRUNCATED:  return "образ обірваний";
    case RELEASE_ERR_ALIGNMENT:  return "буфер не вирівняний на 4 байти";
    case RELEASE_ERR_MAGIC:      return "чуже магічне число";
    case RELEASE_ERR_HARDWARE:   return "прошивка не для цієї ревізії плати";
    case RELEASE_ERR_ROLLBACK:   return "відкат на застарілу версію";
    case RELEASE_ERR_SIZE:       return "тіло не влазить у слот застосунку";
    case RELEASE_ERR_DIGEST:     return "хеш тіла не збігся";
    case RELEASE_ERR_SIGNATURE:  return "підпис не від кореня довіри";
    case RELEASE_ERR_CRYPTO:     return "збій криптографічного модуля";
    default:                     return "невідомий стан";
    }
}

void release_version_unpack(uint32_t packed, uint8_t out[3])
{
    out[0] = (uint8_t)((packed >> 24) & 0xFFu);
    out[1] = (uint8_t)((packed >> 16) & 0xFFu);
    out[2] = (uint8_t)((packed >> 8) & 0xFFu);
}

release_status_t release_header_parse(const uint8_t *image,
                                      size_t image_len,
                                      uint32_t active_counter,
                                      uint32_t max_payload,
                                      const release_header_t **out_header)
{
    if (out_header != NULL) {
        *out_header = NULL;
    }
    if (image == NULL || image_len < RELEASE_HEADER_SIZE) {
        return RELEASE_ERR_TRUNCATED;
    }

    /* Заголовок читаємо на місці, тож буфер завантаження мусить лежати
       на 4-байтній межі: інакше перше ж звертання до uint32 на Cortex-M
       з увімкненим UNALIGN_TRP дасть HardFault. */
    if (((uintptr_t)image & 3u) != 0u) {
        return RELEASE_ERR_ALIGNMENT;
    }

    const release_header_t *hdr = (const release_header_t *)(const void *)image;

    if (hdr->magic != RELEASE_MAGIC) {
        return RELEASE_ERR_MAGIC;
    }

    /* Бітова маска, а не рівність: один образ може бути придатний
       кільком ревізіям одразу. */
    if ((hdr->hw_mask & RELEASE_CURRENT_HW_MASK) == 0u) {
        return RELEASE_ERR_HARDWARE;
    }

    if (hdr->security_counter < active_counter) {
        return RELEASE_ERR_ROLLBACK;
    }

    if (hdr->payload_size == 0u || hdr->payload_size > max_payload) {
        return RELEASE_ERR_SIZE;
    }

    /* Порівнюємо відніманням, а не сумою: image_len + payload_size
       переповнилося б і пропустило обірваний образ. */
    if (image_len - RELEASE_HEADER_SIZE < (size_t)hdr->payload_size) {
        return RELEASE_ERR_TRUNCATED;
    }

    if (out_header != NULL) {
        *out_header = hdr;
    }
    return RELEASE_OK;
}
