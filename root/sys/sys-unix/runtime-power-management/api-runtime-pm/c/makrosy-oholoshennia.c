/* поля всередині вже наявної struct dev_pm_ops */
#define RUNTIME_PM_OPS(suspend_fn, resume_fn, idle_fn) \
        .runtime_suspend = suspend_fn, \
        .runtime_resume  = resume_fn,  \
        .runtime_idle    = idle_fn,

/* уся структура одним рядком */
#define DEFINE_RUNTIME_DEV_PM_OPS(name, suspend_fn, resume_fn, idle_fn) \
        _DEFINE_DEV_PM_OPS(name, pm_runtime_force_suspend, pm_runtime_force_resume, \
                           suspend_fn, resume_fn, idle_fn)

/* те саме, коли структуру мусить бачити інший модуль */
EXPORT_RUNTIME_DEV_PM_OPS(name, suspend_fn, resume_fn, idle_fn)
EXPORT_GPL_RUNTIME_DEV_PM_OPS(name, suspend_fn, resume_fn, idle_fn)
EXPORT_NS_RUNTIME_DEV_PM_OPS(name, suspend_fn, resume_fn, idle_fn, ns)
