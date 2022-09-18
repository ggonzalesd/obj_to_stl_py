#!/usr/bin/python3
from dataclasses import dataclass
from io import BufferedReader, BufferedWriter
import sys, struct, numpy as np

@dataclass
class Vec3:
    x: float
    y: float
    z: float

    @property
    def array(self):
        return np.array([self.x, self.y, self.z])

    @classmethod
    def read(cls, file: BufferedReader):
        return Vec3(*struct.unpack("fff", file.read(12)))
    
    def write(self, file: BufferedWriter):
        file.write(struct.pack("fff", self.x, self.y, self.z))

@dataclass
class Triangle:
    normal: Vec3
    vertex: list[Vec3]
    attrib: int

    @classmethod
    def generate_from_vectors(cls, v1:Vec3, v2:Vec3, v3:Vec3, attrib:int=0):
        normal = np.cross(v2.array - v1.array, v3.array - v1.array)
        normal = Vec3(*(normal / np.linalg.norm(normal)))
        return Triangle(normal, [v1, v2, v3], attrib)

    @classmethod
    def read(cls, file: BufferedReader):
        normal = Vec3.read(file)
        vertex = [ Vec3.read(file) for _ in range(3) ]
        (attrib,) = struct.unpack('H', file.read(2))
        return Triangle(normal, vertex, attrib)
    
    def write(self, file: BufferedWriter):
        self.normal.write(file)
        for vertex in self.vertex:
            vertex.write(file)
        file.write(struct.pack('H', self.attrib))

@dataclass
class Stl:
    header: str
    triangles: list[Triangle]

    def add_triangle(self, v1:Vec3, v2:Vec3, v3:Vec3, attrib:int=0):
        self.triangles.append( Triangle.generate_from_vectors(v1, v2, v3, attrib) )

    def add_triangle_normal(self, n:Vec3, v1:Vec3, v2:Vec3, v3:Vec3, attrib:int=0):
        self.triangles.append( Triangle(n, [v1, v2, v3], attrib) )

    @classmethod
    def generate_empty(cls):
        return Stl("Python " + sys.version, [])

    @classmethod
    def read(cls, filename: str):

        with open(filename, "rb") as f:
            string = f.read(80).decode()
            (numbers,) = struct.unpack('I', f.read(4))
            triangles = [ Triangle.read(f) for _ in range(numbers) ]

        return Stl(string, triangles)
    
    def write(self, filename):

        with open(filename, "wb") as f:
            header_bytes = self.header[:80].encode()
            header_bytes = header_bytes + b'\x00' * (80 - len(header_bytes))
            f.write(header_bytes)
            f.write(struct.pack('I', len(self.triangles)))
            for triangle in self.triangles:
                triangle.write(f)
    
    def __repr__(self):
        return f"Stl('{self.header}', Triangles({len(self.triangles)}))"


@dataclass
class Wavefront:
    positions: list[list[float]]
    normals: list[list[float]]
    texcoords: list[list[float]]
    faces: list[list[list[int]]]

    def __repr__(self):
        return f"Wavefront(v:{len(self.positions)}, vn:{len(self.normals)}, vt:{len(self.texcoords)}, f:{len(self.faces)})"

    @classmethod
    def read(cls, filename):
        positions = []
        normals = []
        texcoords = []
        faces = []

        with open(filename) as f:
            
            for line in f.readlines():
                line = line.split(" ")
                if len(line) < 1:
                    continue
                
                if line[0] == 'v':
                    p = list(map(float, line[1:]))
                    positions.append([p[0], p[2], p[1]])
                elif line[0] == 'vn':
                    n = list(map(float, line[1:]))
                    normals.append([n[0], n[2], n[1]])
                elif line[0] == 'vt':
                    texcoords.append(list(map(float, line[1:])))
                elif line[0] == 'f':
                    line = line[1:]
                    vertex = [ [int(x)-1 for x in a.split("/")] for a in line ]
                    if len(line) == 3:
                        faces.append(vertex[::-1])
                    elif len(line) == 4:
                        faces.append([vertex[0], vertex[3], vertex[1]])
                        faces.append([vertex[2], vertex[1], vertex[3]])
        return Wavefront(positions, normals, texcoords, faces)

    def stl(self) -> Stl:
        stl = Stl.generate_empty()

        for face in self.faces:
            face = list(zip(*face))
            v1, v2, v3 = [Vec3(*self.positions[a]) for a in face[0]]
            n = Vec3(*self.normals[face[2][0]])

            stl.add_triangle_normal(n, v1, v2, v3)

        return stl
