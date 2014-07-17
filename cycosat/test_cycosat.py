# -*- coding: utf-8 -*-
from cycosat import CoSAT

sat = CoSAT()
sat.add_clause([1, 2])
sat.add_clause([2, 3])
sat.add_clause([3, 4])

print sat.solve()
print "---"
for sol in sat.iter_solve():
    print sol
    
print "---"
    
for sol in sat.iter_solve():
    print sol
    
print "---"

print sat.solve()
sat.add_clause([-2])
print sat.clauses
print sat.solve()
sat.add_clause([-4])
print sat.clauses
print sat.solve()

#print sat.get_failed_assumes()