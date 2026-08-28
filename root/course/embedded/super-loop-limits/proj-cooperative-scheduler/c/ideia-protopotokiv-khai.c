typedef struct { unsigned short line; } pt_t;

#define PT_INIT(pt)        ((pt)->line = 0)
#define PT_BEGIN(pt)       switch ((pt)->line) { case 0:
#define PT_END(pt)         } (pt)->line = 0; return PT_DONE

// «дійшли сюди й виходимо; наступного разу — з наступного рядка»
#define PT_YIELD(pt)                          \
    do { (pt)->line = __LINE__; case __LINE__:; } while (0)

// «чекай, доки умова стане істинною; доти — виходь щооберту»
#define PT_WAIT_UNTIL(pt, cond)               \
    do { (pt)->line = __LINE__; case __LINE__: \
         if (!(cond)) return PT_WAITING; } while (0)
