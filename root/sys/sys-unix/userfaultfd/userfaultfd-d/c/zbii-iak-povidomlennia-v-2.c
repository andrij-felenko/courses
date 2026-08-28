struct uffd_msg msg;
read(uffd, &msg, sizeof msg);              /* після poll(): дескриптор читабельний */

unsigned long page = msg.arg.pagefault.address & ~(pagesize - 1);
fetch_page(page, buf);                     /* мережа, файл, генератор — байдуже ядру */

struct uffdio_copy copy = {
    .dst = page, .src = (unsigned long)buf, .len = pagesize, .mode = 0,
};
ioctl(uffd, UFFDIO_COPY, &copy);           /* сторінка є — винуватець прокинувся */
