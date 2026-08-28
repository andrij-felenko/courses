/* c */
#include <stdint.h>
#include <stdbool.h>

typedef uint32_t Literal;
typedef uint32_t Var;

#define LIT_VAR(lit)      ((lit) >> 1)
#define LIT_SIGN(lit)     ((lit) & 1)
#define LIT_MAKE(v, s)    (((uint32_t)(v) << 1) | ((s) ? 1 : 0))
#define LIT_NEG(lit)      ((lit) ^ 1)
