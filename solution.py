import search 

# we can make the namings more descriptive in relation to the context of the problem

class GardenerProblem(search.Problem):
    def __init__(self):
        super().__init__(initial=None) # Call parent constructor (not strictly necessary here, but good practice), need to understand 
        # Problem data
        self.N = 0
        self.M = 0
        self.W0 = 0
        self.grid = []
        self.plants = {}


    def load(self, fh):
        """Load the grid and plant info from file handle fh."""
        lines = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
        # First line: N, M, W0
        self.N, self.M, self.W0 = map(int, lines[0].split())

        self.grid = [] 
        for i in range(1, 1 + self.N):
            self.grid.append(list(map(int, lines[i].split())))

        for idx, line in enumerate(lines[1 + self.N:], start=1):
            wk, dk = map(int, line.split())
            self.plants[idx] = (wk, dk)


    def check_solution(self, plan, verbose=False) -> bool:  # trenger vi egt verbose her hmm
        row, col = 0, 0
        water = self.W0
        time = 0
        watered = set()

        # for each action we need to fist do the acton and then we can check the state of our position and grid to validate weather the plan has failed or we can continue 
        # If all tests are passed when the plan loop is completed the function returns True
        for action in plan:  
            if action == "U": row -= 1
            elif action == "D": row += 1
            elif action == "L": col -= 1
            elif action == "R": col += 1
            elif action == "W":
                plant_type = self.grid[row][col]
                if plant_type <= 0: return False
                wk, dk = self.plants[plant_type]
                if water < wk or time > dk: return False
                if (row, col) in watered: return False
                water -= wk
                watered.add((row, col))
            else:
                return False  # invalid character
            
            time += 1 # important to add after the Water action as else the test will fail

            # Check boundaries and obstacles
            if not (0 <= row < self.N and 0 <= col < self.M): return False
            if self.grid[row][col] == -1: return False

            # Refill water at (0,0)
            if (row, col) == (0, 0):
                water = self.W0

        # After no more letters in string, check that all plants are watered
        for i in range(self.N):
            for j in range(self.M):
                if self.grid[i][j] > 0 and (i, j) not in watered:
                    return False

        return True