// Надіслати повний байт: старший напівбайт, тоді молодший
//   isData = false → команда (RS=0);  isData = true → символ (RS=1)
void sendByte(uint8_t b, bool isData) {
    digitalWrite(PIN_RS, isData ? HIGH : LOW);

    putNibble(b >> 4);     // старші 4 біти
    pulseE();
    putNibble(b & 0x0F);   // молодші 4 біти
    pulseE();
}

// Зручні обгортки — рівно те, що всередині робить бібліотека
void lcdCommand(uint8_t c) { sendByte(c, false); }   // RS=0
void lcdData(uint8_t d)    { sendByte(d, true);  }   // RS=1
