/* прив'язка: пристрій приходить із disable_depth = 1, тобто механізм вимкнено */
pm_runtime_set_autosuspend_delay(dev, 100);   /* мс */
pm_runtime_use_autosuspend(dev);
pm_runtime_set_active(dev);                   /* прошивка лишила залізо ввімкненим */
pm_runtime_enable(dev);                       /* аж тепер механізм живий */

/* робота */
ret = pm_runtime_resume_and_get(dev);
if (ret < 0)
        return ret;                           /* лічильник уже опущено назад */
... звертання до заліза ...
pm_runtime_put_autosuspend(dev);

/* відв'язка */
pm_runtime_dont_use_autosuspend(dev);
pm_runtime_disable(dev);
pm_runtime_set_suspended(dev);                /* законно саме тому, що механізм уже вимкнено */
