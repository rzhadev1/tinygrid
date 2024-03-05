from pyomo.environ import *
from pyomo.opt import SolverFactory
'''
TODO: 
- Build out ming lang using Pyomo (do according to paper)
- How to I append to a indexed variable?
    Use sets, probably use logical operators to add to the set
- Figure out way to parse the case file/data files (make sure this stuff actually works..)
- Use linear expressions to simply all constraints/objective functions (for speed)
'''

class Network():

    def objective_expr(m): 
        return sum(sum(
            m.cg[g, t] + m.p_cost[g, 1] * m.ug[g,t] + \
                sum(m.su_cost[g, s] * m.dg[t, g, s] for s in m.su_cats[g])
            for t in m.t_steps)
        for g in m.tgens)
    
    m = AbstractModel()
    m.tgens = Set() # thermal gens 
    m.tgens_t0_on = Set() # thermal gens on at t_0 
    m.tgens_t0_off = Set() # thermal gens off at t_0
    m.rgens = Set() # renewable gens
    m.t_steps = RangeSet(1, 24) # time steps
    m.pw_ints = Set(dimen=2) # (generator, production interval) tuples
    m.su_cats = Set(dimen=2) # (generator, start up category) tuples

    m.cg = Var(m.tgens, m.t_steps)
    m.pg = Var(m.tgens, m.t_steps, domain=NonNegativeReals) 
    m.pw = Var(m.tgens, m.t_steps, domain=NonNegativeReals)
    m.rg = Var(m.tgens, m.t_steps, domain=NonNegativeReals)
    m.ug = Var(m.tgens, m.t_steps, domain=Binary) # commitment status of gen 
    m.vg = Var(m.tgens, m.t_steps, domain=Binary) # start up status of gen 
    m.wg = Var(m.tgens, m.t_steps, domain=Binary) # shutdown status of gen

    m.dg = Var(m.t_steps * m.su_cats, domain=Binary) 
    m.lg = Var(m.t_steps * m.pw_ints, domain=UnitInterval) 

    # system parameters
    m.demand = Param(m.t_steps) # demand at time step  
    m.reserve = Param(m.t_steps) # reserve at time step 

    # thermal gen parameters
    m.p_cost = Param(m.pw_ints)
    m.su_cost = Param(m.su_cats)
    m.min_dtime = Param(m.tgens)
    m.time_down_t0 = Param(m.tgens)
    m.min_output = Param(m.tgens)
    m.max_output = Param(m.tgens)
    m.prior_output_t1 = Param(m.tgens)
    m.pw_output_at_int = Param(m.pw_ints)
    m.ramp_down = Param(m.tgens)
    m.ramp_up = Param(m.tgens)
    m.shutdown_lim = Param(m.tgens)
    m.startup_lim = Param(m.tgens)
    m.startup_lag = Param(m.su_cats)
    m.min_up = Param(m.tgens)
    m.time_up_t0 = Param(m.tgens)
    m.unit_on_t0 = Param(m.tgens)
    m.must_run = Param(m.tgens)

    # renewable gen parameters
    m.max_renew_output = Param(m.rgens, m.t_steps)
    m.min_renew_output = Param(m.rgens, m.t_steps)    

    m.obj = Objective(expr=objective_expr, sense=minimize)

    m.demand_constr = Constraint(m.t_steps) # power generated should satisfy demand at all time steps
    m.reserve_constr = Constraint(m.t_steps) # reserve capacity should be sufficient 
    m.uptimet0_constr = Constraint(m.tgens) 
    m.downtimet0_constr = Constraint(m.tgens)
    m.logicalt0_constr = Constraint(m.tgens)
    m.startupt0_constr = Constraint(m.tgens)
    m.rampupt0_constr = Constraint(m.tgens)
    m.rampdownt0_constr = Constraint(m.tgens)
    m.shutdownt0_constr = Constraint(m.tgens)



    def add_generator(generator):
        pass

    def add_branch(branch): 
        pass 

    def add_bus(bus):
        pass 

class Branch():
    pass

class Generator():
    pass 

class Bus(): 
    pass

if __name__ == '__main__': 
    n = Network()