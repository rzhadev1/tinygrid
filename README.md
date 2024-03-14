# tinygrid 

tinygrid is an implementation of the linearized (DC) security constrained economic dispatch problem (SCED), written in pyomo. 

tinygrid is currently tested on the sample Texas ERCOT grid provided by Texas A&M. 
## Background 

The reduced representation of the electrical grid can be compactly described as a graph: 
- Bus: a node in the graph, usually representing a substation (groupings of transformers in the physical grid). Generators are located at a unique bus. 
- Branch: a branch is an edge that connects two buses in the graph. They are defined by a fixed MW capacity, limiting the amount of power flow that is able to be transmitted via a single line. 

Under this model, we view the electrical grid as having constant valued demand (load) and clusters of generators at each bus. 

A transmission line has a fundamental physical value called its $\textbf{impedence}$. This is defined as (note that in EE, they usually use $j$ for an imaginary value): 
$$Z = r + jx$$

$r$ is the resistance of the branch, which is how resistant the branch is to the flow of power. When power flows through a branch, thermal energy is dissipated in the form of heat due to resistance, and some energy is lost from the system. 

$x$ is the reactance of the branch, which does not produce any loss effects, but instead has an effect of storing and returning energy to the system. 
## Formulation

Note that pyomo does not allow for externel functions (without a lot of effort) to be used within a model. This is making applying piecewise linear functions more complicated, see: https://stackoverflow.com/questions/40873161/pyomo-constraint-with-if-statements

https://pyomo.readthedocs.io/en/stable/developer_reference/expressions/design.html
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
