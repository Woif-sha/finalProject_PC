import cv2
import math
import numpy as np
from PIL import Image


def main(para = 1,offset = 0):
    filename = "black_white.jpg"  # 图像路径
    img = cv2.imread(filename)
    drcimg = np.zeros((img.shape[0], img.shape[1], 3), dtype=np.uint8)

    lenscenter = (img.shape[1] // 2 , img.shape[0] // 2 + offset)  # 镜头中心在图像中的位置
    cv2.circle(img, lenscenter, 5, (0,0,255), -1)
    for row in range(img.shape[0]):
        for col in range(img.shape[1]):
            r = math.sqrt((row - lenscenter[1]) ** 2 + (col - lenscenter[0]) ** 2) * para
            s = 0.9998 - 4.2932 * math.pow(10, -4) * r + 3.4327 * math.pow(10, -6) * math.pow(r, 2) - 2.8526 * math.pow(10, -9) * math.pow(
                r, 3) + 9.8223 * math.pow(10, -13) * math.pow(r, 4)  # 比例
            mCorrectPoint = ((col - lenscenter[0]) / s * 1.35 + lenscenter[0], (row - lenscenter[1]) / s * 1.35 + lenscenter[1])
            # 越界判断
            if mCorrectPoint[1] < 0 or mCorrectPoint[1] >= img.shape[0] - 1:
                continue
            if mCorrectPoint[0] < 0 or mCorrectPoint[0] >= img.shape[1] - 1:
                continue
            src_a = (int(mCorrectPoint[0]), int(mCorrectPoint[1]))
            src_b = (src_a[0] + 1, src_a[1])
            src_c = (src_a[0], src_a[1] + 1)
            src_d = (src_a[0] + 1, src_a[1] + 1)
            distance_to_a_x = mCorrectPoint[0] - src_a[0]  # 在原图像中与a点的水平距离
            distance_to_a_y = mCorrectPoint[1] - src_a[1]  # 在原图像中与a点的垂直距离

            drcimg[row, col][0] = (
                    img[src_a[1], src_a[0]][0] * (1 - distance_to_a_x) * (1 - distance_to_a_y) +
                    img[src_b[1], src_b[0]][0] * distance_to_a_x * (1 - distance_to_a_y) +
                    img[src_c[1], src_c[0]][0] * distance_to_a_y * (1 - distance_to_a_x) +
                    img[src_d[1], src_d[0]][0] * distance_to_a_y * distance_to_a_x
            )
            drcimg[row, col][1] = (
                    img[src_a[1], src_a[0]][1] * (1 - distance_to_a_x) * (1 - distance_to_a_y) +
                    img[src_b[1], src_b[0]][1] * distance_to_a_x * (1 - distance_to_a_y) +
                    img[src_c[1], src_c[0]][1] * distance_to_a_y * (1 - distance_to_a_x) +
                    img[src_d[1], src_d[0]][1] * distance_to_a_y * distance_to_a_x
            )
            drcimg[row, col][2] = (
                    img[src_a[1], src_a[0]][2] * (1 - distance_to_a_x) * (1 - distance_to_a_y) +
                    img[src_b[1], src_b[0]][2] * distance_to_a_x * (1 - distance_to_a_y) +
                    img[src_c[1], src_c[0]][2] * distance_to_a_y * (1 - distance_to_a_x) +
                    img[src_d[1], src_d[0]][2] * distance_to_a_y * distance_to_a_x
            )


    # cv2.imshow("after", drcimg)
    cv2.imwrite("reduction.jpg", drcimg)
    image = Image.open("reduction.jpg")
    image.show()


if __name__ == "__main__":
    main(para = 2.5,offset = 80)