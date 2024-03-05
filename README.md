# tinygrid
A compact, toy implementation of a mixed integer linear programming solver for power grid analysis, written in pyomo. This project is philosophically similar to micrograd. The goal is develop a library that allows for the simplest language for modeling the key elements of a power grid. 

# Notes
1. Only do one period (24 hour) solve for unit commitment. 
2. Utilize pyomo abstract models to lazily initialize model parameters
# References
1. https://github.com/power-grid-lib/pglib-uc/blob/master/MODEL.pdf
2. https://github.com/power-grid-lib/pglib-uc/tree/master
3. https://github.com/PyPSA/PyPSA
4. https://adamgreenhall.github.io/minpower/index.html
5. https://optimization-online.org/wp-content/uploads/2018/11/6930.pdf