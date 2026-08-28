/* Виклик методу COM у чистому C */
#include <windows.h>
#include <stdio.h>

void use_com_interface_c(IUnknown *pUnk) {
    if (!pUnk) return;

    /* 1. Збільшуємо лічильник посилань */
    pUnk->lpVtbl->AddRef(pUnk);

    /* 2. Запитуємо цільовий інтерфейс */
    void *pStream = NULL;
    static const IID IID_ISequentialStream = { 
        0x0c733a30, 0x2a1c, 0x11ce, {0xad, 0xe5, 0x00, 0xaa, 0x00, 0x44, 0x77, 0x3d} 
    };

    HRESULT hr = pUnk->lpVtbl->QueryInterface(pUnk, &IID_ISequentialStream, &pStream);
    if (SUCCEEDED(hr) && pStream) {
        printf("Інтерфейс ISequentialStream успішно отримано в C\n");
        
        IUnknown *pStreamUnk = (IUnknown*)pStream;
        pStreamUnk->lpVtbl->Release(pStreamUnk);
    }

    /* 3. Звільняємо початкове посилання */
    pUnk->lpVtbl->Release(pUnk);
}
