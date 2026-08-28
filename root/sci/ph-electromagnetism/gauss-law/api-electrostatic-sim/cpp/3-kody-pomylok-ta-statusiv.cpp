// C++20 Strongly Typed Errors
namespace physics::electrodynamics {

enum class SimError {
    InvalidArgument,
    OutOfMemory,
    Divergence,
    MaxIterationsReached,
    InvalidBoundary
};

} // namespace physics::electrodynamics
