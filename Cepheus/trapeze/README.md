Trapeze
=======

Summary
-------

A utility function for estimating definite integrals. Also a nice demonstration
of generators and first-class functions.

The accuracy of this algorithm is not considered high enough for production
use. Furthermore, any parts of a curve with increasing gradient (such as
exponential functions) will be overestimated, while any parts of a cuve with
decreasing gradient (such as logarithmic functions) will be underestimated.

Usage
-----

To calculate `Integral(a, b, y, dx)`:

```python
include trapeze
result = trapeze.integrate(b, a, y, n)
```

Where `a`, `b` and `y` are as in the integral, while `n` is the accuracy of the
algorithm, in terms of numbers of trapezia to use.

Notes
-----

The original code contained an iterative loop instead of a generator; rewriting
it as a generator yielded (hurr hurr) a speedup of *30%*.

Using a higher number of ordinates will increase accuracy but *significantly
increase calculation time*, so beware. On a Core 2 Duo 3GHz, integration of
f(x) = 2^x from 0 to 1 using 1 000 000 points takes around 570 milliseconds.