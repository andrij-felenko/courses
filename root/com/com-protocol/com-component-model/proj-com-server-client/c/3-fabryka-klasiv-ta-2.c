STDAPI DllGetClassObject(REFCLSID rclsid, REFIID riid, LPVOID *ppv) {
    if (!ppv) return E_POINTER;
    *ppv = NULL;

    if (IsEqualGUID(rclsid, &CLSID_Calculator)) {
        IClassFactory *factory = ClassFactory_Create();
        if (!factory) return E_OUTOFMEMORY;
        HRESULT hr = factory->lpVtbl->QueryInterface(factory, riid, ppv);
        factory->lpVtbl->Release(factory);
        return hr;
    }
    return CLASS_E_CLASSNOTAVAILABLE;
}
