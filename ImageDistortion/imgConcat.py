from PIL import Image

compression_ratios = [0.85, 0.83, 0.85, 0.83,
                      0.83, 0.85, 0.83, 0.85]  # 设置不同的y方向压缩比例，数值越小压缩程度越大


def split_image_y(image_path):
    """
    按照y方向每32像素分割图片
    :param image_path: 原始图片路径
    """
    img = Image.open(image_path)
    width, height = img.size
    num_slices = height // 32  # 计算y方向可分割的切片数量
    print(f"y:图片宽度：{width}，高度：{height}，切片数量：{num_slices}")

    compressed_images = []

    for i in range(num_slices):
        start_y = i * 32
        end_y = (i + 1) * 32 if (i + 1) * 32 < height else height
        box = (0, start_y, width, end_y)
        slice_img = img.crop(box)
        # slice_img.save(f'slice_{i}.png')
        # print(width,height)
        slice_width, slice_height = slice_img.size
        new_height = int(slice_height * compression_ratios[i])  # 根据压缩比例计算新的y方向像素数量
        compressed_img = slice_img.resize((slice_width, new_height), Image.ANTIALIAS)  # 进行尺寸调整，使用抗锯齿算法保证图像质量
        compressed_images.append(compressed_img)

    # 获取单张图片宽度，以宽度最大的为准（便于拼接对齐）
    max_width = max([img.size[0] for img in compressed_images])
    total_height = sum([img.size[1] for img in compressed_images])
    new_img = Image.new('RGB', (max_width, total_height))

    current_y = 0
    for img in compressed_images:
        new_img.paste(img, (0, current_y))
        current_y += img.size[1]

    return new_img


def split_image_x(img):
    # img = Image.open(image_path)
    width, height = img.size
    num_slices = width // 32  # x方向按每列分割，所以切片数量就是图片宽度（每列作为一个切片）
    print(f"x:图片宽度：{width}，高度：{height}，切片数量：{num_slices}")

    # compression_ratios = [0.8, 0.90, 0.88, 0.86,
    #                       0.86, 0.88, 0.90, 0.8]  # 设置不同的压缩比例，数值越小压缩程度越大
    compressed_images = []

    for i in range(num_slices):
        start_x = i * 32
        end_x = (i + 1) * 32 if (i + 1) * 32 < width else width
        box = (start_x, 0, end_x, height)  # 裁剪每一列对应的区域，y方向是整个高度范围
        slice_img = img.crop(box)
        slice_width, slice_height = slice_img.size
        new_width = int(slice_width * compression_ratios[i])  # 根据压缩比例计算新的x方向像素数量，循环使用压缩比例列表
        compressed_img = slice_img.resize((new_width, slice_height), Image.ANTIALIAS)  # 进行尺寸调整，使用抗锯齿算法保证图像质量
        compressed_images.append(compressed_img)

    # 获取单张图片高度，以高度最大的为准（便于拼接对齐）
    max_height = max([img.size[1] for img in compressed_images])
    total_width = sum([img.size[0] for img in compressed_images])
    new_img = Image.new('RGB', (total_width, max_height))

    current_x = 0
    for img in compressed_images:
        new_img.paste(img, (current_x, 0))  # 在x方向（水平方向）依次粘贴图片
        current_x += img.size[0]

    return new_img


if __name__ == "__main__":
    image_path = "black_white.jpg"  # 替换为实际的图片路径
    # image_path = "chessboard_960_540.jpg"
    img_y = split_image_y(image_path)
    result_img = split_image_x(img_y)
    # result_img.show()
    w, h = result_img.size
    print(w, h)
    result_img.save("result_concat_2.jpg")
