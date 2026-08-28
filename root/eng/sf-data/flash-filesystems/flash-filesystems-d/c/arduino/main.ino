#include <LittleFS.h>

void setup() {
  Serial.begin(115200);

  // Змонтувати; true — відформатувати, якщо тому ще немає (перший запуск).
  if (!LittleFS.begin(true)) {
    Serial.println("LittleFS: монтування не вдалося");
    return;
  }

  // FILE_APPEND — відкрити на ДОПИСУВАННЯ: новий текст лягає в кінець,
  // старі рядки лишаються недоторкані (на відміну від FILE_WRITE, що затирає).
  File f = LittleFS.open("/log.txt", FILE_APPEND);
  if (!f) {
    Serial.println("не відкрити /log.txt на запис");
    return;
  }
  f.println("08:01  старт");
  f.println("08:05  кнопка");
  f.close();                       // тільки після close() дані напевно на Flash

  // Прочитати весь файл від початку до кінця.
  f = LittleFS.open("/log.txt", FILE_READ);
  while (f.available()) {
    Serial.write(f.read());
  }
  f.close();
}

void loop() {}
