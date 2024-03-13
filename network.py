from pyomo.environ import *
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
		self._model = ConcreteModel()
		self.bus_set = {} # mapping from bus id -> Bus object 
		self.gen_set = {}
		self.branch_set = {}
		self.slack_bus = None
		self.built = False

	def build(self): # build the optimization problem
		
		def init_gen_out_lim(m, gen_id, level): # init the gen limit parameter 
			if level == 'min':
				return self.gen_set[gen_id].pmin
			return self.gen_set[gen_id].pmax
		
		def init_flow_lim(m, branch_id, level): # init the flow limit parameter
			if level == 'min':
				return -self.branch_set[branch_id].rating
			return self.branch_set[branch_id].rating
		
		def gen_limit_rule(m, gen_id): # bounds on generator output from param 
			return (m.gen_output_lim[gen_id, 'min'], m.gen_output_lim[gen_id, 'max'])
			#return (0, m.gen_output_lim[gen_id, 'max'])
		def flow_limit_rule(m, branch_id): # bounds on line flow from param
			return (m.line_rating[branch_id, 'min'], m.line_rating[branch_id, 'max'])
			#return (0, m.line_rating[branch_id, 'max'])
		def power_flow(m, branch_id): 
			branch = self.branch_set[branch_id]
			return m.f_k[branch_id] == (1 / branch.x) * \
				(m.theta_b[self.bus_set[branch.from_bus].id] - m.theta_b[self.bus_set[branch.to_bus].id])
		
		def cost_func(m, gen_id, mw): 
			return self.gen_set[gen_id](mw) # call the generator cost function at MW

		self._model.gen_output_lim = Param(self.gen_set.keys(), ['min', 'max'], mutable=False, initialize=init_gen_out_lim)
		self._model.line_rating = Param(self.branch_set.keys(), ['min', 'max'], mutable=False, initialize=init_flow_lim)
		self._model.total_load = Param(initialize=sum([b.load for b in self.bus_set.values()]), mutable=False)
		
		# pyomo does not allow for external functions used in objective/constraints 
		# our objective is a piecewise linear cost function for each generator; 
		# some formulations (pglib-uc) use an indicator variable for which segment of the PW 
		# function that a given generation amount falls under. 
		# We sidestep this requirement by using another variable that is defined as the PW linear evaluation 
		# of the generation amount. This of course varies for each generator. 
		self._model.pg = Var(self.gen_set.keys(), domain=Reals, 
			initialize = lambda m,x: (self.gen_set[x].pmin + self.gen_set[x].pmax)/2, bounds=gen_limit_rule)
		self._model.c_pg = Var(self.gen_set.keys()) # cost at generator amount pg
		self._model.f_k = Var(self.branch_set.keys(), domain=Reals, bounds=flow_limit_rule) # the flow along line k
		self._model.theta_b = Var(self.bus_set.keys(), domain=Reals, bounds=(-180, 180), initialize=0) # the voltage angle at bus b
		
		self._model.pw_cost = Piecewise(self.gen_set.keys(), self._model.c_pg, self._model.pg, 
																		pw_pts={g.id:g.get_cost_breakpts() for g in self.gen_set.values()},
																		f_rule=cost_func, pw_constr_type='EQ', 
																		pw_repn='INC', warn_domain_coverage=True)
		self._model.demand = Constraint(expr=sum([self._model.pg[gen_id] for gen_id in self.gen_set.keys()]) == self._model.total_load)

		#self._model.gen_limit = Constraint(self.gen_set.keys(), rule=gen_limit_rule) # gens are within thermal limits
		#self._model.flow_limit = Constraint(self.branch_set.keys(), rule=flow_limit_rule) # branches are within limits
		self._model.power_flow = Constraint(self.branch_set.keys(), rule=power_flow) # B,theta model for flow equations
		self._model.slack_bus_eq = Constraint(expr=self._model.theta_b[self.slack_bus.id] == 0) # reference bus has 0 angle
		
		'''
		self._model.obj = Objective(expr=\
			sum([self.gen_set[gen_id].cost_f(self._model.pg[gen_id]) for gen_id in self.gen_set.keys()]), sense=minimize)
		'''

		self._model.obj = Objective(expr=sum([self._model.c_pg[gen_id] for gen_id in self.gen_set.keys()]), sense=minimize)


		self._model.dual = Suffix(direction=Suffix.IMPORT)
		self.built = True
		return self.built
	
	def solve(self, solver='glpk'): 
		opt = SolverFactory(solver)
		res = opt.solve(self._model, tee=True)
		assert(res.solver.status == SolverStatus.ok)
		assert(res.solver.termination_condition == TerminationCondition.optimal)
		
		self._model.pprint()
		for c in self._model.component_objects(Constraint, active=True):
			print("   Constraint", c)
			for index in c:
				print("      ", index, self._model.dual[c[index]])

	def add_bus(self, bus): # add a node to the graph
		self.bus_set[bus.id] = bus

		if bus.type == 3: # type 3 bus are reference buses
			self.slack_bus = bus
		
	def add_gen(self, gen): # add a generator to a bus
		self.bus_set[gen.at_bus_id].gens.append(gen)
		self.gen_set[gen.id] = gen

	def add_branch(self, branch): # add an edge to the graph
		self.branch_set[branch.id] = branch
