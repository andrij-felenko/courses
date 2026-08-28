/* завершення — linux/completion.h */
DECLARE_COMPLETION(name);              init_completion(&c);
DECLARE_COMPLETION_ONSTACK(name);      /* для змінної на стеку: правильно для lockdep */
void reinit_completion(struct completion *c);          /* перед повторним ужитком */

void          wait_for_completion(struct completion *c);
int           wait_for_completion_interruptible(struct completion *c);
int           wait_for_completion_killable(struct completion *c);
unsigned long wait_for_completion_timeout(struct completion *c, unsigned long jiffies);
long          wait_for_completion_interruptible_timeout(struct completion *c, unsigned long j);
void          wait_for_completion_io(struct completion *c);      /* облік як iowait */

void complete(struct completion *c);       /* будить ОДНОГО чекача; можна з переривання */
void complete_all(struct completion *c);   /* будить усіх і лишає стан «уже сталося» */
bool try_wait_for_completion(struct completion *c);   /* не спить */
bool completion_done(struct completion *c);           /* не спить */
