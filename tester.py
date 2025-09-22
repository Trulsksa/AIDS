from solution import GardenerProblem
from pathlib import Path


public_test_data = Path(__file__).parent / "public1"

solutions: list[bool] = [True, False, False, False, False, False, True, False, True, False]
results: list[bool] = []

for i in range(10):
    stem = f"ex{i}"
    problem_path  = public_test_data / f"{stem}.dat"
    planned_path = public_test_data / f"{stem}.plan"

    gp = GardenerProblem()
    with open(problem_path) as f:
        gp.load(f)

    with open(planned_path) as f:
        plan = f.read().strip()
    result = gp.check_solution(plan, verbose=True)
    print(f"Checking {stem} → {result}")
    results.append(result)


print(f"Results:   {results}")
print(f"Solutions: {solutions}")

if results == solutions:
    print("All tests passed")