from pyomo.environ import *
import numpy as np
import pandas as pd
from pyomo.opt import SolverFactory

class Bus(): # a bus is a node in the graph with demand, generators, and branches in/out
	def __init__(self, n, t, i, theta, l): 
		self.name = n
		self.type = t
		self.id = i 
		self.theta = theta # voltage angle at this bus, mag is approx 1
		self.load = l # real power load at this bus
		self.gens = [] # set of generators at this bus
	
	def __repr__(self):
		return f"{self.name}, {self.type}, {self.id}, {self.theta}, self.load"

class Generator(): 
	_idx = 0 # identifier for optimization, inc whenever we make a new gen
	def __init__(self, pts, ab, s, pmin, pmax): # pts is a set of (mw, cost) pairs
		pts = np.array(pts)
		self.cost_f = lambda mw : np.interp(mw, pts[:, 0], pts[:, 1], left=0) 
		self.at_bus_id = ab # the bus where the gen is located 
		self.status = s # whether the generator is off or not at t0
		self.pmin = pmin # minimum real power output 
		self.pmax = pmax # maximum real power output
		self.id = _idx
		_idx += 1

	def __repr__(self): 
		return f"{self.at_bus_id}, {self.status}, {self.pmin}, {self.pmax}"

class Branch(): # a branch is an edge between two buses with a fixed capacity
	_idx = 0
	def __init__(self, fb, tb, x, s, a, r): 
		self.from_bus = fb # from bus i 
		self.to_bus = tb # to bus j
		self.x = x # reactance of the line in p.u
		self.status = s # whether the branch is off
		self.angle_diff = self.from_bus.theta - self.to_bus.theta
		self.rating = r # line rating in MWA (same in MW)
		self.id = _idx 
		_idx += 1
	def __repr__(self): 
		return f"{self.from_bus}, {self.to_bus}, {self.x}, {self.status}, {self.angle_diff}, {self.rating}"
