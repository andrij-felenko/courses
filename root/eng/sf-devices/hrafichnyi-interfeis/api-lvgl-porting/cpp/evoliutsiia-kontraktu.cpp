namespace embedded::lvgl::v9 {

class Display {
public:
    Display(int32_t width, int32_t height) noexcept
        : handle_(lv_display_create(width, height))
    {
        lv_display_set_user_data(handle_, this);
    }

    void setBuffers(void* buf1, void* buf2, size_t sizeInBytes) noexcept
    {
        lv_display_set_buffers(handle_, buf1, buf2, sizeInBytes, 
                               LV_DISPLAY_RENDER_MODE_PARTIAL);
    }

    void setFlushCallback(lv_display_flush_cb_t callback) noexcept
    {
        lv_display_set_flush_cb(handle_, callback);
    }

    lv_display_t* getHandle() const noexcept { return handle_; }

private:
    lv_display_t* handle_{nullptr};
};

} // namespace embedded::lvgl::v9
