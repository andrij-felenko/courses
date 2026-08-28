// Гасимо ключ навантаження і ПЕРЕКОНУЄМОСЯ, що вихід зник.
// Якщо на виході чуже живлення, body-діод тримає напругу — і ми це побачимо.
digitalWrite(LOAD_EN, LOW);          // закрили канал ключа
delay(10);                            // даємо ємності стекти

int raw = analogRead(VOUT_SENSE);            // дільник із виходу ключа
int mv  = (int)((long)raw * 5000L / 1023L);  // АЦП 10 біт, опора 5 В
if (mv > VOUT_OFF_THRESHOLD_MV) {
    // канал закритий, а напруга лишилась → тече крізь body-діод (зворотне живлення)
    // повне відключення тут потребує ключа з reverse current blocking
    Serial.print(F("vyhid ne znyksya, mV: "));
    Serial.println(mv);
}
