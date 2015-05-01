import numpy as np
from scpy2.cycosat import CoSAT
from scpy2.examples.sudoku_solver import SudokuSolver


def test_cycosat_simple():
    sat = CoSAT()
    problem = [[1, -4], [1, -2], [1, 4], [-4, -2],
               [-4, 4], [-2, 4], [-1, 4, 2, -4]]

    sat.add_clauses(problem)
    assert sat.solve() == [1, -1, -1, -1]


def test_sudoku():
    problem = {
        (0, 0): 1,
        (1, 1): 2,
        (2, 2): 3
    }

    ss = SudokuSolver()
    res = ss.solve(problem)
    assert np.all(np.sort(res, axis=1) == np.arange(1, 10))
    assert np.all(np.sort(res, axis=0) == np.arange(1, 10)[:, None])
    for (r, c), v in problem.items():
        assert res[r, c] == v