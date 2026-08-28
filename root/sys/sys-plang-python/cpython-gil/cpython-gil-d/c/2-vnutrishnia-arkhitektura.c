// pycore_ceval.h
struct _gil_runtime_state {
    /* Атомарний інтервал перемикання потоків у мікросекундах */
    unsigned long interval;
    
    /* Прапорець стану: 1 - замок зайнятий, 0 - вільний */
    _Py_atomic_int locked;
    
    /* Системний м'ютекс ОС для захисту самого стану GIL */
    PyMUTEX_T mutex;
    
    /* Умовна змінна ОС для сповіщення потоків, що чекають */
    PyCOND_T cond;
    
    /* Умовна змінна для підтвердження передачі керування */
    PyCOND_T switch_cond;
    
    /* Покажчик на стан потоку (PyThreadState), що останнім утримував GIL */
    _Py_atomic_address last_holder;
};
