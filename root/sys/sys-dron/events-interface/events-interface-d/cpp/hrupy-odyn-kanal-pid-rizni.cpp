// перевірки готовності мають свій екран, а не стрічку повідомлень
if (event->group() == "health" || event->group() == "arming_check") {
    return;
}
if (event->group() == "calibration") {
    return;
}
if (event->group() != "default" || severity == -1) {
    return;
}
