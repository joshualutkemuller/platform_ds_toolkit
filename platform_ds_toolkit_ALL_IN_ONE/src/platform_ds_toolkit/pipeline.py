class Task:
  def __init__(s,n,f): s.n=n; s.f=f
  def run(s): s.f()
class Pipeline:
  def __init__(s,t): s.t=t
  def run(s): [x.run() for x in s.t]
