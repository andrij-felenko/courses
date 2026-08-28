// include/image_transform.hpp — тип Matrix3x3 є частиною API (C++)
#pragma once
#include "image.hpp"
#include <math/matrix3x3.hpp>

namespace img {

void apply_transform(ImageBuffer& img, const math::Matrix3x3& matrix);

} // namespace img
