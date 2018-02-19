__author__ = 'kyue'


import medfiltmp
from scipy import ndimage
import numpy as np
import ctypes
from multiprocessing import Process, Array

if __name__ == '__main__':

    filter_size = 3
    lensize = 320

    imsizex =lensize # image size for the input
    imsizey = lensize
    prjsize=lensize
    
    #create a 3D test array
    combinedMed = np.zeros(shape=(prjsize,imsizey,imsizex), dtype=np.float32)
    for step in range (5,5+prjsize):
        im_noise = np.arange( 10, imsizey*imsizex*step+10, step ).reshape(imsizey, imsizex)
        im_noise = im_noise.astype(np.float32)
        combinedMed[step-5]=im_noise

    proj = combinedMed

    #median_filter in medfiltmp package
    finalData = medfiltmp.median_filter(proj, footprint=np.ones((filter_size, filter_size, filter_size)))
    
    #median_filter in ndimage package
    sfinaldata = ndimage.median_filter(proj,footprint=np.ones((filter_size, filter_size, filter_size)))
    
    #compare the result of median_filter from medfiltmp package and ndimage package.
    print("the result is ",sfinaldata-finalData)
