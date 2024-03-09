# tinygrid
A compact, toy implementation of a mixed integer linear programming solver for power grid analysis, written in pyomo. This project is philosophically similar to micrograd. The goal is develop a library that allows for the simplest language for modeling the key elements of a power grid. 


# How does an electricity grid work? 
## Basic stuff
Power is generated at generators, which passes through transformers to up/lower the voltage for the transmission grid. This is then transformed again when its stepped down to the distribution grid. A bus is a node in the power grid. A substation is a collection of transformers. 

Power flow can be written as the sum of real power $P$ and reactive power $Q$. It can also be written as the product of voltage and current by Ohm's Law. 

Transmission lines have losses due to resistance. There is also a concept called reactance, which is a delayed effect of storing and returning power to the circuit, but causes no losses. The sum of resistance and reactance is called impedence. This is kind of a measure of the opposition of AC current. The inverse of impedence is called admittance, which is a form of measure of how easily a current will flow. Admittance is the sum of conductance and susceptance. Doing a lot of algebra with these quantities yields the power flow equations for both $P$ and $Q$. 

Kirchoffs Laws define how current and voltage behave in a closed circuit. It states both that the sum of voltages and sum of current out of a node must be 0. 

## Powerflow

One can create a system of equations which describes the power flow through the circuit. Often we are interested in the optimal power flow problem (OPF) which tries to compute the lowest method (production amounts of each generator) of supplying all demand. The generalization of this problem is called the economic dispatch problem (ED). 

The complex power flow equations are highly non-linear and thus difficult to solve at large scale. A common simplification is to linearize the power flow equations by making 3 key assumptions: 

1. The resistance on a transmission line is generally much smaller than its reactance. Thus, we assume that there are no transmission losses. 
2. The voltage angle differences between branches are small, and 
3. The voltage magnitude at each bus is 1 p.u. 

These assumptions turn the ED problem into a linear programming problem. The objective is to minimize the cost of producing electricity, subject to the constraints: 
1. All demand is satisified 
2. The flow along each line is within limits
3. Generation is within the limits of an individual generator 

Notice how the decision variables are the outputs at each generator, and line flows on each transmission line. The primal variable is the system marginal cost. The dual of this problem yields the shadow price of each constraint. Namely, 

1. The cost to balance load and generation, which is the system marginal cost. 
2. The cost per MW unit of a transmission line. If the constraint is binding - i.e in our solution we actually have an equality for the constraint - the shadow price is active in the dual problem (which reduces/increases the price to serve demand at a node). Otherwise, the shadow price is 0. 
3. The cost per MW generation of a unit. 
## Linear Analysis

In the powerflow problem, the linearization problem results in power flow being computed as: 

$$P = B\theta$$

Where $B$ is the susceptance matrix of each line, and $\theta$ is the voltage angle of each line.These are called "shift factors". One can use this matrix to compute the power transfer distribution factor matrix (PTDF), which is the change in a line flow given some change in net injection at a bus. This thus describes how power flow changes when generation changes. Similarly, there is the line outage distribution factor matrix (LODF), which measures change in line flows for a given line outage. Line outages and generation outages are called contingencies. 

# References
1. https://github.com/power-grid-lib/pglib-uc/blob/master/MODEL.pdf
2. https://github.com/power-grid-lib/pglib-uc/tree/master
3. https://github.com/PyPSA/PyPSA
4. https://adamgreenhall.github.io/minpower/index.html
5. https://optimization-online.org/wp-content/uploads/2018/11/6930.pdf
6. Cost-optimal power system extension under flow-based market
coupling
7. 
