enum mode { MODE_SHARED_ATOMIC, MODE_PERCPU_ATOMIC, MODE_RSEQ };

static long shared_counter __attribute__((aligned(128)));

/* Без ділянок номер ядра доводиться питати викликом. */
static inline unsigned current_slot(void)
{
	return area ? area->cpu_id_start : (unsigned)sched_getcpu();
}

static void work(enum mode m, long n)
{
	switch (m) {
	case MODE_SHARED_ATOMIC:
		while (n--)
			__atomic_fetch_add(&shared_counter, 1, __ATOMIC_RELAXED);
		break;
	case MODE_PERCPU_ATOMIC:
		while (n--)
			__atomic_fetch_add(&counters[current_slot() * SLOT_STRIDE_LONGS],
			                   1, __ATOMIC_RELAXED);
		break;
	case MODE_RSEQ:
		while (n--)
			percpu_inc();
		break;
	}
}

struct job { enum mode m; long n; pthread_barrier_t *b; };

static void *worker(void *p)
{
	struct job *j = p;
	rseq_thread_init();                 /* реєстрація суто індивідуальна */
	pthread_barrier_wait(j->b);
	work(j->m, j->n);
	rseq_thread_fini();
	return NULL;
}

static double now(void)
{
	struct timespec ts;
	clock_gettime(CLOCK_MONOTONIC, &ts);
	return ts.tv_sec + ts.tv_nsec * 1e-9;
}

static void run(const char *name, enum mode m, int nthreads, long n)
{
	pthread_barrier_t b;
	pthread_t th[256];
	struct job j = { m, n, &b };
	double t0, dt;

	shared_counter = 0;
	memset(counters, 0, (size_t)nr_slots * SLOT_STRIDE_LONGS * sizeof(long));
	pthread_barrier_init(&b, NULL, nthreads + 1);
	for (int i = 0; i < nthreads; i++)
		pthread_create(&th[i], NULL, worker, &j);

	pthread_barrier_wait(&b);           /* усі стартують разом */
	t0 = now();
	for (int i = 0; i < nthreads; i++)
		pthread_join(th[i], NULL);
	dt = now() - t0;

	long want = (long)nthreads * n;
	long got = (m == MODE_SHARED_ATOMIC) ? shared_counter : counters_total();
	printf("%-22s потоків %3d   %7.2f нс/приріст   сума %s\n",
	       name, nthreads, dt * 1e9 / (double)want,
	       got == want ? "точна" : "ПОМИЛКОВА");
	pthread_barrier_destroy(&b);
}

int main(int argc, char **argv)
{
	int nthreads = argc > 1 ? atoi(argv[1]) : 8;
	long n = argc > 2 ? atol(argv[2]) : 20L * 1000 * 1000;

	if (nthreads < 1 || nthreads > 256)
		return fprintf(stderr, "потоків: 1..256\n"), 1;

	nr_slots = (unsigned)sysconf(_SC_NPROCESSORS_CONF);
	counters = aligned_alloc(128, (size_t)nr_slots * SLOT_STRIDE_LONGS
	                              * sizeof(long));
	if (!counters)
		return fprintf(stderr, "нема пам'яті\n"), 1;
	memset(counters, 0, (size_t)nr_slots * SLOT_STRIDE_LONGS * sizeof(long));

	int have = (rseq_thread_init() == 0);
	printf("rseq: %s · ядро підтримує %u байтів полів · комірок %u\n",
	       have ? "є" : "НЕМАЄ, лишається атомарний приріст",
	       kernel_feature_size(), nr_slots);
	rseq_thread_fini();

	run("спільний, atomic",  MODE_SHARED_ATOMIC, nthreads, n);
	run("по ядрах, atomic",  MODE_PERCPU_ATOMIC, nthreads, n);
	if (have)
		run("по ядрах, rseq", MODE_RSEQ, nthreads, n);
	return 0;
}
