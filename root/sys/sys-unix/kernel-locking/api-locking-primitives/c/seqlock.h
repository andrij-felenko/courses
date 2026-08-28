/* послідовний замок — linux/seqlock.h */
DEFINE_SEQLOCK(sl);                    seqlock_init(&sl);

unsigned seq;                           /* читач */
do {
    seq = read_seqbegin(&sl);
    /* тут читаємо — і НІЧОГО не робимо з прочитаним */
} while (read_seqretry(&sl, seq));

write_seqlock(&sl);   /* письменник: бере вбудований спін-замок */
write_sequnlock(&sl);
/* із суфіксами: write_seqlock_bh / _irq / _irqsave — правила ті самі, що в spin_lock */
read_seqlock_excl(&sl);   /* читач, який не хоче повторювати: бере той самий спін-замок */
