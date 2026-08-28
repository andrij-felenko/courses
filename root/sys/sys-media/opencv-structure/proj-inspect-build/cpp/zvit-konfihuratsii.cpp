static std::string trimmed(const std::string& s)
{
    const size_t b = s.find_first_not_of(" \t\r");
    if (b == std::string::npos) return std::string();
    return s.substr(b, s.find_last_not_of(" \t\r") - b + 1);
}

static size_t indentOf(const std::string& s)
{
    const size_t b = s.find_first_not_of(' ');
    return b == std::string::npos ? 0 : b;
}

// Тіло секції звіту разом із її заголовком.
static std::vector<std::string> buildInfoSection(const std::string& name)
{
    static const std::vector<std::string> lines = [] {
        std::vector<std::string> v;
        std::istringstream in(cv::getBuildInformation());
        for (std::string ln; std::getline(in, ln); ) v.push_back(ln);
        return v;
    }();

    const std::string head = "  " + name + ":";
    std::vector<std::string> body;
    for (size_t i = 0; i < lines.size(); ++i) {
        if (lines[i].compare(0, head.size(), head) != 0) continue;
        body.push_back(lines[i]);
        for (size_t j = i + 1; j < lines.size(); ++j) {
            if (trimmed(lines[j]).empty()) continue;
            if (indentOf(lines[j]) <= 2) break;   // почалася наступна секція
            body.push_back(lines[j]);
        }
        break;
    }
    return body;
}

// buildInfoField("Video I/O", "FFMPEG") → "YES"
static std::string buildInfoField(const std::string& section,
                                  const std::string& key)
{
    const std::string tag = key + ":";
    for (const std::string& line : buildInfoSection(section)) {
        const size_t at = line.find(tag);
        if (at == std::string::npos || at != indentOf(line)) continue;
        return trimmed(line.substr(at + tag.size()));
    }
    return std::string();
}

// Значення в самому заголовку секції: «  Parallel framework:  pthreads»
static std::string buildInfoHead(const std::string& section)
{
    return buildInfoField(section, section);
}
