/* fd — дескриптор /dev/fuse: його відкрив і передав нам fusermount3 */

for (;;) {
    char buf[FUSE_MIN_READ_BUFFER];          /* мінімум; після FUSE_INIT буфер
                                                мусить умістити найбільший запис */
    ssize_t n = read(fd, buf, sizeof buf);   /* блокується, доки нема запиту */
    if (n < 0 && errno == ENODEV)            /* файлову систему відмонтовано */
        break;

    struct fuse_in_header *in = (void *)buf;
    /* in->opcode  — що питають (FUSE_LOOKUP, FUSE_READ, FUSE_GETATTR…)
       in->nodeid  — про який об'єкт
       in->unique  — номер, який треба повернути у відповіді            */

    char out[4096];
    struct fuse_out_header *hdr = (void *)out;
    hdr->unique = in->unique;
    hdr->error  = 0;                          /* або -ENOENT, -EACCES…  */
    hdr->len    = fill_reply(in, out + sizeof *hdr) + sizeof *hdr;

    write(fd, out, hdr->len);                 /* одна відповідь = один write */
}
