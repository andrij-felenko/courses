#define DID_OK                  0x00 /* Команда передана успішно */
#define DID_NO_CONNECT          0x01 /* Немає зв'язку з портом або сплив dev_loss_tmo */
#define DID_BUS_BUSY            0x02 /* Шина зайнята */
#define DID_TIME_OUT            0x03 /* Сплив таймер виконання команди (rq_timeout) */
#define DID_BAD_TARGET          0x04 /* Цільовий пристрій не відповідає на вибір */
#define DID_ABORT               0x05 /* Команду перервано обробником помилок (abort) */
#define DID_PARITY              0x06 /* Помилка парності на шині */
#define DID_ERROR               0x07 /* Внутрішня помилка хост-адаптера */
#define DID_RESET               0x08 /* Команду скинуто через SCSI Reset */
#define DID_BAD_INTR            0x09 /* Неочікуване або спотворене переривання */
#define DID_PASSTHROUGH         0x0a /* Прямий пасстру без втручання ядра */
#define DID_SOFT_ERROR          0x0b /* М'яка відновлювана помилка */
#define DID_IMM_RETRY           0x0c /* Негайний повтор команди без затримки */
#define DID_REQUEUE             0x0d /* Повернення запиту в початок черги планувальника */
#define DID_TRANSPORT_DISRUPTED 0x0e /* Тимчасове порушення зв'язку на транспорті */
#define DID_TRANSPORT_FAILFAST  0x0f /* Сплив fast_io_fail_tmo: негайна відмова для failover */
#define DID_TARGET_FAILURE      0x10 /* Апаратна відмова контролера цілі */
#define DID_NEXUS_FAILURE       0x11 /* Втрата I_T Nexus зв'язку */
#define DID_ALLOC_FAILURE       0x12 /* Брак ресурсів пам'яті для обробки */
#define DID_MEDIUM_ERROR        0x13 /* Помилка фізичного носія */
#define DID_TRANSPORT_MARGINAL  0x14 /* Лінк нестабільний (деградація якості сигналу) */
