

class Renderable:
    _vertexData = None


class Sprite(Renderable):
    def __init__(self, x1, y1, x2, y2):
        self._vertexData = [x1, y1, x2, y2]