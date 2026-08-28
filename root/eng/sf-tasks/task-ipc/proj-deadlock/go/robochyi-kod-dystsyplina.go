// два спільні ресурси, кожен під своїм м'ютексом
var spiMtx, sdMtx sync.Mutex

// ✗ НЕБЕЗПЕЧНО: горутини беруть замки в РІЗНОМУ порядку → можливий дедлок
func taskA() {                     // A: spi, потім sd
    for {
        spiMtx.Lock()
        sdMtx.Lock()               // ← чекає на sd, тримаючи spi
        drawAndLog()
        sdMtx.Unlock()
        spiMtx.Unlock()
        time.Sleep(20 * time.Millisecond)
    }
}
func taskB() {                     // B: sd, потім spi  ← ПРОТИЛЕЖНИЙ порядок!
    for {
        sdMtx.Lock()
        spiMtx.Lock()              // ← кільце замикається тут
        logAndDraw()
        spiMtx.Unlock()
        sdMtx.Unlock()
        time.Sleep(20 * time.Millisecond)
    }
}
