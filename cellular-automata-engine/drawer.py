import gizeh

border_color = (0.5, 0.5, 0.5)
background_color = (0, 0, 0)


def make_cellular_automata_frame_generator(request, cell_size=15, border_width=1):
    generator = request.generator
    rows_count = request.rows
    columns_count = request.columns
    legend = request.legend

    surface_height = (rows_count * cell_size) + ( (rows_count - 1) * border_width )
    surface_width = (columns_count * cell_size) + ( (columns_count - 1) * border_width )
    surface_height_center = surface_height / 2
    surface_width_center = surface_width / 2

    def wrapper(t):
        generation = generator.next()

        surface = gizeh.Surface(width=surface_width, height=surface_height, bg_color=background_color)
        for row in range(rows_count):
            y = (row * cell_size) + (row * border_width)
            gizeh.rectangle(lx=surface_width, ly=border_width,
                            xy=(surface_width_center, y), fill=border_color).draw(surface)
        for column in range(columns_count):
            x = (column * cell_size) + (column * border_width)
            gizeh.rectangle(lx=border_width, ly=surface_height,
                            xy=(x, surface_height_center), fill=border_color).draw(surface)

        for x in range(columns_count):
            for y in range(rows_count):
                cell = generation[y][x]
                cell_color = legend[cell]
                cell_x = (cell_size * x) + (border_width * x) + (cell_size / 2)
                cell_y = (cell_size * y) + (border_width * y) + (cell_size / 2)
                gizeh.rectangle(lx=cell_size, ly=cell_size, xy=(cell_x, cell_y),
                                fill=cell_color).draw(surface)

        return surface.get_npimage()

    return wrapper
