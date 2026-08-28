typedef void (*smp_call_func_t)(void *info);
typedef bool (*smp_cond_func_t)(int cpu, void *info);

int  smp_call_function_single(int cpu, smp_call_func_t func, void *info, int wait);
int  smp_call_function_any(const struct cpumask *mask, smp_call_func_t func,
                           void *info, int wait);
void smp_call_function_many(const struct cpumask *mask, smp_call_func_t func,
                            void *info, bool wait);
void smp_call_function(smp_call_func_t func, void *info, int wait);

void on_each_cpu(smp_call_func_t func, void *info, int wait);
void on_each_cpu_mask(const struct cpumask *mask, smp_call_func_t func,
                      void *info, bool wait);
void on_each_cpu_cond(smp_cond_func_t cond_func, smp_call_func_t func,
                      void *info, bool wait);
void on_each_cpu_cond_mask(smp_cond_func_t cond_func, smp_call_func_t func,
                           void *info, bool wait, const struct cpumask *mask);

int  smp_call_function_single_async(int cpu, call_single_data_t *csd);
bool irq_work_queue_on(struct irq_work *work, int cpu);
