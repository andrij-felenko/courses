std::string describe(const cv::_InputArray& a)
{
    static const char* names[] = {
        "NONE","MAT","MATX","STD_VECTOR","STD_VECTOR_VECTOR","STD_VECTOR_MAT",
        "<removed EXPR>","OPENGL_BUFFER","CUDA_HOST_MEM","CUDA_GPU_MAT","UMAT",
        "STD_VECTOR_UMAT","STD_BOOL_VECTOR","STD_VECTOR_CUDA_GPU_MAT",
        "<removed STD_ARRAY>","STD_ARRAY_MAT","CUDA_GPU_MATND" };

    const int f = a.getFlags();
    std::string s = names[(f & cv::_InputArray::KIND_MASK) >> cv::_InputArray::KIND_SHIFT];

    if (f & cv::ACCESS_READ)   s += " READ";
    if (f & cv::ACCESS_WRITE)  s += " WRITE";
    if (f & cv::_InputArray::FIXED_TYPE) s += " FIXED_TYPE";
    if (f & cv::_InputArray::FIXED_SIZE) s += " FIXED_SIZE";
    return s;
}
