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

        # A2-forberedelser: se forklaring hvordan dette fungerer lenger nede i load()
        self.plant_positions = [] # liste over (i,j) for alle planteceller, i fast rekkefølge
        self.pos_to_bit = {}      # (i,j) -> bitindeks i masken
        self.full_mask = 0      # maske med alle planter vannet

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

        # Bygg plante-mapping for A2: 
        # Det som skjer under her er at vi lager en liste over alle planteposisjoner (i,j) i rekkefølge vi finner dem i grid,
        # og en ordbok som mapper hver (i,j) til en unik bit-indeks (0, 1, 2, ...). Dette gjør det enkelt å representere hvilke 
        # planter som er vannet med en bitmaske. F.eks. hvis vi har 3 planter, vil full_mask være 0b111 (7 i desimal), 
        # og hvis vi har vannet de to første, vil masken være 0b011 (3 i desimal). Vi kan så bruke bit-operasjoner for å sjekke 
        # og oppdatere denne masken effektivt. Hvis vi vil sjekke for eksempel om den andre planten er vannet, kan vi gjøre (mask & (1 << 1)) != 0. 
        # Eller om vi vil markere den tredje planten som vannet, kan vi gjøre mask |= (1 << 2). Eller sjekke om alle planter er vannet ved å sammenligne mask med full_mask.
        
        self.plant_positions = [] #Starter tom her
        self.pos_to_bit = {}     #Starter tom her
        for i in range(self.N):
            for j in range(self.M):
                if self.grid[i][j] > 0: #Hvis vi altså har en plante
                    bit = len(self.plant_positions) #Settes bit til denne til nåværende lengde (første er 0 også videre oppover)
                    self.plant_positions.append((i, j)) #Legger til i liste over planteposisjoner
                    self.pos_to_bit[(i, j)] = bit #Mapper posisjon til bit, første plante får bit 0, andre får bit 1 osv 

        self.full_mask = (1 << len(self.plant_positions)) - 1 #Her lager vi en maske med alle planter vannet. Hvis vi har 3 planter, blir dette 0b111 (7 i desimal).
        
        # Initial state for A2: (row, col, water, watered_mask, time)
        self.initial = (0, 0, self.W0, 0, 0) # Starter i posisjon (0,0) med full vann, ingen vannet, tid 0

    # ----------------------------
    # Assignment 1 validator
    # ----------------------------
    def check_solution(self, plan, verbose=False) -> bool:
        
        # Initialisering
        row, col = 0, 0
        water = self.W0
        time = 0
        watered = set() 
        # Bruker set og ikke mitt bitmaskekode her for enkelhets skyld, 
        # skal ikke være effektivt her som i A2 hvor vi trenger å sjekke mange ganger med BFS
        # watered blir da {(0, 2), (3, 1), (2, 4)} for eksempel

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
                
                # Hvis koden kjører hit uten å ha returnert, vet vi at vi er på et gyldig sted for vanning
                
                plant_type = self.grid[row][col] # Hent plantetype
                if plant_type <= 0: 
                    if verbose: print("No plant to water here")
                    return False
                
                # Hvis vi kjører hit, vet vi at vi har en plante som kan vannes
                
                wk, dk = self.plants[plant_type] # Hent vann- og deadline-krav for denne plantetypen
                if water < wk:
                    if verbose: print("Not enough water")
                    return False
                if time > dk:
                    if verbose: print(f"Deadline missed at time {time} > {dk}")
                    return False
                if (row, col) in watered:
                    if verbose: print("Plant already watered")
                    return False

                # Hvis vi kjører hit, vet vi at vi har nok vann, innen deadline, og planten er ikke vannet fra før

                water -= wk # Bruk vann
                watered.add((row, col)) # Legger til posisjonen til planten som er vannet i settet
            else:
                if verbose: print(f"Invalid action {action}")
                return False
            
            #Hvis vi kjører hit, har vi utført en gyldig handling
        
            time += 1 # Øk tid med 1 for hver handling (uansett type) 

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

        # Hvis vi kjører hit, er planen ferdig kjørt uten å bryte noen regler 
        
        # Nå må vi sjekke at alle planter er vannet (og ingen er glemt) 
        for i in range(self.N):
            for j in range(self.M):
                if self.grid[i][j] > 0 and (i, j) not in watered:
                    if verbose: print(f"Unwatered plant at {(i,j)}")
                    return False # Fant en plante som ikke er vannet med den planen, fikser ikke det her men forteller at planen er ugyldig 

        return True # Hvis vi har kjørt gjennom hele planen uten å returnere False, er planen gyldig

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
