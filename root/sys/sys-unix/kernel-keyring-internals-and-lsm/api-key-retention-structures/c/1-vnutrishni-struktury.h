struct key_type {
	const char *name;			/* Унікальна назва типу ("user", "logon", "keyring") */
	size_t def_datalen;			/* Розмір payload за замовчуванням */

	/* Методи життєвого циклу */
	int (*preparse)(struct key_preparsed_payload *prep);
	void (*free_preparse)(struct key_preparsed_payload *prep);
	int (*instantiate)(struct key *key, struct key_preparsed_payload *prep);
	int (*update)(struct key *key, struct key_preparsed_payload *prep);
	void (*revoke)(struct key *key);
	void (*destroy)(struct key *key);

	/* Методи пошуку, відображення та зчитання */
	void (*describe)(const struct key *key, struct seq_file *m);
	long (*read)(const struct key *key, char *buffer, size_t buflen);
};
