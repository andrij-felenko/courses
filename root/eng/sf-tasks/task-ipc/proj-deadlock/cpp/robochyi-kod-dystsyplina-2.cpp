// ✓ БЕЗПЕЧНО: ЄДИНИЙ порядок для ВСІХ — завжди spiMtx ПЕРЕД sdMtx
//   (домовленість, що рве умову №4 «кругове очікування»)
void takeBoth() {                  // спільний хелпер — один порядок на весь код
    xSemaphoreTake(spiMtx, portMAX_DELAY);   // 1) завжди spi
    xSemaphoreTake(sdMtx,  portMAX_DELAY);   // 2) потім sd
}
void giveBoth() {                  // віддаємо у ЗВОРОТНОМУ порядку
    xSemaphoreGive(sdMtx);
    xSemaphoreGive(spiMtx);
}
// тепер і taskA, і taskB викликають takeBoth()/giveBoth() — кільце неможливе
