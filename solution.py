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
            # Sjekker gyldighet av action før vi utfører den ved å returnere False hvis ugyldig 
            if action == "U":
                row -= 1
            elif action == "D":
                row += 1
            elif action == "L":
                col -= 1
            elif action == "R":
                col += 1
            elif action == "W":
                
                # Sikkerhetsmessig sjekk: sjekk grenser og hindring før tilgang, selv om dette også sjekkes etter hver action
                # Dette er for å unngå å prøve å vanne utenfor grid eller på en hindring, som ville krasje programmet
                # Selv med sjekken etter hver action, er nødvendig fordi vi prøver å aksessere grid[row][col] her for å finne plantetype
                # og uten denne sjekken kan vi få IndexError eller lignende exceptions hvis vi er utenfor grid
                # Kan diskuteres om dette er overflødig sikkerhet, siden vi også sjekker etter hver action som garanterer
                # at vi ikke er utenfor eller på en hindring ved starten av neste loop. Men god sikkerhetspraksis skulle noe flyttes i koden
                # og action skjer før sjekken etter action, så er det greit å ha denne sjekken her også. 
                if not (0 <= row < self.N and 0 <= col < self.M):
                    if verbose: print("Out of bounds before W")
                    return False
                if self.grid[row][col] == -1:
                    if verbose: print("Obstacle at W location")
                    return False
                
                # Hvis koden kjører hit uten å ha returnert, vet vi at vi er på et gyldig sted for 
                # vanning og trygt å aksessere grid[row][col]
                
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

            # Automatisk påfyll kun ved ankomst til (0,0)
            if action in ("U", "D", "L", "R") and (row, col) == (0, 0):
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
        """Returnerer en liste over gyldige handlinger fra denne staten.
            For eksempel: state = (0,0,5,0b00,3) → returnerer ["D","R"] (kan ikke gå U eller L fra (0,0))
        """
        
        row, col, water, mask, time = state # Pakker ut state tuple til individuelle variabler slik at koden blir mer lesbar
        acts = [] # Liste over kun gyldige handlinger fra denne staten slik at vi ikke prøver ugyldige handlinger i search og får unødvendige noder i søketreet

        # Bevegelser (kun hvis innenfor og ikke -1) 
        def ok(nr, nc): #Lokal hjelpefunksjon for å sjekke om en posisjon er innenfor grid og ikke en hindring nr står for new row og nc for new col
            return 0 <= nr < self.N and 0 <= nc < self.M and self.grid[nr][nc] != -1
        # ok(nr, nc) filtrerer ulovlige bevegelser; vi tester hver retning og legger bare gyldige inn i acts:
        # nr < self.N sjekker at vi ikke går utenfor gridet nedover og nr >= 0 sjekker oppover 
        # nc < self.M sjekker at vi ikke går utenfor gridet til høyre og nc >= 0 sjekker venstre
        # self.grid[nr][nc] != -1 sjekker at vi ikke går inn i en hindring

        if ok(row - 1, col): acts.append("U") #Hvis vi kan gå opp, legg til "U" i acts
        if ok(row + 1, col): acts.append("D") #Hvis vi kan gå ned, legg til "D" i acts
        if ok(row, col - 1): acts.append("L") #Hvis vi kan gå venstre, legg til "L" i acts
        if ok(row, col + 1): acts.append("R") #Hvis vi kan gå høyre, legg til "R" i acts

        # Ved start (0,0) kan vi for eksempel ikke gå opp eller venstre, så acts vil da bare få "D" og "R" som gyldige bevegelser
        # Dette hindrer at search prøver å gå utenfor grid eller inn i hindringer og dermed lager unødvendige noder i søketreet
        # som senere blir forkastet fordi de er ugyldige, og vi ville dermed spare tid og minne i søket ved å ikke generere disse nodene i det hele tatt

        # Så må vi sjekke om vi kan vanne på denne posisjonen og legge til "W" hvis det er gyldig
        cell = self.grid[row][col] # Hent cell-typen på nåværende posisjon
        if cell > 0: # Hvis det er en plante her
            # Bit-indeks for denne plantecellen (fra mappingen bygget i load): 
            # Vi bruker én int som maske der hver bit markerer om en plante er vannet (1) eller ikke (0).
            # linjen under her henter bit-indeksen for denne planteposisjonen fra pos_to_bit ordboken
            bit = self.pos_to_bit.get((row, col)) 
            if bit is not None: # Sikkerhetssjekk, burde alltid være sant her fordi cell > 0
                already = (mask >> bit) & 1  # Sjekk om denne planten allerede er vannet ved å skifte masken bit ganger til høyre og AND med 1
                # For eksempel, hvis bit er 2 (tredje planten vi fant i grid), skifter vi masken 2 ganger til høyre slik at bit 2 kommer til posisjon 0
                # Hadde den vært vannet, ville masken hatt en 1 i bit 2, så etter skiftet ville vi hatt 0b...001 (1 i posisjon 0). AND sjekker bare den siste biten
                # når vi gjør (mask >> bit) får vi 1 hvis planten er vannet, 0 hvis ikke, og når vi AND med 1 får vi samme resultat (1 eller 0). 1 AND 1 = 1, 0 AND 1 = 0
                wk, dk = self.plants[cell] # Hent vann- og deadline-krav for denne plantetypen 
                # Deadline-sjekk: lov hvis time <= dk
                if (not already) and (water >= wk) and (time <= dk):
                    acts.append("W") # Hvis ikke allerede vannet, nok vann, og innen deadline, legg til "W" i acts

        return acts # Returner listen over gyldige handlinger fra denne staten

    def result(self, state, action):
        """
            Gitt en tilstand og en handling, returnerer funksjonen den nye tilstanden slik den blir etter at handlingen er utført.
            For eksempel: state = (0,0,5,0b00,3) og action = "D" → ny state = (1,0,5,0b00,4).

            I søketreet representerer hver node en state. Når søkemotoren står på en node, kaller den først actions(state)
            for å finne alle mulige handlinger (grenene ut fra noden). For hver av disse handlingene kalles result(state, action),
            som returnerer den nye staten på enden av denne grenen. Dermed vokser treet ved at nye noder (states) opprettes og kobles
            til den nåværende noden via grener merket med handlingene. Grenen merket med D fra state (0,0,5,0b00,3) fører til en ny
            node med state (1,0,5,0b00,4).
        """
        
        row, col, water, mask, time = state # Pakker ut state tuple til individuelle variabler slik at koden blir mer lesbar

        # Basert på action, oppdaterer vi state variablene tilsvarende
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
            cell = self.grid[row][col] # Hent cell-typen på nåværende posisjon
            wk, dk = self.plants[cell] # Hent vann- og deadline-krav for denne plantetypen
            water -= wk # Oppdater state for gjenværende vann ved å trekke fra tilsvarende mengde som kreves for denne plantetypen
            bit = self.pos_to_bit[(row, col)] # Hent bit-indeks for denne planteposisjonen fra mappingen bygget i load
            mask |= (1 << bit) # VIKTIG: Oppdater masken for vannede planter ved å sette bit-en for denne planten til 1 (vannet) ved å bruke bit-or operasjon
            # |= setter mask til mask ELLER (1 << bit). (1 << bit) lager en maske med bare den bit-en satt til 1, resten 0.
            # For eksempel, hvis bit er 2 (tredje planten vi fant i grid), blir (1 << 2) til 0b00000100. Når vi gjør mask |= 0b00000100, setter vi bit nr 2 i mask til 1, uansett hva den var før.
            # Dette markerer at denne planten nå er vannet i den nye staten. 
        else:
            # Ukjent action, returner uendret state som en sikkerhetsmekanisme
            return state

        time += 1 # Øk tid med 1 for hver handling (uansett type)

        # Automatisk påfyll KUN når vi beveger oss inn i (0,0)
        if action in ("U", "D", "L", "R") and (row, col) == (0, 0):
            water = self.W0
        
        # Returner den nye staten som en tuple 
        return (row, col, water, mask, time)


    def goal_test(self, state):
        """
            Gitt en tilstand, returnerer funksjonen True hvis alle planter er vannet, ellers False.
            For eksempel: state = (3,4,2,0b111,10) → returnerer True hvis vi har 3 planter totalt og alle er vannet (mask 0b111).
        """
        _, _, _, mask, _ = state # Pakker ut bare mask-delen av staten, resten er ikke relevant for måltesten
        return mask == self.full_mask # Sjekk om masken med vannede planter er lik full_mask som har alle planter vannet


    def path_cost(self, c, state1, action, state2):
        """ 
            Denne funksjonen returnerer kostnaden for å nå state2 fra state1 ved å utføre action. 
            I dette problemet er kostnaden for hver handling 1, så vi returnerer c + 1. Overflødig
            å definere denne funksjonen når hver handling har lik kostnad, men det kan
            være nyttig for tilpasning (kanskje i fremtidige utvidelser av problemet og vi ikke bruker BFS). Bruker ikke
            state1, action, state2 her siden kostnaden er konstant. c er den totale kostnaden for å nå state1.
            For eksempel: c = 5, state1 = (0,0,5,0b00,3), action = "D", state2 = (1,0,5,0b00,4) → returnerer 6.
        """
        return c + 1


    def solve(self):
        """
            Søker etter en løsning (sekvens av handlinger) fra initial state til goal state ved å bruke
            en uninformed search-algoritme (f.eks. BFS). Returnerer en streng med handlinger som representerer
            løsningen, eller None hvis ingen løsning finnes.
            For eksempel: returnerer "DDRRWUUW" som en sekvens av handlinger.
        """
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
