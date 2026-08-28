#pragma once

#include <vector>
#include <array>
#include <cmath>
#include <numbers>
#include <string_view>
#include <complex>

enum class ArrayTopology {
    Linear1D,
    Circular2D,
    Planar2D,
    Spherical3D,
    Custom
};

struct Point3D {
    float x{0.0f};
    float y{0.0f};
    float z{0.0f};
};

struct SteeringVector {
    float azimuthDeg{0.0f};
    float elevationDeg{0.0f};
    std::vector<float> delaysSeconds;
    std::vector<float> weights;
    std::vector<std::complex<float>> phaseShifts;
};

class ArrayGeometry {
public:
    ArrayGeometry(ArrayTopology topology, std::vector<Point3D> micPositions,
                  float samplingRate = 16000.0f, float soundSpeed = 343.0f)
        : m_topology(topology), m_positions(std::move(micPositions)),
          m_fs(samplingRate), m_c(soundSpeed) {
        calculateAliasingLimit();
    }

    static ArrayGeometry createUniformLinear(std::size_t numMics, float spacingMeters, float fs = 16000.0f) {
        std::vector<Point3D> pos;
        pos.reserve(numMics);
        for (std::size_t i = 0; i < numMics; ++i) {
            pos.push_back({ static_cast<float>(i) * spacingMeters, 0.0f, 0.0f });
        }
        return ArrayGeometry(ArrayTopology::Linear1D, std::move(pos), fs);
    }

    static ArrayGeometry createUniformCircular(std::size_t numMics, float radiusMeters, float fs = 16000.0f) {
        std::vector<Point3D> pos;
        pos.reserve(numMics);
        for (std::size_t i = 0; i < numMics; ++i) {
            const float angle = 2.0f * std::numbers::pi_v<float> * static_cast<float>(i) / static_cast<float>(numMics);
            pos.push_back({ radiusMeters * std::cos(angle), radiusMeters * std::sin(angle), 0.0f });
        }
        return ArrayGeometry(ArrayTopology::Circular2D, std::move(pos), fs);
    }

    [[nodiscard]] SteeringVector computeSteering(float azimuthDeg, float elevationDeg = 0.0f, float freqHz = 1000.0f) const {
        SteeringVector sv;
        sv.azimuthDeg = azimuthDeg;
        sv.elevationDeg = elevationDeg;
        sv.delaysSeconds.resize(m_positions.size());
        sv.weights.resize(m_positions.size(), 1.0f / static_cast<float>(m_positions.size()));
        sv.phaseShifts.resize(m_positions.size());

        const float azRad = azimuthDeg * std::numbers::pi_v<float> / 180.0f;
        const float elRad = elevationDeg * std::numbers::pi_v<float> / 180.0f;

        const Point3D u{
            std::sin(azRad) * std::cos(elRad),
            std::cos(azRad) * std::cos(elRad),
            std::sin(elRad)
        };

        for (std::size_t i = 0; i < m_positions.size(); ++i) {
            const float pathDiff = m_positions[i].x * u.x + m_positions[i].y * u.y + m_positions[i].z * u.z;
            sv.delaysSeconds[i] = pathDiff / m_c;
            const float phase = -2.0f * std::numbers::pi_v<float> * freqHz * sv.delaysSeconds[i];
            sv.phaseShifts[i] = std::complex<float>(std::cos(phase), std::sin(phase));
        }

        return sv;
    }

    [[nodiscard]] float getAliasingFrequencyHz() const noexcept { return m_aliasingFreqHz; }
    [[nodiscard]] std::size_t getNumMics() const noexcept { return m_positions.size(); }

private:
    void calculateAliasingLimit() {
        float minD = 1e6f;
        for (std::size_t i = 0; i < m_positions.size(); ++i) {
            for (std::size_t j = i + 1; j < m_positions.size(); ++j) {
                const float dx = m_positions[i].x - m_positions[j].x;
                const float dy = m_positions[i].y - m_positions[j].y;
                const float dz = m_positions[i].z - m_positions[j].z;
                const float d = std::sqrt(dx * dx + dy * dy + dz * dz);
                if (d < minD && d > 1e-5f) minD = d;
            }
        }
        m_aliasingFreqHz = m_c / (2.0f * minD);
    }

    ArrayTopology m_topology;
    std::vector<Point3D> m_positions;
    float m_fs;
    float m_c;
    float m_aliasingFreqHz{0.0f};
};
