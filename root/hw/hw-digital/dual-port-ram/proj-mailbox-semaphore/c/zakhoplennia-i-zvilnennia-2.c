// Зачекати замок, але не довше за budget спроб. Повертає false, якщо не дочекались.
// Між спробами — коротка пауза, щоб дати іншому ядру шанс віддати замок.
static bool sem_lock_timeout(volatile uint8_t *sem, uint32_t budget)
{
    while (budget--) {
        if (sem_try_lock(sem))
            return true;         // взяли
        cpu_relax();             // дрібна пауза/підказка ядру; НЕ довге sleep
    }
    return false;                // не дочекались — хай викликач вирішує, що робити
}
