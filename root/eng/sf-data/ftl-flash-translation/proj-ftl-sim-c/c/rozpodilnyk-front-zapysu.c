static void push_free(uint32_t b) { freelist[freetop++] = b; }
static uint32_t pop_free(void)    { return freelist[--freetop]; }

// Наступна фізична сторінка з фронту запису.
static uint32_t alloc_page(void) {
    if (wpage == PPB) {             // поточний блок дописано вщерть
        wblk = pop_free();          // беремо наступний стертий блок
        wpage = 0;
    }
    return wblk * PPB + wpage++;
}
