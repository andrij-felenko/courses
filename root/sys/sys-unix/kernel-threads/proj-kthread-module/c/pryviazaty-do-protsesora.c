static int cpu = -1;
module_param(cpu, int, 0444);
MODULE_PARM_DESC(cpu, "прив'язати потік до цього процесора; -1 — не прив'язувати");

    /* у kdemo_init() замість kthread_run() */
    t = kthread_create(kdemo_thread, demo, "kdemo/%d", cpu < 0 ? 0 : cpu);
    if (IS_ERR(t)) { /* ...як було... */ }

    if (cpu >= 0)
        kthread_bind(t, cpu);   /* лише поки задача ще жодного разу не бігала */

    demo->task = t;
    wake_up_process(t);         /* ось тепер — у чергу готових */
