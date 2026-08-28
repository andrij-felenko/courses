/* ============================================================================
 * test_emb_i18n.c — Повний набір верифікаційних тестів на C99
 * ============================================================================ */
#include <stdio.h>
#include <assert.h>
#include <string.h>
#include "emb_i18n.h"

void test_plural_evaluator(void) {
    printf("[C99 TEST] Перевірка математики множин CLDR...\n");
    
    /* 1. Українська мова (Rule ID = 2) */
    assert(emb_i18n_eval_plural(2, 1)   == EMB_PLURAL_ONE);   /* 1 файл */
    assert(emb_i18n_eval_plural(2, 21)  == EMB_PLURAL_ONE);   /* 21 файл */
    assert(emb_i18n_eval_plural(2, 101) == EMB_PLURAL_ONE);   /* 101 файл */
    
    assert(emb_i18n_eval_plural(2, 2)   == EMB_PLURAL_FEW);   /* 2 файли */
    assert(emb_i18n_eval_plural(2, 3)   == EMB_PLURAL_FEW);   /* 3 файли */
    assert(emb_i18n_eval_plural(2, 4)   == EMB_PLURAL_FEW);   /* 4 файли */
    assert(emb_i18n_eval_plural(2, 22)  == EMB_PLURAL_FEW);   /* 22 файли */
    
    assert(emb_i18n_eval_plural(2, 0)   == EMB_PLURAL_MANY);  /* 0 файлів */
    assert(emb_i18n_eval_plural(2, 5)   == EMB_PLURAL_MANY);  /* 5 файлів */
    assert(emb_i18n_eval_plural(2, 11)  == EMB_PLURAL_MANY);  /* 11 файлів */
    assert(emb_i18n_eval_plural(2, 12)  == EMB_PLURAL_MANY);  /* 12 файлів */
    assert(emb_i18n_eval_plural(2, 14)  == EMB_PLURAL_MANY);  /* 14 файлів */
    assert(emb_i18n_eval_plural(2, 20)  == EMB_PLURAL_MANY);  /* 20 файлів */
    assert(emb_i18n_eval_plural(2, 100) == EMB_PLURAL_MANY);  /* 100 файлів */
    
    /* 2. Арабська мова (Rule ID = 4) */
    assert(emb_i18n_eval_plural(4, 0)   == EMB_PLURAL_ZERO);
    assert(emb_i18n_eval_plural(4, 1)   == EMB_PLURAL_ONE);
    assert(emb_i18n_eval_plural(4, 2)   == EMB_PLURAL_TWO);
    assert(emb_i18n_eval_plural(4, 5)   == EMB_PLURAL_FEW);
    assert(emb_i18n_eval_plural(4, 15)  == EMB_PLURAL_MANY);
    assert(emb_i18n_eval_plural(4, 100) == EMB_PLURAL_OTHER);
}

void test_formatters(void) {
    printf("[C99 TEST] Перевірка безпечних форматувальників стека...\n");
    char buf[64];
    
    /* Форматування числа */
    size_t len = emb_i18n_format_1i(buf, sizeof(buf), "Напруга: {0} мВ", 3300);
    assert(strcmp(buf, "Напруга: 3300 мВ") == 0);
    assert(len == strlen(buf));
    
    /* Від'ємні числа */
    emb_i18n_format_1i(buf, sizeof(buf), "Температура: {0} C", -40);
    assert(strcmp(buf, "Температура: -40 C") == 0);
    
    /* Число + рядок */
    emb_i18n_format_1i_1s(buf, sizeof(buf), "Помилка {0}: {1}", 404, "Not Found");
    assert(strcmp(buf, "Помилка 404: Not Found") == 0);
    
    /* Захист від переповнення */
    char small[8];
    emb_i18n_format_1i(small, sizeof(small), "1234567890", 0);
    assert(small[sizeof(small) - 1] == '\0');
    assert(strlen(small) == 7);
}

int main(void) {
    test_plural_evaluator();
    test_formatters();
    printf("[C99 TEST] Усі тести завершено успішно!\n");
    return 0;
}
