# QGrid Chirp

An educational renewable dispatch studio using a four-qubit, two-layer QAOA simulation, with an exact classical audit.

Live demo: https://qgridchirp.baharsoftbd.com/

Track: Sustainability. Solo participant: MD Zakir Hossain — design, development, and validation. Prepared before the event; confirm organizer policy on pre-existing work before submitting. Do not represent this baseline as work completed during the sprint.

## Run

Serve this folder with `python -m http.server 8000`, then visit http://localhost:8000. The website runs locally in the browser without accounts or API keys.

For Qiskit, use Python 3.12, run `python -m pip install -r requirements.txt`, then `python downloads/qgrid_chirp_qiskit.py`. Optional arguments: `--demand 58 --carbon-priority 0.85 --noise 0.25`.

## Quantum implementation

Qubits q0–q3 represent solar, wind, hydro and battery on/off decisions. Displayed bitstrings are q3q2q1q0. Hadamards prepare 16 states. Two alternating diagonal cost unitaries exp(-i gamma C) and RX(2 beta) mixers create interference. A seeded classical search evaluates 3,200 parameter sets and seven coordinate-refinement passes. The Python CLI now follows the browser seed and search for all-enabled scenarios.

The objective is `2.8*shortage^2 + 0.65*oversupply^2 + (4+13*w)*E + O + I`, where E is tonnes CO2/hour, O is operating cost divided by 100, and I is a browser-only penalty for choosing disabled resources. Inputs and weights are illustrative. The energy balance terms use MW.

The browser calculates exact probabilities. Optional 1,024-shot simulation samples this distribution locally. A uniform mixture `(1-noise)*p + noise/16` flattens probabilities and preserves their ranking. It is not calibrated device noise. Each result is compared with exhaustive evaluation of all 16 schedules.

## Features and theme

English, Bengali and Hindi core interfaces; state inspector; probability chirps; optimization history; Python/OpenQASM exports; JSON reports. The Chi(r)ps connection is an interactive visual treatment of probability and interference, with explicit noise-model limitations.

## Validation and limitations

See VALIDATION.txt. Circuit probabilities were checked against Qiskit at 20 parameter sets. The exported Python script was executed and its OpenQASM parsed successfully. The all-enabled sunny search agrees with the browser. The most probable state is not guaranteed to minimize cost: sunny and evening scenarios miss the classical optimum; the tested storm case matches it.

No real-device execution or quantum advantage is claimed. The single-period model omits battery state of charge, ramping, transmission limits, losses and forecasts. The Python CLI assumes all sources enabled; browser circuit exports reproduce disabled-source scenarios with their frozen cost array and parameters. New workbench controls are in English. Mobile layout and final report download completion still need final visual/user verification.

## Submission artifacts

Public repository and 1–2 minute public video link must be added to Devpost. Register and confirm eligibility with organizers. This README does not certify submission or eligibility.

## License

MIT, copyright 2026 MD Zakir Hossain.
