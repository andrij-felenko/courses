// ✓ БЕЗПЕЧНО: ЄДИНИЙ порядок для ВСІХ — завжди spiMtx ПЕРЕД sdMtx
//   (домовленість, що рве умову №4 «кругове очікування»)
func takeBoth() {                  // спільний хелпер — один порядок на весь код
    spiMtx.Lock()                  // 1) завжди spi
    sdMtx.Lock()                   // 2) потім sd
}
func giveBoth() {                  // віддаємо у ЗВОРОТНОМУ порядку
    sdMtx.Unlock()
    spiMtx.Unlock()
}
// тепер і taskA, і taskB викликають takeBoth()/giveBoth() — кільце неможливе
