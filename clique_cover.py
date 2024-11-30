import subprocess
from argparse import ArgumentParser

def load_instance(input_file):
    # load the instance from the input file
    # return the graph structure
    graph = []
    with open(input_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                u, v = map(int, line.split())
                graph.append((u, v))
    return graph

def encode(instance, k):
    # encode the instance into CNF
    # return CNF formula
    graph = instance
    vertices = set(v for edge in graph for v in edge)
    num_vars = len(vertices) * k
    clauses = []

    # map a pair of vertex and clique to a unique positive number
    def var(v, c):
        return (v - 1) * k + c

    # ensure that each vertex belongs to at least one clique by generating a clause that assign a vertex into all possible cliques
    # prevent a vertex from being assigned to more than one clique by generating a clause for each pair of cliques
    for v in vertices:
        clauses.append([var(v, c) for c in range(1, k + 1)])
        for c1 in range(1, k + 1):
            for c2 in range(c1 + 1, k + 1):
                clauses.append([-var(v, c1), -var(v, c2)])

    # prevent two vertices from being in the same clique if there is no edge between them
    for u in vertices:
        for v in vertices:
            if u != v and (u, v) not in graph and (v, u) not in graph:
                for c in range(1, k + 1):
                    clauses.append([-var(u, c), -var(v, c)])

    # convert clauses to DIMACS format
    cnf = f"p cnf {num_vars} {len(clauses)}\n"
    for clause in clauses:
        cnf += " ".join(map(str, clause)) + " 0\n"

    return cnf

def write_cnf(cnf, output_file):
    # write the CNF formula to a file in DIMACS format
    with open(output_file, "w") as f:
        f.write(cnf)

def call_solver(cnf, output_file, solver_path):
    # call the SAT solver with the given CNF formula
    # return the solver's output
    write_cnf(cnf, output_file)

    solver_args = [solver_path, output_file]
    solver_args.append("-model") # ask for model

    try:
        result = subprocess.run(
            solver_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        output = "\n".join(line for line in result.stdout.splitlines()).strip() # remove comments in solver's output
        return output
    except FileNotFoundError:
        print("Error: SAT solver not found.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error running the SAT solver: {e}")
        return None

def parse_solver_output(output, verbosity):
    # parse the solver output
    # return statistics SAT/UNSAT and model if possible
    lines = output.split("\n")
    stats = []
    status = None
    model = None
    for line in lines:
        line = line.strip()
        if line.startswith("c "): # comment lines
            stats.append(line[2:])
        if line.startswith("s "):  # status line
            if "UNSATISFIABLE" in line:
                status = "UNSAT"
            else:
                status = "SAT"
        if line.startswith("v "):  # model line
            # parse the model
            model = list(map(int, line[2:].split()))
            if model and model[-1] == 0:
                model.pop()
    return stats, status, model

def decode_cliques(model, k):
    cliques = {i: [] for i in range(1, k + 1)}

    for var in model:
        if var > 0:
            v = (var - 1) // k + 1
            c = (var - 1) % k + 1
            cliques[c].append(v)

    return cliques

def print_cliques(cliques):
    # print the cliques in a human-readable format
    for c, vertices in cliques.items():
        print(f"Clique {c}: {sorted(vertices)}")

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-k",
        "--cliques",
        type=int,
        required=True,
        help="Number of cliques for the clique cover problem"
    )
    parser.add_argument(
        "-i",
        "--input",
        default="input.in",
        type=str,
        help="The instance file"
    )
    parser.add_argument(
        "-o",
        "--output",
        default="formula.cnf",
        type=str,
        help="Output file for the DIMACS format (i.e. the CNF formula)"
    )
    parser.add_argument(
        "-s",
        "--solver",
        default="./glucose",
        type=str,
        help="The SAT solver to be used"
    )
    parser.add_argument(
        "-v",
        "--verbose",
        default=0,
        type=int,
        choices =range(0, 2),
        help="Verbosity of the script"
    )
    args = parser.parse_args()

    # load the input instance
    instance = load_instance(args.input)

    # encode the problem to create a CNF formula
    cnf = encode(instance, args.cliques)

    # call the SAT solver and get the result
    output = call_solver(cnf, args.output, args.solver)

    # interpret and print the result
    if output:
        stats, status, model = parse_solver_output(output, args.verbose)
        if args.verbose == 1:
            for line in stats:
                print(line)
        if status == "UNSAT":
            print("UNSATISFIABLE: No solution exists for the given instance")
        elif status == "SAT":
            cliques = decode_cliques(model, args.cliques)
            print("SATISFIABLE: Solution found")
            print_cliques(cliques)
