class RangeStage
{
public:
    void submit(cv::InputArray _frame)
    {
        cv::Mat m = _frame.getMat();
        if (!m.u)          // заголовок нічим не володіє: вектор, чужий буфер, GstBuffer
            m = m.clone();  // єдиний спосіб пережити вихід із функції
        queue_.push_back(m);
    }
private:
    std::deque<cv::Mat> queue_;
};
