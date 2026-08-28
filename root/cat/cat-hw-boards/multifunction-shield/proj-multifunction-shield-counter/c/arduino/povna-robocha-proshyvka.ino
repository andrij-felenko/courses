#include <MultiFuncShield.h>

int counter = 0;   // поточне значення лічильника

void setup() {
  MFS.initialize();       // виводи + фонове переривання (дисплей, кнопки, звук)
  MFS.write(counter);     // одразу показати початкове значення
}

void loop() {
  byte btn = MFS.getButton();   // забрати одну подію з черги (0 — якщо порожньо)

  switch (btn) {

    case BUTTON_1_SHORT_RELEASE:   // S1 коротко: +1
      counter++;
      MFS.write(counter);          // оновити дисплей
      MFS.beep();                  // короткий відгук
      break;

    case BUTTON_2_SHORT_RELEASE:   // S2 коротко: −1
      counter--;
      MFS.write(counter);
      MFS.beep();
      break;

    case BUTTON_1_LONG_PRESSED:    // S1 тримають: швидко біжить угору
      counter++;
      MFS.write(counter);
      break;

    case BUTTON_2_LONG_PRESSED:    // S2 тримають: швидко біжить униз
      counter--;
      MFS.write(counter);
      break;

    case BUTTON_3_LONG_RELEASE:    // S3 утримати й відпустити: скинути в нуль
      counter = 0;
      MFS.write(counter);
      MFS.beep(200, 0, 1);         // довший писк — «скинуто»
      break;
  }

  // світлодіод-індикатор: горить, поки число від'ємне
  MFS.writeLeds(LED_1, counter < 0 ? ON : OFF);
}
