from tree import Tree
import sys

class Reorderer:
    def reorder(self, root):
        assert False, "Not implemented."

class RecursiveReorderer(Reorderer):
    def reorder(self, tree):
        return self.reorder_recursively(tree.root, [])
    
    def reorder_recursively(self, head, ordering):
        # 1. Call 'reorder_head_and_children' to determine order of immediate subtree.
        # 2. Walk through immediate subtree in this order, calling 'reorder_recursively'
        # on children and adding head to 'ordering' when it's reached.
        for node in self.reorder_head_and_children(head):
            if node != head:
                ordering = self.reorder_recursively(node, ordering)
            else:
                ordering.append(head)
        return ordering
    
    def reorder_head_and_children(self, head):
        # Reorder the head and children in the desired order.
        assert False, "TODO: implement me in a subclass."


class DoNothingReorderer(RecursiveReorderer):
    # Just orders head and child nodes according to their original index.
    
    def reorder_head_and_children(self, head):
        all_nodes = ([(child.index, child) for child in head.children] + [(head.index, head)])
        return [node for index, node in sorted(all_nodes)]


class ReverseReorderer(RecursiveReorderer):
    # Reverse orders head and child nodes according original index
    
    def reorder_head_and_children(self, head):
        all_nodes = ([(child.index, child) for child in head.children] + [(head.index, head)])
        return [node for index, node in sorted(all_nodes, reverse=True)]


class HeadFinalReorderer(RecursiveReorderer):
    def reorder_head_and_children(self, head):
        all_nodes = ([(child.index, child) for child in head.children])
        return [node for index, node in sorted(all_nodes)] + [head]
    
    
class SOVReorderer(RecursiveReorderer):
    ''' 
        Rule based reordering for SOV languages.
        Based on:
        - http://www.aclweb.org/anthology/N09-1028
    '''
    def reorder_head_and_children(self, head):
        children = [node for index, node in sorted([(child.index, child) for child in head.children])]
        first_nodes = []
        second_nodes = []
        third_nodes = []
        last_nodes = []
        #before_head_idxs = []
        #after_head_idxs = []
        original_order_nodes = []
        for node in children:
            if node.label == 'ROOT':
                return children + [head]
            
        if head.tag.startswith("VB"):
            for idx, node in enumerate(children):
                #print node.label
                if node.label == 'advcl':
                    first_nodes.append(node)
                elif node.label in set({'nsubj', 'prep'}):
                    second_nodes.append(node)
                elif node.label == 'dobj':
                    third_nodes.append(node)
                elif node.label in set({'prt', 'aux', 'auxpass', 'neg'}):
                    last_nodes.append(node)
                else:
                    original_order_nodes.append(node)
            second_nodes += original_order_nodes
            last_nodes.append(head)
        elif head.tag in set({'JJ', 'JJS', 'JJR'}) :
            for idx, node in enumerate(children):
                if node.label == 'advcl':
                    first_nodes.append(node)
                elif node.label in set({'aux', 'auxpass', 'neg', 'cop'}):
                    last_nodes.append(node)
                else:
                    second_nodes.append(node)
            third_nodes.append(head)
        elif head.tag in set({'NN', 'NNS'}) :
            for idx, node in enumerate(children):
                if node.label == 'prep':
                    first_nodes.append(node)
                elif node.label == 'remod':
                    second_nodes.append(node)
                else:
                    original_order_nodes.append(node)
            third_nodes += original_order_nodes
            third_nodes.append(head)
        elif head.tag in set({'IN', 'TO'}) :
            for idx, node in enumerate(children):
                if node.label == 'pobj':
                    first_nodes.append(node)
                else:
                    second_nodes.append(node)
                    
            third_nodes.append(head)
        else:
            return children + [head]
            
        return first_nodes + second_nodes + third_nodes + last_nodes[::-1]


if __name__ == "__main__":
    if not len(sys.argv) == 3:
        print "python reorderers.py ReordererClass parses"
        sys.exit(0)
    # Instantiates the reorderer of this class name.
    reorderer = eval(sys.argv[1])()
    # Reorders each input parse tree and prints words to std out.
    for line in open(sys.argv[2]):
        t = Tree(line)
        assert t.root
        reordering = reorderer.reorder(t)
        print ' '.join([node.word for node in reordering if node != t.root])

