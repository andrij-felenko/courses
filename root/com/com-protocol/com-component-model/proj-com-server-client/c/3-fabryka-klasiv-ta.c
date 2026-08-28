typedef struct ClassFactoryImpl {
    const IClassFactoryVtbl *lpVtbl;
    LONG m_refCount;
} ClassFactoryImpl;

static HRESULT STDMETHODCALLTYPE Factory_QueryInterface(void *This, REFIID riid, void **ppvObject) {
    if (!ppvObject) return E_POINTER;
    if (IsEqualGUID(riid, &IID_IUnknown) || IsEqualGUID(riid, &IID_IClassFactory)) {
        *ppvObject = This;
        ((ClassFactoryImpl*)This)->lpVtbl->AddRef(This);
        return S_OK;
    }
    *ppvObject = NULL;
    return E_NOINTERFACE;
}

static ULONG STDMETHODCALLTYPE Factory_AddRef(void *This) {
    return (ULONG)InterlockedIncrement(&((ClassFactoryImpl*)This)->m_refCount);
}

static ULONG STDMETHODCALLTYPE Factory_Release(void *This) {
    ULONG count = (ULONG)InterlockedDecrement(&((ClassFactoryImpl*)This)->m_refCount);
    if (count == 0) {
        free(This);
    }
    return count;
}

static HRESULT STDMETHODCALLTYPE Factory_CreateInstance(void *This, IUnknown *pUnkOuter, REFIID riid, void **ppvObject) {
    (void)This;
    if (pUnkOuter != NULL) return CLASS_E_NOAGGREGATION;
    if (!ppvObject) return E_POINTER;

    CalculatorImpl *calc = Calculator_Create();
    if (!calc) return E_OUTOFMEMORY;

    HRESULT hr = calc->lpVtbl->QueryInterface(calc, riid, ppvObject);
    calc->lpVtbl->Release(calc);
    return hr;
}

static HRESULT STDMETHODCALLTYPE Factory_LockServer(void *This, BOOL fLock) {
    (void)This; (void)fLock;
    return S_OK;
}

static const IClassFactoryVtbl g_FactoryVtbl = {
    Factory_QueryInterface,
    Factory_AddRef,
    Factory_Release,
    Factory_CreateInstance,
    Factory_LockServer
};

IClassFactory* ClassFactory_Create(void) {
    ClassFactoryImpl *f = (ClassFactoryImpl*)malloc(sizeof(ClassFactoryImpl));
    if (!f) return NULL;
    f->lpVtbl = &g_FactoryVtbl;
    f->m_refCount = 1;
    return (IClassFactory*)f;
}
