# ⚙️ Дзеркалити діапазон пам'яті процесу: модуль від ioctl до зняття

Це працездатний модуль ядра, який бере в програми діапазон адрес і тримає для нього власну «таблицю пристрою» узгодженою з таблицями процесу: щойно ядро змінює відображення всередині діапазону, записи в табличці зникають, а наступне звертання добудовує їх заново. Справжнього пристрою тут немає — його роль грає звичайний масив у пам'яті модуля, і саме тому в коді не лишається нічого, крім механіки узгодження двох шляхів. Ця механіка й забирає більшу частину зусиль у справжніх драйверах: усе інше в них — черги команд і формат записів, речі місцеві й зрозумілі.

## Задача

Модуль заводить символьний пристрій `/dev/mirror`. Програма відкриває його й через [керуючий канал `ioctl`](book:unix-linux/ioctl-interface) — той самий, яким драйверам передають довільні команди повз `read`/`write`, — каже: «дзеркаль ось цей мій діапазон». З цієї миті модуль підписаний на всі зміни відображень усередині діапазону. Другий `ioctl` імітує звертання пристрою за адресою: якщо в табличці порожньо, модуль іде читати таблиці процесу й заповнює її. Закриття дескриптора все знімає.

Дескриптор тут не прикраса. Він задає час життя всієї конструкції: одна підписка на один відкритий файл, і зняття відбувається рівно там, де ядро гарантує, що більше ніхто цим файлом не користується.

## Ідея

Усе зводиться до трьох речей. Перша — **вузол** `struct mmu_interval_notifier`, вкладений у власну структуру модуля; ядро дає його назад у зворотному виклику, і з нього через `container_of` дістають своє. Друга — **замок оновлення**, звичайний `mutex`, який беруть обидва шляхи: і зворотний виклик знеціннення, і обробник збою. Третя — **послідовне число**, що живе всередині вузла; його ставить знеціннення й звіряє обробник збою, і працює воно точно як [лічильник seqlock](book:algorithms/seqlock) — читач бере число до роботи, звіряє після й перечитує все спочатку, якщо не збіглося.

Складність тут не в кожній із трьох речей окремо, а в тому, що вони мусять зімкнутися в одній точці. Знеціннення міняє число **під замком**; обробник збою звіряє число **під тим самим замком** і, не відпускаючи його, ставить записи. Тільки завдяки цьому між звіркою і записом нічого не встигає вклинитися.

> 🔧 **Навіщо це.** Замок драйвера тут — не захист даних від паралельного доступу, а єдине місце, де перетинаються дві незалежні події: чужа зміна таблиць і власне звертання пристрою. Приберіть його — і дві правильні окремо процедури дадуть запис за адресою, яка вже нікому не належить.

## Код

Спершу домовленість із програмою і власна структура.

```c
/* uapi: те саме визначення включає і модуль, і програма */
struct mirror_range {
        __u64 start;
        __u64 length;
};
#define MIRROR_IOC_ATTACH _IOW('M', 1, struct mirror_range)
#define MIRROR_IOC_FAULT  _IOW('M', 2, struct mirror_range)

#define MIRROR_MAX_PAGES 1024

struct mirror {
        struct mmu_interval_notifier notifier;  /* вузол в інтервальному дереві */
        struct mm_struct *mm;                   /* утримано mmgrab() */
        bool attached;

        struct mutex setup;   /* впорядковує ioctl між собою */
        struct mutex lock;    /* ЗАМОК ОНОВЛЕННЯ: збій ↔ знеціннення */

        unsigned long start;
        unsigned long npages;
        unsigned long *dev_pte;  /* «таблиця пристрою»: номери кадрів або 0 */
        unsigned long *pfns;     /* буфер відповіді hmm_range_fault */
};
```

Замків два, і плутати їх не можна. `lock` бере зворотний виклик, який приходить із-під замків ядра, тож усе, що під ним робиться, має бути коротким. `setup` живе тільки на верхньому рівні `ioctl` і не з'являється в зворотному виклику взагалі — саме тому під ним можна спокійно спати.

Далі зворотний виклик знеціннення.

```c
static bool mirror_invalidate(struct mmu_interval_notifier *mni,
                              const struct mmu_notifier_range *range,
                              unsigned long cur_seq)
{
        struct mirror *m = container_of(mni, struct mirror, notifier);
        unsigned long first, last, addr;

        if (mmu_notifier_range_blockable(range))
                mutex_lock(&m->lock);
        else if (!mutex_trylock(&m->lock))
                return false;   /* тому, хто кликав, піде -EAGAIN */

        mmu_interval_set_seq(mni, cur_seq);

        first = max(range->start, m->start);
        last  = min(range->end, m->start + (m->npages << PAGE_SHIFT));
        for (addr = first; addr < last; addr += PAGE_SIZE)
                m->dev_pte[(addr - m->start) >> PAGE_SHIFT] = 0;

        mutex_unlock(&m->lock);
        return true;
}

static const struct mmu_interval_notifier_ops mirror_ops = {
        .invalidate = mirror_invalidate,
};
```

`mmu_notifier_range_blockable` відповідає на питання «чи вільно тут спати». Коли вільно — беремо замок звичайно. Коли ні, спроба взяти його без сну або вдається, або ми чесно повертаємо `false`: ядро сприйме це як «не зараз», віддасть нагору `-EAGAIN` і спробує пізніше. Багато справжніх драйверів у неблокуючому режимі навіть не пробують і відступають одразу — це теж законно, просто дещо песимістичніше.

Тепер обробник збою: єдине місце, де записи з'являються.

```c
static int mirror_fault(struct mirror *m, unsigned long start, unsigned long len)
{
        unsigned long n = len >> PAGE_SHIFT;
        unsigned long base = (start - m->start) >> PAGE_SHIFT;
        struct hmm_range range = {
                .notifier      = &m->notifier,
                .start         = start,
                .end           = start + len,
                .hmm_pfns      = m->pfns,
                .default_flags = HMM_PFN_REQ_FAULT,
        };
        unsigned long i;
        int ret;

        if (!mmget_not_zero(m->mm))
                return -EFAULT;         /* адресного простору вже немає */

        for (;;) {
                range.notifier_seq = mmu_interval_read_begin(&m->notifier);

                mmap_read_lock(m->mm);
                ret = hmm_range_fault(&range);
                mmap_read_unlock(m->mm);
                if (ret) {
                        if (ret == -EBUSY)
                                continue;       /* зміна саме триває */
                        break;
                }

                mutex_lock(&m->lock);
                if (mmu_interval_read_retry(&m->notifier, range.notifier_seq)) {
                        mutex_unlock(&m->lock);
                        continue;               /* усе спочатку */
                }

                for (i = 0; i < n; i++)
                        m->dev_pte[base + i] = (m->pfns[i] & HMM_PFN_VALID) ?
                                page_to_pfn(hmm_pfn_to_page(m->pfns[i])) : 0;

                mutex_unlock(&m->lock);
                break;
        }

        mmput(m->mm);
        return ret;
}
```

Читає таблиці процесу не сам модуль, а [підсистема дзеркалення `hmm_range_fault`](book:unix-linux/hmm-address-space-mirroring) — вона обходить таблиці, за потреби викликає сторінковий збій і повертає масив номерів кадрів із прапорцями. Вона ж уміє помітити, що посеред її роботи прийшло знеціннення, і повернути `-EBUSY`; це не помилка, а «спробуй іще раз». Заведений у `range` вузол потрібен саме для цього.

Порядок трьох рядків тут не довільний, і кожен переставлений рядок відкриває свою щілину. `mmu_interval_read_begin` іде **перед** читанням таблиць — інакше зміна, що трапилася між читанням і взяттям числа, лишиться невидимою. Він же почекає, поки триває знеціннення: читати таблиці посеред зміни немає сенсу. `mmu_interval_read_retry` і запис у табличку йдуть **під одним взяттям замка**, без жодної проміжної операції.

Реєстрація й зняття.

```c
static long mirror_attach(struct mirror *m, unsigned long start, unsigned long len)
{
        struct mm_struct *mm = current->mm;
        int ret;

        if (m->attached)
                return -EBUSY;
        if (!len || !IS_ALIGNED(start, PAGE_SIZE) || !IS_ALIGNED(len, PAGE_SIZE) ||
            (len >> PAGE_SHIFT) > MIRROR_MAX_PAGES)
                return -EINVAL;

        m->npages = len >> PAGE_SHIFT;
        m->start = start;
        m->dev_pte = kvcalloc(m->npages, sizeof(*m->dev_pte), GFP_KERNEL);
        m->pfns = kvcalloc(m->npages, sizeof(*m->pfns), GFP_KERNEL);
        if (!m->dev_pte || !m->pfns) {
                ret = -ENOMEM;
                goto err_free;
        }

        mmgrab(mm);             /* тримаємо СТРУКТУРУ, а не адресний простір */
        m->mm = mm;

        /* ⚠️ жодного m->lock тут: insert бере mmap_lock на запис */
        ret = mmu_interval_notifier_insert(&m->notifier, mm, start, len,
                                           &mirror_ops);
        if (ret)
                goto err_drop;

        m->attached = true;
        return 0;

err_drop:
        mmdrop(mm);
        m->mm = NULL;
err_free:
        kvfree(m->dev_pte);
        kvfree(m->pfns);
        m->dev_pte = m->pfns = NULL;
        return ret;
}

static int mirror_release(struct inode *inode, struct file *file)
{
        struct mirror *m = file->private_data;

        if (m->attached) {
                mmu_interval_notifier_remove(&m->notifier);
                /* після повернення зворотних викликів немає й не буде */
                mmdrop(m->mm);
        }
        kvfree(m->dev_pte);
        kvfree(m->pfns);
        kfree(m);
        return 0;
}
```

![Структура mm, адресний простір і підписка живуть різні відрізки часу: mmgrab тримає структуру до close(fd), mmget_not_zero перевіряє, чи живий іще простір](/reference/unix-linux/memory/mmu-notifiers/img/mirror-lifetime.svg)

*Три посилання різної природи — і кожне знімається у своєму місці.*

Час життя тут — окрема історія, бо посилань на `mm_struct` два різні. `mmgrab` тримає саму структуру: дешево, і робити це можна надовго. `mmget_not_zero` бере простір — VMA й таблиці — і саме він відповідає «ні», коли процес уже завершився. Тримати простір увесь час підписки не можна: адресний простір не розібрався б, доки живий наш дескриптор, а дескриптор чекав би на смерть процесу. Тому підписка тримає структуру, а простір бере лише на ті кілька мікросекунд, поки читає таблиці.

Смерть процесу підписку не знімає — на неї лише приходить знеціннення на весь простір. Знімати мусимо ми, у `.release`. І сама структура `struct mirror` живе довше за вузол свідомо: `mmu_interval_notifier_remove` повертається лише тоді, коли жоден зворотний виклик уже не виконується на інших ядрах, — тільки після цього пам'ять під вузлом можна віддавати.

Решта — звичайна обв'язка [модуля ядра](book:unix-linux/kernel-modules).

```c
static int mirror_open(struct inode *inode, struct file *file)
{
        struct mirror *m = kzalloc(sizeof(*m), GFP_KERNEL);

        if (!m)
                return -ENOMEM;
        mutex_init(&m->setup);
        mutex_init(&m->lock);
        file->private_data = m;
        return 0;
}

static long mirror_ioctl(struct file *file, unsigned int cmd, unsigned long arg)
{
        struct mirror *m = file->private_data;
        struct mirror_range r;
        long ret;

        if (copy_from_user(&r, (void __user *)arg, sizeof(r)))
                return -EFAULT;

        mutex_lock(&m->setup);
        switch (cmd) {
        case MIRROR_IOC_ATTACH:
                ret = mirror_attach(m, r.start, r.length);
                break;
        case MIRROR_IOC_FAULT:
                if (!m->attached || !r.length ||
                    r.start < m->start || r.length > (m->npages << PAGE_SHIFT) ||
                    r.start + r.length > m->start + (m->npages << PAGE_SHIFT))
                        ret = -EINVAL;
                else
                        ret = mirror_fault(m, r.start, r.length);
                break;
        default:
                ret = -ENOTTY;
        }
        mutex_unlock(&m->setup);
        return ret;
}

static const struct file_operations mirror_fops = {
        .owner          = THIS_MODULE,
        .open           = mirror_open,
        .release        = mirror_release,
        .unlocked_ioctl = mirror_ioctl,
        .compat_ioctl   = compat_ptr_ioctl,
        .llseek         = noop_llseek,
};

static struct miscdevice mirror_dev = {
        .minor = MISC_DYNAMIC_MINOR,
        .name  = "mirror",
        .fops  = &mirror_fops,
};
module_misc_device(mirror_dev);
MODULE_LICENSE("GPL");
```

Збирається це лише там, де ввімкнено дзеркалення адресного простору, тож у `Kconfig` модуля потрібен `depends on HMM_MIRROR`.

## Скільки це коштує

Пошук зачеплених підписок — обхід інтервального дерева, `O(log k)` на `k` вузлів адресного простору плюс довжина відповіді. Ціна знеціннення для системи від того й залежить: платить не кожен підписник, а лише ті, чиї проміжки справді перетнулися зі зміною.

Зате цикл повторів **не обмежений зверху**. Потік, що безперервно міняє відображення в тому самому діапазоні, здатен крутити наш обробник збою скільки завгодно довго: кожен захід читає таблиці й щоразу програє звірку. Практика тут — звужувати діапазон збою до кількох сторінок, щоб перетини траплялися рідше, і рахувати повтори, віддаючи нагору помилку після якоїсь стелі, аби потік користувача не висів вічно.

Робота під `m->lock` теж коштує: доки ми в ній, ядро в зворотному виклику стоїть, а разом із ним стоїть `munmap` або витіснення. Цикл по сторінках у прикладі дешевий, у справжньому драйвері на цьому місці — знімання записів у пристрої й очікування, поки той підтвердить. Саме тому там і потрібен дозвіл спати, і саме тому неблокуючий режим існує окремо.

## Пастки

**`mmu_interval_set_seq` поза замком.** Число має мінятися під тим самим замком, під яким його звіряють, інакше звірка нічого не гарантує. Ставити його треба безумовно на кожному успішному заході в зворотний виклик.

**`mmu_interval_read_begin` після читання таблиць.** Тоді зміна, що трапилася під час читання, потрапляє «до» взятого числа, звірка мовчить, і в табличку осідає застарілий кадр.

**Розрив між звіркою і записом.** Відпустити замок після `read_retry` і взяти знову перед записом — те саме, що не звіряти зовсім: у щілину влазить ціле знеціннення.

**Сон у неблокуючому режимі.** Вдала `mutex_trylock` — не дозвіл спати далі. Ані `GFP_KERNEL`, ані очікування підтвердження від пристрою в цій гілці бути не може; є лише те, що робиться без сну, або чесне `false`.

**Замок оновлення навколо `insert`/`remove`.** Обидві ці функції беруть `mmap_lock` і чекають на зворотні виклики, а зворотний виклик приходить із-під `mmap_lock` і бере `m->lock`. Узяти `m->lock` зовні — і два ядра стануть один проти одного назавжди; про такі перехресні порядки — [замки в ядрі](book:unix-linux/kernel-locking).

**Зняття підписки із самого зворотного виклику.** `mmu_interval_notifier_remove` чекає, поки завершаться всі зворотні виклики, — зокрема той, з якого його покликали.

**Забутий `.release`.** Найдорожча з усіх. Дескриптор закрито, пам'ять модуля звільнено, а вузол лишився в дереві адресного простору: перше ж наступне знеціннення покличе зворотний виклик за адресою, якої вже немає. До того ж утримане `mmgrab` посилання ніколи не віддається, і структура `mm_struct` мертвого процесу висить у системі до перезавантаження.

**`mmgrab` замість `mmget` під час читання таблиць.** Утримана структура ще не означає живий адресний простір. Без `mmget_not_zero` обробник збою полізе в таблиці процесу, якого вже немає.

**`true` без роботи.** Повернене з зворотного виклику `true` ядро розуміє як «підписник упорався»: сторінки підуть далі, а незняті записи в табличці пристрою лишаться вказувати на чужі кадри. Якщо впоратися не вийшло — тільки `false`.
