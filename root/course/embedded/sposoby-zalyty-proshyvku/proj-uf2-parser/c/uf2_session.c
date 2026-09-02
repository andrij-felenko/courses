#include "uf2_session.h"

#include <string.h>

static bool mask_test(const uint32_t *mask, uint32_t bit)
{
    return (mask[bit >> 5] >> (bit & 31u)) & 1u;
}

static void mask_set(uint32_t *mask, uint32_t bit)
{
    mask[bit >> 5] |= (1u << (bit & 31u));
}

void uf2_session_init(uf2_session_t *s,
                      uint32_t       family_id,
                      uint32_t       flash_start,
                      uint32_t       flash_size)
{
    memset(s, 0, sizeof(*s));
    s->family_id   = family_id;
    s->flash_start = flash_start;
    s->flash_size  = flash_size;
}

/*
 * Стирання «за першим дотиком». Наївне правило «стерти, коли target_addr
 * кратна 4096» ламається саме тому, про що йдеться в статті: хост шле сектори
 * у довільному порядку, і вирівняний блок може приїхати ОСТАННІМ — стирання
 * тоді знищить п'ятнадцять уже записаних сусідів. Тому пам'ятаємо, які
 * 4-кілобайтні сектори вже стерті в цьому сеансі, і кожен чіпаємо один раз.
 */
static uf2_status_t ensure_erased(uf2_session_t *s, uint32_t addr, uint32_t len)
{
    uint32_t first = (addr - s->flash_start) / UF2_FLASH_SECTOR_SIZE;
    uint32_t last  = (addr + len - 1u - s->flash_start) / UF2_FLASH_SECTOR_SIZE;

    for (uint32_t i = first; i <= last; ++i) {
        if (i >= UF2_MAX_SECTORS) {
            return UF2_ERR_GEOMETRY;
        }
        if (mask_test(s->erased_mask, i)) {
            continue;
        }
        if (!uf2_flash_erase_sector(s->flash_start + i * UF2_FLASH_SECTOR_SIZE)) {
            return UF2_ERR_FLASH_ERASE;
        }
        mask_set(s->erased_mask, i);
    }
    return UF2_OK;
}

/* Відмітка блоку в карті; повторний приїзд того самого блоку не рахується двічі. */
static void mark_handled(uf2_session_t *s, uint32_t index)
{
    if (!mask_test(s->block_mask, index)) {
        mask_set(s->block_mask, index);
        s->handled_blocks++;
    }
}

uf2_status_t uf2_session_accept_sector(uf2_session_t *s,
                                       const uint8_t *sector,
                                       uint32_t       sector_len)
{
    uf2_block_info_t info;
    uf2_status_t st = uf2_parse_and_validate_block(sector, sector_len, s->family_id,
                                                   s->flash_start, s->flash_size, &info);
    if (st != UF2_OK && st != UF2_SKIPPED) {
        return st;
    }

    if (info.total_blocks > UF2_MAX_BLOCKS) {
        return UF2_ERR_IMAGE_TOO_LARGE;
    }

    /*
     * Перший блок задає розмір образу. Якщо далі приїде блок із іншим
     * numBlocks — на диск копіюють два різні файли .uf2 одночасно, і змішувати
     * їх в один образ не можна.
     */
    if (s->total_blocks == 0) {
        s->total_blocks = info.total_blocks;
    } else if (s->total_blocks != info.total_blocks) {
        return UF2_ERR_BLOCK_COUNT_MISMATCH;
    }

    if (st == UF2_SKIPPED) {
        /* Блок не для Flash, але у numBlocks він порахований — інакше сеанс не завершиться. */
        mark_handled(s, info.block_index);
        return UF2_SKIPPED;
    }

    st = ensure_erased(s, info.target_address, info.payload_length);
    if (st != UF2_OK) {
        return st;
    }

    /*
     * Повторний запис того самого блоку безпечний: дані ті самі, а програмування
     * NOR лише скидає біти в нуль. Хост іноді пересилає сектор після таймауту.
     */
    if (!uf2_flash_program(info.target_address, info.data_ptr, info.payload_length)) {
        return UF2_ERR_FLASH_WRITE;
    }

    mark_handled(s, info.block_index);
    return UF2_OK;
}

bool uf2_session_complete(const uf2_session_t *s)
{
    return s->total_blocks != 0 && s->handled_blocks == s->total_blocks;
}
