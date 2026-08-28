STDAPI DllGetClassObject(REFCLSID rclsid, REFIID riid, LPVOID *ppv) {
    if (!ppv) return E_POINTER;
    *ppv = nullptr;

    if (rclsid == CLSID_Calculator) {
        Microsoft::WRL::ComPtr<IClassFactory> factory;
        factory.Attach(new (std::nothrow) CalculatorClassFactory());
        if (!factory) return E_OUTOFMEMORY;

        return factory->QueryInterface(riid, ppv);
    }
    return CLASS_E_CLASSNOTAVAILABLE;
}
