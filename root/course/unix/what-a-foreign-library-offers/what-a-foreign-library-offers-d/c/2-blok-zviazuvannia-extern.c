#if defined (__cplusplus)
extern "C" {
#endif

/* Оголошення функцій C API без викривлення імен */
size_t ZSTD_compress(void* dst, size_t dstCapacity, const void* src, size_t srcSize, int compressionLevel);

#if defined (__cplusplus)
}
#endif
