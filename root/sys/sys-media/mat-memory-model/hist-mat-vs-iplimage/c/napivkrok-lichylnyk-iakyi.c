typedef struct CvMat
{
    int type;
    int step;

    /* for internal use only */
    int* refcount;
    int hdr_refcount;

    union { uchar* ptr; short* s; int* i; float* fl; double* db; } data;
    int rows;
    int cols;
}
CvMat;
