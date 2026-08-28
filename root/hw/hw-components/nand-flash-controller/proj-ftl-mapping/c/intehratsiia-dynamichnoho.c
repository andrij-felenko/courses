static int32_t ftl_find_best_free_block(const ftl_controller_t *ftl) {
    int32_t best_block = -1;
    uint32_t min_erase = UINT32_MAX;

    for (uint32_t b = 0; b < NUM_BLOCKS; b++) {
        if (b == ftl->active_block_id) continue;
        if (ftl->blocks[b].free_page_idx == 0 && ftl->blocks[b].valid_count == 0) {
            if (ftl->blocks[b].erase_count < min_erase) {
                min_erase = ftl->blocks[b].erase_count;
                best_block = (int32_t)b;
            }
        }
    }
    return best_block;
}
