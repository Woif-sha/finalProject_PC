from PIL import Image, ImageDraw


def fill_circle_with_image(image_path, circle_size=(200, 200),save=False):
    """
    将给定图片拉伸变换后填充到指定大小的圆形中，并保存结果。
    参数:
    image_path (str): 原始图片的文件路径
    output_path (str): 处理后图片保存的文件路径
    circle_size (tuple): 圆形的尺寸（宽，高），默认是(200, 200)
    """
    # 打开原始图片
    img = Image.open(image_path).convert("RGBA")
    width, height = circle_size
    # 创建一个透明的新图像，大小与目标圆形一致
    circle_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(circle_img)
    # 在新图像上绘制圆形，这里填充白色作为示例，可以根据需要调整
    draw.ellipse((0, 0, width, height), fill=(255, 255, 255, 255))

    # 获取图片原始宽高
    orig_width, orig_height = img.size
    # 计算宽高缩放比例，以确保图片能尽量布满圆形，这里取宽高比例较大的那个缩放比例来进行拉伸
    scale = max(width / orig_width, height / orig_height)
    new_width = int(orig_width * scale)
    new_height = int(orig_height * scale)
    # 对原始图片按计算的比例进行缩放
    img = img.resize((new_width, new_height))

    # 计算图片在圆形区域中的放置位置（居中放置）
    offset_x = (new_width - width) // 2
    offset_y = (new_height - height) // 2
    img = img.crop((offset_x, offset_y, offset_x + width, offset_y + height))

    # 使用圆形遮罩来裁剪图片，通过alpha通道合成
    img.putalpha(circle_img.split()[-1])
    circle_img.paste(img, (0, 0), img)

    circle_img.show()
    if save:
        circle_img.save(image_path + '_circle.jpg')

if __name__ == '__main__':
    image_path = "result_concat_res.jpg"  # 替换为你的实际图片路径
    fill_circle_with_image(image_path)
