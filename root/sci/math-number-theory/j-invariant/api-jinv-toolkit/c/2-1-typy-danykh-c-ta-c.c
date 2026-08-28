/* Коди помилок бібліотеки libjinv */
typedef enum {
    JINV_OK = 0,                  /* Успішне виконання */
    JINV_ERR_SINGULAR_CURVE = 1,  /* Крива є сингулярною (дискримінант Delta = 0) */
    JINV_ERR_DIVISION_BY_ZERO = 2,/* Спроба ділення на нульовий елемент поля */
    JINV_ERR_INVALID_PARAM = 3,   /* Некоректні вхідні параметри функції */
    JINV_ERR_NO_ROOT = 4,         /* Корінь многочлена не знайдено у базовому полі */
    JINV_ERR_BUFFER_OVERFLOW = 5  /* Недостатній розмір вихідного буфера */
} jinv_status_t;

/* Елемент квадратичного розширення F_{p^2} = {re + im * i} */
typedef struct {
    int64_t re; /* Дійсна частина: re in [0, p - 1] */
    int64_t im; /* Уявна частина: im in [0, p - 1] */
} fp2_t;

/* Загальна форма Вейєрштрасса: y^2 + a1*xy + a3*y = x^3 + a2*x^2 + a4*x + a6 */
typedef struct {
    fp2_t a1, a2, a3, a4, a6;
} curve_general_t;

/* Коротка форма Вейєрштрасса: y^2 = x^3 + A*x + B */
typedef struct {
    fp2_t a; /* Лінійний коефіцієнт A */
    fp2_t b; /* Вільний член B */
} curve_short_t;
