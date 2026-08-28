#ifndef DRAT_PROOF_LOGGER_H
#define DRAT_PROOF_LOGGER_H

#include <stdio.h>
#include <stdbool.h>

// Контекст реєстратора траси
typedef struct {
    FILE *file;
    bool binary_mode;
    size_t added_clauses;
    size_t deleted_clauses;
} ProofLogger;

// Ініціалізація реєстратора
ProofLogger* proof_logger_open(const char *filename, bool binary_mode);

// Запис додавання диз'юнкта резолюції (завершується 0 у масиві lits)
void proof_logger_add_clause(ProofLogger *logger, const int *lits, size_t size);

// Запис видалення диз'юнкта
void proof_logger_delete_clause(ProofLogger *logger, const int *lits, size_t size);

// Закриття траси з записом порожнього диз'юнкта ⊥
void proof_logger_close(ProofLogger *logger);

#endif // DRAT_PROOF_LOGGER_H
