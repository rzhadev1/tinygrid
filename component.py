from pyomo.environ import *
import numpy as np
import pandas as pd
from pyomo.opt import SolverFactory

#from pyomo.core.kernel.piecewise_library.transforms import PiecewiseLinearFunction
#shouldnt mix kerel and environ
class Bus(): # a bus is a node in the graph with demand, generators, and branches in/out
	def __init__(self, n, t, i, l): 
		self.name = n
		self.type = t # the type of this bus; 1: PQ bus, 2: PV bus, 3: slack, 4: isolated
		self.id = i 
		assert(1 <= self.type <= 4)
		self.load = l # real power load at this bus
		self.gens = [] # set of generators at this bus
	
	def __repr__(self):
		return f"{self.name}, {self.type}, {self.id}, {self.load}"

class Generator(): 
	_idx = 0
	def __init__(self, pts, ab, s, pmin, pmax): # pts is a set of (mw, cost) pairs
		self.pts = np.array(pts)
		self.cost_f = lambda mw: np.interp(mw, self.pts[:, 0], self.pts[:, 1])
		self.at_bus_id = ab # the bus where the gen is located 
		self.status = s # whether the generator is off or not at t0
		self.pmin = pmin # minimum real power output 
		self.pmax = pmax # maximum real power output
		self.pg = 0 # MW power to produce at this generator
		self.id = Generator._idx
		Generator._idx += 1

	def __repr__(self): 
		return f"{self.at_bus_id}, {self.status}, {self.pmin}, {self.pmax}"

	def __call__(self, mw): # return the cost at a mw amount
		return self.cost_f(mw)
	
	def get_cost_breakpts(self): # return the mw breakpoints in cost func
		return self.pts[:, 0].tolist()

class Branch(): # a branch is an edge between two buses

	_idx = 0
	def __init__(self, fb, tb, x, s, r): 
		self.from_bus = fb # from bus i 
		self.to_bus = tb # to bus j
		self.x = x # reactance of the line in p.u
		self.status = s # whether the branch is off
		self.rating = r # line rating in MWA (same in MW)
		self.flow = 0
		self.id = Branch._idx 
		Branch._idx += 1

	def __repr__(self): 
		return "{self.from_bus}, {self.to_bus}, {self.x}, {self.status}, {self.angle_diff}, {self.rating}"
