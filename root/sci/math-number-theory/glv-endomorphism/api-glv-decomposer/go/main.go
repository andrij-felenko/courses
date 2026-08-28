// #include "glv_decomposer.h"
import "C"
import "unsafe"

func DecomposeScalar(scalar [4]uint64, config *C.glv_curve_config_2d_t) (C.glv_split_2d_t, error) {
    var split C.glv_split_2d_t
    status := C.glv_decompose_2d(&split, (*C.uint64_t)(unsafe.Pointer(&scalar[0])), config)
    if status != 0 {
        return split, fmt.Errorf("GLV decomposition failed with status: %d", status)
    }
    return split, nil
}
