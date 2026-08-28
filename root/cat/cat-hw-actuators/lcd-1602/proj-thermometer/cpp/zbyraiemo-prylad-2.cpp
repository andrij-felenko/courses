// Показати температуру в полі, що починається з (col=6, row=0)
void showTemp(float t) {
    lcd.setCursor(6, 0);
    lcd.print(t, 1);             // один знак після коми: "23.5"
    lcd.write(byte(0));          // символ градуса з комірки №0
    lcd.print("C ");             // "C" і пробіл-затирач хвоста старого числа
}

// Показати час роботи як MM:SS у полі з (col=8, row=1)
void showUptime(uint32_t seconds) {
    uint16_t mm = seconds / 60;
    uint8_t  ss = seconds % 60;
    lcd.setCursor(8, 1);
    if (mm < 10) lcd.print('0');
    lcd.print(mm);
    lcd.print(':');
    if (ss < 10) lcd.print('0');
    lcd.print(ss);
}
