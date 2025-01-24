from PIL import Image
import numpy as np
import addGrid


def trapezoid_transform(image_path, scale_factor=0.35):
    try:
        image = Image.open(image_path)
    except:
        image = image_path
    width, height = image.size
    img_array = np.array(image)
    new_img_array = np.zeros_like(img_array)
    for y in range(height):
        scale = 1 - (y / height) * scale_factor
        new_width = int(width * scale)
        offset = (width - new_width) // 2
        for x in range(width):
            if x >= offset and x < offset + new_width:
                new_x = int((x - offset) / scale)
                new_img_array[y, x] = img_array[y, new_x]

    return Image.fromarray(new_img_array.astype('uint8'))


if __name__ == '__main__':
    image_path = 'black_white.jpg'
    # grid_image_path = addGrid.add_grid(image_path, grid_width=30, line_width=10, line_color=(0, 0, 0),show=False)
    # new_image = trapezoid_transform(grid_image_path, scale_factor=0.30)
    # image = Image.open(image_path)
    # image.show()
    new_image = trapezoid_transform(image_path, scale_factor=0.3)
    # new_image = Image.open(grid_image_path)
    new_image.save("trapezoid_transform.jpg")
    new_image.show()
