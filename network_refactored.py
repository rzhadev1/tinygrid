import pyomo.environ as pyo
from pyomo.opt import SolverFactory
from component import Bus, Branch, Generator
from pyomo.opt import TerminationCondition
import numpy as np
import pandas as pd

'''
TODO: shouldnt mix both kernel and environ, using kernel in Generator for cost function
- cost function stuff using piecewise creates integer problem, cant solve
- rewrite using integers? or maybe interpolate with polynomial function first, then use a linear function
- maybe can solve to find c_pg, then fix the cost variables, deactivate integer constraints, then resolve and find duals. 

'''

class Network(): # a graph of the electrical grid
	
	def __init__(self):
		self._model = pyo.ConcreteModel()
		self.bus_set = {} # mapping from bus id -> Bus object 
		self.gen_set = {}
		self.branch_set = {}
		self.slack_bus = None
		self.built = False

	def build(self): # build the optimization problem
		def cost_func(m, gen_id, mw): 
			return self.gen_set[gen_id](mw) # call the generator cost function at MW

		def init_gen_out_lim(m, gen_id, level): # init the gen limit parameter 
			if level == 'min':
				return self.gen_set[gen_id].pmin
			return self.gen_set[gen_id].pmax
		
		def init_flow_lim(m, branch_id, level): # init the flow limit parameter
			if level == 'min':
				return -self.branch_set[branch_id].rating
			return self.branch_set[branch_id].rating
		
		def gen_lim_rule(m, gen_id): # bounds on generator output from param 
			return (m.gen_out_lim[gen_id, 'min'], m.gen_out_lim[gen_id, 'max'])

		def flow_lim_rule(m, branch_id): # bounds on line flow from param
			return (m.line_rating[branch_id, 'min'], m.line_rating[branch_id, 'max'])
			
		self._model.gen_out_lim = pyo.Param(self.gen_set.keys(), ['min', 'max'], initialize=init_gen_out_lim)
		self._model.line_rating = pyo.Param(self.branch_set.keys(), ['min', 'max'], initialize=init_flow_lim)
		self._model.total_load = pyo.Param(initialize=sum([b.load for b in self.bus_set.values()]))
		
		self._model.pg = pyo.Var(self.gen_set.keys(), domain=pyo.Reals, 
			initialize = lambda m,x: (self.gen_set[x].pmin), bounds=gen_lim_rule)
		#self._model.c_pg = pyo.Var(self.gen_set.keys()) # cost at generator amount pg
		self._model.f_k = pyo.Var(self.branch_set.keys(), domain=pyo.Reals, bounds=flow_lim_rule) # the flow along line k
		self._model.theta_b = pyo.Var(self.bus_set.keys(), domain=pyo.Reals, bounds=(-180, 180), initialize=0) # the voltage angle at bus b
		
		'''
		self._model.pw_cost = pyo.Piecewise(self.gen_set.keys(), self._model.c_pg, self._model.pg, 
																		pw_pts={g.id:g.get_cost_breakpts() for g in self.gen_set.values()},
																		f_rule=cost_func, pw_constr_type='EQ', 
																		pw_repn='INC', warn_domain_coverage=True) # assign costs of generation based on interval
		'''
		@self._model.Constraint(self.branch_set.keys())
		def power_flow(m, branch_id): 
			branch = self.branch_set[branch_id]
			return m.f_k[branch_id] == (1 / branch.x) * (m.theta_b[branch.from_bus] - m.theta_b[branch.to_bus])
		
		'''
		@self._model.Constraint()
		def demand(m):
			return sum([m.pg[gen_id] for gen_id in self.gen_set.keys()]) - m.total_load == 0

		'''
		@self._model.Constraint(self.bus_set.keys())  # enforce flow conservation at each bus
		def demand(m, bus_id): 
			out_edge_flow = sum([m.f_k[branch_id] for branch_id in self.bus_set[bus_id].out_edges.keys()])
			in_edge_flow = sum([m.f_k[branch_id] for branch_id in self.bus_set[bus_id].in_edges.keys()])
			gen_amt = sum([m.pg[gen.id] for gen in self.bus_set[bus_id].gens])
			dmd = self.bus_set[bus_id].load
			return gen_amt - dmd == out_edge_flow - in_edge_flow

		@self._model.Constraint() 
		def slack_bus_ang(m):
			return m.theta_b[self.slack_bus.id] == 0	

		@self._model.Objective(sense=pyo.minimize)
		def obj(m): 
			# eval generator cost function at the generated amount
			return sum([self.gen_set[gen_id](m.pg[gen_id])*m.pg[gen_id] for gen_id in self.gen_set.keys()])
		
		self.built = True
		self._model.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
		return self.built
	
	def solve(self, solver='glpk'): 
		opt = SolverFactory(solver)
		res = opt.solve(self._model, tee=True)
		assert(res.solver.status == pyo.SolverStatus.ok)
		assert(res.solver.termination_condition == pyo.TerminationCondition.optimal)
		
		self._model.pprint()
		
		'''
		# we solved the model, but now need to obtain the duals. Fix the values and disable the integer constraints 
		# used to model the piecewise linear functions. 

		# TODO: this doesnt seem to work. Fixing costs allows the solver to put maximum generation for any unit that is expensive
		for g in self.gen_set.keys():
			self._model.c_pg[g].fix() # fix the cost to generate for each generator
		self._model.pw_cost.deactivate() # deactivate piecewise (integer under the hood) constraints
		
		self._model.dual = pyo.Suffix(direction=pyo.Suffix.IMPORT)
		res = opt.solve(self._model, tee=True)
		assert(res.solver.status == pyo.SolverStatus.ok)
		assert(res.solver.termination_condition == pyo.TerminationCondition.optimal)
		#self._model.pprint()
		'''

	def add_bus(self, bus): # add a node to the graph
		self.bus_set[bus.id] = bus

		if bus.type == 3: # type 3 bus are reference buses
			self.slack_bus = bus
		
	def add_gen(self, gen): # add a generator to a bus
		self.bus_set[gen.at_bus_id].gens.append(gen)
		self.gen_set[gen.id] = gen

	def add_branch(self, branch): # add an edge to the graph
		self.branch_set[branch.id] = branch
		self.bus_set[branch.from_bus].out_edges[branch.id] = branch.to_bus # add out edge 
		self.bus_set[branch.to_bus].in_edges[branch.id] = branch.from_bus # add in edge
	
	def __repr__(self): 
		s = "" 
		for k,v in self.bus_set.items(): 
			s += str(v) + "\n"
		s += "\n"
		
		for k,v in self.gen_set.items(): 
			s += str(v) + "\n"
		s += "\n"

		for k,v in self.branch_set.items(): 
			s += str(v) + "\n"
		s += "\n"
		return s
