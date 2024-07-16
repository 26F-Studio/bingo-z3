import z3
from argparse import ArgumentParser

# define a 5x5 bool grid
grid = [[z3.Bool(f'{i}_{j}') for j in range(5)] for i in range(5)]

def in_range(i, j):
  return 0 <= i < 5 and 0 <= j < 5

def get_neighbors(i, j):
  return [
    (i + di, j + dj)
    for di in [-1, 0, 1] for dj in [-1, 0, 1]
    if in_range(i + di, j + dj) and (di, dj) != (0, 0)
  ]

def red(i, j):
  # at least one of the neighbors is true
  return z3.Or([grid[ni][nj] for ni, nj in get_neighbors(i, j)])

def blue(i, j):
  # at most two of the neighbors are true
  return z3.PbLe([(grid[ni][nj], 1) for ni, nj in get_neighbors(i, j)], 2)

def black(i, j):
  # must be true
  return grid[i][j]

def green(i, j):
  # count of trues in the row and column must be the same
  # return whether they are both 0 or both 1 or both 2 etc
  return z3.Or([
    z3.And(
      z3.PbEq([(grid[i][k], 1) for k in range(5)], n),
      z3.PbEq([(grid[k][j], 1) for k in range(5)], n)
    )
    for n in range(5)
  ])

def yellow(i, j):
  # count of trues in the both diagonals must be the same
  return z3.Or([
    z3.And(
      z3.PbEq([(grid[i + k][j + k], 1) for k in range(-5, 5) if in_range(i + k, j + k)], n),
      z3.PbEq([(grid[i + k][j - k], 1) for k in range(-5, 5) if in_range(i + k, j - k)], n)
    )
    for n in range(5)
  ])

def orange(i, j):
  # count of trues in the neighbors should be even
  return z3.Or([
    z3.PbEq([(grid[ni][nj], 1) for ni, nj in get_neighbors(i, j)], n)
    for n in range(8) if n % 2 == 0
  ])

def purple(i, j):
  # count of trues in the neighbors should be odd
  return z3.Or([
    z3.PbEq([(grid[ni][nj], 1) for ni, nj in get_neighbors(i, j)], n)
    for n in range(8) if n % 2 == 1
  ])

def pink(i, j):
  # left, right, up and down cannot be true if this is true
  return z3.Or([
    z3.Not(grid[i][j]),
    z3.And([
      z3.Not(grid[i + di][j + dj])
      for di, dj in [[-1, 0], [1, 0], [0, -1], [0, 1]]
      if in_range(i + di, j + dj)
    ])
  ])

def empty(i, j):
  return True

def bingo():
  # 5 of the same row or column or diagonal are all true
  return z3.Or([
    z3.Or([
      z3.Or([
        z3.And([grid[i][j] for j in range(5)]),
        z3.And([grid[j][i] for j in range(5)])
      ])
      for i in range(5)
    ]),
    z3.And([grid[i][i] for i in range(5)]),
    z3.And([grid[i][4 - i] for i in range(5)])
  ])

maps = {
  'red': red,
  'blue': blue,
  'black': black,
  'green': green,
  'yellow': yellow,
  'orange': orange,
  'purple': purple,
  'pink': pink,
  'empty': empty
}

def graph_to_expression(graph):
  return z3.And(
    z3.And([
      maps[graph[i][j]](i, j)
      for i in range(5) for j in range(5)
    ]),
    bingo()
  )

def solve_and_print(graph):
  s = z3.Solver()
  s.add(graph_to_expression(graph))
  s.check()
  model = s.model()
  for i in range(5):
    for j in range(5):
      print('X' if model[grid[i][j]] else 'O', end=' ')
    print()

def get_parser():
  parser = ArgumentParser()
  # 25 space-separated strings
  parser.add_argument('graph', nargs=25, type=str, choices=list(maps.keys()))
  return parser

def main(args):
  graph = [args.graph[i * 5:(i + 1) * 5] for i in range(5)]
  solve_and_print(graph)

if __name__ == '__main__':
  parser = get_parser()
  main(parser.parse_args())