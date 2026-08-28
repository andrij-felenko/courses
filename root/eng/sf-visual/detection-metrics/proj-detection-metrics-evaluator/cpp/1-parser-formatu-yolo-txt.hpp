#include <string_view>
#include <charconv>
#include <optional>

[[nodiscard]] std::optional<GroundTruth> parse_yolo_line_cpp(
    std::string_view line, int img_w, int img_h
) noexcept {
    int cls = 0;
    float cx = 0.0f, cy = 0.0f, w = 0.0f, h = 0.0f;
    const char* ptr = line.data();
    const char* end = line.data() + line.size();

    auto res1 = std::from_chars(ptr, end, cls);
    if (res1.ec != std::errc{}) return std::nullopt;
    ptr = res1.ptr;
    while (ptr < end && *ptr == ' ') ++ptr;

    auto res2 = std::from_chars(ptr, end, cx);
    if (res2.ec != std::errc{}) return std::nullopt;
    ptr = res2.ptr;
    while (ptr < end && *ptr == ' ') ++ptr;

    auto res3 = std::from_chars(ptr, end, cy);
    if (res3.ec != std::errc{}) return std::nullopt;
    ptr = res3.ptr;
    while (ptr < end && *ptr == ' ') ++ptr;

    auto res4 = std::from_chars(ptr, end, w);
    if (res4.ec != std::errc{}) return std::nullopt;
    ptr = res4.ptr;
    while (ptr < end && *ptr == ' ') ++ptr;

    auto res5 = std::from_chars(ptr, end, h);
    if (res5.ec != std::errc{}) return std::nullopt;

    const float abs_w = w * static_cast<float>(img_w);
    const float abs_h = h * static_cast<float>(img_h);
    const float abs_cx = cx * static_cast<float>(img_w);
    const float abs_cy = cy * static_cast<float>(img_h);

    return GroundTruth{
        .box = {
            .x1 = abs_cx - abs_w * 0.5f,
            .y1 = abs_cy - abs_h * 0.5f,
            .x2 = abs_cx + abs_w * 0.5f,
            .y2 = abs_cy + abs_h * 0.5f
        },
        .class_id = cls,
        .image_id = 0,
        .area = abs_w * abs_h,
        .is_crowd = false,
        .matched = false
    };
}
