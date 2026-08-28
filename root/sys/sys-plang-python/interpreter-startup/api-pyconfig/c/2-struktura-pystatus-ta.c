/* Оголошення структури статусу в Include/cpython/pystate.h */
typedef struct {
    enum {
        _PyStatus_TYPE_OK = 0,
        _PyStatus_TYPE_ERROR = 1,
        _PyStatus_TYPE_EXIT = 2
    } _type;
    const char *func;       /* Назва C-функції, де виникла помилка */
    const char *err_msg;    /* Текстовий опис причини відмови */
    int exitcode;           /* Код завершення процесу для передачі в exit() */
} PyStatus;
