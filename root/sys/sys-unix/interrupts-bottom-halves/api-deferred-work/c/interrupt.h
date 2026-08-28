#include <linux/interrupt.h>

typedef irqreturn_t (*irq_handler_t)(int irq, void *dev_id);

/* повна форма: два обробники — негайний і потоковий */
int request_threaded_irq(unsigned int irq,
                         irq_handler_t handler,    /* верхня половина; NULL → типова, що лише будить потік */
                         irq_handler_t thread_fn,  /* тіло в окремій задачі; NULL → потоку немає */
                         unsigned long flags,      /* IRQF_* через | */
                         const char *name,         /* це ім'я видно у /proc/interrupts */
                         void *dev);               /* прилетить в обробник як dev_id */

/* коротка форма — та сама функція з thread_fn = NULL */
static inline int request_irq(unsigned int irq, irq_handler_t handler,
                              unsigned long flags, const char *name, void *dev);

const void *free_irq(unsigned int irq, void *dev);   /* повертає той самий dev */

/* прив'язані до пристрою: знімаються самі, коли драйвер відпускає пристрій */
int devm_request_irq(struct device *dev, unsigned int irq, irq_handler_t handler,
                     unsigned long flags, const char *name, void *dev_id);
int devm_request_threaded_irq(struct device *dev, unsigned int irq, irq_handler_t handler,
                              irq_handler_t thread_fn, unsigned long flags,
                              const char *name, void *dev_id);
