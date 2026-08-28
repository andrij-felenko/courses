/* Статичне оголошення та ініціалізація глобальних ланцюжків */
#define ATOMIC_NOTIFIER_HEAD(name)
#define BLOCKING_NOTIFIER_HEAD(name)
#define RAW_NOTIFIER_HEAD(name)

/* Динамічна ініціалізація структур у купі або всередині об'єктів пристроїв */
void atomic_notifier_chain_init(struct atomic_notifier_head *nh);
void blocking_notifier_chain_init(struct blocking_notifier_head *nh);
void raw_notifier_chain_init(struct raw_notifier_head *nh);
int  srcu_init_notifier_head(struct srcu_notifier_head *nh);
void srcu_cleanup_notifier_head(struct srcu_notifier_head *nh);
