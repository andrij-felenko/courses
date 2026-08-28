struct IGlobalInterfaceTable : public IUnknown {
    virtual HRESULT STDMETHODCALLTYPE RegisterInterfaceInGlobal(
        /* [in]  */ IUnknown *pUnk,
        /* [in]  */ REFIID   riid,
        /* [out] */ DWORD    *pdwCookie
    ) = 0;

    virtual HRESULT STDMETHODCALLTYPE RevokeInterfaceFromGlobal(
        /* [in] */ DWORD dwCookie
    ) = 0;

    virtual HRESULT STDMETHODCALLTYPE GetInterfaceFromGlobal(
        /* [in]  */ DWORD  dwCookie,
        /* [in]  */ REFIID riid,
        /* [out] */ void   **ppv
    ) = 0;
};
