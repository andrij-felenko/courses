/* м'ютекс — linux/mutex.h */
DEFINE_MUTEX(name);                    mutex_init(&m);
void mutex_lock(struct mutex *m);
int  mutex_lock_interruptible(struct mutex *m);   /* 0 або -EINTR */
int  mutex_lock_killable(struct mutex *m);        /* 0 або -EINTR, лише смертельний сигнал */
void mutex_lock_io(struct mutex *m);              /* очікування рахується як iowait */
int  mutex_trylock(struct mutex *m);              /* 1 — узяли; НЕ з переривання */
void mutex_unlock(struct mutex *m);               /* лише власник */
bool mutex_is_locked(struct mutex *m);            /* лише для налагодження */
int  atomic_dec_and_mutex_lock(atomic_t *cnt, struct mutex *m);

/* семафор читання-письма — linux/rwsem.h */
DECLARE_RWSEM(name);                   init_rwsem(&sem);
void down_read(struct rw_semaphore *sem);
int  down_read_interruptible(struct rw_semaphore *sem);
int  down_read_killable(struct rw_semaphore *sem);
int  down_read_trylock(struct rw_semaphore *sem);      /* 1 — узяли */
void up_read(struct rw_semaphore *sem);
void down_write(struct rw_semaphore *sem);
int  down_write_killable(struct rw_semaphore *sem);
int  down_write_trylock(struct rw_semaphore *sem);
void up_write(struct rw_semaphore *sem);
void downgrade_write(struct rw_semaphore *sem);        /* письменник стає читачем без розриву */
void down_read_non_owner(struct rw_semaphore *sem);    /* виняток; див. нижче */
void up_read_non_owner(struct rw_semaphore *sem);

/* лічильний семафор — linux/semaphore.h */
DEFINE_SEMAPHORE(name, n);             sema_init(&sem, n);
void down(struct semaphore *sem);
int  down_interruptible(struct semaphore *sem);        /* 0 або -EINTR */
int  down_killable(struct semaphore *sem);
int  down_trylock(struct semaphore *sem);              /* 0 — УЗЯЛИ, ненуль — зайнято */
int  down_timeout(struct semaphore *sem, long jiffies);/* 0 або -ETIME */
void up(struct semaphore *sem);
