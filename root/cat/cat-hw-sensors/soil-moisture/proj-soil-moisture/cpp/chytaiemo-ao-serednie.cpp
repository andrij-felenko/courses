const uint8_t SOIL = A0;

int median9() {
    int a[9];
    for (int i = 0; i < 9; i++) {         // набрали 9 відліків
        a[i] = analogRead(SOIL);
        delay(2);                          // коротка пауза між читаннями АЦП
    }
    // проста бульбашка — на 9 елементах це миттєво
    for (int i = 0; i < 8; i++)
        for (int j = 0; j < 8 - i; j++)
            if (a[j] > a[j + 1]) { int t = a[j]; a[j] = a[j + 1]; a[j + 1] = t; }
    return a[4];                           // середнє за порядком число з 9
}
