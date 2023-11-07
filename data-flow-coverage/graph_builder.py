import graphviz
from node import Node, NodeType
from exp import Exp, ExpType
import re


def trim_header(content):
    return content.split('[', 1)[1]


def read_mix(file):
    with open(file) as mix:
        content = trim_header(mix.read())
        exps_string = content.split(')')
        exps = []
        for i in exps_string:
            if i[0] == ']':
                continue
            exps.append(Exp(i))
    return exps


def extract_expressions(filename, exps):
    with open(filename) as file:
        source = file.readlines()
        for exp in exps:
            if exp.begin.line == exp.end.line:
                exp.set_text(source[exp.begin.line - 1][exp.begin.char - 1:exp.end.char])
            else:
                text = ''
                for i in range(exp.begin.line, exp.end.line + 1):
                    if i == exp.begin.line:
                        text += source[i - 1][exp.begin.char - 1:]
                    elif i == exp.end.line:
                        text += source[i - 1][:exp.end.char]
                    else:
                        text += source[i - 1]
                exp.set_text(text)


def remove_duplicates(exps):
    duplicates = [x for n, x in enumerate(exps) if x in exps[:n]]
    duplicates = [x for n, x in enumerate(duplicates) if x in duplicates[:n]]
    non_duplicates = [x for n, x in enumerate(exps) if x not in exps[:n]]
    for d in duplicates:
        index = non_duplicates.index(d)
        if non_duplicates[index].exp_type == ExpType.expression and \
                (d.exp_type == ExpType.guard or d.exp_type == ExpType.condition):
            non_duplicates[index].exp_type = d.exp_type
    return non_duplicates


def create_tree(exps):
    exps = remove_duplicates(exps)
    roots = []
    for exp in exps:
        if len(roots) == 0:
            roots.append(exp)
        else:
            should_be_removed = []
            for root in roots:
                if exp.contains(root):
                    should_be_removed.append(root)
                    exp.add_child(root)
            roots = [exp for exp in roots if exp not in should_be_removed]
            roots.append(exp)
    return roots


def trim_tree(root):
    removable_exp = []
    for exp in root.children:
        if len(exp.children) == 0 and exp.exp_type == ExpType.expression:
            removable_exp.append(exp)
        else:
            trim_tree(exp)
    root.children = [exp for exp in root.children if exp not in removable_exp]


def get_leaves(root):
    leaves = []
    if len(root.children) == 0:
        return [root]
    for exp in root.children:
        if len(exp.children) == 0:
            leaves.append(exp)
        else:
            leaves.extend(get_leaves(exp))
    leaves.sort(key=lambda x: x.begin)
    return leaves


def get_tags(node):
    if node is None:
        return []
    tags = []
    tag = re.search('`\\w+`\\s*\\"(.+)\\"', node.exp.text)
    if tag is not None:
        tags.append(tag.group())
    for n in node.next:
        tags.extend(get_tags(n))
    return tags


# assuming that guard contain only one expression hence the guard expression is in the leaves
def find_guard_exp(exps):
    guards = []
    for exp in exps:
        if exp.exp_type == ExpType.guard:
            guards.append(exp)
    return guards


def get_cfg(root):
    leaves = get_leaves(root)
    guards = find_guard_exp(leaves)
    if len(guards) > 0:
        path = []
        for guard in guards:
            guard_leaves = get_leaves(guard.father.next_child(guard))
            guard_node = create_cfg(guard_leaves)
            guard_node_tags = get_tags(guard_node)
            path.append(Node(guard, [guard_node],tags=guard_node_tags))
        return Node(None, path, NodeType.function_def, root.function_name)
    else:
        function_cfg = create_cfg(leaves)
        return Node(None, [function_cfg], NodeType.function_def, function_name=root.function_name,
                    tags=get_tags(function_cfg))


def create_cfg(leaves):
    if len(leaves) == 0:
        return None
    leaf = leaves.pop(0)
    if leaf.exp_type == ExpType.condition:
        father = leaf.father
        if_branch = father.next_child(leaf)
        else_branch = father.next_child(if_branch)
        if_node = create_cfg(get_leaves(if_branch))
        if_node.tags = get_tags(if_node)
        else_node = create_cfg(get_leaves(else_branch))
        else_node.tags = get_tags(else_node)
        leaves = [exp for exp in leaves if exp not in get_leaves(if_branch) and exp not in get_leaves(else_branch)]
        remaining = create_cfg(leaves)
        if_last_node = get_last_node(if_node)
        else_last_node = get_last_node(else_node)
        if_last_node.next = [remaining]
        else_last_node.next = [remaining]
        return Node(leaf, [if_node, else_node])
    elif leaf.exp_type == ExpType.expression:
        return Node(leaf, [create_cfg(leaves)])


# this function can only be called for traces that have single path and there is no branch
def get_last_node(node):
    if None in node.next:
        return node
    else:
        return get_last_node(node.next[0])


def visualize_exp_tree(root, tree):
    for exp in root.children:
        tree.node(exp.__str__())
        tree.edge(root.__str__(), exp.__str__())
        visualize_exp_tree(exp, tree)


def visualize(roots):
    tree = graphviz.Digraph(filename="exp_tee.gv")
    for root in roots:
        tree.node(root.__str__())
        visualize_exp_tree(root, tree)
    # print(tree.source)
    tree.render('exp_tree', view=True)
    # tree.write_jpeg("exp_tree.jpeg")


def get_functions_graph():
    exps = read_mix("/Users/arvinzakeriyan/Desktop/research-workspace/simple-me-haskell/.hpc/Main.mix")
    extract_expressions("/Users/arvinzakeriyan/Desktop/research-workspace/simple-me-haskell/InternalState.hs", exps)
    roots = create_tree(exps)
    nodes = []
    # visualize(roots)
    for root in roots:
        trim_tree(root)
        node = get_cfg(root)
        nodes.append(node)
    # visualize_data_flow_graph(nodes)
    return nodes


if __name__ == '__main__':
    get_functions_graph()
