// 1) Класика: у заголовку — лише ОГОЛОШЕННЯ, тіло — в одному .c
// helper.h
int helper(int x);                    // обіцянка
// helper.c
int helper(int x) { return x * 2; }   // єдине визначення

// 2) inline: дозволяє однакове визначення в кожному файлі (для коротких)
// helper.h
inline int helper(int x) { return x * 2; }

// 3) static: у кожному файлі — СВОЯ прихована копія (роздуває код)
// helper.h
static int helper(int x) { return x * 2; }
