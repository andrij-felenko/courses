struct IUnknown {
    virtual HRESULT STDMETHODCALLTYPE QueryInterface(
        /* [in] */  REFIID riid,
        /* [out] */ void **ppvObject
    ) = 0;

    virtual ULONG STDMETHODCALLTYPE AddRef(void) = 0;

    virtual ULONG STDMETHODCALLTYPE Release(void) = 0;
};
