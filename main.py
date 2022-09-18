#!/usr/bin/python3
import math
from model_reader import Stl, Triangle, Vec3, Wavefront

if __name__ == '__main__':
    wf = Wavefront.read("wavefront.obj")
    stl = wf.stl()

    print(wf)
    print(wf.stl())

    stl.write("model.edit.stl")