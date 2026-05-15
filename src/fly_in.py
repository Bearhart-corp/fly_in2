import sys
from .visual import Visual
from .parser import Parser
from .graph import GraphBuilder
from .algo import Algo2


def main() -> int:
    if len(sys.argv) == 1:
        print("No arguments provided.")
        return 0
    if len(sys.argv) != 2:
        print("too much arguments.")
    else:
        parsing = Parser()
        try:
            raw_map = parsing.parse_file("src/config.txt")
        except Exception as e:
            print(e)
            return 0
            # raw_map.print_map()
        builder = GraphBuilder(raw_map.nb_drones)
        try:
            graph, start, end = builder.build(raw_map)
        except Exception as e:
            print(e)
            return 0
        st, ending = graph.zones[start], graph.zones[end]
        algo = Algo2(graph, st, ending)
        algo.algo(graph)
        Visual.launch_visualization(graph)
    return 0


if __name__ == "__main__":
    main()
