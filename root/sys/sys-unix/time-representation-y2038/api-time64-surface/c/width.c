/* width.c — макроси СТОЯТЬ ПЕРЕД усіма заголовками */
#define _FILE_OFFSET_BITS 64
#define _TIME_BITS 64

#include <stdio.h>
#include <time.h>

int main(void)
{
	struct timespec ts;

	printf("sizeof(time_t) = %zu\n", sizeof(time_t));
	printf("за межею 2038:   %lld\n", (long long)(time_t)2147483648LL);

	if (clock_gettime(CLOCK_REALTIME, &ts) != 0) {
		perror("clock_gettime");
		return 1;
	}
	printf("зараз:           %lld\n", (long long)ts.tv_sec);
	return 0;
}
