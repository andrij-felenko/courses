/* include/image_transform.h — тип Matrix3x3 є частиною API (C) */
#ifndef IMAGE_TRANSFORM_H
#define IMAGE_TRANSFORM_H

#include "image.h"
#include <math/matrix3x3.h>

void image_apply_transform(ImageBuffer* img, const Matrix3x3* matrix);

#endif
