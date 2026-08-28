// Оголошення IUnknown мовою C++ (чистий абстрактний клас з віртуальними методами)
#pragma once
#include <unknwn.h>

// Компілятор C++ генерує ідентичну двійкову vtable з трьома покажчиками
struct ICustomUnknown {
    virtual HRESULT STDMETHODCALLTYPE QueryInterface(
        REFIID riid, 
        void **ppvObject) = 0;

    virtual ULONG STDMETHODCALLTYPE AddRef() = 0;

    virtual ULONG STDMETHODCALLTYPE Release() = 0;

    virtual ~ICustomUnknown() = default;
};
