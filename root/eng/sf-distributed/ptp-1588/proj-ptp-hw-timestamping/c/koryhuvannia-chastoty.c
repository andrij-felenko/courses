struct timex tx;
memset(&tx, 0, sizeof(tx));
tx.modes = ADJ_FREQUENCY;

// Змінити частоту на +15.4 ppb (частин на мільярд)
double ppb_adjustment = 15.4;
tx.freq = (long)(ppb_adjustment * 65.536);

if (clock_adjtime(clkid, &tx) < 0) {
    perror("clock_adjtime ADJ_FREQUENCY failed");
}
