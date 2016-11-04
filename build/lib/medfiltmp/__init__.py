__author__ = 'kyue'

import numpy as np
import ctypes
from multiprocessing import Process, Array
from scipy import ndimage


def child(x, y, z, shape, footprint, stepx, stepy, stepz, combined, finalData):

    Startx = x*stepx;
    Endx = (x+1)*stepx;
    Starty = y*stepy;
    Endy = (y+1)*stepy;
    Startz = z*stepz;
    Endz = (z+1)*stepz;

    if(Startx >= shape[0] and Starty >= shape[1] and Startz >= shape[2]):
        return 0
    if(Endx > shape[0]):
        Endx = shape[0];
    if(Endy > shape[1]):
        Endy = shape[1];
    if(Endz > shape[2]):
        Endz = shape[2];

    xoffset = footprint.shape[0]
    yoffset = footprint.shape[1]
    zoffset = footprint.shape[2]
    # Extend the filter
    res = ndimage.median_filter(combined[Startx:Endx+2*xoffset,Starty:Endy+2*yoffset,Startz:Endz+2*zoffset],footprint=footprint)

    finalData[Startx:Endx,Starty:Endy,Startz:Endz] = res[xoffset:xoffset+Endx-Startx,yoffset:yoffset+Endy-Starty,zoffset:zoffset+Endz-Startz]

    return 1

def median_filter(proj, footprint = np.ones((3, 3, 3))):

    # filter_size = footprint
    # loffset = filter_size
    # roffset = filter_size

    xoffset = footprint.shape[0]
    yoffset = footprint.shape[1]
    zoffset = footprint.shape[2]

    combined = np.lib.pad(proj, ((xoffset, xoffset), (yoffset, yoffset),(zoffset, zoffset)), 'symmetric')

    # step here is the step size for the filter
    stepx = int(proj.shape[0]/3)
    stepy = int(proj.shape[1]/3)
    stepz = int(proj.shape[2]/3)
    workjob = []

    procsx=int(proj.shape[0]/stepx)+1
    procsy=int(proj.shape[1]/stepy)+1
    procsz=int(proj.shape[2]/stepz)+1

    sharedArray = Array(ctypes.c_double, proj.shape[0]*proj.shape[1]*proj.shape[2], lock=False)
    sharedNpArray = np.frombuffer(sharedArray, dtype=ctypes.c_double)
    finalData = sharedNpArray.reshape(proj.shape[0],proj.shape[1],proj.shape[2])

    # using multiprocessing to do the 3d filter
    for i in range(0,procsx):
        for j in range(0,procsy):
            for p in range(0,procsz):
                        process = Process(target=child, args = (i, j, p, proj.shape, footprint, stepx, stepy, stepz, combined, finalData))
                        workjob.append(process)

    for j in workjob:
        j.start()

    for j in workjob:
        j.join()

    return finalData

# if __name__ == '__main__':
#
#     filter_size = 3
#     lensize = 320
#
#     imsizex =lensize # image size for the input
#     imsizey = lensize
#     prjsize=lensize
#
#     combinedMed = np.zeros(shape=(prjsize,imsizey,imsizex), dtype=np.float32)
#     for step in range (5,5+prjsize):
#         im_noise = np.arange( 10, imsizey*imsizex*step+10, step ).reshape(imsizey, imsizex)
#         im_noise = im_noise.astype(np.float32)
#         combinedMed[step-5]=im_noise
#
#     proj = combinedMed
#
#
#     finalData = median_filter(proj, footprint=np.ones((filter_size, filter_size, filter_size)))
#
#     sfinaldata = ndimage.median_filter(proj,footprint=np.ones((filter_size, filter_size, filter_size)))
#
#     print("the result is ",sfinaldata-finalData)