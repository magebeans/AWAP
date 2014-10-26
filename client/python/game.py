##############################################################################
# game.py - Responsible for generating moves to give to client.py            #
# Moves via stdout in the form of "# # # #" (block index, # rotations, x, y) #
# Important function is find_move, which should contain the main AI          #
##############################################################################

import sys
import json
from operator import itemgetter

# Simple point class that supports equality, addition, and rotations
class Point:
    x = 0
    y = 0

    # Can be instantiated as either Point(x, y) or Point({'x': x, 'y': y})
    def __init__(self, x=0, y=0):
        if isinstance(x, dict):
            self.x = x['x']
            self.y = x['y']
        else:
            self.x = x
            self.y = y

    def __add__(self, point):
        return Point(self.x + point.x, self.y + point.y)

    def __eq__(self, point):
        return self.x == point.x and self.y == point.y

    def __getitem__(self, key):
        if(key == 'x'):
            return self.x
        if(key == 'y'):
            return self.y

    # rotates 90deg counterclockwise
    def rotate(self, num_rotations):
        if num_rotations == 1: return Point(-self.y, self.x)
        if num_rotations == 2: return Point(-self.x, -self.y)
        if num_rotations == 3: return Point(self.y, -self.x)
        return self

    def distance(self, point):
        return abs(point.x - self.x) + abs(point.y - self.y)

class Game:
    blocks = []
    grid = []
    bonus_squares = []
    my_number = -1
    dimension = -1 # Board is assumed to be square
    turn = -1

    def __init__(self, args):
        self.interpret_data(args)

    # find_move is your place to start. When it's your turn,
    # find_move will be called and you must return where to go.
    # You must return a tuple (block index, # rotations, x, y)

    def has_doge(self, block, position):
        for point in block:
            y = position.x + point.x 
            x = position.y + point.y
            doge = [(7,7), (7,12), (12,7), (12,12), (2,10), (17,9), (9,2), (10,17)]
            if (x,y) in doge:
#                debug(str(x) + " " + str(y) + " HAS DOGE")
                return True

        return False

    def in_bounds(self, pos):
        N = self.dimension
        if (pos.x >= 0 and pos.x < N and pos.y >= 0 and pos.y < N):
            return True
        return False

    def cuts_corner(self, block, point):
        for offset in block:
            p = point+offset;
            x = p.x
            y = p.y
            N = self.dimension

            res = 0
            corners = [(1,1),(-1,-1),(1,-1),(-1,1)]
            corners = [Point(c[0],c[1]) for c in corners]
            for c in corners:
                if(self.in_bounds(p+c) and self.other_player(p+c)):
                    res = res+1

        return res

    def adj(self, block, point):
        for offset in block:
            p = point+offset;
            x = p.x
            y = p.y
            N = self.dimension

            res = 0
            sides = [(-1,0), (0,-1), (1,0), (0,1), (-1,0)]
            sides = [Point(side[0], side[1]) for side in sides]
            for i in range(len(sides)-1):
                if(self.in_bounds(p+sides[i]) and self.other_player(p+sides[i])
                    and self.in_bounds(p+sides[i+1]) and self.other_player(p+sides[i+1])):
                        # debug("ADJ")
                        return True

        return False

    def other_player(self, point):
        return self.grid[point.x][point.y] >= 0 and self.grid[point.x][point.y] != self.my_number

    def score(self, block, position, level):
        x = position.x
        y = position.y
        N = self.dimension
        dist    = abs((2*((N/2)**2) - ((N/2-x)**2 + (N/2-y)**2)))
        size    = (len(block) * (1 + 99*self.has_doge(block, position)))
        corner  = (1+14*self.cuts_corner(block,position))
        adj     = (1+14*self.adj(block, position))
        score   = 100*(dist)+50*(size**2)+5*(corner)+5*(adj)

        if level > 0:
            old_grid = self.grid[:]
            for offset in block:
                p = position + offset
                self.grid[p.x][p.y] = self.my_number
            next_move = self.find_move(level-1)
            score += self.score(self.blocks[next_move[0]], Point(next_move[2], next_move[3]), level-1)
            self.grid = old_grid[:]

        # debug(str(level))
        # debug(str(score))
        return score
    def find_move(self, level=0):
        moves = []
        N = self.dimension

        for x in range(N):
            for y in range(N):
                for index, block in enumerate(self.blocks):
                    for rotations in range(0,4):
                        new_block = self.rotate_block(block, rotations)
                        move = (index, rotations, x, y)
                        if self.can_place(new_block, Point(x,y)):
                            moves.append((move, self.score(new_block, Point(x,y), level)))

        moves.sort(key=itemgetter(1), reverse=True)

        # if(self.has_doge(self.blocks[move[0]], Point(move[2], move[3]))):
        # x = move[2]
        # y = move[3]
        # block = self.blocks[move[0]]
        # for point in block:
#            debug(str(point.x + x) + " " + str(point.y + y) + " and was chosen.")
        # else:
#        #     debug("NO DOGE")
#        # debug(str(moves[0][1]))
        return moves[0][0]

        # blocks = zip(range(len(self.blocks)), self.blocks, map(len,self.blocks), map(squarishness,self.blocks))
        # blocks.sort(key=itemgetter(2), reverse=True)
        # blocks.sort(key=itemgetter(3), reverse=False)
        # blocks = zip(map(itemgetter(0), blocks), map(itemgetter(1), blocks))
        # # for index,block in enumerate(self.blocks):
        # center = N/2 + 1
        # for index, block in blocks:
        #     for diag in range(center):
        #         for dist in range(diag):
        #             x = center - diag + dist
        #             y = center - diag - dist
        #             for rotations in range(0, 4):
        #                 new_block = self.rotate_block(block, rotations)
        #                 if self.can_place(new_block, Point(x, y)):
        #                     return (index, rotations, x, y)

        #             x = center - diag - dist
        #             y = center - diag + dist
        #             for rotations in range(0, 4):
        #                 new_block = self.rotate_block(block, rotations)
        #                 if self.can_place(new_block, Point(x, y)):
        #                     return (index, rotations, x, y)

        return (0, 0, 0, 0)

    # Checks if a block can be placed at the given point
    def can_place(self, block, point):
        onAbsCorner = False
        onRelCorner = False
        N = self.dimension - 1

        corners = [Point(0, 0), Point(N, 0), Point(N, N), Point(0, N)]
        corner = corners[self.my_number]

        for offset in block:
            p = point + offset
            x = p.x
            y = p.y
            if (x > N or x < 0 or y > N or y < 0 or self.grid[x][y] != -1 or
                (x > 0 and self.grid[x - 1][y] == self.my_number) or
                (y > 0 and self.grid[x][y - 1] == self.my_number) or
                (x < N and self.grid[x + 1][y] == self.my_number) or
                (y < N and self.grid[x][y + 1] == self.my_number)
            ): return False

            onAbsCorner = onAbsCorner or (p == corner)
            onRelCorner = onRelCorner or (
                (x > 0 and y > 0 and self.grid[x - 1][y - 1] == self.my_number) or
                (x > 0 and y < N and self.grid[x - 1][y + 1] == self.my_number) or
                (x < N and y > 0 and self.grid[x + 1][y - 1] == self.my_number) or
                (x < N and y < N and self.grid[x + 1][y + 1] == self.my_number)
            )

        if self.grid[corner.x][corner.y] < 0 and not onAbsCorner: return False
        if not onAbsCorner and not onRelCorner: return False

        return True

    # rotates block 90deg counterclockwise
    def rotate_block(self, block, num_rotations):
        return [offset.rotate(num_rotations) for offset in block]

    # updates local variables with state from the server
    def interpret_data(self, args):
        if 'error' in args:
#            debug('Error: ' + args['error'])
            return

        if 'number' in args:
            self.my_number = args['number']

        if 'board' in args:
            self.dimension = args['board']['dimension']
            self.turn = args['turn']
            self.grid = args['board']['grid']
            self.blocks = args['blocks'][self.my_number]
            self.bonus_squares = args['board']['bonus_squares']

            for index, block in enumerate(self.blocks):
                self.blocks[index] = [Point(offset) for offset in block]

        if (('move' in args) and (args['move'] == 1)):
            send_command(" ".join(str(x) for x in self.find_move()))

    def is_my_turn(self):
        return self.turn == self.my_number

def get_state():
    return json.loads(raw_input())

def send_command(message):
    print message
    sys.stdout.flush()

def debug(message):
    send_command('DEBUG ' + str(message))

def main():
    setup = get_state()
    game = Game(setup)

    while True:
        state = get_state()
        game.interpret_data(state)

if __name__ == "__main__":
    main()
