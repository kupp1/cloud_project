import json

from generators import LifeGenerator, WireWorldGenerator

type_param = "type"
generation_param = "map"
fps_param = "fps"
duration_param = "duration"
cell_size_param = "cell_size"
requestor_param = "requestor"
format_param = "format"
chat_id_param = "chat_id"

life_parse_legend = {"O": 1, ".": 0}
life_draw_legend = {
    0: (0, 0, 0),
    1: (239 / 255, 83 / 255, 73 / 255)
}

ww_parse_legend = {"H": "H", "t": "t", " ": " ", ".": "."}
ww_draw_legend = {
    "H": (0, 0.5, 1),
    "t": (1, 0.25, 0),
    " ": (0, 0, 0),
    ".": (1, 215 / 255, 0)
}


class Request:
    def __init__(self, generator, request, legend, rows, columns):
        self.generator = generator
        self.type = request[type_param]
        self.fps = request[fps_param]
        self.duration = request[duration_param]
        self.cell_size = request[cell_size_param]
        self.legend = legend
        self.rows = rows
        self.columns = columns
        self.requestor = request[requestor_param]
        self.format = request[format_param]
        self.chat_id = request[chat_id_param]


def parse_generation(generation, legend):
    rows = len(generation)
    columns = len(generation[0])
    print(rows, columns)
    parsed_generation = [[None] * columns for _ in range(rows)]

    for x in range(columns):
        for y in range(rows):
            old_cell_value = generation[y][x]
            new_cell_value = legend[old_cell_value]
            parsed_generation[y][x] = new_cell_value

    return parsed_generation, rows, columns


def create_request(request):
    if request[type_param] == "life":
        generation, rows, columns = parse_generation(request[generation_param], life_parse_legend)
        generator = LifeGenerator(generation)
        draw_legend = life_draw_legend
    elif request[type_param] == "ww":
        generation, rows, columns = parse_generation(request[generation_param], ww_parse_legend)
        generator = WireWorldGenerator(generation)
        draw_legend = ww_draw_legend

    return Request(generator, request, draw_legend, rows, columns)
