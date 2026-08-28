#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define Q_MAX_DEPTH 8

/* Базові типи сигналів та результатів */
typedef uint16_t QSignal;

enum QReservedSignals {
    Q_ENTRY_SIG = 1,
    Q_EXIT_SIG  = 2,
    Q_INIT_SIG  = 3,
    Q_USER_SIG  = 4
};

typedef enum {
    Q_RET_HANDLED,
    Q_RET_IGNORED,
    Q_RET_TRAN,
    Q_RET_SUPER
} QResult;

/* Структура події */
typedef struct {
    QSignal sig;
    uintptr_t param;
} QEvt;

/* Службові статичні події для життєвого циклу */
static const QEvt pkg_entry_evt = { Q_ENTRY_SIG, 0 };
static const QEvt pkg_exit_evt  = { Q_EXIT_SIG,  0 };
static const QEvt pkg_init_evt  = { Q_INIT_SIG,  0 };

/* Оголошення типу автомата та покажчика на функцію стану */
typedef struct QHsm QHsm;
typedef QResult (*QStateHandler)(QHsm *me, const QEvt *e);

struct QHsm {
    QStateHandler state;   /* поточний активний стан */
    QStateHandler temp;    /* тимчасовий стан під час переходу / суперстан */
};

/* Макроси повернення результату для лаконічності коду станів */
#define Q_HANDLED()         (Q_RET_HANDLED)
#define Q_IGNORED()         (Q_RET_IGNORED)
#define Q_TRAN(target_)     (((QHsm *)me)->temp = (QStateHandler)(target_), Q_RET_TRAN)
#define Q_SUPER(super_)     (((QHsm *)me)->temp = (QStateHandler)(super_), Q_RET_SUPER)

/* Топовий суперстан системи (корінь ієрархії) */
static QResult QHsm_top(QHsm *me, const QEvt *e) {
    (void)me;
    (void)e;
    return Q_RET_IGNORED;
}

/* Ініціалізація автомата з початковим станом */
void QHsm_init(QHsm *me, QStateHandler initial) {
    me->state = QHsm_top;
    /* Виклик початкового переходу для визначення цільового стану */
    initial(me, &pkg_init_evt);
    QStateHandler target = me->temp;
    
    /* Побудова шляху входу від кореня до цільового стану */
    QStateHandler entry_path[Q_MAX_DEPTH];
    int8_t depth = 0;
    
    QStateHandler s = target;
    while (s != QHsm_top && s != NULL && depth < Q_MAX_DEPTH) {
        entry_path[depth++] = s;
        me->temp = QHsm_top;
        s(me, &pkg_entry_evt);
        s = me->temp; /* отримали суперстан */
    }
    
    /* Виконання дій Entry згори донизу */
    while (--depth >= 0) {
        entry_path[depth](me, &pkg_entry_evt);
    }
    me->state = target;
    me->state(me, &pkg_init_evt);
}

/* Диспетчеризація події та обчислення переходів із викликом Exit/Entry */
void QHsm_dispatch(QHsm *me, const QEvt *e) {
    QStateHandler s = me->state;
    QResult res;

    /* Бульбашкове підняття події вгору по ієрархії, поки хтось не обробить */
    while (s != QHsm_top && s != NULL) {
        me->temp = QHsm_top;
        res = s(me, e);

        if (res == Q_RET_HANDLED || res == Q_RET_IGNORED) {
            return; /* Подію успішно поглинуто або проігноровано */
        }

        if (res == Q_RET_TRAN) {
            QStateHandler target = me->temp;
            QStateHandler source = s;

            /* 1. Вихід з поточного стану вгору до джерела переходу */
            for (QStateHandler c = me->state; c != source; ) {
                c(me, &pkg_exit_evt);
                me->temp = QHsm_top;
                c(me, &pkg_entry_evt);
                c = me->temp;
            }
            source(me, &pkg_exit_evt);

            /* 2. Обчислення шляху входу до target (LCA шлях) */
            QStateHandler entry_path[Q_MAX_DEPTH];
            int8_t depth = 0;
            QStateHandler t = target;

            while (t != QHsm_top && t != NULL && depth < Q_MAX_DEPTH) {
                entry_path[depth++] = t;
                me->temp = QHsm_top;
                t(me, &pkg_entry_evt);
                t = me->temp;
            }

            /* 3. Виконання Entry згори донизу до цільового стану */
            while (--depth >= 0) {
                entry_path[depth](me, &pkg_entry_evt);
            }

            me->state = target;
            me->state(me, &pkg_init_evt);
            return;
        }

        /* Перехід до суперстану, якщо стан повернув Q_RET_SUPER */
        s = me->temp;
    }
}
