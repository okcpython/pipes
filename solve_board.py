import argparse
import io
import os

from draw_board import Board, draw_board


#######################################################################
class MyTile(object):
    TILE_TYPES = ['_', 'H', 'I', 'L', 'T', '1', '2', '3']
    TILE_ORIENTATIONS = [1, 2, 3, 4]
    TILE_ORIENTATIONS_MAP = {
        1: 'N', 2: 'E', 3: 'S', 4: 'W'
    }

    ###################################################################
    def __init__(self, x, y, tile_type, board, orientation=1):
        self.x = x
        self.y = y
        self.tile_type = tile_type
        self.board = board
        self.orientation = orientation
        self.locked = False
        self.connected_neighbors = []

    ###################################################################
    def __str__(self):
        return "{0} {1} {2} {3}".format(self.y, self.x, self.tile_type, self.TILE_ORIENTATIONS_MAP[self.orientation])

    ###################################################################
    def get_readable_orientation(self):
        if not self.is_empty():
            tile = unicode(self.TILE_ORIENTATIONS_MAP[self.orientation])
        else:
            tile = u'_'
        return tile

    ###################################################################
    def is_empty(self):
        return self.tile_type in ('_',)

    ###################################################################
    def is_gas_tank(self):
        return self.tile_type in ('1', '2', '3')

    ###################################################################
    def is_pipe(self):
        return self.tile_type in ('I', 'L', 'T')

    ###################################################################
    def is_locked(self):
        return self.locked

    ###################################################################
    def tiles_are_connected(self, neighbor):
        if self.orientation == 1 and neighbor.orientation == 3 and self.get_northern_neighbor() == neighbor:
            return True
        if self.orientation == 2 and neighbor.orientation == 4 and self.get_eastern_neighbor() == neighbor:
            return True
        if self.orientation == 3 and neighbor.orientation == 1 and self.get_southern_neighbor() == neighbor:
            return True
        if self.orientation == 4 and neighbor.orientation == 2 and self.get_western_neighbor() == neighbor:
            return True
        return False

    ###################################################################
    def _can_rotate_neighbor_to_connect(self, neighbor):
        if neighbor.is_locked():
            return False
        return True

    ###################################################################
    def _connect_tiles(self, neighbor):
        # do the low level rotating to line things up
        if self._can_rotate_neighbor_to_connect(neighbor):
            for x in range(4):
                if self.tiles_are_connected(neighbor):
                    break
                else:
                    neighbor.rotate()
                    if not self.is_locked():
                        self.rotate()
                        if self.tiles_are_connected(neighbor):
                            break
                        else:
                            self.rotate(num_rotations=3)
        if self.tiles_are_connected(neighbor):
            # TODO: allow for backtracking and unlocking tiles
            self.locked = True
            neighbor.locked = True
            return True
        return False


    ###################################################################
    def connect(self, neighbor):
        # orient neighbor with self, and return if successful
        if neighbor.is_empty():
            return False

        if self.tiles_are_connected(neighbor):
            return True

        elif self.is_gas_tank() and neighbor.is_pipe():
            return self._connect_tiles(neighbor)
        elif self.is_gas_tank() and neighbor.is_house():
            return self._connect_tiles(neighbor)
        elif self.is_pipe() and neighbor.is_pipe():
            return self._connect_tiles(neighbor)
        elif self.is_pipe() and neighbor.is_house():
            return self._connect_tiles(neighbor)
        return False

    ###################################################################
    def is_house(self):
        return self.tile_type in ('H',)

    ###################################################################
    def get_northern_neighbor(self):
        y = None
        if self.y == 0:
            y = self.board.height - 1
        else:
            y = self.y - 1
        return self.board.board[y][self.x]

    ###################################################################
    def get_eastern_neighbor(self):
        x = None
        if self.x == self.board.width:
            x = 0
        else:
            x = self.x + 1
        return self.board.board[self.y][x]

    ###################################################################
    def get_southern_neighbor(self):
        y = None
        if self.y == self.board.height:
            y = 0
        else:
            y = self.y + 1
        return self.board.board[y][self.x]

    ###################################################################
    def get_western_neighbor(self):
        x = None
        if self.x == 0:
            x = self.board.width - 1
        else:
            x = self.x - 1
        return self.board.board[self.y][x]

    ###################################################################
    def get_neighbors(self):
        return (
            self.get_northern_neighbor(), self.get_eastern_neighbor(),
            self.get_southern_neighbor(), self.get_western_neighbor()
        )

    ###################################################################
    def rotate(self, num_rotations=1):
        # always rotate clockwise
        for x in range(num_rotations):
            if self.orientation < 4:
                self.orientation += 1
            else:
                self.orientation = 1


#######################################################################
class MyBoard(object):
    ###################################################################
    def __init__(self, board_start):
        self.board = {}
        self.width = 7
        self.height = 10
        for y in range(self.height):
            for x in range(self.width):
                if y not in self.board:
                    self.board[y] = {}
                self.board[y][x] = None

        f = io.open(board_start)
        lines = f.readlines()
        f.close()
        y = 0
        for line in lines:
            x = 0
            for l in line.strip():
                self.board[y][x] = MyTile(x, y, l, self)
                x += 1
            y += 1

    ###################################################################
    def get_tile(self, x, y):
        return self.board[y][x]

    ###################################################################
    def find_starting_point(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x].is_gas_tank():
                    return self.board[y][x]

    ###################################################################
    def find_path(self, starting_tiles):
        continue_with = []
        for starting_tile in starting_tiles:
            neighbors = starting_tile.get_neighbors()
            for neighbor in neighbors:
                connected = starting_tile.connect(neighbor)
                if connected and neighbor not in starting_tile.connected_neighbors:
                    starting_tile.connected_neighbors.append(neighbor)
                # if connected and starting_tile not in neighbor.connected_neighbors:
                #     neighbor.connected_neighbors.append(starting_tile)
                if connected and neighbor.is_house():
                    # TODO: Verify path back to start
                    return  # Success
                if connected and neighbor not in continue_with:
                    continue_with.append(neighbor)
        if continue_with:
            self.find_path(continue_with)

    ###################################################################
    def solve(self):
        sp = self.find_starting_point()
        if sp:
            self.find_path([sp])

    ###################################################################
    def write_output_board_to_file(self, filename):
        # return a formatted, solved board in a file-like object
        f = io.open(filename, mode="w")
        for y in range(self.height):
            line = []
            for x in range(self.width):
                tile = self.board[y][x].get_readable_orientation()
                line.append(tile)
            if y < self.height - 1:
                line.append("\n")
            f.write(''.join(line))
        f.close()

#######################################################################
def solve_board(board_start, output_filename="board.png"):
    # Read in board
    my_board = MyBoard(board_start)

    # find solution
    my_board.solve()

    # Get solution to/from file
    filename = "my_solution_{}".format(os.path.basename(board_start))
    my_board.write_output_board_to_file(filename)
    solved_board = 'example_boards/board0_solution.txt'

    # construct board and print
    board = Board(board_start, solved_board)
    draw_board(board, output_filename)


#######################################################################
def main():
    parser = argparse.ArgumentParser("Solve a board in a particular state")
    parser.add_argument("board", help="filename for board")
    parser.add_argument("state", help="filename for a board's state")
    parser.add_argument("--output", default="board.png",
                        help="filename for output image. Default: board.png")
    args = parser.parse_args()
    solve_board(args.board, output_filename=args.output)


#######################################################################
if __name__ == "__main__":
    main()