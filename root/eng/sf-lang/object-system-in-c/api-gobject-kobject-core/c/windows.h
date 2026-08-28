/* Оголошення IUnknown мовою C */
#include <windows.h>

typedef struct IUnknownVtbl {
    /* [0] Запит інтерфейсу за GUID */
    HRESULT (*QueryInterface)(void *This, REFIID riid, void **ppvObject);
    
    /* [1] Атомарне додавання посилання */
    ULONG (*AddRef)(void *This);
    
    /* [2] Атомарне зменшення посилання та деструкція */
    ULONG (*Release)(void *This);
} IUnknownVtbl;

typedef struct IUnknown {
    const IUnknownVtbl *lpVtbl;    /* Зсув 0: покажчик на vtable */
} IUnknown;
