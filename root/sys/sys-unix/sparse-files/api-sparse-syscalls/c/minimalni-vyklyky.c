/* Пробити діру: 1 МіБ, починаючи зі зсуву 4096. */
if (fallocate(fd, FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE, 4096, 1 << 20) < 0) {
    if (errno == EOPNOTSUPP) {
        /* ФС не вміє: або лишаємо як є, або чесно пишемо нулі */
    } else {
        perror("punch");
    }
}

/* Зарезервувати 4 ГіБ під файл, щоб запис у них уже не впав з ENOSPC. */
if (fallocate(fd, 0, 0, 4ULL << 30) < 0)
    perror("preallocate");
