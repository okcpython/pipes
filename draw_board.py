import argparse
from PIL import Image


ORIENTATIONS = range(4)
NORTH, EAST, SOUTH, WEST = ORIENTATIONS
SIZE = 322, 460
WIDTH, HEIGHT = SIZE
TILE_SIZE = 46

ORIENTATION_NAME_MAP = {
    NORTH: "north",
    EAST: "east",
    SOUTH: "south",
    WEST: "west"}

ORIENTATION_LETTER_MAP = {
    "N": NORTH,
    "E": EAST,
    "S": SOUTH,
    "W": WEST}

ON_OFF_MAP = {
    True: "on",
    False: "off"}


#######################################################################
def get_opposite_orientation(orientation):
    return (orientation + 2) % len(ORIENTATIONS)


########################################################################
def make_image_map():
    image_map = {"_": Image.open("images/blank.png"),
                 ("2", NORTH): Image.open("images/gas_north_east.png"),
                 ("2", EAST): Image.open("images/gas_south_east.png"),
                 ("2", SOUTH): Image.open("images/gas_south_west.png"),
                 ("2", WEST): Image.open("images/gas_north_west.png")}

    for orientation in ORIENTATIONS:
        orientation_name = ORIENTATION_NAME_MAP[orientation]
        opposite_name = ORIENTATION_NAME_MAP[get_opposite_orientation(orientation)]
        image_map["1", orientation] = Image.open("images/gas_%s.png" % orientation_name)
        image_map["3", orientation] = Image.open("images/gas_not_%s.png" % opposite_name)
        for on in ["on", "off"]:
            filename_template = "images/%s_{}_{}.png".format(on, orientation_name)
            for letter in "itlh":
                im = Image.open(filename_template % letter)
                image_map[letter.upper(), orientation_name, on] = im
    return image_map


########################################################################
class Tile(object):
    def __init__(self, tile="_", orientation=None):
        self.tile = tile
        self.orientation = orientation


########################################################################
class Board(object):
    ####################################################################
    def __init__(self, board_file, solution_file):
        self.data = [[Tile() for x in range(WIDTH)] for y in range(HEIGHT)]
        for y, line in enumerate(open(board_file)):
            line = line.strip()
            for x, character in enumerate(line):
                self[x, y].tile = character
        for y, line in enumerate(open(solution_file)):
            line = line.strip()
            for x, character in enumerate(line):
                if character in ORIENTATION_LETTER_MAP:
                    self[x, y].orientation = ORIENTATION_LETTER_MAP[character]

    ####################################################################
    def __getitem__(self, item):
        x, y = item
        return self.data[x][y]

    ####################################################################
    def __setitem__(self, key, value):
        x, y = key
        self.data[x][y] = value


########################################################################
def draw_board(board, filename):
    white = (255, 255, 255)
    im = Image.new("RGB", SIZE, white)
    image_map = make_image_map()

    for y in range(10):
        for x in range(7):
            item = board[x, y]
            if item.tile == "_":
                image = image_map["_"]
            elif item.tile in ["1", "2", "3"]:
                image = image_map[item.tile, item.orientation]
            else:
                orientation_name = ORIENTATION_NAME_MAP[item.orientation]
                image = image_map[item.tile, orientation_name, "off"]
            im.paste(image, (x*TILE_SIZE, y*TILE_SIZE))

    im.save(filename)


#######################################################################
def main():
    parser = argparse.ArgumentParser("Draw a board in a particular state")
    parser.add_argument("board", help="filename for board")
    parser.add_argument("state", help="filename for a board's state")
    parser.add_argument("--output", default="board.png",
                        help="filename for output image. Default: board.png")
    args = parser.parse_args()
    board = Board(args.board, args.state)
    draw_board(board, args.output)


#######################################################################
if __name__ == "__main__":
    main()
