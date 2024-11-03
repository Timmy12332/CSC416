import re

def negate_query(query):
    if query.startswith("¬"):
        return query[1:]
    else:
        return "¬" + query

def prepare_kb_with_negated_query(kb, query):
    negated_query = negate_query(query)
    kb_with_query = kb.copy()
    kb_with_query.append([negated_query])
    return kb_with_query

def parse_sentence(sentence):
    match = re.match(r"(¬?\w+)\((.*)\)", sentence)
    if not match:
        return None, []
    predicate = match.group(1)
    args = re.split(r",\s*", match.group(2))
    return predicate, args

def unify(sentence1, sentence2):
    substitutions = {}
    predicate1, args1 = parse_sentence(sentence1)
    predicate2, args2 = parse_sentence(sentence2)
    if predicate1 != predicate2:
        return {}  # Unification fails
    if len(args1) != len(args2):
        return {}  # Unification fails
    for arg1, arg2 in zip(args1, args2):
        if not unify_terms(arg1, arg2, substitutions):
            return {}  # Unification fails
    return substitutions  # Unification succeeds

def unify_terms(term1, term2, substitutions):
    term1 = apply_substitution_to_term(term1, substitutions)
    term2 = apply_substitution_to_term(term2, substitutions)

    if term1 == term2:
        return True  # They are the same constant or variable

    if is_variable(term1):
        substitutions[term1] = term2
        return True

    if is_variable(term2):
        substitutions[term2] = term1
        return True

    # Handle nested function terms
    predicate1, args1 = parse_sentence(term1)
    predicate2, args2 = parse_sentence(term2)
    if predicate1 and predicate2 and predicate1 == predicate2 and len(args1) == len(args2):
        for subterm1, subterm2 in zip(args1, args2):
            if not unify_terms(subterm1, subterm2, substitutions):
                return False
        return True

    return False  # Unification fails if terms do not match

def is_variable(term):
    return len(term) > 0 and term[0].islower() and term.isalpha()

def apply_substitution_to_literal(literal, substitution):
    predicate, args = parse_sentence(literal)
    new_args = [apply_substitution_to_term(arg, substitution) for arg in args]
    return predicate + '(' + ', '.join(new_args) + ')'

def apply_substitution_to_term(term, substitution):
    return substitution.get(term, term) if is_variable(term) else term

def resolve(clause1, clause2):
    resolved_clauses = set()
    for literal1 in clause1:
        for literal2 in clause2:
            if literal1.startswith("¬") and not literal2.startswith("¬") and \
               literal1[1:].split('(')[0] == literal2.split('(')[0]:
                substitution = unify(literal1[1:], literal2)
            elif not literal1.startswith("¬") and literal2.startswith("¬") and \
                 literal1.split('(')[0] == literal2[1:].split('(')[0]:
                substitution = unify(literal1, literal2[1:])
            else:
                continue
            if substitution is not None:
                new_clause = (clause1 | clause2) - {literal1, literal2}
                substituted_clause = {apply_substitution_to_literal(lit, substitution) for lit in new_clause}
                resolved_clauses.add(frozenset(substituted_clause))
    return resolved_clauses

def inference_by_resolution(kb, query):
    kb = prepare_kb_with_negated_query(kb, query)
    clauses = set(frozenset(clause) for clause in kb)
    new_clauses = set(frozenset(clause) for clause in [kb[-1]])

    iteration = 0

    while True:
        iteration += 1
        next_new_clauses = set()
        processed_pairs = set()
        for ci in new_clauses:
            for cj in clauses:
                if ci == cj:
                    continue
                pair = frozenset([ci, cj])
                if pair in processed_pairs:
                    continue
                processed_pairs.add(pair)
                resolvents = resolve(ci, cj)
                if frozenset() in resolvents:
                    print("\nEmpty clause derived. The query is inferred to be TRUE.")
                    return True
                next_new_clauses.update(resolvents - clauses)

        if not next_new_clauses:
            print("\nNo new clauses were added. The query cannot be inferred.")
            return False

        clauses.update(next_new_clauses)
        new_clauses = next_new_clauses

def main():

    sentence1 = "Parent(x, y)"
    sentence2 = "Parent(John, Mary)"

    print(unify(sentence1, sentence2))

    print("-" * 50)

    sentence3 = "Loves(father(x), x)"
    sentence4 = "Loves(father(John), John)"

    print(unify(sentence3, sentence4))

    print("-" * 50)
    
    sentence5 = "Parent(x,x)"
    sentence6 = "Parent(John, Mary)"

    print(unify(sentence5, sentence6))

    print("-" * 50)

    kb = [
        ['¬King(x)', '¬Greedy(x)', 'Evil(x)'],
        ['King(John)'],
        ['Greedy(John)']
    ]

    query = 'Evil(John)'

    result = inference_by_resolution(kb, query)
    print(f"\nResult of inference: {result}")

if __name__ == "__main__":
    main()
