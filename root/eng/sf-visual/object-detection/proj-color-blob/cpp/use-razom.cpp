Blob detect_target(int min_area) {
    camera_capture(frame);               // 1. кадр
    threshold_color(frame, mask);        // 2+3. RGB→HSV→поріг (з wraparound)
    erode3 (mask, tmp);                  // 4. розмикання: спершу ерозія…
    dilate3(tmp,  mask);                 //     …тоді дилатація — шум геть
    return find_blob(mask, min_area);    // 5. моменти → центр, площа, рамка
}

// у керуванні:
//   Blob t = detect_target(40);
//   if (t.found) {
//       int err_x = t.cx - W/2;         // зсув цілі від центру кадру → у курс
//       int err_y = t.cy - H/2;         // → у тангаж/висоту
//       // площа t.area росте → ціль ближчає (груба оцінка дальності)
//   }
