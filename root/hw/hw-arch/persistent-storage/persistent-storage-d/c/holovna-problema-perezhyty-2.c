int active_slot(void) {
    Record a, b;
    bool ok_a = read_slot(0, &a) && crc_ok(&a);  // цілий і сума збіглась?
    bool ok_b = read_slot(1, &b) && crc_ok(&b);

    if (ok_a && ok_b) return (a.seq > b.seq) ? 0 : 1;  // обидва цілі — новіший
    if (ok_a) return 0;    // цілий лише слот 0
    if (ok_b) return 1;    // цілий лише слот 1
    return -1;             // обидва биті — перший старт або лихо
}
