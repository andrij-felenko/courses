struct IClassFactory : public IUnknown {
    virtual HRESULT STDMETHODCALLTYPE CreateInstance(
        /* [in]  */ IUnknown *pUnkOuter,
        /* [in]  */ REFIID   riid,
        /* [out] */ void     **ppvObject
    ) = 0;

    virtual HRESULT STDMETHODCALLTYPE LockServer(
        /* [in] */ BOOL fLock
    ) = 0;
};
