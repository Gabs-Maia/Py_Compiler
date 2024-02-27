from sds import parse_and_get_index

def parse_expression(string: str, index: int):

    index = parse_and_get_index(string, index)



def parse_expression(string: str, index: int):

    index = skip_space(string, index)
    #If its a list, parse it until the closing parenthesis.
    if string[index] == '(':
        index += 1
        list = []

        while True:
            index = parse_and_get_index(string, index)
            if index >= len(string):
                raise Exception('unbalaced parenthesis')
            
            if string[index] == ')':
                index += 1
                break
        
            index, vector = parse_expression(string, index)
            list.append(vector)
        
        return index, list            

    elif string[index] == ')':
        raise Exception('bad parenthesis')
    
    else: 
        start = index
        has_no_whitespice = (not string[index].isspace())
        

        while index < len(string) and has_no_whitespice and string[index] not in '()':
            index += 1
        
        if start == index:
            
            raise Exception('empty program')
        
        return index, parse_atoms(string[start:index])
