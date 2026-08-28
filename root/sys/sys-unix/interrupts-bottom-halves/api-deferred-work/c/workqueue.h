#include <linux/workqueue.h>

/* функція елемента завжди така: void fn(struct work_struct *work) */
INIT_WORK(&w, fn);
INIT_DELAYED_WORK(&dw, fn);
DECLARE_WORK(w, fn);                                  /* статичне оголошення */

bool schedule_work(struct work_struct *w);                       /* у спільну system_wq */
bool schedule_delayed_work(struct delayed_work *dw, unsigned long delay);
bool queue_work(struct workqueue_struct *wq, struct work_struct *w);
bool queue_work_on(int cpu, struct workqueue_struct *wq, struct work_struct *w);
bool queue_delayed_work(struct workqueue_struct *wq,
                        struct delayed_work *dw, unsigned long delay);

bool flush_work(struct work_struct *w);               /* дочекатися; сплять — лише процесний контекст */
bool cancel_work_sync(struct work_struct *w);
bool cancel_delayed_work_sync(struct delayed_work *dw);

struct workqueue_struct *alloc_workqueue(const char *fmt, unsigned int flags,
                                         int max_active, ...);
void destroy_workqueue(struct workqueue_struct *wq);
