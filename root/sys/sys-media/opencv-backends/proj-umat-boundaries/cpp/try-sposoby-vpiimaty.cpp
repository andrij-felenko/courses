static std::string where(const cv::UMat& u)
{
    if (!u.u) return "порожній";
    std::string s = u.u->handle ? "буфер пристрою є" : "буфера пристрою нема";
    s += u.u->data ? ", копія в системній є" : ", копії в системній нема";
    if (u.u->hostCopyObsolete())   s += "; свіжа — на пристрої";
    if (u.u->deviceCopyObsolete()) s += "; свіжа — на хості";
    return s;
}

static void probe(const cv::Mat& in)
{
    cv::UMat uin, gray, blur, curved;
    Wall w;
    upload(in, uin, w);
    cv::cvtColor(uin, gray, cv::COLOR_BGR2GRAY);
    std::printf("cvtColor → %s\n", where(gray).c_str());
    cv::GaussianBlur(gray, blur, {5, 5}, 1.5);
    std::printf("blur     → %s\n", where(blur).c_str());
    cv::LUT(blur, g_curveU, curved);
    std::printf("LUT      → %s\n", where(curved).c_str());
}
