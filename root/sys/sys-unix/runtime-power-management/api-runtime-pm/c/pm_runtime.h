#include <linux/pm_runtime.h>

/* увімкнення механізму для пристрою */
void pm_runtime_enable(struct device *dev);       /* −1 до power.disable_depth */
void pm_runtime_disable(struct device *dev);      /* +1; дочекатися й скасувати незавершене */
int  pm_runtime_barrier(struct device *dev);      /* тільки дочекатися й скасувати заявки */

/* заявити потребу: +1 до лічильника */
int  pm_runtime_get_sync(struct device *dev);            /* +1, розбудити, дочекатися */
int  pm_runtime_resume_and_get(struct device *dev);      /* те саме, але −1 назад на помилці */
int  pm_runtime_get(struct device *dev);                 /* +1, пробудження — заявкою */
void pm_runtime_get_noresume(struct device *dev);        /* лише +1, заліза не чіпає */
int  pm_request_resume(struct device *dev);              /* заявка на пробудження, лічильника не чіпає */
int  pm_runtime_get_if_active(struct device *dev);       /* +1 лише якщо статус уже active */
int  pm_runtime_get_if_in_use(struct device *dev);       /* +1 лише якщо лічильник уже ≠ 0 */

/* відпустити: −1 */
int  pm_runtime_put(struct device *dev);                 /* на нулі — заявка на idle */
int  pm_runtime_put_autosuspend(struct device *dev);     /* на нулі — заявка з витримкою */
int  pm_runtime_put_sync(struct device *dev);            /* на нулі — idle тут-таки */
int  pm_runtime_put_sync_suspend(struct device *dev);    /* на нулі — suspend тут-таки */
int  pm_runtime_put_sync_autosuspend(struct device *dev);
void pm_runtime_put_noidle(struct device *dev);          /* лише −1; нижче нуля не піде */

/* прямі дії, лічильника не торкаються */
int  pm_runtime_idle(struct device *dev);
int  pm_runtime_suspend(struct device *dev);
int  pm_runtime_autosuspend(struct device *dev);         /* suspend із урахуванням витримки */
int  pm_runtime_resume(struct device *dev);
int  pm_request_idle(struct device *dev);
int  pm_request_autosuspend(struct device *dev);
int  pm_schedule_suspend(struct device *dev, unsigned int delay_ms);

/* оголосити стан заліза — лише поки механізм вимкнено або після фатальної помилки */
int  pm_runtime_set_active(struct device *dev);
int  pm_runtime_set_suspended(struct device *dev);
bool pm_runtime_status_suspended(struct device *dev);    /* статус саме suspended */
bool pm_runtime_active(struct device *dev);              /* active або механізм вимкнено */
bool pm_runtime_suspended(struct device *dev);           /* suspended і механізм увімкнено */

/* політика */
void pm_runtime_use_autosuspend(struct device *dev);
void pm_runtime_dont_use_autosuspend(struct device *dev);
void pm_runtime_set_autosuspend_delay(struct device *dev, int delay_ms); /* <0 — ніколи */
void pm_runtime_mark_last_busy(struct device *dev);
void pm_runtime_forbid(struct device *dev);   /* +1 і тримати: те саме, що power/control = on */
void pm_runtime_allow(struct device *dev);    /* повернути це −1: power/control = auto */
void pm_runtime_irq_safe(struct device *dev);
void pm_suspend_ignore_children(struct device *dev, bool enable);
void pm_runtime_no_callbacks(struct device *dev);  /* + прибрати атрибути з sysfs */
