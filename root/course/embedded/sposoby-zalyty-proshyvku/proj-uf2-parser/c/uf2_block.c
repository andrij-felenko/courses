#include "uf2_block.h"

/*
 * Послідовність відсіювань. Порядок не випадковий: спершу найдешевші перевірки
 * сигнатур (їх не проходить абсолютна більшість чужих секторів), і лише потім
 * усе, що вимагає арифметики над адресами.
 */
uf2_status_t uf2_parse_and_validate_block(const uint8_t *sector_buf,
                                          uint32_t       sector_len,
                                          uint32_t       expected_family_id,
                                          uint32_t       flash_start_addr,
                                          uint32_t       flash_size_bytes,
                                          uf2_block_info_t *out_info)
{
    if (sector_buf == NULL || out_info == NULL) {
        return UF2_ERR_NULL_PTR;
    }

    /* Неповний сектор читати не можна: magic_end лежить у самому кінці. */
    if (sector_len < UF2_BLOCK_SIZE) {
        return UF2_ERR_BAD_SECTOR_SIZE;
    }

    const uf2_raw_block_t *blk = (const uf2_raw_block_t *)sector_buf;

    /* 1. Сигнатури: захист від сміття на шині й від чужих даних узагалі. */
    if (blk->magic_start0 != UF2_MAGIC_START0 || blk->magic_start1 != UF2_MAGIC_START1) {
        return UF2_ERR_BAD_MAGIC_START;
    }
    if (blk->magic_end != UF2_MAGIC_END) {
        return UF2_ERR_BAD_MAGIC_END;
    }

    /* Блок навмисно позначено як «не для основної Flash» — мовчки пропускаємо. */
    if ((blk->flags & (UF2_FLAG_NOT_MAIN_FLASH | UF2_FLAG_FILE_CONTAINER)) != 0) {
        out_info->target_address = 0;
        out_info->payload_length = 0;
        out_info->block_index    = blk->block_no;
        out_info->total_blocks   = blk->num_blocks;
        out_info->data_ptr       = NULL;
        return UF2_SKIPPED;
    }

    /* 2. Сімейство кристала: бінарник від сусідньої плати сюди не поїде. */
    if ((blk->flags & UF2_FLAG_FAMILY_ID) != 0 && blk->family_id != expected_family_id) {
        return UF2_ERR_FAMILY_MISMATCH;
    }

    /* 3. Довжина корисного навантаження: захист від виходу за межі data[]. */
    if (blk->payload_size == 0 || blk->payload_size > UF2_MAX_PAYLOAD) {
        return UF2_ERR_PAYLOAD_TOO_LARGE;
    }

    if (blk->num_blocks == 0) {
        return UF2_ERR_TOTAL_BLOCKS_ZERO;
    }
    if (blk->block_no >= blk->num_blocks) {
        return UF2_ERR_BLOCK_INDEX_RANGE;
    }

    /*
     * 4. Діапазон адрес. Додавання рахуємо в 64 бітах: інакше target_addr
     * коло 0xFFFFFFFF переповнюється, сума виявляється маленькою — і перевірка
     * пропускає запис у чужу область.
     */
    uint64_t start = (uint64_t)flash_start_addr;
    uint64_t end   = start + (uint64_t)flash_size_bytes;
    uint64_t lo    = (uint64_t)blk->target_addr;
    uint64_t hi    = lo + (uint64_t)blk->payload_size;
    if (lo < start || hi > end) {
        return UF2_ERR_INVALID_ADDRESS;
    }

    out_info->target_address = blk->target_addr;
    out_info->payload_length = blk->payload_size;
    out_info->block_index    = blk->block_no;
    out_info->total_blocks   = blk->num_blocks;
    out_info->data_ptr       = blk->data;
    return UF2_OK;
}

bool uf2_is_foreign_sector(uf2_status_t status)
{
    return status == UF2_ERR_BAD_MAGIC_START || status == UF2_ERR_BAD_MAGIC_END;
}

const char *uf2_status_str(uf2_status_t status)
{
    switch (status) {
    case UF2_OK:                       return "ok";
    case UF2_SKIPPED:                  return "блок пропущено";
    case UF2_ERR_NULL_PTR:             return "нульовий вказівник";
    case UF2_ERR_BAD_SECTOR_SIZE:      return "неповний сектор";
    case UF2_ERR_BAD_MAGIC_START:      return "немає початкових сигнатур";
    case UF2_ERR_BAD_MAGIC_END:        return "немає кінцевої сигнатури";
    case UF2_ERR_FAMILY_MISMATCH:      return "чуже сімейство кристала";
    case UF2_ERR_PAYLOAD_TOO_LARGE:    return "хибний payloadSize";
    case UF2_ERR_INVALID_ADDRESS:      return "адреса поза межами Flash";
    case UF2_ERR_TOTAL_BLOCKS_ZERO:    return "numBlocks == 0";
    case UF2_ERR_BLOCK_INDEX_RANGE:    return "blockNo поза numBlocks";
    case UF2_ERR_BLOCK_COUNT_MISMATCH: return "різні numBlocks в одному образі";
    case UF2_ERR_IMAGE_TOO_LARGE:      return "образ більший за бітову карту";
    case UF2_ERR_GEOMETRY:             return "адреса поза картою секторів";
    case UF2_ERR_FLASH_ERASE:          return "збій стирання Flash";
    case UF2_ERR_FLASH_WRITE:          return "збій запису Flash";
    }
    return "невідомий стан";
}
