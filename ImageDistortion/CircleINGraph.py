from PIL import Image, ImageDraw
import pyautogui


def generate_checkerboard_with_circle(height):
    """
    生成一个高度为输入参数的黑白棋盘格图片，并在其中裁剪直径为高度的圆，圆外部分填充黑色。

    参数:
    height: 图片的高度（正方形图片，宽度与高度相同）
    """
    # 图片分辨率：高度为输入的高度，宽度也设置为高度（正方形图片）
    image_size = height
    grid_size = image_size // 10  # 每个方格的大小（高度/10）

    # 创建图片，设置背景为白色
    image = Image.new("RGB", (image_size, image_size), "white")
    draw = ImageDraw.Draw(image)

    # 绘制黑白相间的方格
    for row in range(10):  # 10 行
        for col in range(10):  # 10 列
            # 计算每个方格的左上角和右下角坐标
            top_left = (col * grid_size, row * grid_size)
            bottom_right = ((col + 1) * grid_size, (row + 1) * grid_size)

            # 黑白交替填充
            if (row + col) % 2 == 0:  # 奇偶决定填充颜色
                draw.rectangle([top_left, bottom_right], fill="black")

    # 创建一个新的图层，用于绘制圆形遮罩
    mask = Image.new("L", (image_size, image_size), 0)
    mask_draw = ImageDraw.Draw(mask)

    # 绘制圆形遮罩（圆心为图片中心，直径等于图片高度）
    center = (image_size // 2, image_size // 2)
    radius = image_size // 2
    mask_draw.ellipse([center[0] - radius, center[1] - radius,
                       center[0] + radius, center[1] + radius], fill=255)

    # 将圆形遮罩应用到棋盘格图片上
    final_image = Image.new("RGB", (image_size, image_size), "black")  # 创建黑色背景
    final_image.paste(image, (0, 0), mask)  # 使用遮罩粘贴圆形区域

    # 保存和显示图片
    # final_image.save("checkerboard_with_circle.png")
    # final_image.show()
    return final_image


def main():
    # 获取屏幕分辨率
    # screen_width, screen_height = pyautogui.size()
    # print(f"屏幕宽度: {screen_width} 像素, 屏幕高度: {screen_height} 像素")
    screen_width = 4096
    screen_height = 4096
    # 生成带圆形裁剪的棋盘格图像
    img = generate_checkerboard_with_circle(screen_height)

    img.show()
    img.save("chessboard_" + str(screen_width) + '_' + str(screen_height) + ".jpg")



if __name__ == "__main__":
    main()
