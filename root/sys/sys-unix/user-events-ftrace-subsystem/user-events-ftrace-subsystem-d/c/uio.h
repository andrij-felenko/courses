#include <sys/uio.h>

/* Перший елемент - ID події (4 байти) */
struct iovec iov[3];
iov[0].iov_base = &reg.write_index;
iov[0].iov_len  = sizeof(reg.write_index);

/* Другий елемент - фіксовані поля структури */
iov[1].iov_base = &payload_header;
iov[1].iov_len  = sizeof(payload_header);

/* Третій елемент - динамічний рядок */
iov[2].iov_base = (void *)dynamic_url_string;
iov[2].iov_len  = dynamic_url_length;

/* Відправка в ядро за один системний виклик */
ssize_t bytes_written = writev(fd, iov, 3);
