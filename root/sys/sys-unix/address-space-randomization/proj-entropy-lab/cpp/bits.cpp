/* bits.cpp — читає зі stdin рядки «ім'я=0xадреса …» і оцінює, скільки
 * двійкових розрядів насправді рухається в кожного орієнтира.
 *
 *   g++ -O2 -Wall -Wextra -o bits bits.cpp
 *   ./bits < plain.txt
 */
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <unordered_map>
#include <algorithm>
#include <numeric>
#include <cmath>
#include <iomanip>

static unsigned long long gcd(unsigned long long a, unsigned long long b)
{
	while (b != 0) {
		unsigned long long t = a % b;
		a = b;
		b = t;
	}
	return a;
}

int main()
{
	std::vector<std::string> names;
	std::unordered_map<std::string, std::size_t> name_to_idx;
	std::vector<std::vector<unsigned long long>> vals;

	std::string line;
	int nrow = 0;
	constexpr int MAXROW = 50000;

	while (nrow < MAXROW && std::getline(std::cin, line)) {
		if (line.empty()) continue;
		std::istringstream iss(line);
		std::string token;
		bool got = false;
		while (iss >> token) {
			auto eq = token.find('=');
			if (eq != std::string::npos && eq > 0 && eq + 1 < token.size()) {
				std::string key = token.substr(0, eq);
				std::string hex_str = token.substr(eq + 1);
				try {
					unsigned long long v = std::stoull(hex_str, nullptr, 16);
					if (name_to_idx.find(key) == name_to_idx.end()) {
						name_to_idx[key] = names.size();
						names.push_back(key);
						vals.emplace_back();
					}
					std::size_t idx = name_to_idx[key];
					if (vals[idx].size() == static_cast<std::size_t>(nrow)) {
						vals[idx].push_back(v);
					} else {
						vals[idx].resize(nrow + 1);
						vals[idx][nrow] = v;
					}
					got = true;
				} catch (...) {}
			}
		}
		if (got) nrow++;
	}

	if (nrow < 2) {
		std::cerr << "потрібно щонайменше два прогони\n";
		return 1;
	}

	std::cout << "прогонів: " << nrow << "\n";
	std::cout << "стовпчики: орієнтир · різних значень · крок · рухомих розрядів ·"
	          << " маска рухомих · ΣH(p) · оцінка за розмахом\n\n";

	for (std::size_t c = 0; c < names.size(); ++c) {
		const auto &v = vals[c];
		if (v.size() < static_cast<std::size_t>(nrow)) continue;
		unsigned long long lo = v[0], hi = v[0], step = 0, mask = 0;
		long ones[64] = { 0 };

		for (int r = 0; r < nrow; ++r) {
			if (v[r] < lo) lo = v[r];
			if (v[r] > hi) hi = v[r];
			for (int b = 0; b < 64; ++b) {
				if ((v[r] >> b) & 1ULL) ones[b]++;
			}
		}
		for (int r = 0; r < nrow; ++r) {
			step = gcd(step, v[r] - lo);
		}

		auto tmp = v;
		std::sort(tmp.begin(), tmp.end());
		int distinct = static_cast<int>(std::distance(tmp.begin(), std::unique(tmp.begin(), tmp.end())));

		double hsum = 0.0;
		int moving = 0;
		for (int b = 0; b < 64; ++b) {
			if (ones[b] == 0 || ones[b] == nrow) continue;
			moving++;
			mask |= 1ULL << b;
			double p = static_cast<double>(ones[b]) / nrow;
			hsum += -(p * std::log2(p) + (1.0 - p) * std::log2(1.0 - p));
		}

		double span = 0.0;
		if (step != 0) {
			double slots = static_cast<double>((hi - lo) / step) + 1.0;
			slots *= static_cast<double>(nrow + 1) / static_cast<double>(nrow - 1);
			span = std::log2(slots);
		}

		std::cout << std::left << std::setw(9) << names[c] << std::right
		          << std::setw(8) << distinct
		          << std::setw(7) << step
		          << std::setw(7) << moving
		          << " 0x" << std::setfill('0') << std::setw(16) << std::hex << mask << std::dec << std::setfill(' ')
		          << std::fixed << std::setprecision(1)
		          << std::setw(10) << hsum
		          << std::setw(10) << span << '\n';
	}
	return 0;
}
