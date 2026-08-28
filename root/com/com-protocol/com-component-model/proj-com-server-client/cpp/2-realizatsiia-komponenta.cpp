class Calculator final : public ICalculator {
public:
    Calculator() : m_refCount(1) {}
    ~Calculator() = default;

    /* Реалізація методів IUnknown */
    HRESULT STDMETHODCALLTYPE QueryInterface(REFIID riid, void **ppvObject) override {
        if (!ppvObject) return E_POINTER;

        if (riid == __uuidof(IUnknown) || riid == IID_ICalculator) {
            *ppvObject = static_cast<ICalculator*>(this);
            AddRef();
            return S_OK;
        }

        *ppvObject = nullptr;
        return E_NOINTERFACE;
    }

    ULONG STDMETHODCALLTYPE AddRef() override {
        return ++m_refCount;
    }

    ULONG STDMETHODCALLTYPE Release() override {
        const ULONG count = --m_refCount;
        if (count == 0) {
            delete this;
        }
        return count;
    }

    /* Реалізація бізнес-методів ICalculator */
    HRESULT STDMETHODCALLTYPE Add(double a, double b, double *result) override {
        if (!result) return E_POINTER;
        *result = a + b;
        return S_OK;
    }

    HRESULT STDMETHODCALLTYPE Multiply(double a, double b, double *result) override {
        if (!result) return E_POINTER;
        *result = a * b;
        return S_OK;
    }

private:
    std::atomic<ULONG> m_refCount;
};
