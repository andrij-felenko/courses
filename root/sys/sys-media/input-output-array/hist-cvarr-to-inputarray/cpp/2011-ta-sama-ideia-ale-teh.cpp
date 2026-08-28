class CV_EXPORTS _InputArray
{
public:
    enum { KIND_SHIFT=16, NONE=0<<KIND_SHIFT, MAT=1<<KIND_SHIFT,
        MATX=2<<KIND_SHIFT, STD_VECTOR=3<<KIND_SHIFT,
        STD_VECTOR_VECTOR=4<<KIND_SHIFT,
        STD_VECTOR_MAT=5<<KIND_SHIFT, EXPR=6<<KIND_SHIFT };
    // ...
};

typedef const _InputArray& InputArray;
