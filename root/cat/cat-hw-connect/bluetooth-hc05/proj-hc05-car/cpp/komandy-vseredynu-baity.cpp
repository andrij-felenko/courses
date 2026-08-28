const int LEFT_MOTOR = 5, RIGHT_MOTOR = 6;   // ШІМ-ніжки моторів (приклад)
int speedLevel = 5;                           // поточна швидкість 0…9

void applyDrive(int leftDir, int rightDir);   // ваша функція: напрям кожного мотора

void handleCommand(char c) {
    switch (c) {
        case 'F': applyDrive(+1, +1); break;   // вперед: обидва мотори вперед
        case 'B': applyDrive(-1, -1); break;   // назад
        case 'L': applyDrive(-1, +1); break;   // поворот: мотори в різні боки
        case 'R': applyDrive(+1, -1); break;
        case 'S': applyDrive( 0,  0); break;   // стоп
        default:
            if (c >= '0' && c <= '9')          // цифра-символ → рівень швидкості
                speedLevel = c - '0';          // '7' - '0' == 7
            break;
    }
}

void loop() {
    while (btSerial.available()) {             // забрати ВСІ накопичені байти
        char c = btSerial.read();
        handleCommand(c);
    }
    // ...тут телеметрія й контроль зв'язку, які додамо нижче...
}
