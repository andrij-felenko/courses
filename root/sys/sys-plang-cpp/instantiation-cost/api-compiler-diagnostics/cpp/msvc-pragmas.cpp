// Приглушення попереджень MSVC щодо експорту шаблонних класів у DLL (C4251)
#pragma warning(push)
#pragma warning(disable: 4251) // class 'A<T>' needs to have dll-interface

template <typename T>
class __declspec(dllexport) DllExportedBuffer {
    // ...
};

#pragma warning(pop)
