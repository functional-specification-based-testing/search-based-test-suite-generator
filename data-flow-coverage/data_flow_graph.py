import graphviz
import graph_builder
import re


def connect_function_calls(node, functions):
    if node is None:
        return
    if node.exp is not None:
        call = re.search('^\\w+\\s\\w+', node.exp.text)
        if call is not None:
            function = re.search('^\\w+', node.exp.text).group()
            node.call = functions[function]
        else:
            call = re.search("^\\(\\w+\\s\\w+", node.exp.text)
            print(str(call))
            if call is not None:
                function = re.search('\\w+', node.exp.text).group()
                node.call = functions[function]
    for n in node.next:
        connect_function_calls(n, functions)


def create_program_graph():
    nodes = graph_builder.get_functions_graph()
    functions = {}
    for node in nodes:
        functions[node.function_name] = node
    for node in nodes:
        connect_function_calls(node, functions)
    visualize_data_flow_graph(nodes)


def visualize_node(node, flow_graph):
    flow_graph.node(node.__str__())
    if node.call is not None:
        flow_graph.edge(node.__str__(), node.call.__str__())
    if None not in node.next:
        for n in node.next:
            flow_graph.edge(node.__str__(), n.__str__())
            visualize_node(n, flow_graph)


def visualize_data_flow_graph(nodes):
    flow_graph = graphviz.Digraph(filename="flow_graph.gv")
    for node in nodes:
        visualize_node(node, flow_graph)
    flow_graph.render('flow_graph', view=True)


if __name__ == '__main__':
    create_program_graph()
