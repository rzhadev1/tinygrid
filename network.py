from pyomo.environ import *
import numpy as np
import pandas as pd
from pyomo.opt import SolverFactory
from component import Bus, Branch, Generator

class Network(): # a graph of the electrical grid
	
	def __init__(self):
		self._model = ConcreteModel()
		self.bus_set = {} # mapping from bus id -> Bus object 
		self.branch_set = []
	
	def build(self): # build the optimization problem
		# TODO: probably want to use params here, maybe except for cost functions (need to look into it )
		gen_map = {g.id : g for b in self.bus_set.values() for g in b.gens} # flatten gens to dict, map from indices to objs
		branch_map {br.id : br for br in self.branch_set}
		total_load = sum([b.load for b in self.bus_set.values()])

		self._model.gen_idxs = Set(gen_map.keys()) # set of generator id's
		self._model.branch_idxs = Set(branch_map.keys())
		self._model.pg = Var(self._model.gen_idxs) # output of generator g
		self._model.f_k = Var(self._model.branch_idxs) # the flow along line l
		self._model.obj = Objective(expr = 
			sum([gen_map[i].cost_f(self._model.pg[i]) for i in self._model.gen_idxs])
		)
		self._model.demand = Constraint(expr=sum([self._model.pg[i] for i in self._model.gen_idxs]) == total_load)
		self._model.gen_limit = Constraint(self._model.gen_idxs)
		for i in self._model.gen_idxs: 
			self._model.gen_limit[i] = gen_map[i].pmin <= self._model.pg[i] <= gen_map[i].pmax
		
		self._model.flow_limit = Constraint(self._model.branch_idxs)
		for i in self._model.branch_idxs: 
			self._model.flow_limit[i] = flow_(1 / (branch_map[i].x)) * (branch_map[i].angle_diff)
	def add_bus(self, bus): # add a node to the graph
		self.bus_set[bus.id] = bus
		
	def add_gen(self, gen): # add a generator to a bus
		self.bus_set[gen.at_bus].gens.append(gen)

	def add_branch(self, branch): # add an edge to the graph
		self.branch_set.append(branch)
