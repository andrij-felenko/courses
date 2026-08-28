/* Створення гарантовано безпечного тимчасового файлу */
int fd = open("/tmp/scratchpad.tmp", O_RDWR | O_CREAT | O_EXCL, 0600);
if (fd >= 0) {
    /* Негайне видалення імені з каталогу! */
    unlink("/tmp/scratchpad.tmp");
    
    /* Продовжуємо читати й писати в fd */
    write(fd, "secret data", 11);
    
    /* При падінні процесу або SIGKILL файл зникне автоматично */
    close(fd);
}
