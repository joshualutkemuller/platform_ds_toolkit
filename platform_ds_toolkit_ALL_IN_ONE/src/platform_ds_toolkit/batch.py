def chunk_list(xs,n):
  for i in range(0,len(xs),n): yield xs[i:i+n]
