   static void watchdog_overflow_callback(struct perf_event *event,
                                          struct perf_sample_data *data,
                                          struct pt_regs *regs)
   {
       /* Перевіряємо, чи змінився лічильник звичайних переривань таймера */
       if (__this_cpu_read(hrtimer_interrupts) == __this_cpu_read(hrtimer_interrupts_saved)) {
           if (__this_cpu_read(hard_watchdog_warn))
               return;

           pr_emerg("Watchdog detected hard LOCKUP on cpu %d\n", smp_processor_id());
           print_modules();
           print_ip_sym(regs->ip);
           show_regs(regs);
           
           if (sysctl_hardlockup_panic)
               panic("Hard LOCKUP");
           
           __this_cpu_write(hard_watchdog_warn, true);
           return;
       }
       
       /* Оновлюємо збережене значення лічильника для наступного циклу */
       __this_cpu_write(hrtimer_interrupts_saved, __this_cpu_read(hrtimer_interrupts));
       __this_cpu_write(hard_watchdog_warn, false);
   }
