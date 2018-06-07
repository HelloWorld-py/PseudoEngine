from PseudoEngine.Graphics.renderable import Renderable as _Renderable


class Renderer:
    """This class is used to do all of the heavy lifting of the rendering. It is all done in a separate process"""
    def __init__(self, vertex_shader, fragment_shader, window):
        self.__vertex_shader = vertex_shader
        self.__fragment_shader = fragment_shader
        self.__window = window

    def push(self, renderable):
        pass

    def flush(self):
        pass

    def clear(self):
        pass
