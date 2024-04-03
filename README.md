# tinygrid 

tinygrid is an implementation of the linearized (DC) security constrained economic dispatch problem (SCED), written in pyomo. Pyomo is a flexible mathematical optimization interface that allows one to abstract implementation details of optimization solvers. 

tinygrid is currently tested on the sample Texas ERCOT grid provided by Texas A&M. 
## Background 

Economic dispatch (abbreviated ED, also called Optimal Power Flow/OPF) is a fundamental optimization problem in power systems that is the centerpiece of real time operation, grid planning, and computation of electricity prices. In ED, we would like to find the production amounts for a fleet of generators that serves electrical demand at minimum cost. Note that we assume we already know which generators are turned on or off in ED. Optimizing costs associated with start up/shut down is a related problem called unit commitment, which is difficult in its own right (it is easy to see that because this optimization involves binary variables, it will be a mixed integer optimization. These are known to be NP-hard.) 

Generators are hetergeneous with respect to size, costs, and operating flexibility: 

- Renewable energy sources such as wind and solar have low costs, but have a variety of interesting problems. They are unreliable in that they do not have completely known production amounts until real time, are located far from centers of high demand [^2], and maximize production during off peak hours of demand [^1]. Renewable sources also tend to be smaller in terms of capacity at each facility. 
- Thermal generators are more reliable in that they can be scheduled [^3], and can be quite large by capacity. However, they emit carbon and have far stricter operational constraints such as ramping speeds, minimum up times, minimum down times, and start up times. Furthermore, thermal generators can be expensive: the marginal cost of producing solar or wind energy is 0 \$ /MWh or possibly even negative. Meanwhile, thermal generators often range from as low as 20 \$ /MWh (combined cycle gas) to as high as 200-1000 \$ /MWh (oil).

![image](https://www.e-education.psu.edu/ebf200/sites/www.e-education.psu.edu.ebf200/files/generation%20stack.jpg)

Furthermore, transmission in the electrical grid is governed by highly nonlinear and nonconvex AC load flow equations. Modeling the full AC economic dispatch problem is highly intractable even with modern computers. 

## Fundamental Power Flow Equations

## DC Linearization



[^1]: See the so called *duck curve* phenomenon. 
[^2]: Wind and solar energy has production maximized in the mid west, but population centers of the U.S are on the west and east coasts. 
[^3]: This is kind of discounting how complex generators truly are. Unexpected outages for thermal generators *will* happen and can drastically alter the topology of the grid. 
[^4]: From the paper `Cost-optimal power system extension under flow-based market
coupling`. 

## Formulation

Note that pyomo does not allow for externel functions (without a lot of effort) to be used within a model. This is making applying piecewise linear functions more complicated, see: https://stackoverflow.com/questions/40873161/pyomo-constraint-with-if-statements
# References 
0. https://electricgrids.engr.tamu.edu/
1. https://optimization-online.org/wp-content/uploads/2018/11/6930.pdf
2. https://github.com/power-grid-lib/pglib-uc/blob/master/MODEL.pdf
3. minpower 
4. PyPSA
5. Cost-optimal power system extension under flow-based market
coupling 
6. https://github.com/karpathy/micrograd/blob/master/micrograd/nn.py
7. https://matpower.org/docs/ref/matpower5.0/caseformat.html
8. Mathematical Programming for Power Systems Operation
9. Optimization of Power System Operation
10. A Dual Method for Computing Power Transfer
Distribution Factors
11. https://invenia.github.io/blog/2021/06/18/opf-intro/
12. https://faculty.sites.iastate.edu/tesfatsi/archive/econ458/tesfatsion/lmp.AdvancedWPM.ELitvinovWEM301.pdf
13. https://pyomo.readthedocs.io/en/stable/developer_reference/expressions/design.html
