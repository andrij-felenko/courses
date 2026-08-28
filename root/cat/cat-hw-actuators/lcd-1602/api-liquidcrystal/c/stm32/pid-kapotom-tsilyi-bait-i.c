// Надіслати повний байт: старший напівбайт, тоді молодший
//   is_data = false → команда (RS=0);  is_data = true → символ (RS=1)
static void send_byte(uint8_t b, bool is_data) {
    HAL_GPIO_WritePin(LCD_RS_PORT, LCD_RS_PIN,
                      is_data ? GPIO_PIN_SET : GPIO_PIN_RESET);

    put_nibble(b >> 4);    // старші 4 біти
    pulse_e();
    put_nibble(b & 0x0F);  // молодші 4 біти
    pulse_e();
}

// Зручні обгортки — саме їх викликає решта драйвера
static void lcd_command(uint8_t c) { send_byte(c, false); }   // RS=0
static void lcd_data(uint8_t d)    { send_byte(d, true);  }   // RS=1
