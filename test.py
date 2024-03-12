from util import network_from_csv 
import os

case_file_pth = './config'
bus_file = os.path.join(case_file_pth, 'bus.csv')
branch_file = os.path.join(case_file_pth, 'branch.csv')
gen_file = os.path.join(case_file_pth, 'gen.csv')
gen_cost_file = os.path.join(case_file_pth, 'gencost.csv')

if __name__ == '__main__':
	network = network_from_csv(bus_file, branch_file, gen_file, gen_cost_file)
	ret = network.build()
	assert(ret)
	network.solve()
	
