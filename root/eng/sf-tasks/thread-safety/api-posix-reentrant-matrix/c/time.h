#include <time.h>

/* ЗАСТАРІЛІ ФУНКЦІЇ (Статичний буфер повернення) */
struct tm *gmtime(const time_t *timep);
struct tm *localtime(const time_t *timep);
char *asctime(const struct tm *tm);
char *ctime(const time_t *timep);

/* РЕЕНТРАБЕЛЬНІ ДВІЙНИКИ СТАНДАРТУ POSIX */
struct tm *gmtime_r(const time_t *timep, struct tm *result);
struct tm *localtime_r(const time_t *timep, struct tm *result);
char *asctime_r(const struct tm *tm, char *buf);
char *ctime_r(const time_t *timep, char *buf);
