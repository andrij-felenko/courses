struct mallinfo2 {
    size_t arena;     /* узято в системи не через mmap, байтів */
    size_t ordblks;   /* вільних блоків, штук                  */
    size_t smblks;    /* вільних fastbin-блоків                */
    size_t hblks;     /* окремих mmap-ділянок, штук            */
    size_t hblkhd;    /* байтів у окремих mmap-ділянках        */
    size_t usmblks;   /* не використовується, завжди 0         */
    size_t fsmblks;   /* байтів у вільних fastbin-блоках       */
    size_t uordblks;  /* зайнято блоками програми, байтів      */
    size_t fordblks;  /* вільно всередині алокатора, байтів    */
    size_t keepcost;  /* скільки можна віддати зверху, байтів  */
};
