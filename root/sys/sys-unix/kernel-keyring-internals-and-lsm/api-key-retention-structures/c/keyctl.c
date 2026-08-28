#define KEYCTL_GET_KEYRING_ID		0	/* Повернути ID спеціальної в'язки */
#define KEYCTL_JOIN_SESSION_KEYRING	1	/* Створити або приєднатися до сесійної в'язки */
#define KEYCTL_UPDATE			2	/* Оновити payload ключа */
#define KEYCTL_REVOKE			3	/* Анулювати ключ */
#define KEYCTL_CHOWN			4	/* Змінити власника UID/GID */
#define KEYCTL_SETPERM			5	/* Змінити маску key_perm_t */
#define KEYCTL_DESCRIBE			6	/* Зчитати текстовий опис ключа */
#define KEYCTL_CLEAR			7	/* Очистити вміст в'язки */
#define KEYCTL_LINK			8	/* Прив'язати ключ до в'язки */
#define KEYCTL_UNLINK			9	/* Видалити посилання з в'язки */
#define KEYCTL_SEARCH			10	/* Пошук ключа у в'язках */
#define KEYCTL_READ			11	/* Зчитати payload у буфер */
#define KEYCTL_INSTANTIATE		12	/* Ініціалізувати ключ під час upcall */
#define KEYCTL_NEGATE			13	/* Відхилити створення ключа в upcall */
#define KEYCTL_SET_REQKEY_KEYRING	14	/* Типова в'язка для ключів, створених через upcall */
#define KEYCTL_SET_TIMEOUT		15	/* Встановити таймер згасання (TTL у секундах) */
#define KEYCTL_ASSUME_AUTHORITY		16	/* Взяти повноваження на ініціалізацію ключа в upcall */
#define KEYCTL_GET_SECURITY		17	/* Отримати текстову мітку LSM */
#define KEYCTL_INVALIDATE		21	/* Негайно знищити ключ з пам'яті */
#define KEYCTL_RESTRICT_KEYRING		29	/* Встановити обмеження на додавання ключів до в'язки */
