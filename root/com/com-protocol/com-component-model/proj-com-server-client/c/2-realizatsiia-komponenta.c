typedef struct CalculatorImpl {
    const ICalculatorVtbl *lpVtbl;
    LONG m_refCount;
} CalculatorImpl;

static HRESULT STDMETHODCALLTYPE Calc_QueryInterface(void *This, REFIID riid, void **ppvObject) {
    CalculatorImpl *pThis = (CalculatorImpl*)This;
    if (!ppvObject) return E_POINTER;

    /* Перевірка ідентичності та підтримуваних інтерфейсів */
    if (IsEqualGUID(riid, &IID_IUnknown) || IsEqualGUID(riid, &IID_ICalculator)) {
        *ppvObject = pThis;
        pThis->lpVtbl->AddRef(This);
        return S_OK;
    }

    *ppvObject = NULL;
    return E_NOINTERFACE;
}

static ULONG STDMETHODCALLTYPE Calc_AddRef(void *This) {
    CalculatorImpl *pThis = (CalculatorImpl*)This;
    return (ULONG)InterlockedIncrement(&pThis->m_refCount);
}

static ULONG STDMETHODCALLTYPE Calc_Release(void *This) {
    CalculatorImpl *pThis = (CalculatorImpl*)This;
    ULONG count = (ULONG)InterlockedDecrement(&pThis->m_refCount);
    if (count == 0) {
        free(pThis);
    }
    return count;
}

static HRESULT STDMETHODCALLTYPE Calc_Add(void *This, double a, double b, double *result) {
    (void)This;
    if (!result) return E_POINTER;
    *result = a + b;
    return S_OK;
}

static HRESULT STDMETHODCALLTYPE Calc_Multiply(void *This, double a, double b, double *result) {
    (void)This;
    if (!result) return E_POINTER;
    *result = a * b;
    return S_OK;
}

static const ICalculatorVtbl g_CalculatorVtbl = {
    Calc_QueryInterface,
    Calc_AddRef,
    Calc_Release,
    Calc_Add,
    Calc_Multiply
};

CalculatorImpl* Calculator_Create(void) {
    CalculatorImpl *p = (CalculatorImpl*)malloc(sizeof(CalculatorImpl));
    if (!p) return NULL;
    p->lpVtbl = &g_CalculatorVtbl;
    p->m_refCount = 1;
    return p;
}
