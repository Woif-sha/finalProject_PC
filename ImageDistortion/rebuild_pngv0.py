import cv2
from PIL import Image, ImageDraw, ImageTk
import tkinter as tk


def show_original_image(image_path, crop_size=300, offset_y=500):
    # 打开原图
    img = Image.open(image_path)

    # 获取图片尺寸
    width, height = img.size

    # 计算图片的中心坐标，中心向上偏移 20 像素
    center_x, center_y = width // 2, height // 2 - 20

    # 设置截取区域的大小（默认为300x300）
    left = center_x - crop_size // 2
    top = center_y - crop_size // 2
    right = center_x + crop_size // 2
    bottom = center_y + crop_size // 2

    # 裁剪图片
    cropped_img = img.crop((left, top, right, bottom))
    # print(cropped_img.size)
    resize_para = 1.5
    resized_image = cropped_img.resize((int(crop_size * resize_para),
                                         int(cropped_img.size[1] * (crop_size * resize_para) / cropped_img.size[0])))
    print(resized_image.size)

    # 旋转裁剪后的图片 180°
    resized_image = resized_image.rotate(90)
    resized_image.show()
    # 创建一个黄色背景的图片，大小为 1920x1080
    yellow_background = Image.new('RGB', (1920, 1080), (255, 205, 89))

    # 计算将旋转后的图片放到背景的左上角的位置
    paste_position_org = ((yellow_background.width - resized_image.width + offset_y) // 2,  # 500 球幕的y方向，“+”靠下
                          (yellow_background.height - resized_image.height + 25) // 2)  # 25 球幕的x方向，“+”靠左
    # 将旋转后的裁剪图片粘贴到黄色背景上
    yellow_background.paste(resized_image, paste_position_org)

    # 使用 Tkinter 显示图片全屏（去掉边框）
    show_full_screen(yellow_background)


# 定义一个函数，用来执行图片裁剪和背景合成处理
def crop_and_add_circle(image_path, crop_size=300, rotate_para=90, offset=25, output_path=None, show=False):
    # 打开原图
    img = Image.open(image_path)

    # 获取图片尺寸
    width, height = img.size

    # 计算图片的中心坐标，中心向上偏移 20 像素
    center_x, center_y = width // 2, height // 2 - 20

    # 设置截取区域的大小（默认为300x300）
    left = center_x - crop_size // 2
    top = center_y - crop_size // 2
    right = center_x + crop_size // 2
    bottom = center_y + crop_size // 2

    # 裁剪图片
    cropped_img = img.crop((left, top, right, bottom))
    # cropped_img = Image.open('face_res.jpg')
    # 旋转裁剪后的图片 180°
    cropped_img = cropped_img.rotate(rotate_para)  # 90

    # 填充黑色区域
    data = cropped_img.getdata()
    new_data = []
    for item in data:
        if item[0] == 0 and item[1] == 0 and item[2] == 0:  # 如果是黑色像素
            new_data.append((255, 205, 89))  # 填充黄色
        else:
            new_data.append(item)
    cropped_img.putdata(new_data)
    # cropped_img.show()

    # 创建一个黄色背景的图片，大小为 1920x1080
    yellow_background = Image.new('RGB', (1920, 1080), (255, 205, 89))

    # 计算将旋转后的图片放到背景的左上角的位置
    paste_position_org = ((yellow_background.width - cropped_img.width + 500) // 2,  # 500 球幕的y方向，“+”靠下
                          (yellow_background.height - cropped_img.height + offset) // 2)  # 25 球幕的x方向，“+”靠左
    # 将旋转后的裁剪图片粘贴到黄色背景上
    yellow_background.paste(cropped_img, paste_position_org)

    # 保存最终的图像
    yellow_background.save(output_path)

    # 使用 Tkinter 显示图片全屏（去掉边框）
    if show:
        show_full_screen(yellow_background)


def join(image_path, crop_size, rotate_para1, rotate_para2, offsety,offset1, offset2):
    # 打开原图
    img = Image.open(image_path)

    # 获取图片尺寸
    width, height = img.size

    # 计算图片的中心坐标，中心向上偏移 20 像素
    center_x, center_y = width // 2, height // 2 - 20

    # 设置截取区域的大小（默认为300x300）
    left = center_x - crop_size // 2
    top = center_y - crop_size // 2
    right = center_x + crop_size // 2
    bottom = center_y + crop_size // 2

    # 裁剪图片
    cropped_img = img.crop((left, top, right, bottom))

    # 旋转裁剪后的图片 180°
    cropped_img1 = cropped_img.rotate(rotate_para1)  # 90
    cropped_img2 = cropped_img.rotate(rotate_para2)  # 90

    # 填充黑色区域
    data = cropped_img1.getdata()
    new_data = []
    for item in data:
        if item[0] == 0 and item[1] == 0 and item[2] == 0:  # 如果是黑色像素
            new_data.append((255, 205, 89))  # 填充黄色
        else:
            new_data.append(item)
    cropped_img1.putdata(new_data)
    # cropped_img1.show()

    data2 = cropped_img2.getdata()
    new_data2 = []
    for it in data2:
        if it[0] == 0 and it[1] == 0 and it[2] == 0:  # 如果是黑色像素
            new_data2.append((255, 205, 89))  # 填充黄色
        else:
            new_data2.append(it)
    cropped_img2.putdata(new_data2)
    # cropped_img2.show()


    # 创建一个黄色背景的图片，大小为 1920x1080
    yellow_background = Image.new('RGB', (1920, 1080), (255, 205, 89))

    cropped_img3 = cropped_img.rotate(90)
    # 计算将旋转后的图片放到背景的左上角的位置
    paste_position_org = ((yellow_background.width - cropped_img3.width + offsety) // 2,  # 500 球幕的y方向，“+”靠下
                          (yellow_background.height - cropped_img3.height + 25) // 2)  # 25 球幕的x方向，“+”靠左
    # 将旋转后的裁剪图片粘贴到黄色背景上
    yellow_background.paste(cropped_img3, paste_position_org)
    # 计算将旋转后的图片放到背景的左上角的位置
    paste_position_org = ((yellow_background.width - cropped_img1.width + 500) // 2,  # 500 球幕的y方向，“+”靠下
                          (yellow_background.height - cropped_img1.height + offset1) // 2)  # 25 球幕的x方向，“+”靠左
    # 将旋转后的裁剪图片粘贴到黄色背景上
    yellow_background.paste(cropped_img1, paste_position_org)
    paste_position_org = ((yellow_background.width - cropped_img2.width + 500) // 2,  # 500 球幕的y方向，“+”靠下
                          (yellow_background.height - cropped_img2.height + offset2) // 2)  # 25 球幕的x方向，“+”靠左
    # 将旋转后的裁剪图片粘贴到黄色背景上
    yellow_background.paste(cropped_img2, paste_position_org)

    show_full_screen(yellow_background)


# 定义一个函数来显示图片全屏并去掉边框
def show_full_screen(image):
    # 创建一个 Tkinter 窗口
    root = tk.Tk()

    # 获取屏幕大小
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # 设置窗口大小为屏幕大小
    root.geometry(f"{screen_width}x{screen_height}+0+0")

    # 去掉窗口的边框
    root.overrideredirect(True)

    # 将 Pillow 图像转换为 Tkinter 可以显示的格式
    image_tk = ImageTk.PhotoImage(image)

    # 创建一个标签并显示图像
    label = tk.Label(root, image=image_tk)
    label.pack()

    # 定义一个函数来处理 ESC 键的退出事件
    def on_escape(event=None):
        root.quit()  # 退出主事件循环
        root.destroy()  # 销毁窗口

    # 绑定 ESC 键事件
    root.bind('<Escape>', on_escape)

    # 使窗口全屏并显示
    root.mainloop()


# 在main中调用该函数
if __name__ == '__main__':
    # 示例：调用函数，输入图片路径、裁剪区域大小及输出路径

    show_original_image('笑脸\笑脸_00007.png', crop_size=300, offset_y=585)
    # # 主驾驶
    # crop_and_add_circle('笑脸\笑脸_00007.png', crop_size=300, rotate_para=66.5, offset=400,
    #                     output_path='left.jpg', show=True)
    # # 副驾驶
    # crop_and_add_circle('笑脸\笑脸_00007.png', crop_size=300, rotate_para=113.5, offset=-350,
    #                     output_path='right.jpg', show=True)

    # join('笑脸\笑脸_00007.png', offsety=600, crop_size=300, rotate_para1=62, offset1=500, rotate_para2=180-62, offset2=-475)
    # cv2.waitKey(0)