/* guide/unix/manifest.js — КУРС «Unix крок за кроком» (тип "guide").
   Послідовна доріжка крізь Unix/Linux: спирається на пройдене й поступово поглиблює.

   ДВА ВИДИ КРОКІВ (§1):
   • `ref` на атом довідника reference/unix-linux — коли самодостатня стаття покриває крок як є;
   • ВЛАСНА стаття курсу — коли потрібен кумулятивний кут, якого атом дати не може:
     наскрізний розбір, синтез кількох механізмів, «чому саме так», метод діагностики.
     Файл: guide/unix/<модуль>/<slug>/<slug>.md (тека кроку — в теці свого модуля).

   Слуг курсу `unix` НЕ збігається з довідником `unix-linux` навмисно: ключ прогресу читання —
   "<книга|курс>/<slug>", тож однакові слуги ділили б стан «прочитано».

   15 модулів · 152 кроки: 126 ref (усі 126 атомів довідника, кожен рівно раз) + 26 власних статей.
   Власні — усі detailed:pending (basic за потреби, §3).
   Схема v6 (AUTHORING §2): modules[] → chapters[] → steps[]; нумерація — з порядку масивів. */
(window.__GUIDES__ = window.__GUIDES__ || []).push({
  type: "guide", slug: "unix", title: "Unix крок за кроком",
  modules: [
    { n: 1, slug: "ideia", title: "Що таке Unix і чому саме так", scope: "", chapters: [
      { title: "Засадничі рішення", steps: [
        { ref: "unix-linux/foundations/unix-philosophy", title: "Філософія Unix" },
        { ref: "unix-linux/foundations/everything-is-a-file", title: "«Усе є файлом»" },
        { ref: "unix-linux/foundations/kernel-and-userspace", title: "Ядро й простір користувача" },
        { slug: "why-unix-won", title: "Чому ця модель пережила все інше", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
      { title: "Родовід і що з нього сьогодні", steps: [
        { ref: "unix-linux/foundations/unix-lineage", title: "Родовід Unix" },
        { ref: "unix-linux/foundations/posix-standard", title: "POSIX" },
        { ref: "unix-linux/foundations/kernel-vs-distribution", title: "Ядро й дистрибутив" },
        { ref: "unix-linux/foundations/gnu-userland", title: "Інструментарій GNU" },
        { slug: "reading-a-distribution", title: "Як читати незнайомий дистрибутив", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
    ] },

    { n: 2, slug: "mezha-yadra", title: "Межа з ядром", scope: "", chapters: [
      { title: "Як програма говорить із ядром", steps: [
        { ref: "unix-linux/foundations/syscall-mechanics", title: "Системний виклик" },
        { ref: "unix-linux/foundations/libc-as-gateway", title: "libc як шлюз" },
        { ref: "unix-linux/foundations/monolithic-with-modules", title: "Монолітне ядро з модулями" },
        { slug: "tracing-one-call", title: "Один виклик наскрізь: від рядка коду до драйвера", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
    ] },

    { n: 3, slug: "protses", title: "Процес", scope: "", chapters: [
      { title: "Народження процесу", steps: [
        { ref: "unix-linux/processes/process-model", title: "Процес" },
        { ref: "unix-linux/processes/pid-and-hierarchy", title: "PID і дерево процесів" },
        { ref: "unix-linux/processes/fork-semantics", title: "fork" },
        { ref: "unix-linux/processes/exec-semantics", title: "exec" },
        { slug: "fork-exec-why-two", title: "Чому саме два виклики, а не один", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
      { title: "Завершення й прибирання", steps: [
        { ref: "unix-linux/processes/exit-wait-zombies", title: "Завершення, wait і зомбі" },
        { ref: "unix-linux/processes/orphan-reparenting", title: "Сироти й перепідпорядкування" },
        { ref: "unix-linux/processes/process-states", title: "Стани процесу" },
        { slug: "process-lifecycle-walkthrough", title: "Життя процесу від запуску до прибирання", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
    ] },

    { n: 4, slug: "chas-resursy", title: "Час і ресурси процесу", scope: "", chapters: [
      { title: "Хто коли виконується", steps: [
        { ref: "unix-linux/processes/scheduler-model", title: "Планувальник" },
        { ref: "unix-linux/processes/priority-nice-realtime", title: "Пріоритети й nice" },
        { ref: "unix-linux/processes/threads-as-tasks", title: "Потоки як задачі" },
        { slug: "why-my-process-is-slow", title: "Чому процес «гальмує»: розбір за моделлю", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
      { title: "Обмежити й ізолювати", steps: [
        { ref: "unix-linux/processes/cgroups", title: "cgroups" },
        { ref: "unix-linux/processes/namespaces", title: "Простори імен" },
        { slug: "container-from-primitives", title: "Контейнер із примітивів: звідки береться ізоляція", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
    ] },

    { n: 5, slug: "pamyat", title: "Пам'ять", scope: "", chapters: [
      { title: "Ілюзія власного адресного простору", steps: [
        { ref: "unix-linux/memory/virtual-address-space", title: "Віртуальний адресний простір" },
        { ref: "unix-linux/memory/paging-and-mmu", title: "Сторінки й MMU" },
        { ref: "unix-linux/memory/page-fault", title: "Сторінковий збій" },
        { ref: "unix-linux/memory/copy-on-write", title: "Копіювання при записі" },
        { slug: "memory-illusion", title: "Ілюзія власної пам'яті: на чому вона тримається", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
      { title: "Коли пам'яті мало", steps: [
        { ref: "unix-linux/memory/mmap-model", title: "mmap" },
        { ref: "unix-linux/memory/swap-and-reclaim", title: "Свопінг і витіснення" },
        { ref: "unix-linux/memory/overcommit-and-oom", title: "Overcommit і OOM-killer" },
        { ref: "unix-linux/memory/memory-accounting", title: "VSZ, RSS, PSS" },
        { ref: "unix-linux/memory/allocator-and-kernel", title: "Алокатор і ядро" },
        { slug: "reading-memory-numbers", title: "Як читати цифри пам'яті й не обманутися", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
    ] },

    { n: 6, slug: "fayly", title: "Файли", scope: "", chapters: [
      { title: "Дескриптор як спільний інтерфейс", steps: [
        { ref: "unix-linux/files/file-descriptor", title: "Файловий дескриптор" },
        { ref: "unix-linux/files/open-file-description", title: "Опис відкритого файлу" },
        { ref: "unix-linux/io/socket-as-descriptor", title: "Сокет як дескриптор" },
        { slug: "one-interface-many-things", title: "Один інтерфейс на файл, сокет і пристрій", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
      { title: "Ім'я і вміст — різні речі", steps: [
        { ref: "unix-linux/files/inode-model", title: "Inode" },
        { ref: "unix-linux/files/directory-as-mapping", title: "Каталог як відображення" },
        { ref: "unix-linux/files/hard-and-symbolic-links", title: "Жорсткі й символьні посилання" },
        { ref: "unix-linux/files/path-resolution", title: "Розбір шляху" },
        { slug: "name-is-not-the-file", title: "Ім'я — не файл: наслідки для щоденної роботи", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
      { title: "Файлові системи й довговічність", steps: [
        { ref: "unix-linux/files/vfs-layer", title: "VFS" },
        { ref: "unix-linux/files/mount-model", title: "Монтування" },
        { ref: "unix-linux/files/filesystem-families", title: "Родини файлових систем" },
        { ref: "unix-linux/files/journaling-consistency", title: "Журналювання" },
        { ref: "unix-linux/files/page-cache-durability", title: "Кеш сторінок і fsync" },
        { ref: "unix-linux/files/pseudo-filesystems", title: "Псевдо-ФС" },
        { slug: "when-write-is-really-written", title: "Коли запис справді записаний", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
    ] },

    { n: 7, slug: "obolonka", title: "Оболонка як модель", scope: "", chapters: [
      { title: "Складання процесів", steps: [
        { ref: "unix-linux/shell/shell-role", title: "Що робить оболонка" },
        { ref: "unix-linux/shell/argv-and-environment", title: "argv і оточення" },
        { ref: "unix-linux/shell/standard-streams", title: "Три потоки" },
        { ref: "unix-linux/shell/redirection-model", title: "Перенаправлення" },
        { ref: "unix-linux/shell/pipeline-composition", title: "Конвеєр" },
        { ref: "unix-linux/shell/exit-status", title: "Код виходу" },
        { slug: "shell-is-a-composer", title: "Оболонка як композитор: один конвеєр наскрізь", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
      { title: "Текст, що стає аргументами", steps: [
        { ref: "unix-linux/shell/expansion-and-quoting", title: "Розкриття й лапки" },
        { ref: "unix-linux/shell/job-control", title: "Керування завданнями" },
        { ref: "unix-linux/shell/session-environment", title: "Оточення сеансу" },
        { slug: "why-quoting-bites", title: "Чому лапки кусаються: модель розкриття крок за кроком", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
    ] },

    { n: 8, slug: "vvid-vyvid", title: "Ввід-вивід і очікування", scope: "", chapters: [
      { title: "Як чекати на дані", steps: [
        { ref: "unix-linux/io/blocking-and-nonblocking", title: "Блокуючий і неблокуючий режим" },
        { ref: "unix-linux/io/readiness-vs-completion", title: "Готовність проти завершення" },
        { ref: "unix-linux/io/select-poll-epoll", title: "select, poll, epoll" },
        { ref: "unix-linux/io/io-uring", title: "io_uring" },
        { slug: "one-thread-many-connections", title: "Один потік на багато з'єднань", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
      { title: "Канали, копії й переривання", steps: [
        { ref: "unix-linux/io/pipes-and-fifo", title: "Канали й FIFO" },
        { ref: "unix-linux/io/unix-domain-sockets", title: "Сокети домену Unix" },
        { ref: "unix-linux/io/buffered-and-direct-io", title: "Буферизований і прямий ввід-вивід" },
        { ref: "unix-linux/io/zero-copy", title: "Передача без копіювання" },
        { ref: "unix-linux/io/eintr-and-restart", title: "EINTR" },
        { slug: "io-cost-model", title: "Скільки коштує ввід-вивід", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
    ] },

    { n: 9, slug: "syhnaly", title: "Сигнали й взаємодія", scope: "", chapters: [
      { title: "Сигнал як переривання програми", steps: [
        { ref: "unix-linux/signals-ipc/signal-model", title: "Сигнал" },
        { ref: "unix-linux/signals-ipc/signal-disposition", title: "Диспозиція сигналу" },
        { ref: "unix-linux/signals-ipc/async-signal-safety", title: "Безпека в обробнику" },
        { ref: "unix-linux/signals-ipc/signal-mask-signalfd", title: "Маскування і signalfd" },
        { slug: "graceful-shutdown", title: "Коректне завершення програми", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
      { title: "Домовитися між процесами", steps: [
        { ref: "unix-linux/signals-ipc/ipc-landscape", title: "Огляд засобів взаємодії" },
        { ref: "unix-linux/signals-ipc/posix-shared-memory", title: "Спільна пам'ять" },
        { ref: "unix-linux/signals-ipc/message-queues", title: "Черги повідомлень" },
        { ref: "unix-linux/signals-ipc/eventfd-and-futex", title: "eventfd і futex" },
        { slug: "choosing-ipc", title: "Як обрати спосіб взаємодії під задачу", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
    ] },

    { n: 10, slug: "prava", title: "Права й доступ", scope: "", chapters: [
      { title: "Хто ти для системи", steps: [
        { ref: "unix-linux/permissions/uid-gid-model", title: "Користувачі й групи" },
        { ref: "unix-linux/permissions/permission-bits", title: "Біти прав" },
        { ref: "unix-linux/permissions/umask-and-defaults", title: "umask" },
        { ref: "unix-linux/permissions/setuid-and-privilege", title: "setuid і підвищення прав" },
        { slug: "permission-denied-walkthrough", title: "«Permission denied»: розбір за моделлю", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
      { title: "Тонший контроль", steps: [
        { ref: "unix-linux/permissions/capabilities", title: "Можливості (capabilities)" },
        { ref: "unix-linux/permissions/acl-and-xattr", title: "ACL і xattr" },
        { ref: "unix-linux/permissions/mac-selinux-apparmor", title: "SELinux і AppArmor" },
        { ref: "unix-linux/permissions/device-access-groups", title: "Групи доступу до пристроїв" },
        { slug: "least-privilege-in-practice", title: "Найменші привілеї на практиці", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
    ] },

    { n: 11, slug: "prystroyi-sluzhby", title: "Пристрої, завантаження, служби", scope: "", chapters: [
      { title: "Залізо як файл", steps: [
        { ref: "unix-linux/devices/device-file-model", title: "Файл пристрою" },
        { ref: "unix-linux/devices/major-minor-numbers", title: "Старший і молодший номери" },
        { ref: "unix-linux/devices/sysfs-device-model", title: "Модель пристроїв у sysfs" },
        { ref: "unix-linux/devices/udev-rules", title: "udev" },
        { ref: "unix-linux/devices/kernel-modules", title: "Модулі ядра" },
        { ref: "unix-linux/devices/tty-and-termios", title: "TTY і termios" },
        { ref: "unix-linux/devices/usb-in-linux", title: "USB у Linux" },
        { ref: "unix-linux/devices/interrupts-bottom-halves", title: "Переривання й softirq" },
        { ref: "unix-linux/devices/dma-and-buffers", title: "DMA і буфери" },
        { slug: "device-appears-walkthrough", title: "Що відбувається, коли ти встромив пристрій", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
      { title: "Від живлення до працюючої системи", steps: [
        { ref: "unix-linux/boot-init/boot-chain", title: "Ланцюг завантаження" },
        { ref: "unix-linux/boot-init/bootloader-and-cmdline", title: "Завантажувач і cmdline" },
        { ref: "unix-linux/boot-init/initramfs", title: "initramfs" },
        { ref: "unix-linux/boot-init/init-and-pid1", title: "init і PID 1" },
        { ref: "unix-linux/boot-init/systemd-model", title: "systemd" },
        { ref: "unix-linux/boot-init/service-lifecycle", title: "Життєвий цикл служби" },
        { ref: "unix-linux/boot-init/socket-activation", title: "Активація за сокетом" },
        { ref: "unix-linux/boot-init/journald-logging", title: "journald" },
        { slug: "from-power-to-login", title: "Від живлення до запрошення входу", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
    ] },

    { n: 12, slug: "merezha", title: "Мережа в ядрі", scope: "", chapters: [
      { title: "Шлях даних крізь стек", steps: [
        { ref: "unix-linux/networking/network-stack", title: "Мережевий стек" },
        { ref: "unix-linux/networking/interfaces-and-addresses", title: "Інтерфейси й адреси" },
        { ref: "unix-linux/networking/socket-api-linux", title: "Сокети в Linux" },
        { ref: "unix-linux/networking/routing-decision", title: "Рішення про маршрут" },
        { ref: "unix-linux/networking/netfilter-model", title: "netfilter" },
        { ref: "unix-linux/networking/name-resolution-path", title: "Розв'язання імені" },
        { ref: "unix-linux/networking/network-namespaces", title: "Мережеві простори імен" },
        { ref: "unix-linux/networking/tun-tap", title: "TUN/TAP" },
        { slug: "packet-journey", title: "Шлях пакета крізь Linux", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
    ] },

    { n: 13, slug: "zapusk", title: "Від файлу до процесу", scope: "", chapters: [
      { title: "Що відбувається при запуску", steps: [
        { ref: "unix-linux/linking/elf-structure", title: "ELF" },
        { ref: "unix-linux/linking/static-and-dynamic-linking", title: "Статичне й динамічне лінкування" },
        { ref: "unix-linux/linking/dynamic-loader", title: "Динамічний завантажувач" },
        { ref: "unix-linux/linking/soname-versioning", title: "SONAME і версіонування" },
        { ref: "unix-linux/linking/library-search-order", title: "Порядок пошуку бібліотек" },
        { ref: "unix-linux/linking/symbol-resolution", title: "Розв'язання символів" },
        { ref: "unix-linux/linking/plt-and-got", title: "PLT і GOT" },
        { ref: "unix-linux/linking/library-abi-compat", title: "Сумісність ABI бібліотеки" },
        { slug: "why-it-runs-here-not-there", title: "Чому запускається в тебе й не запускається в них", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
    ] },

    { n: 14, slug: "sposterezhennia", title: "Побачити систему", scope: "", chapters: [
      { title: "Механізми самопоказу", steps: [
        { ref: "unix-linux/observability/proc-filesystem", title: "/proc" },
        { ref: "unix-linux/observability/ptrace-model", title: "ptrace" },
        { ref: "unix-linux/observability/syscall-tracing", title: "Трасування системних викликів" },
        { ref: "unix-linux/observability/perf-events", title: "perf" },
        { ref: "unix-linux/observability/ftrace-tracepoints", title: "ftrace і трасувальні точки" },
        { ref: "unix-linux/observability/ebpf", title: "eBPF" },
        { ref: "unix-linux/observability/core-dump", title: "Аварійний дамп" },
        { ref: "unix-linux/observability/load-and-pressure", title: "Навантаження й тиск на ресурси" },
        { slug: "diagnosis-method", title: "Метод діагностики: від симптому до причини", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
    ] },

    { n: 15, slug: "postachannia", title: "Постачання програм", scope: "", chapters: [
      { title: "Як програма доходить до користувача", steps: [
        { ref: "unix-linux/packaging/package-manager-model", title: "Модель пакетного менеджера" },
        { ref: "unix-linux/packaging/deb-and-rpm", title: "deb і rpm" },
        { ref: "unix-linux/packaging/repositories-and-trust", title: "Репозиторії й довіра" },
        { ref: "unix-linux/packaging/dependency-resolution", title: "Розв'язання залежностей" },
        { ref: "unix-linux/packaging/fhs-layout", title: "Ієрархія файлової системи" },
        { ref: "unix-linux/packaging/self-contained-bundles", title: "AppImage, Flatpak, Snap" },
        { ref: "unix-linux/packaging/containers-vs-packages", title: "Контейнер проти пакунка" },
        { slug: "shipping-a-linux-app", title: "Доставити свою програму на чужий Linux", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
    ] },
  ]
});
