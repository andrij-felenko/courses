inline _InputArray::_InputArray(const Mat& m)  { init(+MAT + ACCESS_READ, &m); }
inline _InputArray::_InputArray(const UMat& m) { init(+UMAT + ACCESS_READ, &m); }

template<typename _Tp> inline
_InputArray::_InputArray(const std::vector<_Tp>& vec)
{
    init(FIXED_TYPE + STD_VECTOR + traits::Type<_Tp>::value + ACCESS_READ, &vec);
}

template<typename _Tp, int m, int n> inline
_InputArray::_InputArray(const Matx<_Tp, m, n>& mtx)
{
    init(FIXED_TYPE + FIXED_SIZE + MATX + traits::Type<_Tp>::value + ACCESS_READ,
         &mtx, Size(n, m));
}
