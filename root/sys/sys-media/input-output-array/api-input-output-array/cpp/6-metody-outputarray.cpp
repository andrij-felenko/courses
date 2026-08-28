enum DepthMask {
    DEPTH_MASK_8U = 1 << CV_8U,   DEPTH_MASK_8S  = 1 << CV_8S,
    DEPTH_MASK_16U = 1 << CV_16U, DEPTH_MASK_16S = 1 << CV_16S,
    DEPTH_MASK_32S = 1 << CV_32S, DEPTH_MASK_32F = 1 << CV_32F,
    DEPTH_MASK_64F = 1 << CV_64F, DEPTH_MASK_16F = 1 << CV_16F,
    DEPTH_MASK_ALL = (DEPTH_MASK_64F<<1)-1,
    DEPTH_MASK_ALL_BUT_8S = DEPTH_MASK_ALL & ~DEPTH_MASK_8S,
    DEPTH_MASK_ALL_16F = (DEPTH_MASK_16F<<1)-1,
    DEPTH_MASK_FLT = DEPTH_MASK_32F + DEPTH_MASK_64F
};

void create(Size sz, int type, int i=-1, bool allowTransposed=false,
            DepthMask fixedDepthMask=static_cast<DepthMask>(0)) const;
void create(int rows, int cols, int type, int i=-1, bool allowTransposed=false,
            DepthMask fixedDepthMask=static_cast<DepthMask>(0)) const;
void create(int dims, const int* size, int type, int i=-1, bool allowTransposed=false,
            DepthMask fixedDepthMask=static_cast<DepthMask>(0)) const;
void createSameSize(const _InputArray& arr, int mtype) const;

void release() const;
void clear() const;
void setTo(const _InputArray& value, const _InputArray& mask = _InputArray()) const;

bool needed() const;
bool fixedSize() const;
bool fixedType() const;

Mat&  getMatRef(int i=-1) const;
UMat& getUMatRef(int i=-1) const;
cuda::GpuMat&   getGpuMatRef() const;
cuda::GpuMatND& getGpuMatNDRef() const;
std::vector<cuda::GpuMat>& getGpuMatVecRef() const;
ogl::Buffer&    getOGlBufferRef() const;
cuda::HostMem&  getHostMemRef() const;

void assign(const Mat& m) const;   void assign(const std::vector<Mat>& v) const;
void assign(const UMat& u) const;  void assign(const std::vector<UMat>& v) const;
void move(Mat& m) const;           void move(UMat& u) const;
