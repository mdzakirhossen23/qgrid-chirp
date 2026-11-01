"""QGrid Chirp: reproducible 4-qubit QAOA dispatch simulation."""
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass, asdict

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import DiagonalGate
from qiskit.quantum_info import Statevector


@dataclass(frozen=True)
class Source:
    name: str
    capacity: float
    carbon: float
    cost: float


SOURCES = (
    Source("Solar", 42, 18, 14),
    Source("Wind", 34, 11, 12),
    Source("Hydro", 28, 24, 19),
    Source("Battery", 22, 35, 27),
)


def objective(index: int, demand: float, carbon_priority: float) -> dict:
    selected = [(index >> q) & 1 for q in range(4)]
    power = sum(s.capacity * bit for s, bit in zip(SOURCES, selected))
    emissions = sum(s.capacity * s.carbon / 1000 * bit for s, bit in zip(SOURCES, selected))
    operating = sum(s.capacity * s.cost / 100 * bit for s, bit in zip(SOURCES, selected))
    shortage, oversupply = max(0, demand - power), max(0, power - demand)
    score = shortage**2 * 2.8 + oversupply**2 * 0.65
    score += emissions * (4 + carbon_priority * 13) + operating
    return {
        "cost": score,
        "power_mw": power,
        "carbon_t_h": emissions,
        "sources": [s.name for s, bit in zip(SOURCES, selected) if bit],
    }


def qaoa_circuit(normalized_costs: np.ndarray, gammas: list[float], betas: list[float]) -> QuantumCircuit:
    qc = QuantumCircuit(4)
    qc.h(range(4))
    for gamma, beta in zip(gammas, betas):
        qc.append(DiagonalGate(np.exp(-1j * gamma * normalized_costs)), range(4))
        qc.rx(2 * beta, range(4))
    return qc


def solve(demand: float = 75, carbon_priority: float = 0.60, noise: float = 0.08) -> dict:
    if not (demand > 0 and 0 <= carbon_priority <= 1 and 0 <= noise <= 1):
        raise ValueError("Demand must be positive; carbon priority and noise must be in [0,1].")
    states = [objective(i, demand, carbon_priority) for i in range(16)]
    raw = np.array([s["cost"] for s in states])
    normalized = (raw - raw.min()) / max(float(np.ptp(raw)), 1.0)
    best = {"expected": math.inf}
    seed = 2166136261
    def random():
        nonlocal seed
        seed = (seed * 1664525 + 1013904223) & 0xffffffff
        return seed / 4294967296

    for _ in range(3200):
        gammas = [random() * 2 * np.pi, random() * 2 * np.pi]
        betas = [random() * np.pi / 2, random() * np.pi / 2]
        statevector = Statevector.from_instruction(qaoa_circuit(normalized, gammas, betas))
        probabilities = np.abs(statevector.data) ** 2
        expected = float(probabilities @ normalized)
        if expected < best["expected"]:
            best = {
                "expected": expected,
                "gammas": gammas,
                "betas": betas,
                "probabilities": probabilities,
            }

    step = 0.25
    for _ in range(7):
        for parameter in range(4):
            for direction in [-1, 1]:
                gammas, betas = best["gammas"].copy(), best["betas"].copy()
                if parameter < 2:
                    gammas[parameter] += direction * step
                else:
                    betas[parameter - 2] += direction * step
                probabilities = Statevector.from_instruction(qaoa_circuit(normalized, gammas, betas)).probabilities()
                expected = float(probabilities @ normalized)
                if expected < best["expected"]:
                    best = dict(expected=expected, gammas=gammas, betas=betas, probabilities=probabilities)
        step *= 0.55
    probabilities = best["probabilities"] * (1 - noise) + noise / 16
    measured = int(np.argmax(probabilities))
    classical = int(np.argmin(raw))
    return {
        "model": "QGrid Chirp p=2 QAOA",
        "demand_mw": demand,
        "carbon_priority": carbon_priority,
        "uniform_noise_mixture": noise,
        "gammas": best["gammas"],
        "betas": best["betas"],
        "expected_normalized_cost": best["expected"],
        "most_probable_state": format(measured, "04b"),
        "most_probable_probability": float(probabilities[measured]),
        "dispatch": states[measured],
        "exact_classical_state": format(classical, "04b"),
        "exact_match": measured == classical,
        "sources": [asdict(s) for s in SOURCES],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--demand", type=float, default=75)
    parser.add_argument("--carbon-priority", type=float, default=0.60)
    parser.add_argument("--noise", type=float, default=0.08)
    args = parser.parse_args()
    print(json.dumps(solve(args.demand, args.carbon_priority, args.noise), indent=2))


