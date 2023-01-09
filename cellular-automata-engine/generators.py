class LifeGenerator:
    def __init__(self, curr_gen):
        self.curr_gen = curr_gen
        self.rows = len(curr_gen)
        self.columns = len(curr_gen[0])

    def next(self):
        next_gen = [[0] * self.columns for _ in range(self.rows)]

        for x in range(self.columns):
            for y in range(self.rows):
                env = 0
                for dx in range(-1, 2):
                    for dy in range(-1, 2):
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if nx < 0 or nx >= self.columns or ny < 0 or ny >= self.rows:
                            continue
                        env += self.curr_gen[ny][nx]

                if not self.curr_gen[y][x] and env == 3:
                    next_gen[y][x] = 1
                if self.curr_gen[y][x] and env in (2, 3):
                    next_gen[y][x] = 1

        self.curr_gen = next_gen
        return next_gen


class WireWorldGenerator:
    def __init__(self, curr_gen):
        self.head, self.tail, self.conductor, self.empty = self.allstates = 'Ht. '

        self.curr_gen = curr_gen
        self.rows = len(curr_gen)
        self.columns = len(curr_gen[0])

    def newcell(self, x, y):
        istate = self.curr_gen[y][x]
        assert istate in self.allstates, 'Wireworld cell set to unknown value "%s"' % istate

        if istate == self.head:
            ostate = self.tail
        elif istate == self.tail:
            ostate = self.conductor
        elif istate == self.empty:
            ostate = self.empty
        else:  # istate == conductor
            n = 0
            for dx,dy in ( (-1,-1), (-1,+0), (-1,+1),
                           (+0,-1),          (+0,+1),
                           (+1,-1), (+1,+0), (+1,+1) ):
                nx, ny = x + dx, y + dy

                if nx < 0 or nx >= self.columns or ny < 0 or ny >= self.rows:
                    continue

                if self.curr_gen[ny][nx] == self.head:
                    n += 1
            ostate = self.head if 1 <= n <= 2 else self.conductor
        return ostate

    def next(self):
        'compute next generation of wireworld'
        newworld = [["-"] * self.columns for _ in range(self.rows)]
        for x in range(self.columns):
            for y in range(self.rows):
                newworld[y][x] = self.newcell(x, y)
        self.curr_gen = newworld
        return self.curr_gen
