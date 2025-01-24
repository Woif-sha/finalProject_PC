import cv2
import numpy as np
from PIL import Image


def barrel_distortion(image, k=0.001, center=None):
    """
    对输入图像进行桶形畸变处理

    参数:
    image: 输入的图像（numpy数组形式，例如通过cv2.imread读取的图像）
    k: 畸变系数，控制桶形畸变的程度，正值表示桶形畸变，值越大畸变越明显，可根据实际需求调整
    center: 畸变中心坐标，默认为图像中心，如果指定则以指定坐标为中心进行畸变，格式为 (x, y)

    返回:
    经过桶形畸变处理后的图像
    """
    height, width = image.shape[:2]

    if center is None:
        center = (width // 2, height // 2)

    # 构建映射矩阵，用于存储目标坐标
    map_x = np.zeros((height, width), dtype=np.float32)
    map_y = np.zeros((height, width), dtype=np.float32)

    for y in range(height):
        for x in range(width):
            # 计算当前像素点相对于中心的坐标偏移量
            dx = x - center[0]
            dy = y - center[1]

            # 计算原始的极坐标半径
            r = np.sqrt(dx * dx + dy * dy)

            # 根据桶形畸变模型计算新的极坐标半径
            new_r = r * (1 + k * r * r)

            # 根据新半径和原始角度计算新的坐标偏移量
            theta = np.arctan2(dy, dx)
            new_dx = new_r * np.cos(theta)
            new_dy = new_r * np.sin(theta)

            # 计算畸变后的坐标
            map_x[y, x] = new_dx + center[0]
            map_y[y, x] = new_dy + center[1]

    # 应用重映射实现畸变效果
    distorted_image = cv2.remap(image, map_x, map_y, cv2.INTER_LINEAR)

    return distorted_image

if __name__ == '__main__':

    # 示例用法
    image_path = "black_white.jpg"
    img = cv2.imread(image_path)
    # 进行桶形畸变处理，这里设置畸变系数k为0.001，可自行调整该值改变畸变程度
    distorted_img = barrel_distortion(img, k=0.00006)
    cv2.imwrite("distorted_image.jpg", distorted_img)


    image = Image.open("distorted_image.jpg")
    image.show()
