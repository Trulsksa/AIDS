from solution import GardenerProblem
from pathlib import Path

public_test_data = Path(__file__).parent / "public2"

for i in range(10):
    stem = f"ex{i}"
    problem_path  = public_test_data / f"{stem}.dat"

    gp = GardenerProblem()
    with open(problem_path) as f:
        gp.load(f)

    plan = gp.solve()
    if plan is None:
        print(f"{stem}: Ingen løsning funnet")
    else:
        valid = gp.check_solution(plan)
        print(f"{stem}: Foreslått plan = {plan}, gyldig? {valid}")
