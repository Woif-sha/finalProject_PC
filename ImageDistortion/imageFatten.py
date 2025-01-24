#author: FarryNiu
#https://niuzifan.blog.csdn.net/article/details/108394740
import cv2
import numpy as np
from PIL import Image

img = cv2.imread('black_white.jpg')
rows = img.shape[0]
cols = img.shape[1]
blank = np.zeros_like(img)
# blank = np.zeros((4000,4000,3))
#圆心定为图片中心
center_x = int(rows / 2)
center_y = int(cols / 2)
#假设球的半径
r = int(((rows**2+cols**2)**0.5)/2) + 20
#假设映射平面位于 z = r 处
pz = r
for x in range(rows):
    ox = x
    x = x - center_x
    for y in range(cols):
        oy = y
        y = y - center_y
        z = (r*r - x*x - y*y)**0.5
        #假设光源点为(0,0,2r)
        k = (pz - 2*r)/(z - 2*r)
        px = int(k*x)
        py = int(k*y)
        px = px + center_x
        py = py + center_y
        blank[px, py, :] = img[ox , oy ,:]
cv2.imshow('show.jpg',blank)
cv2.waitKey(0)
# cv2.imwrite("fatten.jpg", blank)
#
# image = Image.open("fatten.jpg")
# image.show()