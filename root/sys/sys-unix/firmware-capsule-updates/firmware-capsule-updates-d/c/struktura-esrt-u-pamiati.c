/* Визначення структур ESRT специфікації UEFI мовою C */
typedef struct {
    UINT32 FwResourceCount;       // Кількість записів у таблиці
    UINT32 FwResourceCountMax;    // Максимальна можлива кількість записів
    UINT64 FwResourceVersion;     // Версія структури ESRT (наразі 1)
} EFI_SYSTEM_RESOURCE_TABLE;

typedef struct {
    EFI_GUID FwClass;                     // GUID класу пристрою (унікальний ID)
    UINT32   FwType;                      // Тип ресурсу (1=System, 2=Device, 3=UEFI Driver)
    UINT32   FwVersion;                   // Поточна встановлена версія прошивки
    UINT32   LowestSupportedFwVersion;    // Мінімальна дозволена версія (захист від Anti-Rollback)
    UINT32   CapsuleFlags;                // Прапорці оновлення
    UINT32   LastAttemptVersion;          // Версія останнього спробованого оновлення
    UINT32   LastAttemptStatus;           // Код результату останньої спроби (0=Success)
} EFI_SYSTEM_RESOURCE_ENTRY;
