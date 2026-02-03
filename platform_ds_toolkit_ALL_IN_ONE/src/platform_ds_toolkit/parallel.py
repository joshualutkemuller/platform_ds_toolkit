import multiprocessing as mp

def parallel_map(f, xs):
  with mp.Pool() as p: return p.map(f,xs)
