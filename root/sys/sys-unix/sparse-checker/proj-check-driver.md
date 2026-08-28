# ⚙️ Приклад виправлення помилки в драйвері

Припустимо, під час компіляції вашого нового драйвера з прапорцем перевірки `make C=1` Sparse видає такі попередження:

```
drivers/misc/my_driver.c:42:19: warning: incorrect type in assignment (different address spaces)
drivers/misc/my_driver.c:42:19:    expected void *regs
drivers/misc/my_driver.c:42:19:    got void [noderef] __iomem *
drivers/misc/my_driver.c:45:24: warning: incorrect type in argument 1 (different address spaces)
drivers/misc/my_driver.c:45:24:    expected void const volatile [noderef] __iomem *addr
drivers/misc/my_driver.c:45:24:    got void *regs
```

**Що сталося?**
Попереджень два, і причина в них спільна, тож читати їх треба разом і згори вниз. Перше — на **присвоєнні**: `ioremap()` повертає `void __iomem *`, а поле, куди ви кладете результат, оголошене звичайним `void *`; для Sparse це перехід між адресними просторами, і саме тут анотація губиться. Друге — на **аргументі**: `readl()` очікує `__iomem`-вказівник, а дістає вже знеанотований `void *` із того самого поля. Друге попередження — лише наслідок першого; виправляти треба місце, на яке вказує перше.

**Хибний код:**
:::code proj-check-driver/c/part.c

**Як виправити?**
Проблема полягає у визначенні структури. Поле `regs` повинне явно вказувати, що воно адресує I/O пам'ять. Одна правка в оголошенні прибирає обидва попередження — саме це й підтверджує, що вони мали спільний корінь.

**Правильний код:**
:::code proj-check-driver/c/part-2.c
Таке виправлення не просто "затикає" аналізатор, воно робить код самодокументованим і зрозумілим для інших розробників.
