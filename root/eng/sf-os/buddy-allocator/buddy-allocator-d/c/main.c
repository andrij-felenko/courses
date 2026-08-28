/* Базові операції двійкового розщеплення та злиття мовою C */
uintptr_t buddy_find_twin(uintptr_t offset, uint8_t order) {
    return offset ^ ((uintptr_t)1 << order);
}

uintptr_t buddy_find_parent(uintptr_t offset, uint8_t order) {
    return offset & ~((uintptr_t)1 << order);
}

/* Перевірка можливості злиття двох блоків */
bool buddy_can_coalesce(const block_tag_t *tags, uintptr_t buddy_idx, uint8_t order) {
    return tags[buddy_idx].is_free && (tags[buddy_idx].order == order);
}
