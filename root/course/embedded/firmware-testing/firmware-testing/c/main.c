// логіка — про залізо не знає нічого:
bool pump_on(int level, bool alarm) {
    return level > 0 && !alarm;
}

// тест на хості — звичайна програма на ПК:
assert( pump_on(50, false) == true  );   // бак повний, тривоги нема → так
assert( pump_on( 0, false) == false );   // бак порожній → ні
assert( pump_on(50, true ) == false );   // аварія → ні попри повний бак
assert( pump_on( 0, true ) == false );   // обидві біди → точно ні
