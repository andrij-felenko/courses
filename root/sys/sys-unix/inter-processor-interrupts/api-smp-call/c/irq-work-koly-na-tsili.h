struct irq_work {
        struct __call_single_node node;
        void (*func)(struct irq_work *);   /* аргумент — сам описувач */
        struct rcuwait irqwait;
};

#define IRQ_WORK_INIT(_func)        /* звичайна робота                    */
#define IRQ_WORK_INIT_LAZY(_func)   /* без переривання, до найближчого тику */
#define IRQ_WORK_INIT_HARD(_func)   /* жорсткий контекст навіть на PREEMPT_RT */
#define DEFINE_IRQ_WORK(name, _f)

void init_irq_work(struct irq_work *work, void (*func)(struct irq_work *));
bool irq_work_queue(struct irq_work *work);           /* своє ядро; NMI-безпечно */
bool irq_work_queue_on(struct irq_work *work, int cpu);
void irq_work_sync(struct irq_work *work);            /* спить: лише контекст задачі */
