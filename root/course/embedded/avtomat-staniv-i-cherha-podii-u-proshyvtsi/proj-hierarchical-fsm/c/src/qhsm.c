/*
 * qhsm.c — реалізація рушія HSM: диспетчеризація події по ієрархії та
 * перехід із обчисленням найближчого спільного предка (LCA).
 */
#include "qhsm.h"

/* Службові події живуть у ПЗП: рушій ніколи їх не змінює. */
static const QEvt l_emptyEvt = { Q_EMPTY_SIG, 0U };
static const QEvt l_entryEvt = { Q_ENTRY_SIG, 0U };
static const QEvt l_exitEvt  = { Q_EXIT_SIG,  0U };
static const QEvt l_initEvt  = { Q_INIT_SIG,  0U };

QTranAction QHsm_pendingAction_ = NULL;

/* Позначка «стану в гілці цілі немає». Гілка не буває довшою за
 * Q_MAX_DEPTH, тож 0xFF ніколи не збігається зі справжнім індексом. */
#define TPATH_NONE 0xFFU

QResult QHsm_top(QHsm *me, const QEvt *e) {
    (void)me;
    (void)e;
    return Q_RET_IGNORED;
}

/* Питає стан про його суперстан зондом Q_EMPTY_SIG.
 * Обробник зобов'язаний провалити невідомий сигнал у default і відповісти
 * Q_SUPER — інакше дерево станів не замкнене й рушій зупиняє програму. */
static QStateHandler parent_of(QHsm *me, QStateHandler s) {
    QResult r;
    me->temp = QHsm_top;
    r = (*s)(me, &l_emptyEvt);
    Q_ASSERT(r == Q_RET_SUPER);
    (void)r;
    Q_ASSERT(me->temp != NULL);
    return me->temp;
}

static void exec_action(QHsm *me, QTranAction act) {
    if (act != NULL) {
        (*act)(me);
    }
}

/* Спуск від lca (виключно) до target (включно) з викликом Q_ENTRY_SIG.
 * Порядок має бути зверху вниз, а дерево ми вміємо обходити лише знизу
 * вгору — тому шлях спершу лягає в масив, а вже потім розкручується
 * у зворотному порядку. */
static void enter_from(QHsm *me, QStateHandler lca, QStateHandler target) {
    QStateHandler entry_path[Q_MAX_DEPTH];
    uint8_t depth = 0U;
    QStateHandler s = target;

    while (s != lca) {
        Q_ASSERT(s != QHsm_top);              /* lca мусить бути предком target */
        Q_ASSERT(depth < (uint8_t)Q_MAX_DEPTH);
        entry_path[depth] = s;
        ++depth;
        s = parent_of(me, s);
    }
    while (depth > 0U) {
        --depth;
        (void)(*entry_path[depth])(me, &l_entryEvt);
    }
}

/* Фаза внутрішньої ініціалізації: складений стан має право оголосити
 * типовий підстан, той — свій, і так далі. Ланцюжок обмежений глибиною
 * дерева, тож зациклитися неможливо. */
static void take_init_transitions(QHsm *me) {
    uint8_t guard;

    for (guard = 0U; guard <= (uint8_t)Q_MAX_DEPTH; ++guard) {
        QStateHandler source = me->state;
        QStateHandler target;
        QTranAction act;
        QResult r;

        me->temp = QHsm_top;
        QHsm_pendingAction_ = NULL;
        r = (*source)(me, &l_initEvt);
        if (r != Q_RET_TRAN) {
            /* Стан не складений або типового підстану не оголошує —
             * спуск завершено. */
            QHsm_pendingAction_ = NULL;
            return;
        }
        target = me->temp;
        act = QHsm_pendingAction_;
        QHsm_pendingAction_ = NULL;

        exec_action(me, act);
        enter_from(me, source, target);
        me->state = target;
    }
    Q_onAssert(__FILE__, __LINE__); /* ланцюг типових підстанів не має дна */
}

static uint8_t tpath_index(QStateHandler const *tpath, uint8_t n, QStateHandler s) {
    uint8_t i;
    for (i = 0U; i < n; ++i) {
        if (tpath[i] == s) {
            return i;
        }
    }
    return TPATH_NONE;
}

/*
 * Ядро переходу. Виконує чотири фази в такому порядку:
 *   1. вихід від активного стану вгору до LCA (LCA не виходить);
 *   2. дія, прив'язана до самого переходу;
 *   3. вхід від LCA вниз до цілі;
 *   4. ланцюжок типових підстанів цілі.
 */
static void take_transition(QHsm *me, QStateHandler source,
                            QStateHandler target, QTranAction act) {
    QStateHandler tpath[Q_MAX_DEPTH];
    uint8_t tdepth = 0U;
    uint8_t enter_count;
    uint8_t d;
    QStateHandler s;
    QStateHandler a;
    QStateHandler t;

    /* 1а. Стани, глибші за джерело переходу, гинуть завжди: подія
     * піднялася повз них, отже жоден із них її не обробив. */
    s = me->state;
    for (d = 0U; s != source; ++d) {
        Q_ASSERT(d < (uint8_t)Q_MAX_DEPTH);
        Q_ASSERT(s != QHsm_top);
        (void)(*s)(me, &l_exitEvt);
        s = parent_of(me, s);
    }

    /* Перехід у себе: стан гарантовано перезапускається — вихід, дія, вхід. */
    if (source == target) {
        (void)(*source)(me, &l_exitEvt);
        exec_action(me, act);
        (void)(*source)(me, &l_entryEvt);
        me->state = target;
        take_init_transitions(me);
        return;
    }

    /* 1б. Гілка цілі, знизу вгору: tpath[0] — сама ціль, останній
     * елемент — найвищий стан під коренем. */
    for (t = target; t != QHsm_top; t = parent_of(me, t)) {
        Q_ASSERT(tdepth < (uint8_t)Q_MAX_DEPTH);
        tpath[tdepth] = t;
        ++tdepth;
    }

    /* 1в. Підйом від джерела вгору, доки не натрапимо на стан, що вже є
     * у гілці цілі — це і є LCA. Усе, що пройшли дорогою, покидаємо;
     * сам LCA лишається активним і Q_EXIT_SIG не дістає. */
    enter_count = tdepth; /* LCA не знайшовся — ним буде корінь */
    a = source;
    for (d = 0U; a != QHsm_top; ++d) {
        uint8_t k;
        Q_ASSERT(d <= (uint8_t)Q_MAX_DEPTH);
        k = tpath_index(tpath, tdepth, a);
        if (k != TPATH_NONE) {
            enter_count = k; /* входимо лише в те, що лежить нижче LCA */
            break;
        }
        (void)(*a)(me, &l_exitEvt);
        a = parent_of(me, a);
    }

    /* 2. Дія переходу: старої гілки вже немає, нової ще немає. */
    exec_action(me, act);

    /* 3. Вхід згори вниз до цілі. */
    while (enter_count > 0U) {
        --enter_count;
        (void)(*tpath[enter_count])(me, &l_entryEvt);
    }

    me->state = target;

    /* 4. Якщо ціль складена — спускаємось у її типовий підстан. */
    take_init_transitions(me);
}

void QHsm_ctor(QHsm *me, QStateHandler initial) {
    Q_ASSERT(me != NULL);
    Q_ASSERT(initial != NULL);
    me->state = QHsm_top;
    me->temp = initial;
}

void QHsm_init(QHsm *me, const QEvt *e) {
    QStateHandler initial;
    QStateHandler target;
    QTranAction act;
    QResult r;

    Q_ASSERT(me != NULL);
    initial = me->temp;
    Q_ASSERT(me->state == QHsm_top); /* QHsm_ctor виконано, QHsm_init — ще ні */
    Q_ASSERT(initial != NULL);

    me->temp = QHsm_top;
    QHsm_pendingAction_ = NULL;
    r = (*initial)(me, (e != NULL) ? e : &l_initEvt);
    Q_ASSERT(r == Q_RET_TRAN); /* початковий псевдостан зобов'язаний перейти */
    (void)r;

    target = me->temp;
    act = QHsm_pendingAction_;
    QHsm_pendingAction_ = NULL;

    exec_action(me, act);
    enter_from(me, QHsm_top, target);
    me->state = target;
    take_init_transitions(me);
}

void QHsm_dispatch(QHsm *me, const QEvt *e) {
    QStateHandler source;
    QStateHandler target;
    QTranAction act;
    uint8_t d;

    Q_ASSERT(me != NULL);
    Q_ASSERT(e != NULL);
    Q_ASSERT(me->state != NULL);

    /* Бульбашкове підняття події: подія йде вгору, доки хтось не забере
     * її собі. Саме тут працює поведінкове наслідування — підстан описує
     * лише свою унікальну реакцію, решту бере суперстан. */
    source = me->state;
    for (d = 0U;; ++d) {
        QResult r;
        Q_ASSERT(d <= (uint8_t)Q_MAX_DEPTH);
        if (source == QHsm_top) {
            return; /* подію не забрав ніхто — тихо гасимо */
        }
        me->temp = QHsm_top;
        QHsm_pendingAction_ = NULL;
        r = (*source)(me, e);

        if ((r == Q_RET_HANDLED) || (r == Q_RET_IGNORED)) {
            QHsm_pendingAction_ = NULL;
            return;
        }
        if (r == Q_RET_TRAN) {
            break;
        }
        Q_ASSERT(r == Q_RET_SUPER);
        source = me->temp;
    }

    target = me->temp;
    act = QHsm_pendingAction_;
    QHsm_pendingAction_ = NULL;

    take_transition(me, source, target, act);
}

bool QHsm_isIn(QHsm *me, QStateHandler state) {
    QStateHandler s;
    uint8_t d;

    Q_ASSERT(me != NULL);
    Q_ASSERT(state != NULL);

    s = me->state;
    for (d = 0U; s != QHsm_top; ++d) {
        Q_ASSERT(d <= (uint8_t)Q_MAX_DEPTH);
        if (s == state) {
            return true;
        }
        s = parent_of(me, s);
    }
    return (state == QHsm_top);
}
