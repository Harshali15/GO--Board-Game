import random
import sys
from copy import deepcopy
from numpy.random import normal
import heapq
import queue

BLACK_STONES=0
WHITE_STONES=0


def read_write_file(read, write, result):

    def read_input(path="input.txt"):        #read previous and current boards
        f=open(path, 'r')
        lines = f.readlines()

        player = int(lines[0])
        pre=lines[1:6]
        cur=lines[7:12]
        previous_board=[]
        temp=[]
        
        for line in lines[1:6]:
            for x in line.strip('\n'):
                temp.append(int(x))
            previous_board.append(temp)
            temp=[]
        current_board=[]
        temp=[]
        for line in lines[6:11]:
            for x in line.strip('\n'):
                temp.append(int(x))
            current_board.append(temp)
            temp=[]
        return player, previous_board, current_board

    def write_output(result):
        res = ""
        
        path="output.txt"
        fp = open(path, 'w')
        if result != "PASS":
            res += str(result[0]) + ',' + str(result[1])
        else:
            res = "PASS"

        fp.write(res)

    if read:
        b, prev, curr = read_input("input.txt")
        return b, prev, curr
    else:
        write_output(result)
        return None, None, None
    
def ko(previousboard, currentboard):
    for i in range(0,5):
        for j in range(0,5):
            if currentboard[i][j] != previousboard[i][j]:
                return False
    return True
    
def check_allies_exist(x,y, allies):
    for a in allies:
        if(a[0]==x and a[1]==y):
            return True
    return False

def add_to_libertySet(point,free):
    #l=len(free)
    free.append(point)

def neighbors_fn(i, j, board, player, choice):
    
    def detect_neighbor(x, y):
        neighbors = []

        if x+1 < 5:
            neighbors.append((x+1,y))
        if x-1 >= 0:
            neighbors.append((x-1,y))
        if y+1 < 5:
            neighbors.append((x,y+1))
        if y-1 >= 0:
            neighbors.append((x,y-1))

        return neighbors
    
    def detectfour_neighally(i, j, board, player):
        ally = detect_neighbor(i, j)
        allygroup = []
        for a in ally:
            invalid_ch=invalid_check(board,i,j)
            if board[a[0]][a[1]] == player:
                allygroup.append(a)

        return allygroup

    if choice != 1:
        s =  detect_neighbor(i, j)
        return s
    else:
        s = detectfour_neighally(i, j, board, player)
        return s

def positions(a, b, choices, prev, bot):

    def all_ally_positions(i, j, board, player):

        if not (i < 5 and j < 5  and i >= 0 and j >= 0):
            return None

        all_allies = []
        neighbors = neighbors_fn(i, j, board, player, 1)
        all_allies.append((i, j))
        visited = {}
        visited[(i, j)] = True
        while True:
            temp_list, neighbors = neighbors, []
            
            for x, y in temp_list:
                invalid_ch=invalid_check(board,x,y)
                if (x, y) not in visited and board[x][y] == player:
                    exist=check_allies_exist(x,y,all_allies)
                    all_allies.append((x, y))
                    visited[(x, y)] = True
                    next_neighbor = neighbors_fn(x, y, board, player, 1)
                    
                    for ne in next_neighbor:
                        invalid_ch=invalid_check(board,x,y)
                        neighbors.append(ne)
                        
            if len(neighbors) == 0:
                return []
            
        return all_allies

    def all_positions(i, j, board, player):
        lfqueue = queue.LifoQueue()
        lfqueue.put((i, j))
        ally_members = []
        free=[]
        
        while not lfqueue.empty():
            piece = lfqueue.get()
            
            ally_members.append(piece)
            neighbor_allies = neighbors_fn(piece[0], piece[1], board, player, 1)
            add_to_libertySet(piece,free)
            for ally in neighbor_allies:
                if ally not in list(lfqueue.queue) and ally not in ally_members:
                    add_to_libertySet(ally,free)
                    lfqueue.put(ally)
                    
        return ally_members
    
    def libertyPos(i, j,board,player):
        allyMembers = all_positions(i, j, board,player)
        liberties=set()
        for m in allyMembers:
            allneighbors = neighbors_fn(m[0], m[1], None, None, 0)
            for point in allneighbors:
                check_valid_or_not=invalid_check(board,i,j)
                if board[point[0]][point[1]] == 0:
                    free=[]
                    free=add_to_libertySet(point,free)
                    liberties = liberties  | set([point])



        return list(liberties)
    
    def get_neigh_liberty_positions(i,j,board,player):
        
        neighbors = neighbors_fn(i,j, None, None, 0)
        neigh_lib = set()
        for piece in neighbors:
            check_valid_or_not=invalid_check(board,piece[0],piece[1])
            if board[piece[0]][piece[1]] == 0:
                data=board[piece[0]][piece[1]]
                neigh_lib=neigh_lib|set([piece])

        return list(neigh_lib)


    if choices == 3:
        all_vals = get_neigh_liberty_positions(a, b, prev, bot)
    elif choices == 2:
        all_vals = libertyPos(a, b, prev, bot)
    elif choices == 1:
        all_vals = all_positions(a, b, prev, bot)
    elif choices == 0:
        all_vals = all_ally_positions(a, b, prev, bot)
 
    return all_vals

def invalid_check(board,i,j):
    if board[i][j]==0:
        return True;
    else:
        return False;

#def isPass(prevboard, currboard)
#    if prevboard==currboard


def find_and_died(a, b, fimdOrRemoved, bot, board):
    def find_died_pieces(player, board):
        died_pieces = []

        for i in range(0, 5):
            for j in range(0, 5):

                if board[i][j] == player:

                    if not find_count_liberty(i, j, board, player):
                        died_pieces.append((i, j))
        return died_pieces


    
    def find_count_liberty(i, j, board, player):
        my_all_allies = positions(i, j, 1, board, player)
        invalid_check(board,i,j)
        my_all_allies_len = len(my_all_allies)
        i=0
        while i != my_all_allies_len:
            ally = my_all_allies[i]
            neighbors = neighbors_fn(ally[0], ally[1], None, None, 0)
            free=[]
            for piece in neighbors:
                if board[piece[0]][piece[1]] == 0:
                    add_to_libertySet(piece,free)
                    return True
            i=i+1
        return False

    if fimdOrRemoved == 0:
        all_vals = find_died_pieces(bot, board)
        
    elif fimdOrRemoved == 1:
        #all_vals = remove_died_pieces(bot, board)
        for p in bot:
            board[p[0]][p[1]] = 0
            
        all_vals=board
        
    elif fimdOrRemoved == 2:
        all_vals = find_count_liberty(a, b, board, bot)
        
    return all_vals


def try_move(i, j, board, player):
    new_board = board

    new_board[i][j] = player
    if player==1:
        invalid_check(board,i,j)
        died_pieces = find_and_died(i, j, 0, 2, new_board)
    else:
        died_pieces = find_and_died(i, j, 0, 1, new_board)

    if len(died_pieces) != 0:
        next_board = find_and_died(None, None, 1, died_pieces, new_board)
    else:
        return new_board, len(died_pieces),new_board

    return next_board,len(died_pieces),new_board



def valid_moves(player, previous_board, new_board):
    move_all_liberty=set()
    moves = []
    must_moves=[]
    oppo_end_2=set()
    

    for i in range(0, 5):
        for j in range(0, 5):
            if new_board[i][j]==player:
                self_end=positions(i,j,2,new_board,player)
                invalid_ch=invalid_check(new_board,i,j)
                if len(self_end)==1:
                    free=[]
                    add_to_libertySet([i,j],free)
                    move_all_liberty=move_all_liberty|set(self_end)
                    if i==0 or i==4 or j==0 or j==4:
                        invalid_ch=invalid_check(new_board,i,j)
                        
                        safe_positions= positions(self_end[0][0],self_end[0][1], 3,new_board,player)
                        if safe_positions:
                            check_KO= ko(new_board,previous_board)
                            move_all_liberty = move_all_liberty|set(safe_positions)
                       
     
            elif new_board[i][j]==3-player:
                if (3-player)==1:
                    invalid_ch=invalid_check(new_board,i,j)
                    oppo_end=positions(i,j,2,new_board,1)
                else:
                    invalid_ch=invalid_check(new_board,i,j)
                    oppo_end=positions(i,j,2,new_board,2)
                move_all_liberty=move_all_liberty|set(oppo_end)
        
    if len(list(move_all_liberty))!=0:
        check_KO= ko(new_board,previous_board)
        for x in list(move_all_liberty):
            
            tri_board = deepcopy(new_board)
            p=x[0]
            q=x[1]
            check=invalid_check(new_board,p,q)
            board_after_move,died_pieces,_ = try_move(x[0],x[1], tri_board, player)
            ko(board_after_move, tri_board)
            if find_and_died(x[0], x[1], 2, player, board_after_move) and board_after_move != new_board and board_after_move != previous_board:
                #adding move
                ko(board_after_move, new_board)
                must_moves.append((x[0], x[1],died_pieces))
                
                
        if len(must_moves)!= 0:
         
            return sorted(must_moves, key=lambda x: x[2],reverse=True)
  
    for i in range(0, 5):
        for j in range(0, 5):

            if  new_board[i][j] == 0:
              
                trial_board = deepcopy(new_board)
                check=invalid_check(trial_board,i,j) #check if already exists a player
                board_after_move,died_pieces,_ = try_move(i, j, trial_board, player)
                if find_and_died(i, j, 2, player, board_after_move) and board_after_move != new_board and board_after_move != previous_board:
                    moves.append((i, j,died_pieces))

    return sorted(moves, key=lambda x: x[2],reverse=True)


def score_calculator(board, player,died_pieces_black,died_pieces_white):
    
    bc = 0
    wc = 2.5
    bd=0
    wd=0
    
    for i in range(0, 5):
        for j in range(0, 5):
            invalid_ch=invalid_check(board,i,j)
            
            if board[i][j] == 2:
                num=2
                lib=positions(i,j,num,board,num)
                if len(lib)<=1:
                    wd=wd+1
                wc += 1
                
            elif board[i][j] == 1:
                num=1
                lib=positions(i,j,2,board,num)
                if len(lib)<=1:
                    bd=bd+1
                bc += 1
                
    #wc = wc + 2.5
    ad1=died_pieces_white*10-died_pieces_black*16
    ad2=died_pieces_black*10-died_pieces_white*16
    if player==1:
        score = bc-wc+wd-bd+ad1
    else:
        score = -bc+wc-wd+bd+ad2

    return score


def best_move(player, depth,board,previous_board):
    a=float("-inf")
    b=float("inf")
    funct="max"
    died_pieces_white=0
    score, actions = maxmin(board,previous_board,player,depth, a, b,board,funct)
    if len(actions)==0:
        return "PASS"
    else:
        return actions[0]
        #return random.choice(actions)
    
def maxmin(board,previous_board,player,depth, alpha, beta,new_board_without_died_pieces,type="max"):
    global BLACK_STONES
    global WHITE_STONES
    
    if player==1:
        
        died_pieces_black=len(find_and_died(None, None, 0, player,new_board_without_died_pieces))
        BLACK_STONES=BLACK_STONES+died_pieces_black
    
    if player==2:
        
        died_pieces_white=len(find_and_died(None, None, 0, player,new_board_without_died_pieces))
        WHITE_STONES=WHITE_STONES+died_pieces_white
    
    if depth == 0:
        value = score_calculator(board,player,BLACK_STONES, WHITE_STONES)
        
        if player==1:
            BLACK_STONES=BLACK_STONES-len(find_and_died(None, None, 0, 1,new_board_without_died_pieces))
        if player==2:
            WHITE_STONES=WHITE_STONES-len(find_and_died(None, None, 0, 2,new_board_without_died_pieces))
        return value,[]
    
    opp = 3-player
    if type=="min":
        min_score = float("inf")
        min_score_actions = []
        check_KO= ko(previous_board,board)
        my_moves = valid_moves(player, previous_board, board)

        for move in my_moves:
            ch=1
            trial_board = deepcopy(board)
            next_board,died_pieces,new_board_without_died_pieces = try_move(move[0], move[1], trial_board, player)
            score, actions = maxmin(next_board,board,opp,depth-1, alpha, beta,new_board_without_died_pieces,"max")

            if score < min_score:
                ch=2
                min_score = score
                min_score_actions = [move] + actions


            if min_score < alpha:
                ch=3
                return min_score, min_score_actions

            if min_score < beta:
                ch=4
                alpha = min_score

        return min_score, min_score_actions
        
        
    else:
        
        max_score = float("-inf")
        max_score_actions = []
        check_KO= ko(previous_board,board)


        my_moves = valid_moves(player, previous_board, board)

        if len(my_moves)==25:
            #implies empty board, all zeroes, put in center to maximize chances
            init_score=100
            center_point=[(2,2)]
            return init_score, center_point
        
        for move in my_moves:
            ch=1
            trial_board = deepcopy(board)
            
            next_board,died_pieces,new_board_without_died_pieces = try_move(move[0], move[1], trial_board, player)
            check_KO= ko(next_board,new_board_without_died_pieces)
            score, actions = maxmin(next_board,board, opp,depth-1, alpha, beta,new_board_without_died_pieces,"min")

            if score > max_score:
                ch=2
                max_score = score
                max_score_actions = [move] + actions
            
            if max_score > beta:
                ch=3
                return max_score, max_score_actions

            if max_score > alpha:
                ch=4
                alpha = max_score

        return max_score, max_score_actions

def GamePlayer(player, previous_board, new_board):
    depth=4
    good_move = best_move(player,depth,new_board,previous_board)
    _, _, _ = read_write_file(False, True, good_move)
    
def start():
    player, previous_board, board = read_write_file(True, False, None)
    GamePlayer(player, previous_board, board)

start()


