typedef struct _IplROI {
    int coi;                 /* 0 — усі канали, 1 — нульовий, ... */
    int xOffset, yOffset;
    int width, height;
} IplROI;

typedef struct _IplImage {
    int   nChannels, depth;
    int   width, height;
    struct _IplROI *roi;     /* NULL — вибрано все зображення */
    char *imageData;
    int   widthStep;         /* байтів на вирівняний рядок */
    /* ... і ще з десяток полів, частину яких OpenCV просто ігнорує ... */
} IplImage;
