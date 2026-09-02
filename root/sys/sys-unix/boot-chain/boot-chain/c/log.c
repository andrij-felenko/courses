/* Реалізація єдиного каналу повідомлень. */

#define _GNU_SOURCE
#include <errno.h>
#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#include "log.h"

void boot_err(const char *fmt, ...)
{
	va_list ap;

	fputs("switch_root: ", stderr);
	va_start(ap, fmt);
	vfprintf(stderr, fmt, ap);
	va_end(ap);
	fputc('\n', stderr);

	/* Наступним кроком може бути стирання пам'яті або підміна кореня, після
	 * яких буферизований рядок пропав би мовчки. Виштовхуємо негайно. */
	fflush(stderr);
}

void boot_errno(const char *op, const char *arg)
{
	/* errno читаємо ПЕРШИМ ділом: усе, що нижче, має право його зіпсувати. */
	const int saved = errno;

	if (arg != NULL)
		boot_err("%s(\"%s\"): %s", op, arg, strerror(saved));
	else
		boot_err("%s: %s", op, strerror(saved));

	errno = saved;
}
