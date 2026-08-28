/* 1. Створення тимчасового файла в тому ж каталозі */
int fd = open("/usr/bin/nginx.dpkg-new", O_WRONLY | O_CREAT | O_TRUNC | O_NOFOLLOW, 0755);

/* 2. Запис даних та примусовий скид кешу сторінок на фізичний диск */
write(fd, payload_buffer, payload_len);
fsync(fd);
close(fd);

/* 3. Атомарна заміна оригінального файла */
rename("/usr/bin/nginx.dpkg-new", "/usr/bin/nginx");
