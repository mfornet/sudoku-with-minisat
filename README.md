# Sudoku with SAT solver

Install [minisat](https://github.com/niklasso/minisat):

```
brew install minisat
```

Generate and solve sudokus using:

```
python sudoku_sat.py
```

## How it works

The script generates the constraints that needs to be satisfied in a valid sudoku solution.
The clauses are written to a file `sat_tmp.cnf` and then `minisat` is used to compute the solution in `sat_tmp.out`.

In the generated sat there are 9 variables per cell (9 x 81 = 243 in total), one per potential value. Constraints are created with respect to these variables. Notice that in the output, each batch of consecutive 9 elements, contains exactly one positive element (the value on that cell).

## Motivation

This project was done to learn how to use minisat in practice, and how hard would be for a computer to solve [this challenge](https://www.youtube.com/watch?v=wO1G7GkIrWE) from Cracking the Cryptic. In my machine it takes 6.9 seconds.
