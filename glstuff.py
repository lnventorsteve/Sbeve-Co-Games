from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import ctypes


data_type_vertex = np.dtype({
    'names':   [       'x',        'y',        'z',   'color'],
    'formats': [np.float32, np.float32, np.float32, np.uint32],
    'offsets': [         0,          4,          8,        12],
    'itemsize': 16})

class Triangle:
    def __init__(self):
        self.vertices = [
            -0.5, -0.5, 0.0, 1.0, 0.0, 0.0,
            0.5, -0.5, 0.0, 0.0, 1.0, 0.0,
            0.0, 0.5, 0.0, 0.0, 0.0, 1.0]

        self.vertices = np.array(self.vertices,dtype=np.float32)

        self.vertex_count = 3

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER,self.vao)
        glBufferData(GL_ARRAY_BUFFER,self.vertices.nbytes,self.vertices,GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0,3,GL_FLOAT,GL_FALSE,24,ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1,3,GL_FLOAT,GL_FALSE,24,ctypes.c_void_p(12))

    def destroy(self):
        glDeleteVertexArrays(1,[self.vao])
        glDeleteBuffers(1,[self.vbo])

def create_shader_program(vertex_filepath: str, fragment_filepath: str) -> int:
    """
        Compile and link a shader program.

        Parameters:

            vertex_filepath: filepath to the vertex module source code.

            fragment_filepath: filepath to the fragment module source code.

        returns:

            A handle to the created shader program.
    """

    vertex_module = create_shader_module(vertex_filepath, GL_VERTEX_SHADER)
    fragment_module = create_shader_module(fragment_filepath, GL_FRAGMENT_SHADER)

    shader = compileProgram(vertex_module, fragment_module)

    glDeleteShader(vertex_module)
    glDeleteShader(fragment_module)

    return shader

def create_shader_module(filepath: str, module_type: int) -> int:
    """
        Compile a shader module.

        Parameters:

            filepath: filepath to the module source code.

            module_type: indicates which type of module to compile.

        returns:

            A handle to the created shader module.
    """

    source_code = ""
    with open(filepath, "r") as file:
        source_code = file.readlines()

    return compileShader(source_code, module_type)


def createShader():
    with open("Shaders/vertex.txt", "r") as f:
        vertex_src = f.readlines()
    with open("Shaders/fragment.txt", "r") as f:
        fragment_src = f.readlines()

    shader = compileProgram(compileShader(vertex_src, GL_VERTEX_SHADER), compileShader(fragment_src, GL_FRAGMENT_SHADER))
    return shader


def build_triangle_mesh() -> tuple[tuple[int], int]:
    """
        Builds a mesh representing a triangle.

        Returns:

            vbos, vao. Where vbos is a tuple of the vertex buffers, and vao is the
            vertex array.
    """

    position_data = np.array(
        (-0.75, -0.75, 0.0,
         0.75, -0.75, 0.0,
         0.0, 0.75, 0.0), dtype=np.float32)

    color_data = np.array((0, 1, 2), dtype=np.uint32)

    # generate one vertex array to hold everything.
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    # position buffer
    position_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, position_buffer)

    # attribute 0: position
    attribute_index = 0
    size = 3
    stride = 12
    offset = 0
    glVertexAttribPointer(
        attribute_index, size, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(offset))
    glEnableVertexAttribArray(attribute_index)

    # upload positions to GPU
    glBufferData(GL_ARRAY_BUFFER, position_data.nbytes, position_data, GL_STATIC_DRAW)

    # color buffer
    color_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, color_buffer)

    # attribute 1: color
    attribute_index = 1
    size = 1
    stride = 4
    offset = 0
    glVertexAttribIPointer(
        attribute_index, size, GL_UNSIGNED_INT, stride, ctypes.c_void_p(offset))
    glEnableVertexAttribArray(attribute_index)

    # upload colors to GPU
    glBufferData(GL_ARRAY_BUFFER, color_data.nbytes, color_data, GL_STATIC_DRAW)

    return ((position_buffer, color_buffer), vao)


def build_triangle_mesh2() -> tuple[int, int]:
    """
        Builds a mesh representing a triangle.

        Returns:

            vbo, vao.
    """

    vertex_data = np.zeros(3, dtype=data_type_vertex)
    vertex_data[0] = (-0.75, -0.75, 0.0, 0)
    vertex_data[1] = (0.75, -0.75, 0.0, 1)
    vertex_data[2] = (0.0, 0.75, 0.0, 2)

    # generate one vertex array to hold everything.
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    # vertex buffer
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)

    # attribute 0: position
    attribute_index = 0
    size = 3
    offset = 0
    glVertexAttribPointer(
        attribute_index, size, GL_FLOAT, GL_FALSE,
        data_type_vertex.itemsize, ctypes.c_void_p(offset))
    glEnableVertexAttribArray(attribute_index)

    # attribute 1: color
    attribute_index = 1
    size = 1
    offset = 12
    glVertexAttribIPointer(
        attribute_index, size, GL_UNSIGNED_INT,
        data_type_vertex.itemsize, ctypes.c_void_p(offset))
    glEnableVertexAttribArray(attribute_index)

    # upload vertices to GPU
    glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

    return (vbo, vao)


def build_quad_mesh() -> tuple[int, int, int]:
    """
        Builds a mesh representing a triangle.

        Returns:

            ebo, vbo, vao.
    """

    vertex_data = np.zeros(4, dtype=data_type_vertex)
    vertex_data[0] = (-0.75, -0.75, 0.0, 0)
    vertex_data[1] = (0.75, -0.75, 0.0, 1)
    vertex_data[2] = (0.75, 0.75, 0.0, 2)
    vertex_data[3] = (-0.75, 0.75, 0.0, 1)

    index_data = np.array((0, 1, 2, 2, 3, 0), dtype=np.ubyte)

    # generate one vertex array to hold everything.
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    # vertex buffer
    vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)

    # attribute 0: position
    attribute_index = 0
    size = 3
    offset = 0
    glVertexAttribPointer(
        attribute_index, size, GL_FLOAT, GL_FALSE,
        data_type_vertex.itemsize, ctypes.c_void_p(offset))
    glEnableVertexAttribArray(attribute_index)

    # attribute 1: color
    attribute_index = 1
    size = 1
    offset = 12
    glVertexAttribIPointer(
        attribute_index, size, GL_UNSIGNED_INT,
        data_type_vertex.itemsize, ctypes.c_void_p(offset))
    glEnableVertexAttribArray(attribute_index)

    # upload vertices to GPU
    glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

    # element buffer
    ebo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)

    # upload indices to GPU
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_data.nbytes, index_data, GL_STATIC_DRAW)

    return (ebo, vbo, vao)