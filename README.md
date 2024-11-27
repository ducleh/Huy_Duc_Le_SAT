# Clique cover SAT solver

This repository contains a Python implementation for solving the clique cover problem using SAT reduction. The script encodes the problem into Conjunctive Normal Form (CNF), solves it, returns SAT/UNSAT, clique labeling if possible and time spent running the script.

The SAT solver used is [Glucose 4.2.1](https://github.com/audemard/glucose). A precompiled UNIX binary of Glucose is included.

## Problem description
The clique cover problem asks whether a graph can be partitioned into *k* cliques. A clique *X* of a graph *G* is a subset of vertices such that every pair of distinct vertices in *X* is adjacent in *G*.

A valid graph for the script should be a connected, undirected, simple graph. Vertices should be labeled sequentially with positive integers and no gaps (1, 2, ...). Each edge is uniquely identified by a pair of vertex labels.

## Input format
Each edge is represented by a line with two integers separated by a space. Lines beginning with # are treated as comments. Blank lines are ignored.

```
# example graph
1 2
1 3
2 3
4 5
```

This file describes a graph with five vertices and edges between vertices (1, 2), (1, 3), (2, 3) and (4, 5).

## Encoding
The encoding introduces variables for each pair of vertex and clique, denoted x_{v, c} which represents whether vertex *v* is in clique *c*. For example, if x_{3, 5} is 1, the vertex 3 is in clique 5 and vice versa. The clauses in the CNF formula are:
* Clauses that ensures every vertex belongs to at least one clique
* Clauses that prevent a vertex from being to more than one clique
* Clauses that prevent two disconnected vertices from being in the same clique

The encoding is obviously very primitive and can be optimized in numerous ways, such as decomposing the graph into strongly connected components, encoding pairs of vertices instead of vertex-clique pair, terminating earlier by incrementing the number of cliques, etc.

## User documentation
Usage
```
clique_cover.py [-h] [-k CLIQUES] [-i INPUT] [-o OUTPUT] [-s SOLVER]
```

Options:
* -h, --help: Show a help message
* -k CLIQUES, --cliques CLIQUES: Number of cliques for the problem. **Required**.
* -i INPUT, --input INPUT: Input file containing the graph description. Default: "input.in".
* -o OUTPUT, --output OUTPUT: Output file for the DIMACS format (CNF formula). Default: "formula.cnf".
* -s SOLVER, --solver SOLVER: Path to the SAT solver executable. Default: "./glucose".

## Instances
Input graphs:
* input_small_sat.in: A triangle graph, satisfiable for all *k* >= 1
* input_small_unsat.in: A line graph with 4 vertices, unsatifiable for k = 1
* input_large_sat.in: A large graph with 200 vertices, satisfiable for k = 160 after 11.12 seconds running the script with an AMD Ryzen 5 5600H

By testing with multiple graphs, the number of vertices and edges in a graph do not seem as much a problem as the number of cliques. The more cliques that are allowed, the faster the script runs. For example. a graph with 50 vertices and edges distributed randomly is unsolvable after 30 minutes for k = 10, but is very quick for k = 30.

## Extensions
* Alternative SAT solvers can be tried with the scripts.
* Optimizations such as ones mentioned above can be studied.
* Extend the problem to find the smallest *k*-clique.

## Acknowledgement
This repository was part of the homework solution for Propositional and Predicate Logic (NAIL062) at Charles University.
