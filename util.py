import pandas as pd 
from network_refactored import Network
from component import Bus, Branch, Generator

def network_from_csv(bus_file, branch_file, gen_file, gen_cost_file): 
	
	bus_df = pd.read_csv(bus_file)
	branch_df = pd.read_csv(branch_file)
	gen_df = pd.read_csv(gen_file)
	gen_cost_df = pd.read_csv(gen_cost_file)
	
	gen_df = gen_df.merge(gen_cost_df)
	network = Network()
	for idx, row in bus_df.iterrows(): 
		b = Bus(str(row.bus_name), int(row.BUS_TYPE), int(row.BUS_I), float(row.PD))
		network.add_bus(b)
	
	assert len(network.bus_set.items()) == len(bus_df)
	
	for idx, row in gen_df.iterrows():
		num_pts = int(row.NCOST) * 2 # number of points on offer curve
		pts = []
		for mw_i in range(num_pts-1, 0, -2): 
			cost_i = mw_i - 1
			pts.append((float(row[f'COST_{mw_i}']), float(row[f'COST_{cost_i}'])))

		g = Generator(pts, int(row.GEN_BUS), int(row.GEN_STATUS), float(row.PMIN), float(row.PMAX))

		network.add_gen(g)

	assert len(gen_df) == len(set([g.id for b in network.bus_set.values() for g in b.gens]))

	for idx, row in branch_df.iterrows(): 
		br = Branch(int(row.F_BUS), int(row.T_BUS), float(row.BR_X), int(row.BR_STATUS), float(row.RATE_C))
		network.add_branch(br)

	assert len(branch_df) == len(network.branch_set)

	return network
