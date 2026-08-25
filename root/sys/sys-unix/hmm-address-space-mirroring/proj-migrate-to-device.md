# ⚙️ Переселити діапазон у пам'ять пристрою й повернути назад

Зберемо ядерний модуль, який уміє рівно дві речі: за командою забрати шматок анонімної пам'яті процесу до власної пам'яті «плати», а коли процесор торкнеться тих самих адрес — тихо привезти його назад. Заліза під ним немає навмисно: тоді в коді не лишається нічого, крім тієї механіки, якої з опису самого підходу не видно, — реєстрації описувачів кадрів, лічильників на них, посторінкових відмов і того, чому найпростіше згортання підвисає назавжди.

Мова тут не обговорюється: це модуль ядра, отже C. Код написано на ядро 6.12; усередині ядра [сталого API немає](topic:sys-unix/kernel-abi-stability), а саме ця його частина міняється часто — про свіжі зміни сказано наприкінці.

## Задача

Модуль реєструє 128 МіБ «пам'яті пристрою» й приймає команду «забери діапазон `[addr, addr + len)` до себе». Після неї програма не міняється ані на рядок: ті самі вказівники, ті самі читання. Просто перше ж читання з процесора коштуватиме мікросекунди — бо його обслужить наш обробник збою, — а прискорювач читатиме ці сторінки з локальної пам'яті.

Уся конструкція складається з трьох шматків, і кожен наступний спирається на попередній: описувачі кадрів для пам'яті плати, власний розподільник цих кадрів, три такти переселення.

## Реєстрація: попросити діру, а не пам'ять

Ядро вміє працювати лише з кадрами, у яких є `struct page`. Щоб такі описувачі з'явилися на пам'ять плати, треба зайняти шматок **фізичного простору адрес** — не оперативної пам'яті, а саме простору номерів — і сказати, що на ньому тепер живе [модель фізичної пам'яті](topic:sys-unix/sparsemem-and-vmemmap) з особливою позначкою.

```c
// SPDX-License-Identifier: GPL-2.0
#include <linux/hmm.h>
#include <linux/ioport.h>
#include <linux/memremap.h>
#include <linux/migrate.h>
#include <linux/mm.h>
#include <linux/module.h>

struct pereselnyk {
	struct dev_pagemap  pagemap;
	struct resource    *res;
	spinlock_t          lock;
	struct page        *free_list;   /* однозв'язний список вільних кадрів */
	unsigned long       nfree;
};

static void pereselnyk_page_free(struct page *pg);
static vm_fault_t pereselnyk_migrate_to_ram(struct vm_fault *vmf);

static const struct dev_pagemap_ops pereselnyk_pagemap_ops = {
	.page_free	= pereselnyk_page_free,
	.migrate_to_ram	= pereselnyk_migrate_to_ram,
};

static int pereselnyk_reserve(struct pereselnyk *p, unsigned long size)
{
	unsigned long pfn, first, last;
	void *addr;

	/* Просимо ДІРУ у фізичному просторі адрес: місце, де немає ні
	   оперативної пам'яті, ні вікон інших пристроїв. Байтів нам звідти
	   не треба — треба номери, на які ядро заведе описувачі.          */
	p->res = request_free_mem_region(&iomem_resource, size, "pereselnyk");
	if (IS_ERR(p->res))
		return PTR_ERR(p->res);

	p->pagemap.type        = MEMORY_DEVICE_PRIVATE;
	p->pagemap.range.start = p->res->start;
	p->pagemap.range.end   = p->res->end;
	p->pagemap.nr_range    = 1;
	p->pagemap.ops         = &pereselnyk_pagemap_ops;
	p->pagemap.owner       = p;   /* «ці кадри мої» — на цьому полі тримається
					 половина правильної поведінки, див. нижче */

	addr = memremap_pages(&p->pagemap, numa_node_id());
	if (IS_ERR(addr)) {
		release_mem_region(p->res->start, resource_size(p->res));
		return PTR_ERR(addr);
	}

	/* Описувачі вже є, і всі — з НУЛЬОВИМ лічильником посилань.
	   Складаємо їх у свій вільний список: розподільник цієї пам'яті — ми. */
	first = PHYS_PFN(p->res->start);
	last  = PHYS_PFN(p->res->end);
	spin_lock(&p->lock);
	for (pfn = first; pfn <= last; pfn++) {
		struct page *pg = pfn_to_page(pfn);

		pg->zone_device_data = p->free_list;
		p->free_list = pg;
		p->nfree++;
	}
	spin_unlock(&p->lock);
	return 0;
}
```

Варто спинитися на тому, що ці фізичні номери — несправжні. Вони не ведуть ні в яке вікно на шині, і читати за ними ніхто ніколи не буде: процесор до цієї пам'яті все одно не дотягнеться, а плата адресує свою пам'ять по-своєму. Номер кадру тут — лише спосіб дати ядру за що вхопитися, а перерахунок «описувач → адреса в пам'яті плати» драйвер робить сам, звичайним відніманням початку діапазону (це і є `local_offset_of()` нижче). Саме тому просити треба **вільний** шматок простору адрес: якби він накладався на щось справжнє, два різні описувачі описували б одні байти.

Поле `owner` виглядає дрібницею, а насправді це ключ, за яким решта ядра відрізняє «наші» сторінки від сторінок сусіднього драйвера. Без нього обидва механізми, заради яких усе затівалося, поводяться протилежно задуманому.

## Свій розподільник: `zone_device_page_init` і `page_free`

Кадр плати не береться зі [сторінкового розподільника](topic:sys-unix/physical-page-allocator) — його роздаємо ми. Але лічильник посилань на описувачі веде ядро, і повернути кадр у пул можна рівно одним способом: дочекатися, поки ядро само покличе `page_free`.

```c
static struct page *devpage_alloc(struct pereselnyk *p)
{
	struct page *pg;

	spin_lock(&p->lock);
	pg = p->free_list;
	if (pg) {
		p->free_list = pg->zone_device_data;
		p->nfree--;
	}
	spin_unlock(&p->lock);
	if (!pg)
		return NULL;

	/* Оце — і є «взяти кадр»: лічильник з нуля стає одиницею, сторінка
	   ЗАМИКАЄТЬСЯ, а pagemap дістає посилання, яке потім не дасть
	   згортанню пройти повз живий кадр.                              */
	zone_device_page_init(pg);
	return pg;
}

/* Ядро кличе це, коли лічильник кадру впав до нуля. Спати не можна:
   останнє посилання цілком може віддати хтось із контексту, де сон
   заборонений, — звідси spinlock, а не мутекс.                      */
static void pereselnyk_page_free(struct page *pg)
{
	struct pereselnyk *p = pg->pgmap->owner;

	spin_lock(&p->lock);
	pg->zone_device_data = p->free_list;
	p->free_list = pg;
	p->nfree++;
	spin_unlock(&p->lock);
}
```

Виходить замкнене коло, у якому лічильник посилань міняється всього двічі — і обидва рази не там, де очікуєш. Взяти кадр значить поставити одиницю; віддати його — не «покласти назад», а дозволити одиниці впасти в нуль.

![П'ять станів описувача кадру плати по колу: у вільному пулі з нульовим лічильником, узятий викликом zone_device_page_init із лічильником один і замкненою сторінкою, вписаний у таблицю процесу відсутнім записом, повернений обробником migrate_to_ram із падінням лічильника до нуля, і нарешті відданий у пул зворотним викликом page_free](img/devpage-life.svg)

*Лічильник тут відповідає не на питання «скільки пам'яті зайнято», а на єдине питання «чи належить цей кадр комусь просто зараз».*

## Переселення: що робиться між тактами

Робота драйвера між першим і другим тактом виглядає як цикл копіювання, але половина його рядків — про сторінки, які **не** поїдуть.

```c
static void copy_to_device(struct migrate_vma *args, struct pereselnyk *p)
{
	unsigned long i;

	for (i = 0; i < args->npages; i++) {
		struct page *spage = migrate_pfn_to_page(args->src[i]);
		struct page *dpage;
		int ret;

		/* Ядро вже вирішило, що цю сторінку рухати не можна. Єдина
		   правильна відповідь — лишити dst нулем і не чіпати нічого. */
		if (!(args->src[i] & MIGRATE_PFN_MIGRATE))
			continue;

		dpage = devpage_alloc(p);
		if (!dpage)
			continue;          /* кадри скінчилися — теж просто пропуск */

		/* spage == NULL при виставленій позначці — не помилка, а дірка:
		   сторінки ще не існує, бо процес її не торкався. Переселяємо
		   порожнечу, і перший дотик станеться вже на платі.           */
		if (spage)
			ret = dma_copy_to_device(p, dpage, spage);
		else
			ret = dma_zero_device_page(p, dpage);

		if (ret) {
			/* Кадр наш і лише наш: у dst його не буде, отже ядро про
			   нього не дізнається. Розмикаємо самі — це нас замкнув
			   zone_device_page_init().                              */
			unlock_page(dpage);
			put_page(dpage);
			continue;
		}

		args->dst[i] = migrate_pfn(page_to_pfn(dpage));
		if ((args->src[i] & MIGRATE_PFN_WRITE) ||
		    (!spage && (args->vma->vm_flags & VM_WRITE)))
			args->dst[i] |= MIGRATE_PFN_WRITE;
	}
}
```

Тепер самі такти. Найважливіше в цьому шматку — цикл **після** другого такту: він виглядає надлишковим і саме тому його найчастіше не пишуть.

```c
static int migrate_range_to_device(struct pereselnyk *p, struct mm_struct *mm,
				   unsigned long start, unsigned long len)
{
	unsigned long npages = len >> PAGE_SHIFT, i;
	unsigned long *src, *dst;
	struct migrate_vma args;
	struct vm_area_struct *vma;
	int ret;

	src = kvcalloc(npages, sizeof(*src), GFP_KERNEL);
	dst = kvcalloc(npages, sizeof(*dst), GFP_KERNEL);
	if (!src || !dst) {
		ret = -ENOMEM;
		goto out;
	}

	mmap_read_lock(mm);
	vma = vma_lookup(mm, start);
	if (!vma || start + len > vma->vm_end) {
		ret = -EINVAL;
		goto out_unlock;
	}

	args = (struct migrate_vma){
		.vma		= vma,
		.start		= start,
		.end		= start + len,
		.src		= src,
		.dst		= dst,
		.flags		= MIGRATE_VMA_SELECT_SYSTEM,
		.pgmap_owner	= p,   /* щоб скасування від ЦЬОГО переселення
					  наш власний сповіщувач упізнав і
					  не викидав свої ж таблиці            */
	};

	ret = migrate_vma_setup(&args);
	if (ret)
		goto out_unlock;

	copy_to_device(&args, p);      /* довга частина: рушій прямого доступу */
	migrate_vma_pages(&args);

	/* Другий такт міг не вдатися ПОСТОРІНКОВО: комусь із сусідів
	   пощастило торкнутися адреси раніше, і позначку погашено вже тут.
	   Такий кадр у таблицю процесу не потрапив — вписати його в
	   апаратуру означало б дати платі писати в нічию пам'ять.
	   Прибирати його самим НЕ треба: третій такт розімкне й віддасть
	   посилання за нас, а зайвий put_page() віддав би в пул кадр,
	   який ще комусь належить.                                        */
	for (i = 0; i < npages; i++) {
		struct page *dpage = migrate_pfn_to_page(dst[i]);

		if (dpage && (src[i] & MIGRATE_PFN_MIGRATE))
			device_pt_install(p, start + (i << PAGE_SHIFT), dpage);
	}

	migrate_vma_finalize(&args);
	ret = 0;
out_unlock:
	mmap_read_unlock(mm);
out:
	kvfree(src);
	kvfree(dst);
	return ret;
}
```

Асиметрія тут навмисна й вона плутає найбільше: **кадр, який ядро взяло в роботу, прибирає ядро; кадр, про який ядро не дізналося, прибираємо ми.** Межа проходить рівно по масиву `dst`: поклали туди номер — і кадр більше не ваш.

## Дорога назад

Обробник дотику — це те саме переселення, тільки в інший бік, на одну сторінку й із двома додатковими полями.

```c
static vm_fault_t pereselnyk_migrate_to_ram(struct vm_fault *vmf)
{
	struct pereselnyk *p = vmf->page->pgmap->owner;
	unsigned long addr = vmf->address & PAGE_MASK;
	unsigned long src_pfn = 0, dst_pfn = 0;
	struct page *spage, *dpage;
	struct migrate_vma args = {
		.vma		= vmf->vma,
		.start		= addr,
		.end		= addr + PAGE_SIZE,
		.src		= &src_pfn,
		.dst		= &dst_pfn,
		.flags		= MIGRATE_VMA_SELECT_DEVICE_PRIVATE,
		.pgmap_owner	= p,
		/* Сторінка, на якій стався збій, УЖЕ замкнена й УЖЕ має зайве
		   посилання — від збою. Без цього поля перевірка «чи ніхто її
		   не тримає» побачила б це посилання й відмовилася рухати
		   сторінку, а збій повторювався б вічно.                    */
		.fault_page	= vmf->page,
	};

	if (migrate_vma_setup(&args))
		return VM_FAULT_SIGBUS;
	if (!args.cpages)
		return 0;   /* хтось випередив: сторінка вже в пам'яті, збій повторять */

	spage = migrate_pfn_to_page(src_pfn);
	dpage = alloc_page_vma(GFP_HIGHUSER, vmf->vma, addr);
	if (!dpage)
		goto fail;
	lock_page(dpage);
	if (dma_copy_to_host(p, dpage, spage)) {
		unlock_page(dpage);
		put_page(dpage);
		goto fail;
	}
	dst_pfn = migrate_pfn(page_to_pfn(dpage));

	migrate_vma_pages(&args);
	device_pt_drop(p, addr);       /* плата сюди більше не ходить */
	migrate_vma_finalize(&args);
	return 0;

fail:
	/* dst порожній: третій такт просто поверне на місце те, що було. */
	migrate_vma_finalize(&args);
	return VM_FAULT_SIGBUS;
}
```

> 🔧 **Навіщо це.** Тут закінчується вся ілюзія прозорості: `SIGBUS` із цього обробника — не діагностика для розробника драйвера, а сигнал, який отримає програма, що просто читала свою пам'ять. Тому в дорозі назад немає жодного шляху, де можна відповісти «спробуйте пізніше»: або сторінка приїхала, або процесові кінець. Звідси й `__GFP_NOFAIL` у згортанні нижче.

## Згортання, яке підвисає

Найпростіший `pereselnyk_exit()` виглядає як `memunmap_pages()` плюс `release_mem_region()`. Він працюватиме рівно доти, доки жодна сторінка не переїхала на плату, — а далі повисне намертво.

Причина в тому самому лічильнику: кожен виданий кадр тримає посилання на `pagemap`, і `memunmap_pages()` гасить це посилання й **чекає**, доки останній кадр не повернеться. Кадри ж повернуться лише тоді, коли процеси доторкнуться своїх сторінок, а вони можуть не доторкнутися ніколи. Отже, виселяти мусимо ми — і не по одному процесу, а по номерах кадрів, бо власників у нашої пам'яті може бути багато.

```c
static void pereselnyk_evict_all(struct pereselnyk *p)
{
	unsigned long npages = PHYS_PFN(resource_size(p->res));
	unsigned long start  = PHYS_PFN(p->res->start);
	unsigned long *src, *dst, i;

	src = kvcalloc(npages, sizeof(*src), GFP_KERNEL | __GFP_NOFAIL);
	dst = kvcalloc(npages, sizeof(*dst), GFP_KERNEL | __GFP_NOFAIL);

	/* Ті самі такти, але без vma: сторінки перебираємо за номерами. */
	migrate_device_range(src, start, npages);

	for (i = 0; i < npages; i++) {
		struct page *spage = migrate_pfn_to_page(src[i]);
		struct page *dpage;

		if (!spage || !(src[i] & MIGRATE_PFN_MIGRATE))
			continue;

		/* Відступати нікуди: дані з плати мусять доїхати. */
		dpage = alloc_page(GFP_HIGHUSER | __GFP_NOFAIL);
		lock_page(dpage);
		dma_copy_to_host(p, dpage, spage);
		dst[i] = migrate_pfn(page_to_pfn(dpage));
	}

	migrate_device_pages(src, dst, npages);
	migrate_device_finalize(src, dst, npages);
	kvfree(src);
	kvfree(dst);
}

static void pereselnyk_shutdown(struct pereselnyk *p)
{
	pereselnyk_evict_all(p);
	memunmap_pages(&p->pagemap);      /* аж тепер він не повисне */
	release_mem_region(p->res->start, resource_size(p->res));
}
```

## Дзеркалення того, що не переїхало

Частина сторінок діапазону лишиться в системній пам'яті, і драйвер бачить їх через `hmm_range_fault()`. Тут є поле, забути яке — значить зруйнувати все, що зроблено вище, і не отримати жодного повідомлення про помилку:

```c
	struct hmm_range range = {
		.notifier          = &mirror->sub,
		.start             = addr,
		.end               = addr + len,
		.hmm_pfns          = pfns,
		.default_flags     = HMM_PFN_REQ_FAULT,
		.dev_private_owner = p,   /* «свої сторінки не чіпай» */
	};
```

Механіка проста. Натрапивши на відсутній запис приватної сторінки пристрою, ядро звіряє власника кадру з `dev_private_owner`. Збіглося — воно просто віддає номер кадру плати, і драйвер вписує в апаратуру локальну адресу. Не збіглося (а `NULL` не збігається ніколи) — сторінка вважається недосяжною, ядро тягне її назад збоєм, і ваш власний `migrate_to_ram()` слухняно повертає в оперативну пам'ять усе, що ви щойно переселили. Симптом — переселення, яке «нічого не пришвидшило».

Наслідок для коду читання відповідей: у масиві тепер зустрічаються кадри обох родів, і розрізняти їх треба явно.

```c
	struct page *pg = hmm_pfn_to_page(pfns[i]);

	if (is_device_private_page(pg))
		dev_addr = local_offset_of(p, pg);       /* адреса в пам'яті плати */
	else
		dev_addr = dma_map_page(dev, pg, ...);   /* адреса на шині */
```

## Пастки

**Позначка `MIGRATE_PFN_MIGRATE` гасне двічі, і це різні події.** Перший раз — у першому такті: сторінка [закріплена](topic:sys-unix/page-pinning-gup) під ввід-вивід, відображена в кількох процесів, файлова, велика. Другий раз — усередині другого такту, коли конкретна сторінка не дійшла до кінця. Перевіряти треба обидва рази, і код у цих місцях різний: до другого такту кадр призначення ще ваш, після нього — вже ні.

**`spage == NULL` при виставленій позначці — нормальний випадок, а не збій.** Так виглядає ділянка, яку процес виділив, але не торкався: сторінки немає, переселяти нема чого, зате місце для неї одразу можна віддати платі. Драйвер, що пропускає такі записи, змушує програму спершу пройтися по всій пам'яті процесором — тобто робить рівно ту зайву роботу, від якої тікали.

**Кадр плати не звільняють через `__free_page()`.** Такого шляху не існує взагалі: єдиний спосіб — довести лічильник до нуля, після чого ядро само покличе ваш `page_free`. І навпаки: `put_page()` на кадр, який уже стоїть у таблиці процесу, віддає в пул чужу власність. Наступне переселення видасть цей самий кадр іншому діапазону, і два адресні простори мовчки поділять одні байти.

**Виділений кадр приходить замкненим.** `zone_device_page_init()` не лише ставить лічильник в одиницю, а й замикає сторінку. Кадр, який ви відкинули на півдорозі, треба розімкнути самому; кадр, який пішов у `dst`, розімкне третій такт. Переплутати — значить або підвісити наступного, хто чекає на цій сторінці, або впасти на `VM_BUG_ON`.

**`pgmap_owner` у `migrate_vma` і `dev_private_owner` у `hmm_range` — різні поля, і обидва не мають розумного значення за замовчуванням.** Перше потрапляє в подію [сповіщувача](topic:sys-unix/mmu-notifiers), яку розсилає саме переселення: упізнавши там себе, драйвер не викидає власні таблиці на власну ж роботу. Друге керує тим, чи вважати ваші сторінки видимими для вас. Мовчазний `NULL` у будь-якому з них не ламає складання й не пише в журнал — він лише робить систему повільною.

**Копіювання довге, а `mmap`-замок узято на читання.** Між першим і третім тактом мапу пам'яті процесу тримають, тож усе, що всередині, має бути коротким або асинхронним: рушій прямого доступу запускають, а на його завершення чекають перед `migrate_vma_pages()`, а не в циклі виділення. Про те, що можна робити під яким замком, — [замки в ядрі й атомарний контекст](topic:sys-unix/kernel-locking); `page_free` при цьому взагалі не має права спати, бо останнє посилання іноді віддають із контексту, де сон заборонений.

**Переїзд туди-сюди дорожчий за все інше разом.** Один збій — одиниці мікросекунд; цикл, де процесор і плата по черзі торкаються тих самих сторінок, перетворює обчислення на безперервне копіювання через шину. Тому переселяють великими діапазонами й за прямими підказками програми, а не за кожним промахом.

**Код прив'язаний до версії.** `migrate_device_range()` з'явився лише в 6.1 — до нього виселяти пам'ять перед вивантаженням доводилося обхідними шляхами. У ядрах, свіжіших за 6.12, поле `pgmap` переїхало зі `struct page` у `struct folio`, і замість `pg->pgmap` пишуть `page_pgmap(pg)`; там-таки з'явилися складені сторінки пам'яті пристрою. Це звичайна для ядра рухливість, і збирати такий модуль поза деревом ядра доводиться з оглядкою на конкретні заголовки.
