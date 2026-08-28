struct grant_entry_v1 {
    uint16_t flags;    /* Прапорці доступу (GTF_permit_access, GTF_reading, GTF_writing) */
    domid_t  domid;    /* ID домену, якому надається доступ (наприклад, 0 для Dom0) */
    uint32_t frame;    /* Machine Frame Number (MFN) фізичної сторінки ОЗП */
};
typedef struct grant_entry_v1 grant_entry_v1_t;

/* Основні бітові прапорці flags */
#define GTF_invalid       (0U<<0) /* Запис недійсний / вільний для використання */
#define GTF_permit_access (1U<<0) /* Надано дозвіл на відображення сторінки іншим доменом */
#define GTF_accept_transfer (2U<<0) /* Надано дозвіл на повну передачу власності сторінки */
#define GTF_readonly      (1U<<2) /* Дозвіл тільки для читання (якщо не встановлено — читання/запис) */
#define GTF_reading       (1U<<3) /* Встановлюється гіпервізором: домен наразі мапить для читання */
#define GTF_writing       (1U<<4) /* Встановлюється гіпервізором: домен наразі мапить для запису */
