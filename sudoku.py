import itertools
import random
import os
import time

MAX_ALLOWED_RUNTIME= 1000
start_t = time.time()
elapsed_time = 0
statenum=0


def valid_sudoku(line):
    result = (len(line) == 9 and sum(line) == sum(set(line)))
    return result

def filled_sudoku(line):
    result = 0 not in line
    return result

def no_blanks(grid):
    unfilled_rows = [True for row in grid if not filled_sudoku(row)]
    #transpose the matrix
    return not unfilled_rows

def check_sudoku(grid):
    bad_rows = [row for row in grid if not valid_sudoku(row)]
    grid = list(zip(*grid))
    bad_cols = [col for col in grid if not valid_sudoku(col)]
    if bad_rows or bad_cols:
        return False

    squares = []
    for i in range(0, 9, 3):
        for j in range(0, 9, 3):
            square = list(itertools.chain(row[j:j+3] for row in grid[i:i+3]))
            squares.append(list(itertools.chain(*square)))
    bad_squares = [square for square in squares if not valid_sudoku(square)]
    return not (bad_rows or bad_cols or bad_squares)

def find_unassigned(grid):
    i = 0
    for row in grid:
        j = 0
        for var in row:
            if var == 0:
                return [i,j]
            j+=1
        i+=1
    print("No more blanks found")
    return [-1,-1]

def find_unassigned_random(grid):
    i = 0
    blank_lst = []
    for row in grid:
        j = 0
        for var in row:
            if var == 0:
                blank_lst.append([i,j])
            j+=1
        i+=1
    upper = len(blank_lst) - 1
    index = random.randint(0,upper)
    return blank_lst[index]

def find_remaining_vars(grid):
    i = 0
    blank_lst = []
    for row in grid:
        j = 0
        for var in row:
            if var == 0:
                blank_lst.append([i,j])
            j+=1
        i+=1
    return blank_lst

def forward_check(grid, vars_left):
    state = grid
    for var in vars_left:
        legalnum = 0
        for value in range(1,10):
            state = assign_var(state, var[0], var[1], value)
            if check_sudoku(state):
                #print("Legal assignment of:", value, "to", var[0], var[1])
                legalnum +=1
            state = assign_var(state, var[0], var[1], 0)   
        if legalnum == 0:
            #print("Var at", var[0], var[1], "has no more legal values!")
            return False

    return True

def assign_var(grid,i,j,val):
    if grid[i][j] == 0 or val == 0:
        grid[i][j] = val
        #print("Selected Variable", [i,j], "assigned value of", val) 
    elif val != 0:
        print("Selected Variable", "Trying to assign a value of", val, "when", [i,j], "is already assigned!") 

    return grid

def most_constrained(grid, vars_left):
    mrv = []
    mrv_lst = [mrv]
    min_moves = 10
    for var in vars_left:
        legalnum = 0
        for value in range(1,10):
            grid = assign_var(grid, var[0], var[1], value)
            if check_sudoku(grid):
                legalnum +=1
            #revert to initial state    
            grid = assign_var(grid, var[0], var[1], 0)   

        #print("var:", var,"has ", legalnum, "possible values")

        if legalnum < min_moves:
            mrv_lst = []
            mrv = var
            min_moves = legalnum
            mrv_lst.append(var)
            #print("mrv is now:", mrv_lst) 
        elif legalnum == min_moves:
            mrv_lst.append(var)

    return mrv_lst  

#returns the a list of blanks constrained by a var at (i,j)
def get_contraining(index, vars_left):
    degree = 0
    deg_lst =[]
    x = index[0]
    y = index[1]

    for var in vars_left:
        if var[0] == x or var[1] == y:
            degree += 1
            deg_lst.append(var)

        cell_x = x/3
        cell_y = y/3

        for i in range(0,3):
            for j in range(0, 3):
                if [cell_x*3+i, cell_y*3+j] == var and var != [x,y]:
                    #print("Var:", var)
                    degree+= 1
                    deg_lst.append(var)

    return deg_lst

def most_constraining(var_lst, grid):
    max_deg = 0
    max_var = []
    mcv_lst = [max_var]
    blanks_lst = find_remaining_vars(grid)
    for var in var_lst:
        degree = len(get_contraining(var, blanks_lst))
        #print(var, "constrains:", degree, "other vars")
        if degree > max_deg:
            max_deg = degree

            #purge the list of old vars
            mcv_lst = []
            max_var=var
            mcv_lst.append(var)
        elif degree == max_deg:
            mcv_lst.append(var)
    return mcv_lst

def get_domain_size(var, grid):
    mrv_lst = []
    legalnum = 0
    for value in range(1,10):
        grid = assign_var(grid, var[0], var[1], value)
        if check_sudoku(grid):
            legalnum +=1

        #revert to initial state    
        grid = assign_var(grid, var[0], var[1], 0)  

    return legalnum   

def least_constrain_val(grid, index, domain):
    x = index[0]
    y = index[1]
    lcv = 1
    max_dsum = 0
    lcv_lst=[]
    for value in domain:
        domain_lst =[]
        grid = assign_var(grid, x, y, value)
        blank_lst = find_remaining_vars(grid)
        for var in blank_lst:
            dsize = get_domain_size(var, grid)
            #print(var, dsize)
            domain_lst.append(dsize)

        dsum = sum(domain_lst)
        #print("dsum", dsum)
        if dsum > max_dsum:
            max_dsum = dsum
            lcv_lst = []
            lcv = value
            lcv_lst.append(lcv)
        elif dsum == max_dsum:
            lcv_lst.append(value)

        grid = assign_var(grid, x, y, 0)    
    return lcv_lst

def solve_sudoku_random(grid, depth, var_lst):
    global statenum
    global elapsed_time
    global start_t    
    statenum+=1
    if elapsed_time > MAX_ALLOWED_RUNTIME:
        return False    
    if no_blanks(grid) and check_sudoku(grid):
        #if given state is the goal state, just return it
        print("Solution found!")
        print("Total # of Nodes Traversed", statenum)
        statenum = 0
        return grid
    elif no_blanks(grid):
        #puzzle has no blanks, but also invalid
        print("Invalid Input!")
        return False  
    else:
        domain = [1,2,3,4,5,6,7,8,9]
        var_ind=random.randrange(0, len(var_lst))
        indices = var_lst[var_ind]
        
        while len(domain) > 0:
            index = random.randrange(0,len(domain))
            val = domain[index]
            #assign
            grid = assign_var(grid, indices[0], indices[1], val)  
            domain.remove(val)
            var_lst.remove(indices)
            if check_sudoku(grid):          
                if solve_sudoku_random(grid, (depth + 1), var_lst):
                    return grid
                else:
                    currTime = time.time() - start_t
                    elapsed_time = int(currTime)                        
                    if elapsed_time > MAX_ALLOWED_RUNTIME and depth == 0:
                        start_t = time.time()
                        elapsed_time = 0
                        print("Total # of Nodes Traversed", statenum)
                        statenum = 0
                        return False                     

            #backtrack to last valid state
            var_lst.append(indices)
            grid = assign_var(grid, indices[0], indices[1], 0)
            #print("Backtracked to State #", statenum, "reverted var at", indices[0], indices[1])              

    return False

def solve_sudoku_FC(grid, depth):
    global statenum
    global elapsed_time
    global start_t
    currTime = time.time() - start_t
    elapsed_time = int(currTime)

    if elapsed_time > MAX_ALLOWED_RUNTIME:
        return False

    statenum+=1

    if no_blanks(grid) and check_sudoku(grid):
        #if given state is the goal state, just return it
        print("Solution found!")
        elapsed_time = 0
        start_t = time.time()
        print("Total # of Nodes Traversed", statenum)
        statenum = 0
        return grid
    elif no_blanks(grid):
        #puzzle has no blanks, but also invalid
        print("Invalid Input!")
        return False  
    else:
        domain = [1,2,3,4,5,6,7,8,9]
        indices = find_unassigned_random(grid)

        while len(domain) > 0:
            index = random.randrange(0,len(domain))
            val = domain[index]         
            #assign
            grid = assign_var(grid, indices[0], indices[1], val)  
            domain.remove(val) 
            vars_left = find_remaining_vars(grid)
            if check_sudoku(grid):
                if forward_check(grid,vars_left):            
                    if solve_sudoku_FC(grid, (depth + 1)):
                        return grid
                    else:
                        currTime = time.time() - start_t
                        elapsed_time = int(currTime)                        
                        if elapsed_time > MAX_ALLOWED_RUNTIME and depth == 0:
                            start_t = time.time()
                            elapsed_time = 0
                            statenum = 0
                            print("Total # of Nodes Traversed", statenum)
                            return False                        

            #backtrack to last valid state
            grid = assign_var(grid, indices[0], indices[1], 0)             

    return False

#backtracking, Forward checking + heuristics
def solve_sudoku_FCH(grid):
    global statenum
    statenum+=1

    if no_blanks(grid) and check_sudoku(grid):
        #if given state is the goal state, just return it
        print("Solution found!")
        print("Total # of Nodes Traversed", statenum)
        statenum = 0
        return grid
    elif no_blanks(grid):
        #puzzle has no blanks, but also invalid
        print("Invalid Input!")
        return False  
    else:
        domain = [1,2,3,4,5,6,7,8,9]
        vars_lst = find_remaining_vars(grid)
        mcv_lst = most_constrained(grid,vars_lst)
        if len(mcv_lst) == 1:
            indices = mcv_lst[0]
        else:
            #break the tie with most constraining
            new_lst = most_constraining(mcv_lst, grid)
            if len(new_lst) == 1:
                indices = new_lst[0]            
            else:
                #if there is still a tie, pick one randomly
                index = random.randrange(0,len(new_lst))
                indices = new_lst[index]

        #print("Chose index of:", indices)        
        while len(domain) > 0: 
            val_lst = least_constrain_val(grid, indices,domain)

            if len(val_lst) == 1:
                value = val_lst[0]            
            else:
                #if there is a tie, pick one randomly
                index = random.randrange(0,len(val_lst))
                value = val_lst[index]

            #print("Chose value of:", value)   
            #assign
            grid = assign_var(grid, indices[0], indices[1], value)
            domain.remove(value) 
            vars_left = find_remaining_vars(grid)
            if check_sudoku(grid):
                if forward_check(grid,vars_left):
                    if check_sudoku(grid):
                        if solve_sudoku_FCH(grid):
                            return grid

            #backtrack to last valid state
            grid = assign_var(grid, indices[0], indices[1], 0)


    return False
