#define WELD_PIN        12       // затвор силового MOSFET-ключа
#define PULSE1_US     1500       // «пробити»: 1.5 мс
#define GAP_US        3000       // пауза між імпульсами: 3 мс
#define PULSE2_US     5000       // «зварити»: 5 мс

void fire_weld(void)
{
    // перший імпульс — притерти контакт, пробити оксид
    digitalWrite(WELD_PIN, HIGH);
    delayMicroseconds(PULSE1_US);
    digitalWrite(WELD_PIN, LOW);

    // пауза: метал трохи стухає, оксид уже продавлено
    delayMicroseconds(GAP_US);

    // другий імпульс — робоча порція тепла, сплав ядра
    digitalWrite(WELD_PIN, HIGH);
    delayMicroseconds(PULSE2_US);
    digitalWrite(WELD_PIN, LOW);
}
