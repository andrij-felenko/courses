struct psi_trigger {
	/* Стан, за яким стежить тригер: PSI_MEM_SOME, PSI_IO_FULL, … */
	enum psi_states state;
	/* Поріг у наносекундах */
	u64 threshold;
	/* Вузол у списку тригерів групи */
	struct list_head node;
	struct psi_group *group;
	/* Черга очікування для poll()/epoll() */
	wait_queue_head_t event_wait;
	/* Прапор нової події (скидається при опитуванні) */
	int event;
	/* Рухоме вікно відстеження */
	struct psi_window win;
	u64 last_event_time;
	/* Який агрегатор обслуговує тригер: PSI_AVGS чи PSI_POLL */
	enum psi_aggregators aggregator;
};

struct psi_group {
	struct psi_group *parent;
	bool enabled;
	/* Per-CPU масив накопичувачів */
	struct psi_group_cpu __percpu *pcpu;
	/* Відкладена робота оновлення EWMA (раз на 2 с) */
	struct delayed_work avgs_work;
	/* Тригери на повільному агрегаторі (безпривілейовані, вікно N·2 с) */
	struct list_head avg_triggers;
	/* Тригери на швидкому RT-опитуванні та його потік */
	struct list_head rtpoll_triggers;
	struct task_struct __rcu *rtpoll_task;
	u64 rtpoll_min_period;
	/* Накопичений час за станами та готові середні */
	u64 total[NR_PSI_AGGREGATORS][NR_PSI_STATES - 1];
	unsigned long avg[NR_PSI_STATES - 1][3];
};
