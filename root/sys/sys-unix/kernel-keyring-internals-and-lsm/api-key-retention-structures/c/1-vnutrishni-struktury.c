struct key {
	refcount_t		usage;		/* Лічильник посилань на об'єкт (RCU/atomic) */
	key_serial_t		serial;		/* 32-бітний унікальний додатний ідентифікатор */
	union {
		struct list_head graveyard_link;
		struct rb_node serial_node;
	};
	struct key_type		*type;		/* Вказівник на таблицю методів типу ключа */
	struct rw_semaphore	sem;		/* Семафор блокування читання/запису */
	struct key_user		*user;		/* Структура обліку квот пам'яті за UID */
	void			*security;	/* Вказівник на контекст безпеки LSM (SELinux/AppArmor) */
	
	time64_t		expiry;		/* Абсолютний час закінчення дії (0 = безлімітно) */
	time64_t		last_used_at;	/* Час останнього звернення до ключа */
	
	kuid_t			uid;		/* UID користувача-власника */
	kgid_t			gid;		/* GID групи-власника */
	key_perm_t		perm;		/* 32-бітна маска прав доступу */
	unsigned short		quotalen;	/* Розмір об'єкта в квотах кількості */
	unsigned short		datalen;	/* Довжина корисного навантаження в байтах */
	
	unsigned long		flags;		/* Прапорці стану (KEY_FLAG_REVOKED, KEY_FLAG_DEAD) */
	
	char			*description;	/* Пошуковий текстовий опис (тег) ключа */
	
	union {
		union key_payload payload;	/* Симетричний/асиметричний секретний payload */
		struct assoc_array keys;	/* Дерево посилань на інші ключі (для keyring) */
	};
};
