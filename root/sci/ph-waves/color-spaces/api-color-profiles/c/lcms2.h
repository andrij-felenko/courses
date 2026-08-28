/* C (C99): Прямий C-API контракт бібліотеки LittleCMS (lcms2) */
#include <lcms2.h>

/* 1. Відкриття файлу профілю з диска або пам'яті */
cmsHPROFILE cmsOpenProfileFromFile(const char *FileName, const char *Access);
cmsHPROFILE cmsOpenProfileFromMem(const void *Buffer, cmsUInt32Number size);

/* 2. Створення віртуального профілю sRGB у пам'яті */
cmsHPROFILE cmsCreate_sRGBProfile(void);

/* 3. Створення трансформаційного конвеєра між двома профілями */
cmsHTRANSFORM cmsCreateTransform(
    cmsHPROFILE InputProfile,       /* Профіль джерела */
    cmsUInt32Number InputFormat,    /* Формат пікселів (наприклад TYPE_RGB_8) */
    cmsHPROFILE OutputProfile,      /* Профіль пристрою виводу */
    cmsUInt32Number OutputFormat,   /* Формат виводу (наприклад TYPE_CMYK_8) */
    cmsUInt32Number Intent,         /* Намір рендерингу (INTENT_PERCEPTUAL тощо) */
    cmsUInt32Number Flags           /* Прапори (наприклад cmsFLAGS_BLACKPOINTCOMPENSATION) */
);

/* 4. Виконання колірного перетворення над масивом пікселів */
void cmsDoTransform(
    cmsHTRANSFORM Transform,
    const void *InputBuffer,
    void *OutputBuffer,
    cmsUInt32Number Size            /* Кількість пікселів для обробки */
);

/* 5. Звільнення ресурсів */
void cmsDeleteTransform(cmsHTRANSFORM Transform);
cmsBool cmsCloseProfile(cmsHPROFILE hProfile);
