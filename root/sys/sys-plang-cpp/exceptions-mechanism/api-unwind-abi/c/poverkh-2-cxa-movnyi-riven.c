struct __cxa_exception {
    std::type_info       *exceptionType;         // статичний тип кинутого
    void                (*exceptionDestructor)(void *);
    std::terminate_handler unexpectedHandler;    // знімки обробників на
    std::terminate_handler terminateHandler;     // момент кидка
    __cxa_exception       *nextException;        // стек спійманих потоку
    int                    handlerCount;         // від'ємне = перекинутий
    int                    handlerSwitchValue;   // ↓ кеш розбору LSDA
    const unsigned char   *actionRecord;         //   з фази 1,
    const unsigned char   *languageSpecificData; //   щоб не читати
    _Unwind_Ptr            catchTemp;            //   таблиці двічі
    void                  *adjustedPtr;
    _Unwind_Exception      unwindHeader;         // ОБОВ'ЯЗКОВО останнє
};
