/* reference/unix-linux/manifest.js — ДОВІДНИК «Unix і Linux» (тип "reference").
   Довідник — 4-й вид книги (AUTHORING §1): рукотворна система, описана як довідка.
   Схема — як у book (§2 v6): sections[] → topics[], статус на КОЖНУ версію.

   ПРИНЦИП ДОБОРУ ТЕМ: суть, а не наповнення. Ціль — ЯК СИСТЕМА ВЛАШТОВАНА Й ЧОМУ САМЕ ТАК,
   а не перелік команд і ключів. Кожна тема відповідає на «що це за механізм, яку задачу
   він розв'язує і які наслідки має», а команди з'являються лише як ілюстрація механізму.
   Тому тут є «Перенаправлення як робота з дескрипторами», але немає «10 ключів ls».

   126 тем у 14 розділах. Усі заведено як detailed:pending (basic — за потреби, §3).
   Послідовна доріжка по цих атомах — курс guide/unix. */
(window.__BOOKS__ = window.__BOOKS__ || []).push({
  type: "reference", slug: "unix-linux", title: "Unix і Linux",
  sections: [
    { slug: "foundations", title: "Ідея та родовід", scope: "Звідки Unix узявся, які рішення в ньому засадничі й що з них випливає для всього іншого.",
      topics: [
        { slug: "unix-philosophy", title: "Філософія Unix: малі програми, що складаються", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "everything-is-a-file", title: "«Усе є файлом»: один інтерфейс на все", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "kernel-and-userspace", title: "Ядро й простір користувача", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "syscall-mechanics", title: "Системний виклик: як програма просить ядро", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "unix-lineage", title: "Родовід Unix: AT&T, BSD і поява Linux", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "posix-standard", title: "POSIX: що саме стандартизовано", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "kernel-vs-distribution", title: "Ядро, дистрибутив і що між ними", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "gnu-userland", title: "Інструментарій GNU і чому «GNU/Linux»", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "libc-as-gateway", title: "libc як шлюз до ядра", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "monolithic-with-modules", title: "Монолітне ядро з модулями: вибір Linux", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "processes", title: "Процес", scope: "Процес як головна одиниця системи: як народжується, як планується, як ізолюється.",
      topics: [
        { slug: "process-model", title: "Процес: що це насправді", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "pid-and-hierarchy", title: "PID і дерево процесів", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "fork-semantics", title: "fork: розмноження процесу", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "exec-semantics", title: "exec: заміна образу", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "exit-wait-zombies", title: "Завершення, wait і зомбі", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "orphan-reparenting", title: "Сироти й перепідпорядкування", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "process-states", title: "Стани процесу і що означає стан D", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "scheduler-model", title: "Планувальник: як ядро ділить час", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "priority-nice-realtime", title: "Пріоритети, nice і реальночасові класи", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "threads-as-tasks", title: "Потоки в Linux: задача як одиниця планування", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "cgroups", title: "cgroups: облік і обмеження ресурсів", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "namespaces", title: "Простори імен: ізоляція погляду на систему", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "memory", title: "Пам'ять процесу", scope: "Віртуальна пам'ять як механізм: чому адреси брешуть і що з цього виходить.",
      topics: [
        { slug: "virtual-address-space", title: "Віртуальний адресний простір процесу", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "paging-and-mmu", title: "Сторінки, таблиці сторінок і MMU", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "page-fault", title: "Сторінковий збій: чому все ліниве", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "mmap-model", title: "mmap: файл і пам'ять як одне", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "copy-on-write", title: "Копіювання при записі", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "swap-and-reclaim", title: "Свопінг і витіснення сторінок", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "overcommit-and-oom", title: "Overcommit і OOM-killer", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "memory-accounting", title: "Як міряти пам'ять процесу: VSZ, RSS, PSS", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "allocator-and-kernel", title: "Звідки алокатор бере пам'ять: brk і mmap", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "files", title: "Файли й файлові системи", scope: "Що таке файл у Unix, як імена відв'язані від вмісту й на чому тримається узгодженість.",
      topics: [
        { slug: "file-descriptor", title: "Файловий дескриптор", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "open-file-description", title: "Опис відкритого файлу: що спільне після fork", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "inode-model", title: "Inode: файл без імені", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "directory-as-mapping", title: "Каталог як відображення імен", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "hard-and-symbolic-links", title: "Жорсткі й символьні посилання", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "path-resolution", title: "Розбір шляху", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "vfs-layer", title: "VFS: спільний шар над файловими системами", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "mount-model", title: "Монтування й дерево монтувань", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "filesystem-families", title: "Родини файлових систем: ext4, XFS, Btrfs, F2FS", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "journaling-consistency", title: "Журналювання й узгодженість після збою", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "page-cache-durability", title: "Кеш сторінок, fsync і довговічність запису", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "pseudo-filesystems", title: "Псевдо-ФС: procfs, sysfs, tmpfs, devtmpfs", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "io", title: "Ввід-вивід і очікування", scope: "Як програма чекає на дані й чому саме тут вирішується, скільки з'єднань вона потягне.",
      topics: [
        { slug: "blocking-and-nonblocking", title: "Блокуючий і неблокуючий режим", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "readiness-vs-completion", title: "Готовність проти завершення: дві моделі вводу-виводу", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "select-poll-epoll", title: "select, poll, epoll: чекати на багато джерел", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "io-uring", title: "io_uring: кільця подань і завершень", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "pipes-and-fifo", title: "Канали й іменовані канали", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "unix-domain-sockets", title: "Сокети домену Unix і передача дескрипторів", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "socket-as-descriptor", title: "Сокет як дескриптор", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "buffered-and-direct-io", title: "Буферизований і прямий ввід-вивід", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "zero-copy", title: "Передача без копіювання: sendfile і splice", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "eintr-and-restart", title: "EINTR: перервані виклики й перезапуск", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "signals-ipc", title: "Сигнали й взаємодія процесів", scope: "Асинхронні сповіщення та способи, якими процеси домовляються між собою.",
      topics: [
        { slug: "signal-model", title: "Сигнал: асинхронне сповіщення", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "signal-disposition", title: "Диспозиція сигналу: обробник, ігнорування, типова дія", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "async-signal-safety", title: "Що взагалі можна робити в обробнику сигналу", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "signal-mask-signalfd", title: "Маскування сигналів і signalfd", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "ipc-landscape", title: "Огляд засобів взаємодії: що коли обирати", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "posix-shared-memory", title: "Спільна пам'ять POSIX", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "message-queues", title: "Черги повідомлень", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "eventfd-and-futex", title: "eventfd і futex: сповіщення й дешеве очікування", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "permissions", title: "Права й ідентичність", scope: "Хто такий процес з погляду системи і як вирішується, що йому дозволено.",
      topics: [
        { slug: "uid-gid-model", title: "Користувачі, групи й ідентичність процесу", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "permission-bits", title: "Біти прав і як їх перевіряють", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "setuid-and-privilege", title: "setuid, setgid і підвищення прав", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "umask-and-defaults", title: "umask і типові права новоствореного", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "capabilities", title: "Можливості (capabilities) замість всесильного root", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "acl-and-xattr", title: "Розширені права (ACL) і атрибути (xattr)", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "mac-selinux-apparmor", title: "Обов'язковий контроль доступу: SELinux і AppArmor", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "device-access-groups", title: "Доступ до пристроїв через групи: dialout, plugdev", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "devices", title: "Пристрої та ядро", scope: "Як залізо стає файлом і як ядро керує тим, що під'єднали.",
      topics: [
        { slug: "device-file-model", title: "Файл пристрою: символьний і блоковий", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "major-minor-numbers", title: "Старший і молодший номери пристрою", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "sysfs-device-model", title: "Модель пристроїв у sysfs", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "udev-rules", title: "udev: іменування пристроїв і правила", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "kernel-modules", title: "Модулі ядра: завантаження, параметри, залежності", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "tty-and-termios", title: "TTY і послідовний порт: модель termios", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "usb-in-linux", title: "USB у Linux: шина, класи, доступ із простору користувача", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "interrupts-bottom-halves", title: "Переривання, softirq і робочі черги", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "dma-and-buffers", title: "DMA і відображення буферів у ядрі", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "boot-init", title: "Завантаження й служби", scope: "Шлях від увімкнення живлення до працюючої системи та як тримають служби.",
      topics: [
        { slug: "boot-chain", title: "Ланцюг завантаження: від прошивки до init", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "bootloader-and-cmdline", title: "Завантажувач і командний рядок ядра", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "initramfs", title: "initramfs: тимчасовий корінь", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "init-and-pid1", title: "Роль init і особливість PID 1", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "systemd-model", title: "systemd: юніти, залежності, цілі", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "service-lifecycle", title: "Життєвий цикл служби й політика перезапуску", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "socket-activation", title: "Активація за сокетом", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "journald-logging", title: "journald: журнал як структуровані записи", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "shell", title: "Оболонка як модель", scope: "Оболонка не як набір команд, а як механізм складання процесів і потоків даних.",
      topics: [
        { slug: "shell-role", title: "Оболонка: що вона робить насправді", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "argv-and-environment", title: "argv, оточення й що успадковує дитина", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "standard-streams", title: "Три потоки: stdin, stdout, stderr", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "redirection-model", title: "Перенаправлення як робота з дескрипторами", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "pipeline-composition", title: "Конвеєр: композиція процесів", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "exit-status", title: "Код виходу як інтерфейс програми", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "expansion-and-quoting", title: "Розкриття й лапки: коли текст стає аргументами", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "job-control", title: "Керування завданнями й термінальні сигнали", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "session-environment", title: "Оточення сеансу: profile, rc і пошук у PATH", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "networking", title: "Мережа в ядрі", scope: "Як Linux бачить мережу зсередини: від інтерфейсу до маршруту й фільтра.",
      topics: [
        { slug: "network-stack", title: "Мережевий стек у ядрі", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "interfaces-and-addresses", title: "Інтерфейси, адреси й стан лінка", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "socket-api-linux", title: "Сокети в Linux: від дескриптора до з'єднання", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "routing-decision", title: "Таблиця маршрутів і рішення про маршрут", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "netfilter-model", title: "netfilter: ланцюги, таблиці й NAT", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "network-namespaces", title: "Мережеві простори імен, veth і мости", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "name-resolution-path", title: "Шлях розв'язання імені: NSS, resolv, systemd-resolved", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "tun-tap", title: "TUN/TAP: віртуальні інтерфейси", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "linking", title: "Від файлу до процесу", scope: "Що відбувається між «є виконуваний файл» і «є працюючий процес».",
      topics: [
        { slug: "elf-structure", title: "ELF: сегменти, секції, точка входу", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "static-and-dynamic-linking", title: "Статичне й динамічне лінкування", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "dynamic-loader", title: "Динамічний завантажувач і його робота", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "soname-versioning", title: "SONAME і версіонування спільних бібліотек", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "library-search-order", title: "Порядок пошуку бібліотек: rpath, LD_LIBRARY_PATH, кеш", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "symbol-resolution", title: "Розв'язання символів і перекриття (interposition)", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "plt-and-got", title: "PLT і GOT: як працює виклик через межу бібліотеки", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "library-abi-compat", title: "Сумісність ABI бібліотеки й що її ламає", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "observability", title: "Побачити, що відбувається", scope: "Механізми, якими система показує себе зсередини — і що з них можна дізнатися.",
      topics: [
        { slug: "proc-filesystem", title: "/proc: процеси як файли", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "ptrace-model", title: "ptrace: на чому тримається трасування й налагодження", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "syscall-tracing", title: "Трасування системних викликів", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "perf-events", title: "Підсистема perf: лічильники й вибірковий профіль", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "ftrace-tracepoints", title: "ftrace і трасувальні точки ядра", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "ebpf", title: "eBPF: власні програми всередині ядра", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "core-dump", title: "Аварійний дамп: як налаштувати й що з нього видно", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "load-and-pressure", title: "Середнє навантаження й тиск на ресурси (PSI)", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },

    { slug: "packaging", title: "Постачання програм", scope: "Як програма доходить до користувача і чому способів кілька.",
      topics: [
        { slug: "package-manager-model", title: "Модель пакетного менеджера", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "deb-and-rpm", title: "deb і rpm: два світи пакування", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "repositories-and-trust", title: "Репозиторії, підписи й довіра", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "dependency-resolution", title: "Розв'язання залежностей і конфлікти версій", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "fhs-layout", title: "Ієрархія файлової системи: куди що кладуть", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "self-contained-bundles", title: "Самодостатні пакунки: AppImage, Flatpak, Snap", basic: { status: "empty" }, detailed: { status: "pending" } },
        { slug: "containers-vs-packages", title: "Контейнер проти пакунка", basic: { status: "empty" }, detailed: { status: "pending" } },
      ] },
  ]
});
