import copy, heapq

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

class Node(object):
    def __init__(self, board, coords, node_id, parent, f, g, head, direction):
        self.board = board
        self.coords = coords
        self.f = f
        self.g = g
        self.head = head
        self.info = {'id': node_id, 'parent': parent, 'direction': direction}

    def __lt__(self, other):
        if self.f == other.f:
            return self.g > other.g
        else:
            return self.f < other.f

    def __eq__(self, other):
        if not other:
            return False
        if not isinstance(other, Node):
            return False
        return self.f == other.f


class SnakeAI(object):
    def __init__(self, coords, coord, direction):
        self.coords = []
        self.path = None
        self.node_id = 0
        self.direction = self.get_direction(direction)
        self.board = self.get_board()
        # self.find_path(coords, coord)

    def get_board(self):
        board = [[0 for x in range(27)] for y in range(27)]
        for i in range(27):
            board[0][i] = board[26][i] = board[i][0] = board[i][26] = 2
        return board

    def get_xy(self, coord):
        x = (coord[0] - 10) // 20 + 1
        y = (coord[1] - 90) // 20 + 1
        return x, y

    def get_direction(self, direction):
        d = [UP, DOWN, LEFT, RIGHT]
        return d.index(direction)

    def clear_board(self):
        for x in range(1, len(self.board) - 1, 1):
            for y in range(1, len(self.board[0]) - 1, 1):
                self.board[y][x] = 0

    def make_board(self, coords, coord):
        self.coords.clear()
        x, y = self.get_xy(coord)
        self.goal = x, y
        self.board[y][x] = 1
        self.head = self.get_xy(coords[0])

        for coord in coords:
            x, y = self.get_xy(coord)
            self.coords.append((x, y))
            self.board[y][x] = 2
            
    def get_where(self, coords, coord):
        if not self.path:
            self.find_path(coords, coord)
        if self.path:
            return self.path.pop();
        else:
            return -1

    def copy_coords(self, coords):
        coordies = []
        for coord in coords:
            coordies.append(coord)
        return coordies

    def copy_board(self, coords):
        board = self.get_board()
        for coord in coords:
            x, y = coord
            board[y][x] = 2
        x, y = self.goal
        board[y][x] = 1
        return board
    
    def get_heuristic(self, x, y):
        x1, y1 = self.goal
        return (abs(x - x1) + abs(y - y1))

    def find_path(self, coords, coord):
        self.clear_board()
        self.make_board(coords, coord)
        self.path = self.a_star()

    def a_star(self):
        h = self.get_heuristic(self.head[0], self.head[1])
        g = 0
        node = Node(self.board, self.coords, 0, 0, h, g, self.coords[0], self.direction)
        open = []
        closed = []
        self.expand_node(open, node)
        # heapq.heappush(open, node)
        while open:
            node = heapq.heappop(open)
            #path = [node.info['direction']]
            #return path
            if g < node.g:
                g = node.g
            if g - node.g > 1:
               continue
            if node.head == self.goal:
                #print("found goal", len(open), len(closed))
                return self.make_path(closed, node.info)
            closed.append(node.info)
            self.expand_node(open, node)
        ## print("not found")
        if closed:
            path = [closed[0]['direction']]
            return path
        return None

    def is_hole(self, x, y, direction, board):
        if y - 1 >= 0 and direction > 1:
            if x == 25 and board[y - 1][x] == 2:
                return 10
        if y + 1  < 27  and direction > 1:
            if board[y + 1][x] == 2 and x == 1:
                return 10
        if y + 1  < 27 and y - 1 >= 0 and direction > 1:
            if board[y + 1][x] == 2 and board[y - 1][x] == 2:
                return 10
            if (board[y + 1][x] == 2 or board[y - 1][x] == 2):
                return 0
        if x - 1 >= 0 and direction < 2:
            if y == 25 and board[y][x - 1] == 2:
                return 10
        if x + 1  < 27 and direction < 2:
            if board[y][x + 1] == 2 and y == 1:
                return 10
        if x + 1  < 27 and x - 1 >= 0 and direction < 2:
            if board[y][x + 1] == 2 and board[y][x - 1] == 2:
                return 10
            if (board[y][x + 1] == 2 or board[y][x - 1] == 2):
                return 0
        return 3
            
    def expand_node(self, open, nodes):
        moves = [UP, DOWN, LEFT, RIGHT]
        x, y = nodes.head
        # d = nodes.info['direction']
        for i in range(4):
            dx, dy = moves[i]
            x1 = x + dx
            y1 = y + dy
            if nodes.board[y1][x1] < 2:
                coords = self.copy_coords(nodes.coords)
                head = (x1, y1)
                coords.insert(0, head)
                coords.pop()
                board = self.copy_board(coords)
                h = self.get_heuristic(x1, y1)
                if h > 0:
                    h1 = self.is_hole(x1, y1, i, board)
                    h += h1
                g = nodes.g + 1
                self.node_id += 1
                id = self.node_id
                parent = nodes.info['id']
                node = Node(board, coords, id, parent, g + h, g, head, i)
                heapq.heappush(open, node)
                
    def make_path(self, closed, inf):
        path = [inf['direction']]
        while closed:
            info = closed.pop()
            if info['id'] == inf['parent']:
                path.append(info['direction'])
                inf = info
        # path.reverse()
        # print(len(path), self.head, self.goal)
        return path
