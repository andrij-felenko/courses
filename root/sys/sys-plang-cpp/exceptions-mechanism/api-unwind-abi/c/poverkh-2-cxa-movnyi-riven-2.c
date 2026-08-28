struct __cxa_refcounted_exception {
    _Atomic_word    referenceCount;   // ним живе exception_ptr
    __cxa_exception exc;              // мусить бути останнім, без вирівнювального хвоста
};

struct __cxa_dependent_exception {    // те, що кидає rethrow_exception
    void *primaryException;           // ← справжній об'єкт, спільний для всіх копій
    /* далі — поле в поле як у __cxa_exception, включно з unwindHeader */
};

struct __cxa_eh_globals {             // по одній на потік
    __cxa_exception *caughtExceptions;    // стек спійманих, найновіший перший
    unsigned int     uncaughtExceptions;  // ← це і є std::uncaught_exceptions()
};
