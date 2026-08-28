int fd = open(tmp, O_WRONLY | O_CREAT | O_EXCL, 0644);
write(fd, data, len);
fsync(fd);              /* дані нової версії — на носії */
close(fd);

rename(tmp, target);    /* заміна: неподільна для читачів */

int dir = open(dirname_of_target, O_RDONLY | O_DIRECTORY);
fsync(dir);             /* сам запис у каталозі — на носії */
close(dir);
