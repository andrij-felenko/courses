#include <stdint.h>
#include <stdbool.h>

/* --- keypad_begin / keypad_scan_raw / keypad_char / keypad_read — з кроків 1..4 --- */

void setup(void)
{
    Serial.begin(115200);
    keypad_begin();          // ніжки: рядки INPUT_PULLUP, стовпці OUTPUT=HIGH
}

void loop(void)
{
    char key;
    if (keypad_read(&key)) { // з'явився свіжий натиск?
        Serial.print("натиснуто: ");
        Serial.println(key);
        // тут — своя реакція: додати цифру до PIN, зрушити меню, ввести число…
    }
    // loop крутиться швидко й вільно; скан коштує лічені мікросекунди на прохід
}
