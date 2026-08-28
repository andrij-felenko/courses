#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MIN_GALLOP_DEFAULT 7
#define MAX_STACK_SIZE 85

typedef struct {
    size_t start;
    size_t len;
} TimSortRun;

typedef struct {
    int *array;
    size_t size;
    int *temp_buf;
    size_t temp_capacity;
    size_t min_gallop;
    TimSortRun stack[MAX_STACK_SIZE];
    size_t stack_size;
} TimSortState;
