const (
    FLAG      = 0x7E // межа кадру (прапорець HDLC/PPP)
    ESC       = 0x7D // байт екранування
    XORMask   = 0x20 // маска перекручування екранованого байта
    MaxFrame  = 64   // стеля тіла кадру
)

type rxState int

const (
    stWait rxState = iota
    stData
    stEsc
)

type FrameRx struct {
    state rxState
    buf   []byte // скільки байтів уже в buf = len(buf)
}

// згодувати один прийнятий байт; викликати на кожен октет з UART
func (rx *FrameRx) RxByte(b byte) {
    switch rx.state {

    case stWait: // шукаємо початок кадру
        if b == FLAG { // знайшли межу — відкриваємо кадр
            rx.buf = rx.buf[:0]
            rx.state = stData
        }
        // будь-що інше — сміття, мовчки викидаємо (ресинхронізація)

    case stData:
        if b == FLAG { // межа: кадр скінчився
            rx.complete()      // звірити CRC й, якщо ок, віддати
            rx.buf = rx.buf[:0] // готуємось до наступного кадру
            rx.state = stWait
        } else if b == ESC { // далі — екранований байт
            rx.state = stEsc
        } else { // звичайний байт даних
            if len(rx.buf) < MaxFrame {
                rx.buf = append(rx.buf, b)
            } else {
                rx.state = stWait // ПЕРЕПОВНЕННЯ: скидаємо кадр
                rx.buf = rx.buf[:0]
            }
        }

    case stEsc: // попередній байт був ESC
        if b == FLAG { // ESC перед межею — кадр порваний
            rx.state = stWait // відкидаємо, чекаємо нового
            rx.buf = rx.buf[:0]
        } else {
            d := b ^ XORMask // перекрутити назад: 0x5E→0x7E, 0x5D→0x7D
            if len(rx.buf) < MaxFrame {
                rx.buf = append(rx.buf, d)
                rx.state = stData // повертаємось у тіло кадру
            } else {
                rx.state = stWait // переповнення й тут
                rx.buf = rx.buf[:0]
            }
        }
    }
}
