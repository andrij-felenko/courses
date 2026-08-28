#include <windows.h>
#include <unknwn.h>
#include <wrl/client.h>
#include <iostream>
#include <atomic>

/* CLSID_Calculator: {E4A28B10-53D2-4A73-98D1-9B5A2D6E4310} */
inline constexpr GUID CLSID_Calculator = {
    0xe4a28b10, 0x53d2, 0x4a73,
    { 0x98, 0xd1, 0x9b, 0x5a, 0x2d, 0x6e, 0x43, 0x10 }
};

/* IID_ICalculator: {A1B2C3D4-E5F6-4A5B-8C7D-9E0F1A2B3C4D} */
inline constexpr GUID IID_ICalculator = {
    0xa1b2c3d4, 0xe5f6, 0x4a5b,
    { 0x8c, 0x7d, 0x9e, 0x0f, 0x1a, 0x2b, 0x3c, 0x4d }
};

/* Чистий абстрактний інтерфейс у C++ */
struct __declspec(novtable) ICalculator : public IUnknown {
    virtual HRESULT STDMETHODCALLTYPE Add(double a, double b, double *result) = 0;
    virtual HRESULT STDMETHODCALLTYPE Multiply(double a, double b, double *result) = 0;
};
