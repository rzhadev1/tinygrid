from pyomo.environ import *
from pyomo.opt import SolverFactory
from component import Bus, Branch, Generator
import numpy as np
import pandas as pd

class Network(): # a graph of the electrical grid
	
	def __init__(self):
		self._model = ConcreteModel()
		self.bus_set = {} # mapping from bus id -> Bus object 
		self.gen_set = {}
		self.branch_set = {}
		self.slack_bus = None
		self.built = False

	def build(self): # build the optimization problem
		
		def init_gen_out_lim(m, gen_id, level): 
			if level == 'min':
				return self.gen_set[gen_id].pmin
			return self.gen_set[gen_id].pmax
		
		def init_flow_lim(m, branch_id, level):
			if level == 'min':
				return -self.branch_set[branch_id].rating
			return self.branch_set[branch_id].rating

		def gen_limit_rule(m, gen_id): 
			return (m.gen_output_lim[gen_id, 'min'], m.pg[gen_id], m.gen_output_lim[gen_id, 'max'])

		def flow_limit_rule(m, branch_id):
			return (m.line_rating[branch_id, 'min'], m.f_k[branch_id], m.line_rating[branch_id, 'max'])

		def power_flow(m, branch_id): 
			branch = self.branch_set[branch_id]
			return m.f_k[branch_id] == (1 / branch.x) * \
				(m.theta_b[self.bus_set[branch.from_bus].id] - m.theta_b[self.bus_set[branch.to_bus].id])
		
		self._model.gen_output_lim = Param(self.gen_set.keys(), ['min', 'max'], mutable=False, initialize=init_gen_out_lim)
		self._model.line_rating = Param(self.branch_set.keys(), ['min', 'max'], mutable=False, initialize=init_flow_lim)
		self._model.total_load = Param(initialize=sum([b.load for b in self.bus_set.values()]), mutable=False)

		self._model.pg = Var(self.gen_set.keys(), domain=Reals, 
			initialize = lambda m,x: (self.gen_set[x].pmin + self.gen_set[x].pmax)/2)
		self._model.f_k = Var(self.branch_set.keys(), domain=Reals) # the flow along line l
		self._model.theta_b = Var(self.bus_set.keys(), domain=Reals, bounds=(-180, 180), initialize=0) # the voltage angle at bus b

		self._model.demand = Constraint(expr=\
			sum([self._model.pg[gen_id] for gen_id in self.gen_set.keys()]) == self._model.total_load)

		self._model.gen_limit = Constraint(self.gen_set.keys(), rule=gen_limit_rule) # gens are within thermal limits
		self._model.flow_limit = Constraint(self.branch_set.keys(), rule=flow_limit_rule) # branches are within limits
		self._model.power_flow = Constraint(self.branch_set.keys(), rule=power_flow) # B,theta model for flow equations
		self._model.slack_bus_eq = Constraint(expr=self._model.theta_b[self.slack_bus.id] == 0) # reference bus has 0 angle

		self._model.obj = Objective(expr=\
			sum([self.gen_set[gen_id].cost_f(value(self._model.pg[gen_id])) for gen_id in self.gen_set.keys()]), sense=minimize)

		self._model.dual = Suffix(direction=Suffix.IMPORT)
		self.built = True
		return self.built
	
	def solve(self, solver='glpk'): 
		opt = SolverFactory(solver)
		res = opt.solve(self._model)
		assert(str(res.solver.status) == 'ok')
		
	def add_bus(self, bus): # add a node to the graph
		self.bus_set[bus.id] = bus

		if bus.type == 3: # type 3 bus are reference buses
			self.slack_bus = bus
		
	def add_gen(self, gen): # add a generator to a bus
		self.bus_set[gen.at_bus_id].gens.append(gen)
		self.gen_set[gen.id] = gen

	def add_branch(self, branch): # add an edge to the graph
		self.branch_set[branch.id] = branch
