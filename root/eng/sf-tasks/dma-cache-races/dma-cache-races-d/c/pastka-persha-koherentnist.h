/* Приймання (периферія → пам'ять → ядро): invalidate ПЕРЕД читанням */

// 1. Запустити приймання по DMA в buf
dma_start_receive(buf, BUF_SIZE);

// 2. Дочекатися завершення DMA (переривання / семафор)
xSemaphoreTake(sem_ready, portMAX_DELAY);

// 3. Інвалідувати кеш: наступне читання піде в пам'ять, не в кеш
esp_cache_msync(buf, BUF_SIZE, ESP_CACHE_MSYNC_FLAG_DIR_M2C);

// 4. Читати buf — ядро бачить актуальне з пам'яті
process_block(buf, BUF_SIZE);


/* Передавання (ядро → пам'ять → периферія): write-back ПЕРЕД стартом DMA */

// 1. Заповнити buf
fill_frame(buf, BUF_SIZE);

// 2. Write-back: виштовхнути «брудні» рядки кешу в пам'ять
esp_cache_msync(buf, BUF_SIZE, ESP_CACHE_MSYNC_FLAG_DIR_C2M);

// 3. Запускати DMA — він побачить у пам'яті актуальне
dma_start_send(buf, BUF_SIZE);
