long get_user_pages(unsigned long start, unsigned long nr_pages,
                    unsigned int gup_flags, struct page **pages);
long pin_user_pages(unsigned long start, unsigned long nr_pages,
                    unsigned int gup_flags, struct page **pages);

long get_user_pages_remote(struct mm_struct *mm,
                           unsigned long start, unsigned long nr_pages,
                           unsigned int gup_flags, struct page **pages,
                           int *locked);
long pin_user_pages_remote(struct mm_struct *mm,
                           unsigned long start, unsigned long nr_pages,
                           unsigned int gup_flags, struct page **pages,
                           int *locked);

long get_user_pages_unlocked(unsigned long start, unsigned long nr_pages,
                             struct page **pages, unsigned int gup_flags);
long pin_user_pages_unlocked(unsigned long start, unsigned long nr_pages,
                             struct page **pages, unsigned int gup_flags);

int  get_user_pages_fast(unsigned long start, int nr_pages,
                         unsigned int gup_flags, struct page **pages);
int  pin_user_pages_fast(unsigned long start, int nr_pages,
                         unsigned int gup_flags, struct page **pages);

int  get_user_pages_fast_only(unsigned long start, int nr_pages,
                              unsigned int gup_flags, struct page **pages);
