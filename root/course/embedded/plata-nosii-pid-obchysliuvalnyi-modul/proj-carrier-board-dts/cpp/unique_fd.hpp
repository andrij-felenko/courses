#pragma once

#include <utility>

#include <unistd.h>

namespace carrier {

// Дескриптор, що закриває себе сам. У C-версії ту саму роботу робили
// гілки goto fail, і кожна нова помилка вимагала не забути про close().
class UniqueFd {
public:
	UniqueFd() noexcept = default;
	explicit UniqueFd(int fd) noexcept : fd_{fd} {}

	UniqueFd(const UniqueFd&) = delete;
	UniqueFd& operator=(const UniqueFd&) = delete;

	UniqueFd(UniqueFd&& other) noexcept : fd_{std::exchange(other.fd_, -1)} {}

	UniqueFd& operator=(UniqueFd&& other) noexcept
	{
		if (this != &other)
			reset(std::exchange(other.fd_, -1));
		return *this;
	}

	~UniqueFd() { reset(); }

	[[nodiscard]] int get() const noexcept { return fd_; }
	[[nodiscard]] explicit operator bool() const noexcept { return fd_ >= 0; }

	void reset(int fd = -1) noexcept
	{
		if (fd_ >= 0 && fd_ != fd)
			::close(fd_);
		fd_ = fd;
	}

	[[nodiscard]] int release() noexcept { return std::exchange(fd_, -1); }

private:
	int fd_{-1};
};

}  // namespace carrier
