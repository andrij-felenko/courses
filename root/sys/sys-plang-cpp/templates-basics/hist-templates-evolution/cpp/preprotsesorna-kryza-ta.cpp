#include <generic.h>

#define Stack(type) name2(type,Stack)
#define Stackdeclare(type) \
struct Stack(type) {       \
    type* data;            \
    int top;               \
    void push(type val);   \
    type pop();            \
};
