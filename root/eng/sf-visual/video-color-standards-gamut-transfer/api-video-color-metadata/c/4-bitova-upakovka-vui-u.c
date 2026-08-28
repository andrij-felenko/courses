/* c */
void parse_vui_parameters(BitReader *br, VUIParameters *vui) {
    vui->aspect_ratio_info_present_flag = read_bits(br, 1);
    if (vui->aspect_ratio_info_present_flag) {
        vui->aspect_ratio_idc = read_bits(br, 8);
        if (vui->aspect_ratio_idc == Extended_SAR) {
            vui->sar_width  = read_bits(br, 16);
            vui->sar_height = read_bits(br, 16);
        }
    }
    vui->overscan_info_present_flag = read_bits(br, 1);
    
    vui->video_signal_type_present_flag = read_bits(br, 1);
    if (vui->video_signal_type_present_flag) {
        vui->video_format = read_bits(br, 3);
        vui->video_full_range_flag = read_bits(br, 1);
        vui->colour_description_present_flag = read_bits(br, 1);
        
        if (vui->colour_description_present_flag) {
            vui->colour_primaries         = read_bits(br, 8);
            vui->transfer_characteristics = read_bits(br, 8);
            vui->matrix_coefficients      = read_bits(br, 8);
        }
    }
}
