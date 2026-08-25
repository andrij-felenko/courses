# Api Opp Functions

**Основні функції OPP API у Linux:**

```c
#include <linux/pm_opp.h>

// Знайти точний збіг частоти (в Гц) та отримати OPP
struct dev_pm_opp *dev_pm_opp_find_freq_exact(struct device *dev,
                                              unsigned long freq,
                                              bool available);

// Знайти найближчу доступну частоту, яка більша або дорівнює заданій
struct dev_pm_opp *dev_pm_opp_find_freq_ceil(struct device *dev,
                                             unsigned long *freq);

// Встановити робочу точку пристрою за заданою частотою
int dev_pm_opp_set_rate(struct device *dev, unsigned long target_freq);

// Звільнити посилання на OPP (важливо для управління пам'яттю)
void dev_pm_opp_put(struct dev_pm_opp *opp);
```
