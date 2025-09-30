# solution.py
import search

# Aksjoner som tegn, for konsistens med oppgaven
ACTIONS = ("U", "D", "L", "R", "W")

class GardenerProblem(search.Problem):
    def __init__(self):
        # A1-data
        super().__init__(initial=None)
        self.N = 0
        self.M = 0
        self.W0 = 0
        self.grid = []
        self.plants = {}          # plant_type -> (wk, dk)

        # A2-forberedelser
        self.plant_positions = [] # liste over (i,j) for alle planteceller, i fast rekkefølge
        self.pos_to_bit = {}      # (i,j) -> bitindeks i masken
        self.full_mask = 0

    def load(self, fh):
        """Load the grid and plant info from file handle fh, and set self.initial (A2)."""
        lines = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
        self.N, self.M, self.W0 = map(int, lines[0].split())

        self.grid = []
        for i in range(1, 1 + self.N):
            row = list(map(int, lines[i].split()))
            assert len(row) == self.M, "Row length mismatch"
            self.grid.append(row)

        # Plantetyper (1..K)
        self.plants.clear()
        for idx, line in enumerate(lines[1 + self.N:], start=1):
            wk, dk = map(int, line.split())
            self.plants[idx] = (wk, dk)

        # Bygg plante-mapping for A2
        self.plant_positions = []
        self.pos_to_bit = {}
        for i in range(self.N):
            for j in range(self.M):
                if self.grid[i][j] > 0:
                    bit = len(self.plant_positions)
                    self.plant_positions.append((i, j))
                    self.pos_to_bit[(i, j)] = bit

        self.full_mask = (1 << len(self.plant_positions)) - 1

        # Initial state for A2: (row, col, water, watered_mask, time)
        self.initial = (0, 0, self.W0, 0, 0)

    # ----------------------------
    # Assignment 1 validator
    # ----------------------------
    def check_solution(self, plan, verbose=False) -> bool:
        row, col = 0, 0
        water = self.W0
        time = 0
        watered = set()

        for action in plan:
            # Utfør handling
            if action == "U":
                row -= 1
            elif action == "D":
                row += 1
            elif action == "L":
                col -= 1
            elif action == "R":
                col += 1
            elif action == "W":
                # Sikkerhetsmessig: sjekk grenser og hindring før tilgang
                if not (0 <= row < self.N and 0 <= col < self.M):
                    if verbose: print("Out of bounds before W")
                    return False
                if self.grid[row][col] == -1:
                    if verbose: print("Obstacle at W location")
                    return False

                plant_type = self.grid[row][col]
                if plant_type <= 0:
                    if verbose: print("No plant to water here")
                    return False
                wk, dk = self.plants[plant_type]
                if water < wk:
                    if verbose: print("Not enough water")
                    return False
                if time > dk:
                    if verbose: print(f"Deadline missed at time {time} > {dk}")
                    return False
                if (row, col) in watered:
                    if verbose: print("Plant already watered")
                    return False
                water -= wk
                watered.add((row, col))
            else:
                if verbose: print(f"Invalid action {action}")
                return False

            time += 1

            # Felles grense- og hinder-sjekk (etter action)
            if not (0 <= row < self.N and 0 <= col < self.M):
                if verbose: print("Out of bounds after action")
                return False
            if self.grid[row][col] == -1:
                if verbose: print("Moved into obstacle")
                return False

            # Automatisk påfyll
            if (row, col) == (0, 0):
                water = self.W0

        # Etter planen: alle planter må være vannet
        for i in range(self.N):
            for j in range(self.M):
                if self.grid[i][j] > 0 and (i, j) not in watered:
                    if verbose: print(f"Unwatered plant at {(i,j)}")
                    return False

        return True

    # ----------------------------
    # Assignment 2: Uninformed Search API
    # ----------------------------
    def actions(self, state):
        """Return a list of applicable actions in the given state."""
        row, col, water, mask, time = state
        acts = []

        # Bevegelser (kun hvis innenfor og ikke -1)
        def ok(nr, nc):
            return 0 <= nr < self.N and 0 <= nc < self.M and self.grid[nr][nc] != -1

        if ok(row - 1, col): acts.append("U")
        if ok(row + 1, col): acts.append("D")
        if ok(row, col - 1): acts.append("L")
        if ok(row, col + 1): acts.append("R")

        # Vanning
        cell = self.grid[row][col]
        if cell > 0:
            # Finn bit for (row,col)
            bit = self.pos_to_bit.get((row, col))
            if bit is not None:
                already = (mask >> bit) & 1
                wk, dk = self.plants[cell]
                # Deadline-sjekk: lov hvis time <= dk
                if (not already) and (water >= wk) and (time <= dk):
                    acts.append("W")

        return acts

    def result(self, state, action):
        """Return the resulting state after applying action."""
        row, col, water, mask, time = state

        if action == "U":
            row -= 1
        elif action == "D":
            row += 1
        elif action == "L":
            col -= 1
        elif action == "R":
            col += 1
        elif action == "W":
            # Vann på stedet
            cell = self.grid[row][col]
            wk, dk = self.plants[cell]
            water -= wk
            bit = self.pos_to_bit[(row, col)]
            mask |= (1 << bit)
        else:
            # Ukjent action -> returner uendret eller raise
            return state

        time += 1

        # Automatisk påfyll ved (0,0)
        if (row, col) == (0, 0):
            water = self.W0

        return (row, col, water, mask, time)

    def goal_test(self, state):
        """All plants watered?"""
        _, _, _, mask, _ = state
        return mask == self.full_mask

    # Valgfritt: eksplisitt path_cost hvis bibliotekt forventer den
    def path_cost(self, c, state1, action, state2):
        return c + 1

    def solve(self):
        """Call exactly one uninformed search method and return the plan string or None."""
        # Avhengig av search.py kan funksjonsnavnet variere:
        # Prøv en typisk BFS på grafer:
        node = search.breadth_first_graph_search(self)
        if node is None:
            return None

        # Hent aksjonssekvensen (AIMA-style: node.solution() -> list of actions)
        actions = node.solution() if hasattr(node, "solution") else node
        if actions is None:
            return None
        return "".join(actions)
