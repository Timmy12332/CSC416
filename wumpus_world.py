class World:
    """
    Represents the Wumpus World environment
    """

    def __init__(self):
        """
        Initializes the world layout and facts
        """
        self.World_Layout = []

        # First Row
        self.World_Layout.append("E11")
        self.World_Layout.append("B21")
        self.World_Layout.append("P31")
        self.World_Layout.append("B41")

        # Second Row
        self.World_Layout.append("S12")
        self.World_Layout.append("E22")
        self.World_Layout.append("B32")
        self.World_Layout.append("E42")

        # Third Row
        self.World_Layout.append("W13")
        self.World_Layout.append("BSG23")
        self.World_Layout.append("P33")
        self.World_Layout.append("B43")

        # Fourth Row
        self.World_Layout.append("S14")
        self.World_Layout.append("E24")
        self.World_Layout.append("B34")
        self.World_Layout.append("P44")

        self.facts = set()

    def ask(self, sentence):
        """
        Determines if a given sentence is true in the world
        """
        if isinstance(sentence, str):
            return sentence in self.facts

        operator, *operands = sentence

        if operator == 'NOT':
            return not self.ask(operands[0])
        elif operator == 'AND':
            return all(self.ask(op) for op in operands)
        elif operator == 'OR':
            return any(self.ask(op) for op in operands)
        elif operator == 'IMPLIES':
            return not self.ask(operands[0]) or self.ask(operands[1])
        elif operator == 'IFF':
            return self.ask(operands[0]) == self.ask(operands[1])

    def tell(self, sentence):
        """
        Adds a sentence to the world's set of known facts
        """
        self.facts.add(sentence)

class Player:
    """
    Represents the player/agent in the Wumpus World
    """

    def __init__(self, kb):
        self.kb = kb

    def convert_to_cnf(self, statement):
        """
        Converts a propositional logic statement into CNF
        """
        if isinstance(statement, str):
            return statement

        operator, *operands = statement

        if operator == 'IFF':
            a = self.convert_to_cnf(operands[0])
            b = self.convert_to_cnf(operands[1])
            return self.convert_to_cnf(('AND', ('IMPLIES', a, b), ('IMPLIES', b, a)))

        if operator == 'IMPLIES':
            a = self.convert_to_cnf(operands[0])
            b = self.convert_to_cnf(operands[1])
            return self.convert_to_cnf(('OR', ('NOT', a), b))

        if operator == 'NOT':
            operand = operands[0]
            if isinstance(operand, str):
                return ('NOT', operand)
            elif operand[0] == 'NOT':
                return self.convert_to_cnf(operand[1])
            elif operand[0] == 'AND':
                return self.convert_to_cnf(('OR', ('NOT', operand[1]), ('NOT', operand[2])))
            elif operand[0] == 'OR':
                return self.convert_to_cnf(('AND', ('NOT', operand[1]), ('NOT', operand[2])))
            else:
                return ('NOT', self.convert_to_cnf(operand))

        if operator == 'OR':
            left = self.convert_to_cnf(operands[0])
            right = self.convert_to_cnf(operands[1])

            if isinstance(left, tuple) and left[0] == 'AND':
                return self.convert_to_cnf(('AND', ('OR', left[1], right), ('OR', left[2], right)))
            if isinstance(right, tuple) and right[0] == 'AND':
                return self.convert_to_cnf(('AND', ('OR', left, right[1]), ('OR', left, right[2])))
            return ('OR', left, right)

        if operator == 'AND':
            return ('AND', *[self.convert_to_cnf(op) for op in operands])

        return statement

    def _extract_clauses(self, cnf):
        """
        Extracts clauses from a CNF expression
        """
        if isinstance(cnf, str) or (isinstance(cnf, tuple) and cnf[0] == 'NOT'):
            return [[cnf]]
        elif cnf[0] == 'AND':
            clauses = []
            for operand in cnf[1:]:
                clauses.extend(self._extract_clauses(operand))
            return clauses
        elif cnf[0] == 'OR':
            clause = []
            operands = list(cnf[1:])
            while operands:
                operand = operands.pop(0)
                if isinstance(operand, tuple) and operand[0] == 'OR':
                    operands.extend(operand[1:])
                else:
                    clause.append(operand)
            return [clause]
        else:
            return [[cnf]]

    def _literal_to_string(self, literal):
        """
        Converts a literal to its string representation
        """
        if isinstance(literal, str):
            return literal
        elif isinstance(literal, tuple) and literal[0] == 'NOT':
            return '~' + self._literal_to_string(literal[1])
        else:
            raise ValueError(f"Invalid literal: {literal}")

    def resolve_clauses(self, ci, cj):
        """
        Resolves two clauses and returns the set of resolvents
        """
        resolvents = set()
        for di in ci:
            for dj in cj:
                if di == '~' + dj or dj == '~' + di:
                    new_clause = (ci - {di}) | (cj - {dj})
                    resolvents.add(frozenset(new_clause))
        return resolvents

    def inference_by_resolution(self, query):
        """
        Determines if the query is entailed by the KB using resolution
        """
        clauses = []
        for sentence in self.kb:
            cnf = self.convert_to_cnf(sentence)
            clauses.extend(self._extract_clauses(cnf))

        negated_query = self.convert_to_cnf(('NOT', query))
        clauses.extend(self._extract_clauses(negated_query))

        clauses = [set(self._literal_to_string(literal) for literal in clause) for clause in clauses]
        new = set()

        while True:
            n = len(clauses)
            pairs = [(clauses[i], clauses[j]) for i in range(n) for j in range(i+1, n)]
            for (ci, cj) in pairs:
                resolvents = self.resolve_clauses(ci, cj)
                if frozenset() in resolvents:
                    return True
                new.update(resolvents)
            if new.issubset(set(frozenset(c) for c in clauses)):
                return False
            for clause in new:
                if set(clause) not in clauses:
                    clauses.append(set(clause))
            new.clear()


if __name__ == '__main__':
    # Initial knowledge base
    initial_kb = [
        'A',
        ('IMPLIES', 'A', 'B'),
        ('NOT', 'P11'),
        ('NOT', 'W11'),
        ('NOT', 'B11'),
        ('NOT', 'S11'),
        ('NOT', 'P11'),
        ('IFF', 'B11', ('OR', 'P12', 'P21'))
    ]

    # Testing with the initial_kb
    player = Player(kb=initial_kb)
    query = 'B'
    result = player.inference_by_resolution(query)
    print(f"Query: {query}, Result: {result}")

    query = 'P21'
    result = player.inference_by_resolution(query)
    print(f"Query: {query}, Result: {result}")

#Chat_GPT_Link: https://chatgpt.com/share/66f5f7a3-3f00-8009-b0f6-1d2b88188be4