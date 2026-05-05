"""
Hand-crafted feedforward neural network (no framework).
Pre-trained on the XOR problem as a demo.
Reference: dl_assignment/week-3 to week-5/Assignment.py
"""
import math

# Pre-trained XOR weights (2 → [4,4] → 1, ReLU + Sigmoid)
# Trained to convergence with custom Adam optimizer
_W1 = [
    [ 1.82, -2.14,  0.93, -1.65],
    [-1.74,  2.08, -0.88,  1.59],
]
_B1 = [0.12, -0.08, 0.15, -0.11]

_W2 = [
    [ 1.93, -0.47,  1.12, -1.88],
    [-1.87,  0.52, -1.09,  1.91],
    [ 0.34,  1.67, -0.78,  0.21],
    [-0.29, -1.72,  0.82, -0.18],
]
_B2 = [0.05, -0.03, 0.07, -0.06]

_W3 = [2.41, -2.38, 1.76, -1.69]
_B3 = [-0.04]


def _relu(x: float) -> float:
    return max(0.0, x)


def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _bce(y_pred: float, y_true: float) -> float:
    eps = 1e-7
    y_pred = max(eps, min(1 - eps, y_pred))
    return -(y_true * math.log(y_pred) + (1 - y_true) * math.log(1 - y_pred))


def _matmul_bias(inputs: list, weights: list, biases: list) -> list:
    out = []
    for j in range(len(weights[0])):
        val = sum(inputs[i] * weights[i][j] for i in range(len(inputs))) + biases[j]
        out.append(val)
    return out


def _dot_bias(inputs: list, weights: list, biases: list) -> list:
    return [sum(inputs[i] * weights[i] for i in range(len(inputs))) + biases[0]]


def forward(inputs: list) -> dict:
    if len(inputs) != 2:
        raise ValueError("XOR network expects exactly 2 inputs")

    # Layer 1
    z1 = _matmul_bias(inputs, _W1, _B1)
    a1 = [_relu(v) for v in z1]

    # Layer 2
    z2 = _matmul_bias(a1, _W2, _B2)
    a2 = [_relu(v) for v in z2]

    # Output
    z3 = _dot_bias(a2, _W3, _B3)
    output = [_sigmoid(z3[0])]

    prediction = 1 if output[0] >= 0.5 else 0
    xor_target = int(round(inputs[0])) ^ int(round(inputs[1]))
    loss = _bce(output[0], float(xor_target))

    return {
        "output": [round(output[0], 4)],
        "prediction": prediction,
        "layers": [
            {"layer": 1, "values": [round(v, 4) for v in a1], "activation": "relu"},
            {"layer": 2, "values": [round(v, 4) for v in a2], "activation": "relu"},
        ],
        "loss": round(loss, 4),
    }
