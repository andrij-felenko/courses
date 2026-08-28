void* pool_alloc_atomic(fixed_pool_t* pool) {
    void* head;
    void* next;
    do {
        /* Ексклюзивне завантаження адреси голови списку */
        head = (void*)__LDREXW((uint32_t*)&pool->free_list);
        if (!head) {
            __CLREX();
            return NULL; /* Пул порожній */
        }
        next = *(void**)head;
        /* Спроба ексклюзивного запису: повертає 0 при успіху, 1 якщо відбулося переривання */
    } while (__STREXW((uint32_t)next, (uint32_t*)&pool->free_list) != 0);

    return head;
}
