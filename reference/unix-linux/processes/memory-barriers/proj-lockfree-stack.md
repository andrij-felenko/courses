# ⚙️ Безблокувальний стек Трайбера на Acquire-Release

Ця проектна стаття демонструє практичний C-код реалізації безблокувального стека (Treiber Lock-Free Stack) у ядрі Linux із використанням Acquire-Release семантики впорядкування пам'яті та примітива `cmpxchg`.

Безблокувальний стек Трайбера (R. Kent Treiber, 1986) дозволяє довільній кількості паралельних ядер процесора одночасно додавати (`push`) та витягувати (`pop`) елементи зі зв'язаного списку без використання спінлоків, м'ютексів чи будь-яких затримок у контексті ядра.

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/slab.h>
#include <linux/atomic.h>

struct lstack_node {
    struct lstack_node *next;
    int value;
};

struct lstack {
    struct lstack_node *top;
};

void lstack_init(struct lstack *s)
{
    smp_store_release(&s->top, NULL);
}

void lstack_push(struct lstack *s, int val)
{
    struct lstack_node *node = kmalloc(sizeof(*node), GFP_KERNEL);
    if (!node)
        return;

    node->value = val;

    struct lstack_node *old_top;
    do {
        // Зчитуємо поточну вершину стека з Acquire-семантикою
        old_top = smp_load_acquire(&s->top);
        node->next = old_top;
        // Намагаємося атомарно замінити s->top на новий вузол
    } while (cmpxchg(&s->top, old_top, node) != old_top);
}

bool lstack_pop(struct lstack *s, int *val)
{
    struct lstack_node *old_top;
    struct lstack_node *new_top;

    do {
        // Зчитуємо вершину з Acquire-семантикою
        old_top = smp_load_acquire(&s->top);
        if (!old_top)
            return false; // Стек повністю порожній

        new_top = old_top->next;
    } while (cmpxchg(&s->top, old_top, new_top) != old_top);

    *val = old_top->value;
    kfree(old_top);
    return true;
}
```

## Вимоги до впорядкування пам'яті у коді

1. **`smp_load_acquire(&s->top)`**: Поміщає бар'єр читання одразу після отримання вказівника на вершину. Це гарантує, що поля сайз-інфо та вказівника `old_top->next` будуть зчитані з пам'яті строго **після** отримання дійсного адреси вершини. Жодне читання не зможе з'їхати вище цієї точки.
2. **`cmpxchg`**: Функція порівняння з обміном у ядрі Linux розгортається у повний двосторонній апаратний бар'єр пам'яті (`smp_mb`), який забороняє будь-якому прочитанню або запису витікати за межі CAS-операції.
3. **Захист від проблеми ABA**: У базовій реалізації стек Трайбера може піддаватися описуваній в інженерії «проблемі ABA». У ядрі Linux для її запобігання застосовується механізм RCU (Read-Copy-Update) або виклики `kfree_rcu()`, які відкладають фізичну деалокацію вузла до проходження граційної фази.
