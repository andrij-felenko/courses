#include <stdio.h>
#include <stdlib.h>
#include <solv/pool.h>
#include <solv/repo.h>
#include <solv/solver.h>
#include <solv/selection.h>
#include <solv/transaction.h>

void run_c_libsolv_demo(void) {
    // 1. Створення центрального пулу
    Pool *pool = pool_create();
    if (!pool) {
        fprintf(stderr, "Помилка створення libsolv Pool\n");
        return;
    }

    // 2. Створення системного репозиторію (встановлені пакунки)
    Repo *installed_repo = repo_create(pool, "@system");
    pool_set_installed(pool, installed_repo);

    // 3. Створення мережевого репозиторію
    Repo *updates_repo = repo_create(pool, "updates");

    // 4. Додавання пакунка curl до мережевого репозиторію
    Id pkg_id = repo_add_solvable(updates_repo);
    Solvable *s = pool_id2solvable(pool, pkg_id);
    s->name = pool_str2id(pool, "curl", 1);
    s->evr = pool_str2id(pool, "7.76.1-1.el8", 1);
    s->arch = pool_str2id(pool, "x86_64", 1);

    // 5. Побудова індексу залежностей
    pool_createwhatprovides(pool);

    // 6. Формування черги завдань: встановити пакунок curl
    Queue job;
    queue_init(&job);
    queue_push2(&job, SOLVER_INSTALL | SOLVER_SOLVABLE, pkg_id);

    // 7. Створення та запуск SAT-солвера
    Solver *solver = solver_create(pool);
    int problems = solver_solve(solver, &job);

    if (problems == 0) {
        printf("[libsolv C] Транзакцію успішно розв'язано!\n");
        Transaction *trans = solver_create_transaction(solver);
        printf("  Кількість операцій у транзакції: %d\n", trans->steps.count);
        transaction_free(trans);
    } else {
        printf("[libsolv C] Знайдено %d конфліктів залежностей!\n", problems);
        for (int p = 1; p <= problems; p++) {
            Id rule = solver_findproblemrule(solver, p);
            printf("  Проблема #%d: %s\n", p, solver_problemrule2str(solver, rule));
        }
    }

    // 8. Звільнення ресурсів
    solver_free(solver);
    queue_free(&job);
    pool_free(pool);
}
