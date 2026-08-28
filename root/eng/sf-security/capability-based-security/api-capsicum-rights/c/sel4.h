#include <sel4/sel4.h>

/* Створення нового повноваження зі звуженням прав та бейджем */
seL4_Error seL4_CNode_Mint(
    seL4_CNode service,        /* CNode, у якому виконується операція */
    seL4_Word dest_index,      /* Індекс цільового слота */
    seL4_Uint8 dest_depth,     /* Глибина адресації цільового слота */
    seL4_CNode src_root,       /* Кореневий CNode джерела */
    seL4_Word src_index,       /* Індекс слота джерела */
    seL4_Uint8 src_depth,      /* Глибина адресації джерела */
    seL4_CapRights_t rights,   /* Нова (звужена) маска прав */
    seL4_CapData_t badge       /* Ідентифікатор (бейдж) для розрізнення клієнтів */
);

/* Копіювання повноваження без зміни бейджа */
seL4_Error seL4_CNode_Copy(
    seL4_CNode service, seL4_Word dest_index, seL4_Uint8 dest_depth,
    seL4_CNode src_root, seL4_Word src_index, seL4_Uint8 src_depth,
    seL4_CapRights_t rights
);

/* Переміщення повноваження зі слота в слот із вивільненням джерела */
seL4_Error seL4_CNode_Move(
    seL4_CNode service, seL4_Word dest_index, seL4_Uint8 dest_depth,
    seL4_CNode src_root, seL4_Word src_index, seL4_Uint8 src_depth
);

/* Каскадне відкликання: рекурсивне видалення всіх похідних копій */
seL4_Error seL4_CNode_Revoke(
    seL4_CNode service, seL4_Word index, seL4_Uint8 depth
);

/* Очищення окремого слота CNode */
seL4_Error seL4_CNode_Delete(
    seL4_CNode service, seL4_Word index, seL4_Uint8 depth
);
