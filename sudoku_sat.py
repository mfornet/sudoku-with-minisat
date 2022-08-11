import sys
import time
from subprocess import PIPE, call
from typing import List


class Clause:
    def __init__(self, clause: List[int]):
        self.clause = clause

    def __or__(self, var):
        self.clause.append(var)
        return self


class SAT:
    def __init__(self):
        self._clauses = []
        self._variables = {}
        self._value = None
        self.solved = False

    def __getitem__(self, *args) -> int:
        if not args in self._variables:
            ix = len(self._variables) + 1
            self._variables[args] = ix
        return self._variables[args]

    def clause(self):
        self._clauses.append([])
        return Clause(self._clauses[-1])

    def __str__(self):
        return f"Variables: {len(self._variables)} Clauses: {len(self._clauses)}"

    def num_variables(self):
        return len(self._variables)

    def num_clauses(self):
        return len(self._clauses)

    def print(self, io):
        print(f'p cnf {self.num_variables()} {self.num_clauses()}', file=io)
        for clause in self._clauses:
            print(' '.join(map(str, clause + [0])), file=io)

    def value(self, *args) -> int:
        return self._value[self[args]-1]

    def solve(self):
        with open('sat_tmp.cnf', 'w') as f:
            self.print(f)

        start = time.perf_counter()
        ret = call(
            ['minisat', 'sat_tmp.cnf', 'sat_tmp.out'], stdout=PIPE)
        end = time.perf_counter()

        print("Solving took {} seconds".format(end - start), file=sys.stderr)

        self._solved = True

        with open('sat_tmp.out') as f:
            lines = f.read().strip(' \n').split('\n')
            if lines[0] == 'SAT':
                self._value = [int(x) > 0 for x in lines[1].split()[:-1]]
                return True
            else:
                return False


class Sudoku:
    def __init__(self, sat: SAT):
        self._sat = sat
        self._solution = None

    def get_solution(self):
        if not self._sat.solved:
            self._sat.solve()

        board = [[0] * 9 for _ in range(9)]

        if self._sat._value is None:
            self._solution = board
            return board

        for x in range(1, 10):
            for y in range(1, 10):
                for n in range(1, 10):
                    if self._sat.value(x, y, n):
                        board[x-1][y-1] = n
                        break

        self._solution = board
        return board

    def __str__(self):
        if self._solution is None:
            self.get_solution()
        return '\n'.join(' '.join(map(str, line)) for line in self._solution)


def get_sudoku_solution(sat: SAT):
    assert sat.solve()


def square(n):
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            yield (i, j)


def generate_sudoku():
    sat = SAT()

    for x in range(1, 10):
        for y in range(1, 10):
            # One most be active
            c = sat.clause()
            for n in range(1, 10):
                c |= sat[x, y, n]
                for m in range(1, n):
                    # No two can be active
                    c_in = sat.clause()
                    c_in |= -sat[x, y, m]
                    c_in |= -sat[x, y, n]

    # Rows
    for row in range(1, 10):
        for x in range(1, 10):
            for y in range(1, x):
                for n in range(1, 10):
                    c = sat.clause()
                    c |= -sat[row, x, n]
                    c |= -sat[row, y, n]

    # Rows
    for col in range(1, 10):
        for x in range(1, 10):
            for y in range(1, x):
                for n in range(1, 10):
                    c = sat.clause()
                    c |= -sat[x, col, n]
                    c |= -sat[y, col, n]

    # Squares
    for sx, sy in square(3):
        for x1, y1 in square(3):
            for x2, y2 in square(3):
                if (x1, y1) == (x2, y2):
                    break

                nx1 = x1 - 1 + (sx - 1) * 3 + 1
                ny1 = y1 - 1 + (sy - 1) * 3 + 1
                nx2 = x2 - 1 + (sx - 1) * 3 + 1
                ny2 = y2 - 1 + (sy - 1) * 3 + 1
                for n in range(1, 10):
                    c = sat.clause()
                    c |= -sat[nx1, ny1, n]
                    c |= -sat[nx2, ny2, n]

    return sat


def classic(description: str):
    sat = generate_sudoku()
    for x, line in enumerate(line for line in description.replace(' ', '').strip('\n').split('\n') if line):
        if not line:
            continue

        assert len(line) == 9
        for y, n in enumerate(line):
            if n != '.':
                c = sat.clause()
                c |= sat[x + 1, y + 1, int(n)]
    return sat


# Check rules for crack the cryptic in this video
# https://www.youtube.com/watch?v=wO1G7GkIrWE
def crack_the_cryptic(cages, numbers):
    sat = classic(numbers)

    dic = {}

    # Numbers in cages are different
    for x, line in enumerate(line for line in cages.replace(' ', '').strip('\n').split('\n') if line):
        assert len(line) == 9
        for y, n in enumerate(line):
            if n != '.':
                value = dic.get(n, [])
                value.append((x + 1, y + 1))
                dic[n] = value

    for value in dic.values():
        for i in range(len(value)):
            for j in range(i):
                xi, yi = value[i]
                xj, yj = value[j]
                for n in range(1, 10):
                    c = sat.clause()
                    c |= -sat[xi, yi, n]
                    c |= -sat[xj, yj, n]

    # No consecutive numbers
    for i in range(1, 10):
        for j in range(1, 10):
            for n in range(1, 10):
                for dx, dy in ([0, +1], [+1, 0]):
                    for dn in [-1, +1]:
                        nx, ny, nn = i + dx, j + dy, n + dn
                        if 1 <= nx <= 9 and 1 <= ny <= 9 and 1 <= nn <= 9:
                            c = sat.clause()
                            c |= -sat[i, j, n]
                            c |= -sat[nx, ny, nn]
    return sat


if __name__ == '__main__':
    s = Sudoku(classic("""
    ..4 .6. 97.
    ... 7.9 ..4
    2.. .1. ...

    ..8 .26 ...
    3.. 194 ...
    5.9 3.. 1..

    7.. 9.. 64.
    4.. 6.. .3.
    ..3 ... .21
    """))

    print("\nSolving classic sudoku:")
    print(s)

    s = Sudoku(crack_the_cryptic(
        """
    AAA DDD III
    A.B DED IHI
    AAB DEI IHH

    AAB DEE I.H
    BBB DDE EGH
    B.B BF. FGH

    CCC CFF FGG
    C.C .F. FGG
    C.C FF. GGG
    """, """
    ... ... ...
    ... ... ...
    ... ... ...

    ... ... ...
    ... ... ...
    ... ... ...

    ... 2.. ...
    ... ... ...
    ... ... ...
    """))

    print("\nSolving sudoku from crack the cryptic (https://www.youtube.com/watch?v=wO1G7GkIrWE):")
    print(s)
