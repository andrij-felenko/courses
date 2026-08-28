// Великий кеш зображень — явно у PSRAM:
uint8_t *cache = heap_caps_malloc(512 * 1024, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);

// Маленький, гарячий, критичний за часом буфер — явно у внутрішній SRAM:
uint8_t *hot = heap_caps_malloc(2 * 1024, MALLOC_CAP_INTERNAL | MALLOC_CAP_8BIT);

if (cache == NULL || hot == NULL) {
    ESP_LOGE(TAG, "бракує пам'яті під буфери");
    // тут — чесна обробка браку, а не мовчазне «якось працюватиме»
}
// звільняють обидва звичайним free()
