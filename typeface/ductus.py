"""Hypothetical pen routes; jerk regularization, not historical handwriting data."""

import numpy as np

ROUTES = {
    "lifted": (
        ((300, 700), (650, 350), (300, 0)),
        ((80, 560), (475, 175)),
        ((80, 140), (475, 525)),
    ),
    "retraced": (
        ((300, 700), (650, 350), (300, 0), (475, 175),
         (80, 560), (295, 350), (475, 525), (80, 140)),
    ),
    "bowl_leg": (
        ((100, 685), (300, 685), (465, 610), (480, 490),
         (355, 365), (125, 345), (475, 0)),
    ),
}
SAMPLES, STIFFNESS = 96, 1200


def resample(vertices):
    p = np.asarray(vertices, dtype=float)
    lengths = np.r_[0, np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))]
    t = np.linspace(0, lengths[-1], SAMPLES)
    return np.column_stack([np.interp(t, lengths, p[:, axis]) for axis in (0, 1)])


def smooth(vertices, stiffness=STIFFNESS):
    """Minimize fidelity error + lambda * squared discrete third differences.

    Samples stand for equal time intervals; constant-speed polyline traversal is
    the reference motion. Endpoints are fixed. No human calibration or inferred
    stroke order is claimed. This is not the Flash/Hogan constrained solution.
    """
    p = resample(vertices)
    d3 = np.diff(np.eye(SAMPLES), n=3, axis=0)
    matrix = np.eye(SAMPLES) + stiffness * d3.T @ d3
    ends = p[[0, -1]]
    rhs = p[1:-1] - matrix[1:-1][:, [0, -1]] @ ends
    result = p.copy()
    result[1:-1] = np.linalg.solve(matrix[1:-1, 1:-1], rhs)
    return result


def trajectories(name, smoothing=True):
    return [(smooth(route) if smoothing else resample(route))
            for route in ROUTES[name]]


def length(routes):
    return sum(float(np.linalg.norm(np.diff(p, axis=0), axis=1).sum()) for p in routes)


def em_print_path():
    # The route change is an authored proposal, not discovered by smoothing.
    p = trajectories("bowl_leg")[0]
    return "M " + " L ".join(f"{x:.3f} {y:.3f}" for x, y in p)


if __name__ == "__main__":
    for name in ROUTES:
        paths = trajectories(name)
        print(f"{name}: {len(paths)} strokes, {length(paths):.0f} units pen travel")
