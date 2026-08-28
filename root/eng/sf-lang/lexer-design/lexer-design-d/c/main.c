#include <ctype.h>   // isspace, isdigit, isalpha, isalnum
#include <string.h>

typedef enum { T_NUM, T_IDENT, T_PLUS, T_MINUS,
               T_STAR, T_LPAREN, T_RPAREN, T_END } Kind;

typedef struct {
    Kind  kind;
    int   value;        // для T_NUM — розібране число
    char  text[32];     // для T_IDENT — саме ім'я (лексема)
} Token;

static const char *p;   // поточна позиція у вхідному тексті

Token next_token(void) {
    Token t = {0};

    while (isspace((unsigned char)*p))   // 1) проковтнути пробіли
        p++;

    if (*p == '\0') {                    // кінець вводу
        t.kind = T_END;
        return t;
    }

    if (isdigit((unsigned char)*p)) {    // 2) НАЙДОВШЕ число
        int v = 0;
        while (isdigit((unsigned char)*p))   // тягнемо цифри, доки йдуть
            v = v * 10 + (*p++ - '0');       // тут-таки рахуємо значення
        t.kind  = T_NUM;
        t.value = v;
        return t;
    }

    if (isalpha((unsigned char)*p)) {    // 3) НАЙДОВШЕ ім'я
        int i = 0;
        while (isalnum((unsigned char)*p) && i < 31)
            t.text[i++] = *p++;          // тягнемо буквоцифри
        t.text[i] = '\0';
        t.kind = T_IDENT;                // (ключові слова — окрема перевірка нижче)
        return t;
    }

    switch (*p++) {                      // 4) односимвольні оператори й дужки
        case '+': t.kind = T_PLUS;   break;
        case '-': t.kind = T_MINUS;  break;
        case '*': t.kind = T_STAR;   break;
        case '(': t.kind = T_LPAREN; break;
        case ')': t.kind = T_RPAREN; break;
        default:  t.kind = T_END;    break;   // невідомий символ — тут спрощено
    }
    return t;
}
