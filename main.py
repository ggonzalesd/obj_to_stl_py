#!/usr/bin/python3
import math
from model_reader import Wavefront

if __name__ == '__main__':
    wf = Wavefront.read("models/obj/wavefront.obj")
    stl = wf.stl()

    print("OBJ File:", wf)
    print("STL File:", stl)

    stl.write("models/stl/model.edit.stl")