// Два робочих буфери на весь конвеєр — більше не потрібно.
static uint8_t buf_a[H][W];
static uint8_t buf_b[H][W];

// Відкриття: src → (ерозія) tmp → (дилатація) dst.  tmp ≠ src, tmp ≠ dst.
void opening3(const uint8_t src[H][W], uint8_t dst[H][W], uint8_t tmp[H][W]) {
    erode3(src, tmp);
    dilate3(tmp, dst);
}

// Закриття: src → (дилатація) tmp → (ерозія) dst.
void closing3(const uint8_t src[H][W], uint8_t dst[H][W], uint8_t tmp[H][W]) {
    dilate3(src, tmp);
    erode3(tmp, dst);
}
