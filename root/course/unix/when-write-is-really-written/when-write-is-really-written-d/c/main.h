/* 1. Запис та скидання вмісту файлу */
int fd = open("/etc/app/config.json.tmp", O_WRONLY | O_CREAT | O_TRUNC, 0644);
write(fd, data, len);
fsync(fd);
close(fd);

/* 2. Атомарне перейменування */
rename("/etc/app/config.json.tmp", "/etc/app/config.json");

/* 3. Обов'язкова синхронізація дескриптора батьківського каталогу! */
int dir_fd = open("/etc/app", O_RDONLY | O_DIRECTORY);
fsync(dir_fd);
close(dir_fd);
