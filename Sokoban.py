from lib import text2dimacs
import subprocess

import tkinter as tk
from pathlib import Path
import shutil


class Sokoban:

    def __init__(self):
        self.limit = 23
        self.iteracia = 1
        self.listOfActions = []
        self.map_name = self.choose_map()
        self.map = self.load_map(self.map_name)
        self.x1S = 1
        self.x1E = len(self.map) - 1
        self.y1S = 1
        self.y1E = len(self.map[0]) - 2

    def choose_map(self):
        maps = ["map1.txt", "map8.txt", "map4.txt", "map5.txt", "map6.txt", "map7.txt"]
        for i, k in enumerate(maps):
            if (i == 0):
                print("Povinné mapy:")
            if (i == 2):
                print()
                print("Testovacie mapy:")
            if (i == 5):
                print()
                print("Bonusova mapa:")
            print(str(i + 1) + " - (" + str(k) + str(")"))
        print()
        print("Vyber si číslo mapy, ktorá sa má riešiť:")
        input_chossen_map = input()
        return maps[int(input_chossen_map) - 1].split(".")[0]

    def load_map(self, map_name):
        with open("maps/" + map_name + ".txt") as f:
            lines = f.readlines()
        return lines

    def solve(self):
        dirpath = Path('results') / self.map_name
        if dirpath.exists() and dirpath.is_dir():
            shutil.rmtree(dirpath)
        dirpath.mkdir()

        while self.iteracia < self.limit:
            iter_dir = dirpath / f"{self.iteracia}_iteration"
            iter_dir.mkdir()

            CNF_clausules = self.CNF()
            cnf_path = iter_dir / 'cnf.txt'
            with cnf_path.open("w", encoding="utf-8") as f:
                for line in CNF_clausules:
                    f.write(f"{line}\n")
            dinamics_path = iter_dir / 'dinamics.txt'
            text2dimacs.translate(
                cnf_path.open("r", encoding="utf-8"),
                dinamics_path.open("w", encoding="utf-8"))

            minisat_path = iter_dir / 'minisat.txt'
            args = ('lib/minisat/win/minisat.exe',
                    str(dinamics_path),
                    str(minisat_path))
            popen = subprocess.Popen(args, stdout=subprocess.PIPE)
            popen.wait()

            with minisat_path.open("r", encoding="utf-8") as f:
                ms_lines = f.readlines()

            if ms_lines[0].strip() == "UNSAT":
                self.iteracia += 1
                self.listOfActions = []
                continue
            else:
                break
        moves = {}
        moves_list = []
        with dinamics_path.open("r", encoding="utf-8") as f:
            # all_dimacs = f.readlines()
            variables = f.read().split("Variables")[1].split("\n")
        sat = ms_lines[1].strip().split(" ")
        for i in sat:
            if (int(i) > 0):
                for k in variables:
                    c = k.split("c")
                    if (len(c) > 1):
                        pom = c[1].strip().split(" ")
                        if (int(pom[0]) == int(i)):
                            n = pom[1].split("(")
                            if (n[0] == "move" or n[0] == "push"):
                                p = n[1].split(",")[4].split(")")[0]
                                moves[p] = pom[1]
        out_path = dirpath / 'output.txt'

        print()
        with out_path.open("w", encoding="utf-8") as f:
            for move in range(len(moves)):
                f_move = str(move + 1) + ". " + moves[str(move + 1)]
                print(f_move)
                moves_list.append(moves[str(move + 1)])
                f.write(f_move + "\n")
        self.animation(moves)

    def animation(self, moves):
        self.mapV = []
        for i in self.map:
            self.mapV.append(list(i.replace('\n', '')))
            if len(self.mapV[len(self.mapV) - 1]) < len(self.mapV[0]):
                self.mapV[len(self.mapV) - 1].append(" ")

        root = tk.Tk()
        canvas = tk.Canvas(root, width=len(self.mapV[0]) * 75 + 50, height=len(self.mapV) * 75 + 50)
        canvas.pack()

        for i in range(len(moves)):
            canvas.delete("all")
            self.print_map(canvas)
            root.update()
            root.after(1300)
            cl = moves[str(i + 1)]
            action = cl.strip().split('(')[0]
            cord = cl.strip().split('(')[1].split(',')

            if action == "move":
                if self.mapV[int(cord[0])][int(cord[1])] == "S":
                    self.mapV[int(cord[0])][int(cord[1])] = " "
                elif self.mapV[int(cord[0])][int(cord[1])] == "s":
                    self.mapV[int(cord[0])][int(cord[1])] = "X"
                if self.mapV[int(cord[2])][int(cord[3])] == "X":
                    self.mapV[int(cord[2])][int(cord[3])] = "s"
                elif self.mapV[int(cord[2])][int(cord[3])] == " ":
                    self.mapV[int(cord[2])][int(cord[3])] = "S"

            if action == "push":
                dx = 0
                dy = 0
                if int(cord[0]) < int(cord[2]):
                    dx = 1
                if int(cord[0]) > int(cord[2]):
                    dx = -1
                if int(cord[1]) < int(cord[3]):
                    dy = 1
                if int(cord[1]) > int(cord[3]):
                    dy = -1

                if self.mapV[int(cord[0])][int(cord[1])] == "S":
                    self.mapV[int(cord[0])][int(cord[1])] = " "
                if self.mapV[int(cord[2])][int(cord[3])] == "C":
                    self.mapV[int(cord[2])][int(cord[3])] = "S"
                if self.mapV[int(cord[0])][int(cord[1])] == "s":
                    self.mapV[int(cord[0])][int(cord[1])] = "X"
                if self.mapV[int(cord[2])][int(cord[3])] == "c":
                    self.mapV[int(cord[2])][int(cord[3])] = "s"

                if self.mapV[int(cord[2]) + dx][int(cord[3]) + dy] == " ":
                    self.mapV[int(cord[2]) + dx][int(cord[3]) + dy] = "C"
                if self.mapV[int(cord[2]) + dx][int(cord[3]) + dy] == "X":
                    self.mapV[int(cord[2]) + dx][int(cord[3]) + dy] = "c"
        canvas.delete("all")
        self.print_map(canvas)
        root.update()
        root.after(1300)
        root.mainloop()

    def print_map(self, canvas):
        for x in range(len(self.mapV)):
            for y in range(len(self.mapV[0])):
                if self.mapV[x][y] == '#':
                    canvas.create_rectangle(y * 75 + 25, x * 75 + 25, y * 75 + 100, x * 75 + 100, outline="black",
                                            fill="grey")
                    canvas.create_text(y * 75 + 65, x * 75 + 65, text="#", font=('Helvetica', '50', 'bold'))
                elif self.mapV[x][y] == 'S':
                    canvas.create_rectangle(y * 75 + 25, x * 75 + 25, y * 75 + 100, x * 75 + 100, outline="black",
                                            fill="turquoise")
                    canvas.create_text(y * 75 + 65, x * 75 + 65, text="S", font=('Helvetica', '50', 'bold'))
                elif self.mapV[x][y] == 'C':
                    canvas.create_rectangle(y * 75 + 25, x * 75 + 25, y * 75 + 100, x * 75 + 100, outline="black",
                                            fill="red")
                    canvas.create_text(y * 75 + 65, x * 75 + 65, text="C", font=('Helvetica', '50', 'bold'))
                elif self.mapV[x][y] == 'X':
                    canvas.create_rectangle(y * 75 + 25, x * 75 + 25, y * 75 + 100, x * 75 + 100, outline="black",
                                            fill="orange")
                    canvas.create_text(y * 75 + 65, x * 75 + 65, text="X", font=('Helvetica', '50', 'bold'))
                elif self.mapV[x][y] == 's':
                    canvas.create_rectangle(y * 75 + 25, x * 75 + 25, y * 75 + 100, x * 75 + 100, outline="black",
                                            fill="turquoise")
                    canvas.create_text(y * 75 + 65, x * 75 + 65, text="s", font=('Helvetica', '50', 'bold'))
                elif self.mapV[x][y] == 'c':
                    canvas.create_rectangle(y * 75 + 25, x * 75 + 25, y * 75 + 100, x * 75 + 100, outline="black",
                                            fill="green")
                    canvas.create_text(y * 75 + 65, x * 75 + 65, text="c", font=('Helvetica', '50', 'bold'))
                else:
                    canvas.create_rectangle(y * 75 + 25, x * 75 + 25, y * 75 + 100, x * 75 + 100, outline="black")

    def CNF(self):
        CNF_clauses = []
        ## INIT/GOAl STATE
        x = 0
        y = 0
        CNF_clauses.append(f"c Initial/Goal State")
        for line in self.map:
            for symbol in line:
                if (symbol == "#"):
                    for i in range(self.iteracia):
                        CNF_clauses.append(f"at(#,{x},{y},{i})")
                if (symbol == "S"):
                    CNF_clauses.append(f"at(S,{x},{y},0)")
                if (symbol == "C"):
                    CNF_clauses.append(f"at(C,{x},{y},0)")
                if (symbol == "X"):
                    CNF_clauses.append(f"-at(C,{x},{y},0)")
                    for i in range(self.iteracia):
                        CNF_clauses.append(f"at(X,{x},{y},{i})")

                    CNF_clauses.append(f"at(c,{x},{y},{self.iteracia - 1})")
                    CNF_clauses.append(f"-at(c,{x},{y},{self.iteracia - 1}) v at(C,{x},{y},{self.iteracia - 1})")
                if (symbol == " "):
                    CNF_clauses.append(f"-at(C,{x},{y},0)")
                if (symbol == "c"):
                    CNF_clauses.append(f"at(C,{x},{y},0)")
                    for i in range(self.iteracia):
                        CNF_clauses.append(f"at(X,{x},{y},{i})")

                    CNF_clauses.append(f"at(c,{x},{y},{self.iteracia - 1})")
                if (symbol == "s"):
                    CNF_clauses.append(f"at(c,{x},{y},{self.iteracia - 1})")
                    CNF_clauses.append(f"-at(c,{x},{y},{self.iteracia - 1}) v at(C,{x},{y},{self.iteracia - 1})")
                    CNF_clauses.append(f"at(S,{x},{y},0)")
                    for i in range(self.iteracia):
                        CNF_clauses.append(f"at(X,{x},{y},{i})")
                y += 1
            y = 0
            x += 1

        ##ACTIONS
        self.x1S = 1
        self.x1E = len(self.map) - 1
        self.y1S = 1
        self.y1E = len(self.map[0]) - 2
        CNF_clauses.append(f"c Actions")
        # MOVE
        CNF_clauses.append(f"c move(x1,y1,x2,y2,i)")
        for x1 in range(self.x1S, self.x1E):
            for y1 in range(self.y1S, self.y1E):
                # HORE
                if (x1 - 1 >= self.x1S):
                    for i in range(1, self.iteracia):
                        self.listOfActions.append([0, x1, y1, x1 - 1, y1, i])
                        CNF_clauses.append(f"-move({x1},{y1},{x1 - 1},{y1},{i}) v at(S,{x1},{y1},{i - 1})")
                        CNF_clauses.append(f"-move({x1},{y1},{x1 - 1},{y1},{i}) v -at(S,{x1},{y1},{i})")
                        CNF_clauses.append(f"-move({x1},{y1},{x1 - 1},{y1},{i}) v at(S,{x1 - 1},{y1},{i})")

                # DOLE
                if (x1 + 1 < self.x1E):
                    for i in range(1, self.iteracia):
                        self.listOfActions.append([0, x1, y1, x1 + 1, y1, i])
                        CNF_clauses.append(f"-move({x1},{y1},{x1 + 1},{y1},{i}) v at(S,{x1},{y1},{i - 1})")
                        CNF_clauses.append(f"-move({x1},{y1},{x1 + 1},{y1},{i}) v -at(S,{x1},{y1},{i})")
                        CNF_clauses.append(f"-move({x1},{y1},{x1 + 1},{y1},{i}) v at(S,{x1 + 1},{y1},{i})")

                # VLAVO
                if (y1 - 1 >= self.y1S):
                    for i in range(1, self.iteracia):
                        self.listOfActions.append([0, x1, y1, x1, y1 - 1, i])
                        CNF_clauses.append(f"-move({x1},{y1},{x1},{y1 - 1},{i}) v at(S,{x1},{y1},{i - 1})")
                        CNF_clauses.append(f"-move({x1},{y1},{x1},{y1 - 1},{i}) v -at(S,{x1},{y1},{i})")
                        CNF_clauses.append(f"-move({x1},{y1},{x1},{y1 - 1},{i}) v at(S,{x1},{y1 - 1},{i})")

                # VPRAVO
                if (y1 + 1 < self.y1E):
                    for i in range(1, self.iteracia):
                        self.listOfActions.append([0, x1, y1, x1, y1 + 1, i])
                        CNF_clauses.append(f"-move({x1},{y1},{x1},{y1 + 1},{i}) v at(S,{x1},{y1},{i - 1})")
                        CNF_clauses.append(f"-move({x1},{y1},{x1},{y1 + 1},{i}) v -at(S,{x1},{y1},{i})")
                        CNF_clauses.append(f"-move({x1},{y1},{x1},{y1 + 1},{i}) v at(S,{x1},{y1 + 1},{i})")

        # PUSH
        CNF_clauses.append(f"c push(x1,y1,x2,y2,i)")
        for x1 in range(self.x1S, self.x1E):
            for y1 in range(self.y1S, self.y1E):
                # HORE
                if (x1 - 2 >= self.x1S):
                    for i in range(1, self.iteracia):
                        self.listOfActions.append([1, x1, y1, x1 - 1, y1, i])
                        CNF_clauses.append(f"-push({x1},{y1},{x1 - 1},{y1},{i}) v move({x1},{y1},{x1 - 1},{y1},{i})")
                        CNF_clauses.append(f"-push({x1},{y1},{x1 - 1},{y1},{i}) v at(C,{x1 - 1},{y1},{i - 1})")
                        CNF_clauses.append(f"-push({x1},{y1},{x1 - 1},{y1},{i}) v -at(C,{x1 - 1},{y1},{i})")
                        CNF_clauses.append(f"-push({x1},{y1},{x1 - 1},{y1},{i}) v at(C,{x1 - 2},{y1},{i})")
                        CNF_clauses.append(f"-push({x1},{y1},{x1 - 1},{y1},{i}) v -at(C,{x1 - 2},{y1},{i - 1})")

                # DOLE
                if (x1 + 2 < self.x1E):
                    for i in range(1, self.iteracia):
                        self.listOfActions.append([1, x1, y1, x1 + 1, y1, i])
                        CNF_clauses.append(f"-push({x1},{y1},{x1 + 1},{y1},{i}) v move({x1},{y1},{x1 + 1},{y1},{i})")
                        CNF_clauses.append(f"-push({x1},{y1},{x1 + 1},{y1},{i}) v at(C,{x1 + 1},{y1},{i - 1})")
                        CNF_clauses.append(f"-push({x1},{y1},{x1 + 1},{y1},{i}) v -at(C,{x1 + 1},{y1},{i})")
                        CNF_clauses.append(f"-push({x1},{y1},{x1 + 1},{y1},{i}) v at(C,{x1 + 2},{y1},{i})")
                        CNF_clauses.append(f"-push({x1},{y1},{x1 + 1},{y1},{i}) v -at(C,{x1 + 2},{y1},{i - 1})")

                # VLAVO
                if (y1 - 2 >= self.y1S):
                    for i in range(1, self.iteracia):
                        self.listOfActions.append([1, x1, y1, x1, y1 - 1, i])
                        CNF_clauses.append(f"-push({x1},{y1},{x1},{y1 - 1},{i}) v move({x1},{y1},{x1},{y1 - 1},{i})")
                        CNF_clauses.append(f"-push({x1},{y1},{x1},{y1 - 1},{i}) v at(C,{x1},{y1 - 1},{i - 1})")
                        CNF_clauses.append(f"-push({x1},{y1},{x1},{y1 - 1},{i}) v -at(C,{x1},{y1 - 1},{i})")
                        CNF_clauses.append(f"-push({x1},{y1},{x1},{y1 - 1},{i}) v at(C,{x1},{y1 - 2},{i})")
                        CNF_clauses.append(f"-push({x1},{y1},{x1},{y1 - 1}, {i}) v -at(C, {x1}, {y1 - 2}, {i - 1})")

                        # VPRAVO
                if (y1 + 2 < self.y1E):
                    for i in range(1, self.iteracia):
                        self.listOfActions.append([1, x1, y1, x1, y1 + 1, i])
                        CNF_clauses.append(f"-push({x1},{y1},{x1},{y1 + 1},{i}) v move({x1},{y1},{x1},{y1 + 1},{i})")
                        CNF_clauses.append(f"-push({x1},{y1},{x1},{y1 + 1},{i}) v at(C,{x1},{y1 + 1},{i - 1})")
                        CNF_clauses.append(f"-push({x1},{y1},{x1},{y1 + 1},{i}) v -at(C,{x1},{y1 + 1},{i})")
                        CNF_clauses.append(f"-push({x1},{y1},{x1},{y1 + 1},{i}) v at(C,{x1},{y1 + 2},{i})")
                        CNF_clauses.append(f"-push({x1},{y1},{x1},{y1 + 1},{i}) v -at(C,{x1},{y1 + 2},{i - 1})")

        # TRIGGERING
        pom = 0
        CNF_clauses.append(f"c At least one")
        for i in range(1, self.iteracia):
            cl = ""
            for act in self.listOfActions:
                if act[5] == i:
                    if (pom != 0):
                        cl += " v "
                    else:
                        pom += 1
                    if act[0] == 0:
                        cl += f"move({act[1]},{act[2]},{act[3]},{act[4]},{act[5]})"
                    else:
                        cl += f"push({act[1]},{act[2]},{act[3]},{act[4]},{act[5]})"
            pom = 0
            CNF_clauses.append(cl)

        ##file.write("c Mutually exclusive\n")
        CNF_clauses.append(f"c Mutually exclusive")
        for act in self.listOfActions:
            for act2 in self.listOfActions:
                if act != act2:
                    if act[5] == act2[5] and (
                            act[1] == act2[1] and act[2] == act2[2] and act[3] == act2[3] and act[4] == act2[
                        4]) == False:
                        if act[0] == 0:
                            if act2[0] == 0:
                                CNF_clauses.append(
                                    f"-move({act[1]},{act[2]},{act[3]},{act[4]},{act[5]}) v -move({act2[1]},{act2[2]},{act2[3]},{act2[4]},{act2[5]})")
                            else:
                                CNF_clauses.append(
                                    f"-move({act[1]},{act[2]},{act[3]},{act[4]},{act[5]}) v -push({act2[1]},{act2[2]},{act2[3]},{act2[4]},{act2[5]})")
                        else:
                            if act2[0] == 0:
                                CNF_clauses.append(
                                    f"-push({act[1]},{act[2]},{act[3]},{act[4]},{act[5]}) v -move({act2[1]},{act2[2]},{act2[3]},{act2[4]},{act2[5]})")
                            else:
                                CNF_clauses.append(
                                    f"-push({act[1]},{act[2]},{act[3]},{act[4]},{act[5]}) v -push({act2[1]},{act2[2]},{act2[3]},{act2[4]},{act2[5]})")

        ##BACKGROUND
        ## file.write("c Background\n")
        ##file.write("c Player box and wall cant be on same place\n")
        CNF_clauses.append(f"c Background")
        CNF_clauses.append(f"c Player box and wall cant be on same place")
        for x1 in range(self.x1S, self.x1E):
            for y1 in range(self.y1S, self.y1E):
                for i in range(0, self.iteracia):
                    CNF_clauses.append(f"-at(S,{x1},{y1},{i}) v -at(#,{x1},{y1},{i})")
                    CNF_clauses.append(f"-at(S,{x1},{y1},{i}) v -at(C,{x1},{y1},{i})")

        ##file.write("c Player can be only on one place\n")
        CNF_clauses.append(f"c Player can be only on one place")
        for x1 in range(self.x1S, self.x1E):
            for y1 in range(self.y1S, self.y1E):
                for x2 in range(self.x1S, self.x1E):
                    for y2 in range(self.y1S, self.y1E):
                        for i in range(0, self.iteracia):
                            if ((x1 == x2 and y1 == y2) == False):
                                CNF_clauses.append(f"-at(S,{x1},{y1},{i}) v -at(S,{x2},{y2},{i})")

        ##FRAME
        ##file.write("c FRAME\n")
        CNF_clauses.append(f"c FRAME")
        for x1 in range(self.x1S, self.x1E):
            for y1 in range(self.y1S, self.y1E):
                cl = ""
                for i in range(1, self.iteracia):
                    cl += f"at(S,{x1},{y1},{i - 1}) v -at(S,{x1},{y1},{i})"
                    for act in self.listOfActions:
                        if (act[3] == x1 and act[4] == y1 and act[5] == i):
                            if act[0] == 0:
                                cl += f" v move({act[1]},{act[2]},{act[3]},{act[4]},{act[5]})"
                            else:
                                cl += f" v push({act[1]},{act[2]},{act[3]},{act[4]},{act[5]})"
                    CNF_clauses.append(cl)
                    cl = ""
                    cl += f"-at(S,{x1},{y1},{i - 1}) v at(S,{x1},{y1},{i})"
                    for act in self.listOfActions:
                        if (act[1] == x1 and act[2] == y1 and act[5] == i):
                            if act[0] == 0:
                                cl += f" v move({act[1]},{act[2]},{act[3]},{act[4]},{act[5]})"
                            else:
                                cl += f" v push({act[1]},{act[2]},{act[3]},{act[4]},{act[5]})"

                    CNF_clauses.append(cl)
                    cl = ""
                    if ((x1 == 1 and y1 == 1) or (x1 == 1 and y1 == self.y1E - 1) or (
                            x1 == self.x1E - 1 and y1 == 1) or (x1 == self.x1E - 1 and y1 == self.y1E - 1)) == False:
                        cl += f"-at(C,{x1},{y1},{i - 1}) v at(C,{x1},{y1},{i})"
                        for act in self.listOfActions:
                            if (((act[3] == x1 and act[4] == y1 and act[1] == x1 - 1 and act[2] == y1) or (
                                    act[3] == x1 and act[4] == y1 and act[1] == x1 + 1 and act[2] == y1) or (
                                         act[3] == x1 and act[4] == y1 and act[1] == x1 and act[2] == y1 - 1) or (
                                         act[3] == x1 and act[4] == y1 and act[1] == x1 and act[2] == y1 + 1)) and act[
                                5] == i):
                                if act[0] == 1:
                                    cl += f" v push({act[1]},{act[2]},{act[3]},{act[4]},{act[5]})"
                    CNF_clauses.append(cl)
                    cl = ""
                    cl += f"at(C,{x1},{y1},{i - 1}) v -at(C,{x1},{y1},{i})"
                    for act in self.listOfActions:
                        if (((act[3] == x1 - 1 and act[4] == y1 and act[1] == x1 - 2 and act[2] == y1) or (
                                act[3] == x1 + 1 and act[4] == y1 and act[1] == x1 + 2 and act[2] == y1) or (
                                     act[3] == x1 and act[4] == y1 - 1 and act[1] == x1 and act[2] == y1 - 2) or (
                                     act[3] == x1 and act[4] == y1 + 1 and act[1] == x1 and act[2] == y1 + 2)) and act[
                            5] == i):
                            if act[0] == 1:
                                cl += f" v push({act[1]},{act[2]},{act[3]},{act[4]},{act[5]})"
                    CNF_clauses.append(cl)
                    cl = ""
        return CNF_clauses


s = Sokoban()
s.solve()
