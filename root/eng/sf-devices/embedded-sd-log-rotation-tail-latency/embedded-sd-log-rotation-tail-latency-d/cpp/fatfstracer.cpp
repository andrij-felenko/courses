#include "ff.h"
#include <iostream>

class FatFsTracer {
public:
    static FRESULT writeAndTrace(FIL *fp, const void *buff, UINT btw, UINT *bw) {
        DWORD previousCluster = fp->clust;
        FRESULT res = f_write(fp, buff, btw, bw);

        if (res == FR_OK && fp->clust != previousCluster) {
            std::cout << "[FatFs] Зміна кластера! Попередній: " << previousCluster 
                      << ", Новий: " << fp->clust 
                      << ". Відбулося оновлення FAT та директорії." << std::endl;
        }
        return res;
    }
};
