// Гасимо ключ і ПЕРЕКОНУЄМОСЯ, що вихід зник.
// Одинарний ключ: якщо на виході чуже живлення, body-діод тримає напругу.
digitalWrite(SWITCH_EN, LOW);                 // закрили канал
delay(10);                                    // даємо ємності стекти

int raw = analogRead(VOUT_SENSE);             // дільник із виходу ключа
int mv  = (int)((long)raw * 5000L / 1023L);   // АЦП 10 біт, опора 5 В
if (mv > VOUT_OFF_THRESHOLD_MV) {
    // канал закрито, а напруга є → тече крізь body-діод (зворотне живлення)
    // справжнє відключення тут потребує пари спина-до-спини або true-RCB ключа
    Serial.print(F("vyhid ne znyksya, mV: "));
    Serial.println(mv);
}
