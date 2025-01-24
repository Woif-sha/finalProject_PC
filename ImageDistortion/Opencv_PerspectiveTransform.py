import cv2
import numpy as np

# 读取有失真的图像（假设图像名为distorted_image.jpg）
img = cv2.imread("black_white_test.jpg")
rows, cols, _ = img.shape
# print(rows,cols)
# 定义源图像（有失真的图像）上的四个点，这里假设是一个简单的梯形（扇形可以近似看作梯形）
# 这些点需要根据实际图像失真情况调整，例如通过手动选择或自动检测
src_points = np.float32([[0, 0], [cols - 1, 0], [cols - 1, rows - 1], [0, rows - 1]])   #顺序：顺时针
# 定义目标图像（矫正后的矩形图像）上对应的四个点
dst_points = np.float32([[0, 50], [cols - 1, 50], [200, rows - 1], [56, rows - 1]])
# 计算透视变换矩阵
M = cv2.getPerspectiveTransform(src_points, dst_points)
# 应用透视变换
corrected_img = cv2.warpPerspective(img, M, (cols, rows))

# 显示原始图像和矫正后的图像
# cv2.imshow("Original Image", img)
# cv2.imshow("Corrected Image", corrected_img)
cv2.imwrite("cv_correct.jpg",corrected_img)
cv2.waitKey(0)
cv2.destroyAllWindows()