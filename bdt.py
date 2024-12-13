import csv
import math

class Node:
    def __init__(self, feature=None, decision=None):
        # If decision is not None, this is a leaf node
        # If decision is None and feature is not None, it is an internal node
        self.feature = feature
        self.decision = decision
        # Dictionary mapping feature values -> child nodes
        self.children = {}

    def add_child(self, value, node):
        self.children[value] = node

    def is_leaf(self):
        return self.decision is not None

def read_data(filename):
    """
    Reads CSV data into a list of dictionaries.
    """
    data = []
    with open(filename, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(dict(row))
    return data

def entropy(data):
    """
    Calculate the entropy
    """
    # Count occurrences of each decision
    decision_counts = {}
    for row in data:
        decision = row['Decision']
        if decision not in decision_counts:
            decision_counts[decision] = 0
        decision_counts[decision] += 1

    # Calculate proportions and entropy
    total = len(data)
    ent = 0.0
    for decision_val, count in decision_counts.items():
        p = count / total
        ent -= p * math.log2(p)
    return ent

def calculate_information_gain(feature, data):
    """
    Compute the information gain
    """
    # Compute the original entropy
    original_entropy = entropy(data)
    total = len(data)

    # Partition data by feature value
    subsets = {}
    for row in data:
        val = row[feature]
        if val not in subsets:
            subsets[val] = []
        subsets[val].append(row)

    # Compute weighted entropy for each subset
    weighted_entropy = 0.0
    for val, subset in subsets.items():
        p = len(subset) / total
        weighted_entropy += p * entropy(subset)

    # Information gain
    ig = original_entropy - weighted_entropy
    return ig

def all_same_decision(data):
    """
    Check if all rows have the same decision.
    """
    if not data:
        return True
    first_decision = data[0]['Decision']
    return all(row['Decision'] == first_decision for row in data)

def majority_decision(data):
    """
    If the data runs out of features, return the majority decision.
    """
    decision_counts = {}
    for row in data:
        d = row['Decision']
        if d not in decision_counts:
            decision_counts[d] = 0
        decision_counts[d] += 1
    # Return the decision with the maximum count
    return max(decision_counts, key=decision_counts.get)

def build_decision_tree(data, features=None):
    """
    Recursively build a decision tree
    """
    # If all data have the same decision, return a leaf node
    if all_same_decision(data):
        return Node(decision=data[0]['Decision'])

    # Initialize features if not provided
    if features is None:
        features = [f for f in data[0].keys() if f != 'Decision']

    # If no features left, return leaf node based on majority decision
    if len(features) == 0:
        return Node(decision=majority_decision(data))

    # Calculate information gain for each feature and pick the best one
    best_feature = None
    best_ig = -1
    for f in features:
        ig = calculate_information_gain(f, data)
        if ig > best_ig:
            best_ig = ig
            best_feature = f

    # Error Check
    if best_feature is None:
        return Node(decision=majority_decision(data))


    # Create a node for this feature
    node = Node(feature=best_feature)

    # Split data by the best_feature
    subsets = {}
    for row in data:
        val = row[best_feature]
        if val not in subsets:
            subsets[val] = []
        subsets[val].append(row)

    # Remove the chosen feature from the list before recursion
    remaining_features = [f for f in features if f != best_feature]

    # Build child nodes for each subset
    for val, subset in subsets.items():
        if all_same_decision(subset):
            # Directly create a leaf node
            child_node = Node(decision=subset[0]['Decision'])
        else:
            # Recursively build subtree with remaining features
            child_node = build_decision_tree(subset, remaining_features)
        node.add_child(val, child_node)

    return node

def print_tree(node, indent=""):
    """
    Pretty-print the decision tree.
    """
    if node.is_leaf():
        print(indent + "Decision:", node.decision)
    else:
        print(indent + "Feature:", node.feature)
        for val, child in node.children.items():
            print(indent + f"  Value: {val}")
            print_tree(child, indent + "    ")

if __name__ == "__main__":
    data = read_data("decision_tree_data.csv")
    tree = build_decision_tree(data)
    print("Decision Tree:")
    print_tree(tree)
