int cursorX = 64, cursorY = 32;         // поточна позиція (напр. пікселі дисплея)

void moveCursor() {
    int vx = readAxis(horizontal);      // −100..+100
    int vy = readAxis(vertical);

    // швидкість у «пікселів за крок»: 100 на осі → 5 пікселів за виклик
    cursorX += vx / 20;
    cursorY += vy / 20;

    // не давати курсору втекти за межі екрана 128×64
    cursorX = constrain(cursorX, 0, 127);
    cursorY = constrain(cursorY,  0,  63);
}
