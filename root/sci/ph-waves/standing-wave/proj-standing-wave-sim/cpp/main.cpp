#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <string>

struct SimResult {
    double dx;
    double dt;
    size_t nodesCount;
    size_t antinodesCount;
    double maxEnvelope;
};

class StandingWaveFDTD {
public:
    StandingWaveFDTD(double length = 1.0, size_t nodes = 200, double waveSpeed = 100.0)
        : m_length(length), m_nodes(nodes), m_waveSpeed(waveSpeed) {
        m_dx = m_length / static_cast<double>(m_nodes - 1);
        m_courant = 0.8; // C <= 1.0 за умовою CFL
        m_dt = m_courant * m_dx / m_waveSpeed;
        m_cSq = m_courant * m_courant;

        m_uPrev.assign(m_nodes, 0.0);
        m_uCurr.assign(m_nodes, 0.0);
        m_uNext.assign(m_nodes, 0.0);
        m_envelope.assign(m_nodes, 0.0);
    }

    SimResult run(double freqHz = 150.0, size_t steps = 1000, const std::string& boundary = "fixed") {
        const double omega = 2.0 * M_PI * freqHz;

        for (size_t step = 0; step < steps; ++step) {
            const double t = static_cast<double>(step) * m_dt;

            // Збудження синусоїдальним джерелом на лівому кінці
            m_uCurr[0] = std::sin(omega * t);

            // Оновлення внутрішніх точок
            for (size_t i = 1; i < m_nodes - 1; ++i) {
                double laplacian = m_uCurr[i + 1] - 2.0 * m_uCurr[i] + m_uCurr[i - 1];
                m_uNext[i] = 2.0 * m_uCurr[i] - m_uPrev[i] + m_cSq * laplacian;
            }

            // Права гранична умова
            if (boundary == "fixed") {
                m_uNext[m_nodes - 1] = 0.0;
            } else if (boundary == "free") {
                m_uNext[m_nodes - 1] = m_uNext[m_nodes - 2];
            }

            // Накопичення обвідної та зсув шарів
            for (size_t i = 0; i < m_nodes; ++i) {
                m_envelope[i] = std::max(m_envelope[i], std::abs(m_uNext[i]));
                m_uPrev[i] = m_uCurr[i];
                m_uCurr[i] = m_uNext[i];
            }
        }

        size_t nNodes = 0;
        size_t nAntinodes = 0;
        double maxEnv = 0.0;
        for (size_t i = 1; i < m_nodes - 1; ++i) {
            if (m_envelope[i] < 0.05) nNodes++;
            if (m_envelope[i] > 1.8) nAntinodes++;
            if (m_envelope[i] > maxEnv) maxEnv = m_envelope[i];
        }

        return {m_dx, m_dt, nNodes, nAntinodes, maxEnv};
    }

private:
    double m_length;
    size_t m_nodes;
    double m_waveSpeed;
    double m_dx;
    double m_dt;
    double m_courant;
    double m_cSq;

    std::vector<double> m_uPrev;
    std::vector<double> m_uCurr;
    std::vector<double> m_uNext;
    std::vector<double> m_envelope;
};

int main() {
    StandingWaveFDTD sim(1.0, 200, 100.0);

    SimResult resFixed = sim.run(150.0, 1000, "fixed");
    std::cout << "[Fixed Boundary] Max Envelope: " << resFixed.maxEnvelope
              << ", Nodes detected: " << resFixed.nodesCount << std::endl;

    SimResult resFree = sim.run(150.0, 1000, "free");
    std::cout << "[Free Boundary] Max Envelope: " << resFree.maxEnvelope
              << ", Antinodes detected: " << resFree.antinodesCount << std::endl;

    return 0;
}
