from PIL import Image, ImageDraw


def add_grid(image_path, grid_width=5, line_width=1, line_color=(255, 0, 0),show=True):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    width, height = image.size

    # 绘制垂直线
    for x in range(0, width, grid_width):
        draw.line((x, 0, x, height), fill=line_color, width=line_width)

    # 绘制水平线
    for y in range(0, height, grid_width):
        draw.line((0, y, width, y), fill=line_color, width=line_width)

    if show:
        image.show()
    new_image_path = image_path.rsplit('.', 1)[0] + '_grid.' + image_path.rsplit('.', 1)[1]
    image.save(new_image_path)
    return new_image_path

if __name__ == '__main__':
    image_path = 'black_white.jpg'
    add_grid(image_path, grid_width=5, line_width=1, line_color=(255, 0, 0),show=True)