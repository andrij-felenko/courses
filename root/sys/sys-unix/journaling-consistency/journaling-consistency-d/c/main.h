int fd = open("cfg.tmp", O_WRONLY | O_CREAT | O_TRUNC, 0644);
write(fd, buf, len);        /* байти лише в кеші сторінок */
fsync(fd);                  /* тепер вони на носії */
close(fd);

rename("cfg.tmp", "cfg");   /* заміна імені — неподільна */

int dir = open(".", O_RDONLY | O_DIRECTORY);
fsync(dir);                 /* саму заміну імені теж треба зробити тривкою */
close(dir);
