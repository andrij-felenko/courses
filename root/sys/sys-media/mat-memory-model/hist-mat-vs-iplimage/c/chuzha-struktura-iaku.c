typedef struct _IplImage
{
    int  nSize;              /* sizeof(IplImage) */
    int  ID;
    int  nChannels;
    int  alphaChannel;       /* ігнорується OpenCV */
    int  depth;
    char colorModel[4];      /* ігнорується OpenCV */
    char channelSeq[4];      /* ігнорується OpenCV */
    int  dataOrder;
    int  origin;
    int  align;              /* ігнорується; вживається widthStep */
    int  width;
    int  height;
    struct _IplROI *roi;     /* область інтересу — окремий об'єкт */
    struct _IplImage *maskROI;    /* мусить бути NULL */
    void  *imageId;               /* мусить бути NULL */
    struct _IplTileInfo *tileInfo;/* мусить бути NULL */
    int  imageSize;
    char *imageData;         /* ← самі пікселі */
    int  widthStep;          /* байтів на рядок */
    int  BorderMode[4];      /* ігнорується */
    int  BorderConst[4];     /* ігнорується */
    char *imageDataOrigin;   /* початок виділеного блоку */
}
IplImage;
