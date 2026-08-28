/* Повертає вказівник на перший заголовок cmsghdr у структурі msghdr */
struct cmsghdr *CMSG_FIRSTHDR(struct msghdr *msgh);

/* Повертає вказівник на наступний cmsghdr або NULL, якщо досягнуто кінця буфера */
struct cmsghdr *CMSG_NXTHDR(struct msghdr *msgh, struct cmsghdr *cmsg);

/* Повертає вказівник на перший байт корисних даних дескрипторів */
unsigned char *CMSG_DATA(struct cmsghdr *cmsg);

/* Обчислює сумарний розмір буфера з урахуванням вирівнювання пам'яті ядра */
size_t CMSG_SPACE(size_t length);
size_t CMSG_LEN(size_t length);
