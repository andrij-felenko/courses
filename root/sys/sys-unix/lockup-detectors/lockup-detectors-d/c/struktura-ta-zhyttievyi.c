   /* Спрощена логіка роботи ядерного потоку watchdog */
   static void watchdog_enable(unsigned int cpu)
   {
       struct hrtimer *hrtimer = &__raw_get_cpu_var(watchdog_hrtimer);
       
       /* Оновлюємо мітку часу поточним монотонним часом */
       __touch_watchdog();
       
       /* Запускаємо високоточний таймер */
       hrtimer_start(hrtimer, ns_to_ktime(sample_period),
                     HRTIMER_MODE_REL_PINNED_HARD);
   }
