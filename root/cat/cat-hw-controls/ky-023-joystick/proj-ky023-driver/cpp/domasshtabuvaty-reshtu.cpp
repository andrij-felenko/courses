// Сире число осі → −100..+100 із мертвою зоною біля нуля.
int readAxis(const Axis &a) {
    int raw = analogRead(a.pin);
    int d   = raw - a.center;                  // відхилення від центру, знакове

    // 1) мертва зона: близько до центру — це строгий нуль
    if (d > -a.deadzone && d < a.deadzone) return 0;

    int out;
    if (d > 0) {
        // додатний бік: від краю мертвої зони до верхнього краю ходу
        out = map(d, a.deadzone, a.hi - a.center, 0, 100);
    } else {
        // від'ємний бік: від краю мертвої зони до нижнього краю ходу
        out = map(d, -a.deadzone, a.lo - a.center, 0, -100);
    }

    out = constrain(out, -100, 100);           // не вилазити за діапазон
    return a.invert ? -out : out;              // 3) інверсія осі, якщо треба
}
