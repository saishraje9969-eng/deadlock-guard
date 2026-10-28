# DeadlockGuard — Deadlock Detection and Avoidance System

Python desktop application for an Operating Systems college project.

## Features
- Banker's safety algorithm and safe sequence
- Need matrix calculation (Maximum - Allocation)
- Resource request checking: need, availability, then safety
- Deadlock detection using Allocation, Current Request and Available
- Resource allocation graph drawn with Tkinter Canvas
- CSV export
- Editable process/resource counts and sample input
- Backend unit tests

## Requirements
- Python 3.10+ recommended
- Tkinter (normally included with Windows Python)
- No third-party packages required

## Run in VS Code on Windows
1. Extract the ZIP.
2. Open the `DeadlockGuard_OS_Project` folder in VS Code.
3. Open Terminal → New Terminal.
4. Run `python main.py` (or `py main.py`).

## Run backend tests
`python -m unittest`

## Files
- `main.py`: GUI/frontend
- `deadlock.py`: backend algorithms
- `test_deadlock.py`: tests
- `requirements.txt`: dependency note

## Concepts
Need = Maximum - Allocation.
A state is safe if all processes can finish in some order using the available Work vector, releasing each completed process's allocation.
A resource request is granted only if it is within the process's remaining Need, within Available, and leaves the system safe.
Deadlock detection attempts to finish processes whose outstanding requests can be satisfied; unfinished processes are reported under the model's assumptions.

## Sample
The built-in classic Banker's example uses five processes, three resource types, and Available = [3, 3, 2]. It has a safe sequence.

## Limitation
This is an educational simulator. It does not control real Windows/Linux processes or kernel resources.
