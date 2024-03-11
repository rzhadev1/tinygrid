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
		self.slack_bus = None
	
	def build(self): # build the optimization problem
		gen_map = {g.id : g for b in self.bus_set.values() for g in b.gens} # flatten gens to dict, map from indices to objs
		branch_map = {br.id : br for br in self.branch_set}
		bus_map = {bus.id : bus for bus in self.bus_set.values()}
		self._model.total_load = Param(initialize=sum([b.load for b in self.bus_set.values()]))
		self._model.gen_idxs = Set(gen_map.keys()) # set of generator id's
		self._model.branch_idxs = Set(branch_map.keys()) # set of branch id's 
		self._model.bus_idxs = Set(bus_map.keys()) # set of bus id's

		self._model.pg = Var(self._model.gen_idxs) # output of generator g
		self._model.f_k = Var(self._model.branch_idxs) # the flow along line l
		self._model.theta_b = Var(self._model.bus_idxs) # the voltage angle at bus b
		
		self._model.obj = Objective(sum([gen_map[i].cost_f(self._model.pg[i]) for i in self._model.gen_idxs]), sense=minimize)
		self._model.demand = Constraint(expr=sum([self._model.pg[i] for i in self._model.gen_idxs]) == self._model.total_load)
		self._model.gen_limit = Constraint(self._model.gen_idxs) # gens are within thermal limits
		self._model.flow_limit = Constraint(self._model.branch_idxs) # branches are within limits
		self._model.power_flow = Constraint(self._model.branch_idxs) # B,theta model for flow equations
		self._model.angle_limit = Constraint(self._model.bus_idxs) # restrict bus angles
		self._model.slack_bus_eq = Constraint(self._model.theta_b[self.slack_bus.id] == 0) # reference bus has 0 angle

		for i in self._model.gen_idxs: 
			self._model.gen_limit[i] = gen_map[i].pmin <= self._model.pg[i] <= gen_map[i].pmax

		for k in self._model.branch_idxs: 
			b_k = branch_map[k]
			self._model.flow_limit[k] = -b_k.rating <= self._model.f_k[k] <= b_k.rating
			self._model.power_flow[k] = self._model.f_k[k] == \
				(1 / b_k.x) * (self._model.theta_b[b_k.from_bus.id] - self._mode.theta_b[b_k.to_bus.id])
		
		for b in self._model.bus_idxs: 
			self._model.angle_limit = -180 <= self._model.theta_b[b] <= 180

	def add_bus(self, bus): # add a node to the graph
		self.bus_set[bus.id] = bus

		if bus.is_slack: # only 1 slack bus allowed
			self.slack_bus = bus
		
	def add_gen(self, gen): # add a generator to a bus
		self.bus_set[gen.at_bus].gens.append(gen)

	def add_branch(self, branch): # add an edge to the graph
		self.branch_set.append(branch)

if __name__ == '__main__':
	n = Network()
