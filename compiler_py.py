"""
IMPORTANT : S-Expressions are basically nested lists.
These lists act like a grap(Tree), which mean that the whole
parsing process can become way easier.

"""

import operator

class LoopBreak(Exception):
    def __init__(self):
        super().__init__('`break` outside of a Loop!')

class LoopContinue(Exception):
    def __init__(self):
        super().__init__('`continue` outside a Loop!')

def name_lookup(scope, key):

    while scope:
        current, scope = scope

        if key in current:
            return current
        
    raise ValueError('undefined name')

#Identifying comments
def identify_comments(string, index):
    while True:
        position = index

        while index < len(string) and string[index].isspace():
            index += 1
        
        if index < len(string) and string[index] == ';':
            index += 1

            while index < len(string) and string[index] != '\n':
                index +=1
        
        if index == position:
            break
    
    return index

def identify_atom(string, index):

    while index < len(string) and string[index].isspace():
        index += 1

        return index
    
# Boolean, number, string or a symbol.
    
def parse_atoms(string):
    import json

    try:
        return ['val', json.loads(string)]
    
    except json.JSONDecodeError:
        return string

def expression_evaluation(scope ,string):

    index, node = parse_expression(string, 0)
    index = identify_atom(string, index)

    if not isinstance(node, list):
        assert isinstance(node, str)
        return name_lookup(scope, node)[node]

    if index < len(string):

        raise ValueError('trailing garbage')
    
    return node 

def language_evaluation(scope, node):

    if len(node) == 0:

        raise ValueError('empty list')
    
    if len(node) == 2 and node[0] == 'val':
        return node[1]
    
    binary_operators = {

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

    
    if len(node) == 3 and node[0] in binary_operators:  

        operators = binary_operators[node[0]]

        return operators(language_evaluation(node[1]), language_evaluation(node[2]))


    unary_operators = {

        '-': operator.neg,
        'not': operator.not_,
    }

    if len(node) == 2 and node[0] in unary_operators:
        operators = unary_operators[node[0]]
        return operators(language_evaluation(node[1]))
    
    #Conditionals statements

    if len(node) == 4 and node[0] == '?':

        _, conditional, yes, no = node

        if language_evaluation(conditional):
            return language_evaluation(yes)
        else:
            return language_evaluation(no)
        
    #Print   
    if node[0] == 'print':
        return print(*(language_evaluation(val) for val in node[1:]))
    
    if node[0] in ('do', 'then', 'else') and len(node) > 1:

        #Add map as the linked list head
        new_scope = (dict(), scope)

        for val in node[1:]:
            val = language_evaluation(new_scope, val)
        
        return val
    
    if node[0] == 'var' and len(node) == 3:
        _, name, val = node
        scope, _ = scope

        if name in scope:
            raise ValueError('duplicated name')
        
        val = language_evaluation(scope, val)
        scope[name] = val
        return val
    
    #Variable update
    if node[0] == 'set' and len(node) == 3:
        _,name,val = node
        scope = name_lookup(scope, name)
        val = language_evaluation(scope, val)
        
        scope[name] = val
        return val
    
    #Conditionals:
    if len(node) in (3, 4) and node[0] in ('?', 'if'):
        _, conditional, yes, *no = node

        no = no[0] if no else ['val', None]
        new_scope = (dict(), scope)

        if language_evaluation(new_scope, conditional):
            return language_evaluation(new_scope, yes)
        else:
            return language_evaluation(new_scope, no)
        
    #Loops
    if node[0] == 'loop' and len(node) == 3:
        _, conditional, body = node
        ret = None

        while True:
            new_scope = (dict(), scope)
            if not language_evaluation(new_scope, conditional):
                break
            
            try:
                ret = language_evaluation(new_scope, conditional)
            except LoopBreak:
                break
            except LoopContinue:
                continue
        
        return ret
    
    #Break and Continue
    if node[0] == 'break' and len(node) == 1:
        raise LoopBreak
    
    if node[0] == 'continue' and len(node) == 1:
        raise LoopContinue
    
    #Defining Functions
    if node[0] == 'def' and len(node) == 4:
        _, name, args, body = node

        for arg_name in args:
            if not isinstance(arg_name, str):
                raise ValueError('bad argument name')
            
        if len(args) != len(set(args)):
            raise ValueError('duplicated arguments')
            
        dictionary, _ = scope
        key = (name, len(args))

        if key in dictionary:
            raise ValueError('duplicated function')
        

        dictionary[key] = (args, body, scope)   
        return 

    # Function Call

    if node[0] == 'call' and len(node) >= 2:
        _, name, *args = node

        key = (name, len(args))
        fargs, fbody, fscope = name_lookup(scope,key)[key]

        #args
        new_scope = dict()
        for          
    
#Testing values

def language_parse_prog(string):
    return language_evaluation('(do ' + string + ')')

def test_eval():
    def f(s):
        return language_evaluation(None, language_parse_prog(s))
    
    assert f('''
             ;; first scope
             (var a 1)
             (var b (+ a 1))
             ;; a=1, b=2
             (do
                
                ;;new scope
                (var a (+ b 5))
                (Set b (+ a 10))
             )
             ;;a=1, b=17
             (* a b)''') == 17

#Testing evaluation
def test_evaluation():

    def function(string):
        return language_evaluation(language_evaluation(string))
    
    assert function('l') == 1
    assert function('(+ 1 3)') == 4
    assert function ('(? (lt 1 3) "yes" "no")') == "yes"
    assert function('(print 1 2 3)') is None
   
def parse_expression(string: str, index: int):

    index = identify_atom(string, index)
    if string[index] == '(':
        
        #If it's a list => 
        index += 1
        list = []

        while True:
            index = identify_atom(string, index)
            if index >= len(string):

                raise Exception('unbalaced parenthesis')
            
            if string[index] == ')':

                index += 1
                break

            index, v = identify_atom(string, index)
            list.append(v)
        
        return index, list
    
    elif string[index] == ')':
        raise Exception('bad parenthesis')
    
    else: 

        start = index
        x = (not string[index].isspace())

        while index < len(string) and string[index] not in '()':

            index += 1
        
        if start == index:

            raise Exception('empty program')
        
        return index, identify_atom(string[start:index])