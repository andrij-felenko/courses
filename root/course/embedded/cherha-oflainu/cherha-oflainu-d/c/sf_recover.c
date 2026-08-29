#include "sf_recover.h"

#include <string.h>

#include "sf_frame.h"

typedef struct {
    bool     used;
    bool     damaged;    /* перший же кадр сектора не пройшов перевірку */
    bool     torn;       /* валідні кадри є, але останній обірвано */
    uint32_t frames;
    uint32_t first_seq;
    uint32_t last_seq;
    uint32_t end_offset; /* кінець останнього валідного кадру в секторі */
} sector_info_t;

/* Кадр ніколи не перетинає межу сектора — інакше одне стирання рвало б
 * два записи, а сканер не міг би йти посекторно. Тому сектор читається
 * незалежно від сусідів, і пошкодження локалізоване. */
static int scan_sector(const sf_ring_t *ring, uint32_t index, sector_info_t *info)
{
    uint8_t buf[SF_MAX_FRAME];

    memset(info, 0, sizeof(*info));

    const uint32_t base = index * ring->sector_size;
    uint32_t off = 0;

    while (off + SF_HDR_SIZE + SF_CRC_SIZE <= ring->sector_size) {
        size_t want = ring->sector_size - off;
        if (want > sizeof(buf)) {
            want = sizeof(buf);
        }
        if (ring->read(ring->ctx, base + off, buf, want) != 0) {
            return -1;
        }

        sf_hdr_t hdr;
        size_t   total = 0;
        const sf_status_t st = sf_parse(buf, want, &hdr, &total);

        if (st == SF_OK) {
            if (info->frames == 0) {
                info->first_seq = hdr.seq;
            }
            info->last_seq = hdr.seq;
            info->frames++;
            off += (uint32_t)total;
            continue;
        }

        /* Стерта область — нормальний кінець сектора. Будь-яка інша
         * помилка означає, що живлення зникло під час запису або
         * комірки деградували; за таким місцем сканування не йде:
         * далі в секторі лежить сміття з попереднього циклу. */
        if (st != SF_ERR_ERASED) {
            if (info->frames == 0) {
                info->damaged = true;
            } else {
                info->torn = true;
            }
        }
        break;
    }

    info->end_offset = off;
    info->used = (info->frames > 0);
    return 0;
}

int sf_recover(const sf_ring_t *ring, sf_state_t *out)
{
    if (ring == NULL || out == NULL || ring->read == NULL) {
        return -1;
    }
    if (ring->sector_count == 0 || ring->sector_size < SF_HDR_SIZE + SF_CRC_SIZE) {
        return -1;
    }

    memset(out, 0, sizeof(*out));
    out->empty = true;
    out->next_seq = 1;

    sector_info_t head_info;
    memset(&head_info, 0, sizeof(head_info));
    bool found = false;

    for (uint32_t i = 0; i < ring->sector_count; i++) {
        sector_info_t info;
        if (scan_sector(ring, i, &info) != 0) {
            return -1;
        }

        if (info.damaged) {
            out->damaged_sectors++;
        }
        if (!info.used) {
            continue;
        }

        out->valid_frames += info.frames;

        if (!found) {
            found = true;
            head_info        = info;
            out->head_sector = i;
            out->tail_sector = i;
            out->tail_seq    = info.first_seq;
            continue;
        }

        /* Голова — сектор із найбільшим номером кадру, хвіст — із
         * найменшим. Порядок індексів тут ні до чого: після обороту
         * кільця голова має менший індекс, ніж хвіст. */
        if (sf_seq_after(info.last_seq, head_info.last_seq)) {
            head_info        = info;
            out->head_sector = i;
        }
        if (sf_seq_after(out->tail_seq, info.first_seq)) {
            out->tail_sector = i;
            out->tail_seq    = info.first_seq;
        }
    }

    if (!found) {
        return 0; /* порожнє кільце: пишемо з нуля, seq починається з 1 */
    }

    out->empty       = false;
    out->head_offset = head_info.end_offset;
    out->torn_tail   = head_info.torn;

    /* Голова стає строго за останнім валідним кадром. Обірваний хвіст
     * запису нікуди не дівається — його накриють наступні байти після
     * чергового стирання сектора, а в мережу він не потрапить ніколи. */
    out->next_seq = head_info.last_seq + 1;
    if (out->next_seq == 0) {
        out->next_seq = 1; /* нуль лишаємо як «номера немає» */
    }

    return 0;
}
