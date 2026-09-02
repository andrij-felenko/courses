#ifndef LOG_H
#define LOG_H

/* Єдиний канал розмови з людиною.
 *
 * Усе йде в stderr, бо в initramfs це /dev/console: іншого місця, куди
 * писати, у PID 1 просто немає — ні syslog, ні журналу ще не існує.
 * Кожен рядок одразу зливається на пристрій: наступний крок може забрати
 * з-під нас і консоль, і саму пам'ять із буфером.
 */

#if defined(__GNUC__)
#define BOOT_PRINTF(fmt_idx, arg_idx) \
	__attribute__((format(printf, fmt_idx, arg_idx)))
#else
#define BOOT_PRINTF(fmt_idx, arg_idx)
#endif

/* Повідомлення з префіксом "switch_root: " і переводом рядка. */
void boot_err(const char *fmt, ...) BOOT_PRINTF(1, 2);

/* Те саме для невдалого системного виклику: op — його ім'я, arg — головний
   аргумент (може бути NULL). errno читається першим і лишається незмінним,
   тому викликач має право розбирати його й після нас. */
void boot_errno(const char *op, const char *arg);

#endif /* LOG_H */
