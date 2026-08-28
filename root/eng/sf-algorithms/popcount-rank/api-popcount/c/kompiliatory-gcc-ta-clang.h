/* Сигнатури вбудованих функцій GCC та Clang */
int __builtin_popcount(unsigned int x);
int __builtin_popcountl(unsigned long x);
int __builtin_popcountll(unsigned long long x);

/* Пов'язані бітові операції */
int __builtin_parity(unsigned int x);
int __builtin_parityl(unsigned long x);
int __builtin_parityll(unsigned long long x);

int __builtin_clz(unsigned int x);      /* Count leading zeros: невизначена поведінка для x = 0 */
int __builtin_ctz(unsigned int x);      /* Count trailing zeros: невизначена поведінка для x = 0 */
int __builtin_ffs(int x);               /* Find first set: повертає індекс 1..32, або 0 для нуля */
