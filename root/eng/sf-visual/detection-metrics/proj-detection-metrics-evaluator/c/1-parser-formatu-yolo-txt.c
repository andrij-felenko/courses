void parse_yolo_line(const char *line, int img_w, int img_h, GroundTruth *out_gt) {
    int cls;
    float cx, cy, w, h;
    if (sscanf(line, "%d %f %f %f %f", &cls, &cx, &cy, &w, &h) == 5) {
        float abs_w = w * (float)img_w;
        float abs_h = h * (float)img_h;
        float abs_cx = cx * (float)img_w;
        float abs_cy = cy * (float)img_h;

        out_gt->class_id = cls;
        out_gt->box.x1 = abs_cx - abs_w * 0.5f;
        out_gt->box.y1 = abs_cy - abs_h * 0.5f;
        out_gt->box.x2 = abs_cx + abs_w * 0.5f;
        out_gt->box.y2 = abs_cy + abs_h * 0.5f;
        out_gt->area = abs_w * abs_h;
        out_gt->is_crowd = false;
        out_gt->matched = false;
    }
}
