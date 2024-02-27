from y_file import parse_expression
import operator

def parse_and_get_index(string, idx):
    
    while True: 

        save = index 

        while index < len(string) and string[index].isspace():
            index += 1
        
        if index < len(string) and string[index] == ';':
            index += 1

            while index < len(string) and string[index] != '\n':
                index += 1

        if index == save :
            break            
    
    return idx

#bool, number, string or symbol
def parse_atoms(string):

    import json

    try:
        return ['val', json.load(string)]

    except json.JSONDecodeError:

        return string 

def pl_parse(string:str):

    index, node = parse_expressions(string, 0)
    index = parse_and_get_index(string, index)

    if index < len(string):

        raise ValueError('trailing garbage')

    return node

def pl_eval(enviroment, node):
    node = parse_expression(string, 0)

    if not isinstance(node, list):

        assert isinstance(node, str)
        
        return name_loopup(enviroment, node)[node]

    if len(node) == 0:

        raise ValueError('empty list')
    
    if len(node) == 2 and node[0] == 'val':
        return node[1]
    
    operators = {

            '+': operator.add,
            '-': operator.sub,
            '*': operator.mul,
            '/': operator.truediv,
            'eq': operator.eq,
            'ne': operator.ne,
            'ge': operator.ge,
            'gt': operator.gt,
            'le': operator.le,
            'lt': operator.lt,
            'and': operator.and_,
            'or': operator.or_,

        }
    
    if len(node) == 3 and node[0] in operators:

        op = operators[node[0]]

        return op(pl_eval(node[1]), pl_eval(node[2]))
    
    unary_operators = {
        
        '-': operator.neg,
        'not' : operator.not_,
    }

    if len(node) == 2 and node[0] in unary_operators:

        op = unary_operators[node[0]]

        return op(pl_eval(node[1]))
    
    if len(node) == 4 and node[0] == '?':

        _, cond, yes, no = node

        if pl_eval(cond):

            return pl_eval(yes)
        else:

            return pl_eval(no)
        
    if node[0] == 'print':
        return print(*(pl_eval(val) for val in node[1:]))
    

    if node[0] in ('do', 'then', 'else') and len(node) > 1:

        new_enviroment = (dict(), enviroment)
        
        for val in node[1:]:
            val = pl_eval(new_enviroment, val)        
        return val

    if node[0] == 'var' and len(node) == 3:

        _, name, val = node

        scope, _ = enviroment

        if name in scope:

            raise ValueError('duplicated name')
        
        val = pl_eval(enviroment, val)

        scope[name] = val
        return val

    if node[0] == 'set' and len(node) == 3:

        _,name, val = node
        scope = name_loopup(enviroment, name)
        val = pl_eval(enviroment, val)
        scope[name] = val

        return val

def name_loopup(enviroment, key):

    while enviroment:

        current, enviroment = enviroment

        if key in current:

            return current 
        
    raise ValueError('undefined name')

def pl_parse_prog(string):

    return pl_parse_prog('(do ' + string + ')')

def test_evaluation():

    def f(string):

        return pl_eval(None, pl_parse_prog(string))
    
    assert f('''
             ;; first scope
             (var a 1)
             (var b (+ a 1))
             ;; a =1, b=2
             (do
             ;; new scope
             (var a (+ b 5))
             (set b (+ a 10))
             )
             ;; a=1, b=17
             (*a b)''') == 17



