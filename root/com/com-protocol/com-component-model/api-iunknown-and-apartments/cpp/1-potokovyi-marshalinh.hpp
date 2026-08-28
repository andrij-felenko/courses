/* У потоці-відправнику: */
HRESULT CoMarshalInterThreadInterfaceInStream(
    REFIID    riid,     /* IID інтерфейсу */
    IUnknown *pUnk,     /* Вказівник на об'єкт */
    LPSTREAM *ppStm     /* Вихідний потік маршалінгу */
);

/* У потоці-отримувачі: */
HRESULT CoGetInterfaceAndReleaseStream(
    LPSTREAM  pStm,     /* Потік, створений відправником */
    REFIID    riid,     /* IID інтерфейсу */
    LPVOID   *ppv       /* Вихідний проксі-вказівник */
);
