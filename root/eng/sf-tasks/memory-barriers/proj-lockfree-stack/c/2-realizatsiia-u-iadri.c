#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/slab.h>
#include <linux/atomic.h>
#include <linux/rcupdate.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Kernel Engineer");
MODULE_DESCRIPTION("Lock-free Treiber Stack with RCU ABA prevention");

struct lstack_node {
    struct lstack_node *next;
    struct rcu_head rcu;
    int value;
};

struct lstack {
    struct lstack_node *top;
};

void lstack_init(struct lstack *s)
{
    // Ініціалізація вершини стека з Release-семантикою
    smp_store_release(&s->top, NULL);
}

void lstack_push(struct lstack *s, int val)
{
    // GFP_ATOMIC, а не GFP_KERNEL: стек поповнюють і з обробника переривання,
    // де спати не можна, а GFP_KERNEL дозволяє алокатору заснути.
    struct lstack_node *node = kmalloc(sizeof(*node), GFP_ATOMIC);
    if (!node)
        return;

    node->value = val;

    struct lstack_node *old_top;
    do {
        // Зчитуємо поточну вершину з Acquire-семантикою.
        // Наступні читання й записи не піднімуться вище цієї точки.
        old_top = smp_load_acquire(&s->top);
        node->next = old_top;

        // Атомарна спроба замінити s->top на новий вузол.
        // cmpxchg розгортається у LOCK CMPXCHG на x86 з повним бар'єром пам'яті.
    } while (cmpxchg(&s->top, old_top, node) != old_top);
}

static void lstack_free_node_rcu(struct rcu_head *head)
{
    struct lstack_node *node = container_of(head, struct lstack_node, rcu);
    kfree(node);
}

bool lstack_pop(struct lstack *s, int *val)
{
    struct lstack_node *old_top;
    struct lstack_node *new_top;

    rcu_read_lock(); // Захищаємо вказівник у RCU критичній секції
    do {
        // Зчитуємо вершину з Acquire-семантикою
        old_top = smp_load_acquire(&s->top);
        if (!old_top) {
            rcu_read_unlock();
            return false; // Стек повністю порожній
        }

        // Завдяки smp_load_acquire читання old_top->next виконається СТРОГО
        // після того, як ми отримали коректне значення old_top.
        new_top = READ_ONCE(old_top->next);

    } while (cmpxchg(&s->top, old_top, new_top) != old_top);

    *val = old_top->value;

    // Відкладаємо фізичне звільнення пам'яті до кінця періоду спокою RCU.
    // Це повністю усуває проблему розіменування звільненої пам'яті (Use-After-Free).
    call_rcu(&old_top->rcu, lstack_free_node_rcu);
    rcu_read_unlock();

    return true;
}
