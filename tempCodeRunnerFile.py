self.map[self.Unfold(row, col)].h = abs(row - self.end[0]) + abs(
            col - self.end[0]
        )