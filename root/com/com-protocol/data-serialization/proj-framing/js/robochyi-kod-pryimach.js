const FLAG = 0x7E;      // межа кадру (прапорець HDLC/PPP)
const ESC  = 0x7D;      // байт екранування
const XOR  = 0x20;      // маска перекручування екранованого байта
const MAX_FRAME = 64;   // стеля тіла кадру

const ST_WAIT = 0, ST_DATA = 1, ST_ESC = 2;

class FrameRx {
  constructor() {
    this.state = ST_WAIT;
    this.buf = [];            // скільки байтів уже в buf = this.buf.length
  }

  // згодувати один прийнятий байт; викликати на кожен октет з UART
  rxByte(b) {
    switch (this.state) {

      case ST_WAIT:                       // шукаємо початок кадру
        if (b === FLAG) {                 // знайшли межу — відкриваємо кадр
          this.buf.length = 0;
          this.state = ST_DATA;
        }
        // будь-що інше — сміття, мовчки викидаємо (ресинхронізація)
        break;

      case ST_DATA:
        if (b === FLAG) {                 // межа: кадр скінчився
          this._complete();               // звірити CRC й, якщо ок, віддати
          this.buf.length = 0;            // готуємось до наступного кадру
          this.state = ST_WAIT;
        } else if (b === ESC) {           // далі — екранований байт
          this.state = ST_ESC;
        } else {                          // звичайний байт даних
          if (this.buf.length < MAX_FRAME) {
            this.buf.push(b);
          } else {
            this.state = ST_WAIT;         // ПЕРЕПОВНЕННЯ: скидаємо кадр
            this.buf.length = 0;
          }
        }
        break;

      case ST_ESC:                        // попередній байт був ESC
        if (b === FLAG) {                 // ESC перед межею — кадр порваний
          this.state = ST_WAIT;           // відкидаємо, чекаємо нового
          this.buf.length = 0;
        } else {
          const d = b ^ XOR;              // перекрутити назад: 0x5E→0x7E, 0x5D→0x7D
          if (this.buf.length < MAX_FRAME) {
            this.buf.push(d);
            this.state = ST_DATA;         // повертаємось у тіло кадру
          } else {
            this.state = ST_WAIT;         // переповнення й тут
            this.buf.length = 0;
          }
        }
        break;
    }
  }
}
