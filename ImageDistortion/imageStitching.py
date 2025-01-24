from PIL import Image

def combine_images(image1_path, image2_path):
    # 打开第一张图像
    img1 = Image.open(image1_path)
    width1, height1 = img1.size
    # 确定第一张图像要截取的上半部分范围并截取
    upper_part1 = img1.crop((0, 0, width1, height1 // 2))

    # 打开第二张图像
    img2 = Image.open(image2_path)
    width2, height2 = img2.size
    # 确定第二张图像要截取的下半部分范围并截取
    lower_part2 = img2.crop((0, height2 // 2, width2, height2))

    # 获取拼接后图像的宽度，取两张图像宽度的最大值
    new_width = max(width1, width2)
    # 获取拼接后图像的高度，为两张图像各自截取部分的高度之和
    new_height = height1 // 2 + (height2 - height2 // 2)
    # 创建一个新的空白图像，用于拼接
    result_img = Image.new('RGB', (new_width, new_height))

    # 将第一张图像的上半部分粘贴到新图像的上半部分
    result_img.paste(upper_part1, (0, 0))
    # 将第二张图像的下半部分粘贴到新图像的下半部分
    result_img.paste(lower_part2, (0, height1 // 2))

    return result_img

# 示例用法，替换为实际的图像路径
image1_path = "distorted_image.jpg"
image2_path = "reduction.jpg"
result = combine_images(image1_path, image2_path)
result.show()