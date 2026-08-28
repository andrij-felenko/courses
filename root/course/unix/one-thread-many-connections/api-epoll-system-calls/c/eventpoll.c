/* Концептуальна схема ключових структур ядра (fs/eventpoll.c) */

struct eventpoll {
    struct mutex            mtx;          /* М'ютекс для операцій epoll_ctl */
    rwlock_t                lock;         /* Блокування для списку готових подій */
    wait_queue_head_t       wq;           /* Черга очікування для epoll_wait() */
    wait_queue_head_t       poll_wait;    /* Черга очікування, якщо сам epoll вкладений в інший epoll */
    struct list_head        rdllist;      /* Двозв'язний список готових дескрипторів */
    struct rb_root_cached   rbr;          /* Червоно-чорне дерево зареєстрованих дескрипторів */
    struct epitem          *ovflist;      /* Тимчасовий список переповнення при копіюванні в userspace */
    struct user_struct     *user;         /* Облік ліміту max_user_watches для UID */
    struct file            *file;         /* Опис файлу самого екземпляра epoll */
};

struct epitem {
    struct rb_node          rb;           /* Вузол червоно-чорного дерева */
    struct list_head        rdllink;      /* Елемент двозв'язного списку rdllist */
    struct epoll_filefd     ffd;          /* Пара: struct file* та номер fd */
    struct eventpoll       *ep;           /* Покажчик на батьківський екземпляр eventpoll */
    struct epoll_event      event;        /* Поточна маска подій та дані користувача */
    struct list_head        pwqlist;      /* Список точок очікування в чергах драйверів */
};
