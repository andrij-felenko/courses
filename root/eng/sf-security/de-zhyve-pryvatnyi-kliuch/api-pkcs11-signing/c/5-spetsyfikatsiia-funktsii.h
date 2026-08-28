CK_RV C_FindObjectsInit(
    CK_SESSION_HANDLE hSession,   /* Дескриптор сесії */
    CK_ATTRIBUTE_PTR  pTemplate,  /* Шаблон пошуку (масив CK_ATTRIBUTE) */
    CK_ULONG          ulCount     /* Кількість атрибутів у шаблоні */
);

CK_RV C_FindObjects(
    CK_SESSION_HANDLE    hSession,          /* Дескриптор сесії */
    CK_OBJECT_HANDLE_PTR phObject,          /* Вихідний масив знайдених дескрипторів */
    CK_ULONG             ulMaxObjectCount,  /* Максимальна кількість об'єктів за виклик */
    CK_ULONG_PTR         pulObjectCount     /* Фактична кількість знайдених об'єктів */
);

CK_RV C_FindObjectsFinal(CK_SESSION_HANDLE hSession);
