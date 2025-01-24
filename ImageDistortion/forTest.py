import os
import threading
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
import time
import numpy as np
from PIL import Image, ImageTk

# 1.获取背景颜色
# 2.裁剪图像
# 3.放大图像
# 4.旋转图像
# 5.黑色区域进行颜色填充
# 6.图像拼接

# 全局变量，用于存储当前的 root 对象
current_root = None


# 参数配置
class FrameConfig:
    def __init__(self):
        # y 方向偏移
        self.offset_y_start = 600  # y 方向起始偏移
        self.offset_y_end = 480  # y 方向结束偏移

        # x 方向偏移
        self.offset_start = 25  # x 方向起始偏移
        self.offset_end = 500  # x 方向结束偏移

        # 旋转角度
        self.rotate_start = 90  # 起始旋转角度
        self.rotate_end = 66.5  # 结束旋转角度

        # 其他配置
        self.step = 2  # 加载帧的步长
        self.gif_interval = 10  # 帧间隔时间（毫秒）
        self.background_color = (255, 205, 89)  # 背景颜色

        self.crop_size = 300
        self.resize_para = 1.5
        self.stay_time = 15000


def get_newimg(img, offset_y, offset, color=(255, 205, 89)):
    """将图像粘贴到黄色背景上"""
    yellow_background = Image.new('RGB', (1920, 1080), color)

    # 计算将旋转后的图片放到背景的位置
    paste_position_org = (
        (yellow_background.width - img.width + offset_y) // 2,  # y 方向偏移
        (yellow_background.height - img.height + offset) // 2  # x 方向偏移
    )

    # 将旋转后的裁剪图片粘贴到黄色背景上
    yellow_background.paste(img, paste_position_org)
    return yellow_background


def get_filled(img, color=(255, 205, 89)):
    """将图像中的黑色像素替换为黄色（使用 numpy 加速）"""
    img_array = np.array(img)
    black_pixels = (img_array[:, :, 0] == 0) & (img_array[:, :, 1] == 0) & (img_array[:, :, 2] == 0)
    img_array[black_pixels] = color
    return Image.fromarray(img_array)


def load_frames(folder_path, step=2):
    """从文件夹中加载帧数据，跳着取数据"""
    frames = []
    frame_index = 1

    while True:
        # 构造文件名
        frame_filename = f"笑脸_00{frame_index:03d}.png"  # 假设图像格式为 PNG
        frame_path = os.path.join(folder_path, frame_filename)
        # print(f"加载文件: {frame_path}")  # 打印文件路径

        # 如果文件存在，加载图像并预处理
        if os.path.exists(frame_path):
            frame = Image.open(frame_path)
            # 预处理：填充颜色
            # frame = get_filled(frame)
            frames.append(frame)
            frame_index += step  # 跳着取数据
        else:
            break  # 如果文件不存在，退出循环

    print(f"成功加载 {len(frames)} 帧")  # 打印加载的帧数
    return frames


def preprocess_frames(frames, config):
    """预先处理所有帧，保存 offset_y、offset 和旋转角度的变化"""
    # 计算每帧的 offset_y、offset 和旋转角度增量
    offset_y_step = (config.offset_y_end - config.offset_y_start) / len(frames)
    offset_step = (config.offset_end - config.offset_start) / len(frames)
    rotate_step = (config.rotate_end - config.rotate_start) / len(frames)

    def process_frame(args):
        i, frame = args
        # 计算当前 offset_y、offset 和旋转角度
        offset_y = config.offset_y_start + i * offset_y_step
        offset = config.offset_start + i * offset_step
        rotate_degree = config.rotate_start + i * rotate_step

        # 获取图片尺寸
        width, height = frame.size
        # print(width, height)
        # 计算图片的中心坐标，中心向上偏移 20 像素
        center_x, center_y = width // 2, height // 2 - 20

        # 设置截取区域的大小（默认为300x300）
        left = center_x - config.crop_size // 2
        top = center_y - config.crop_size // 2
        right = center_x + config.crop_size // 2
        bottom = center_y + config.crop_size // 2

        # 裁剪图片
        cropped_frame = frame.crop((left, top, right, bottom))

        # 放大图片
        resized_frame = cropped_frame.resize((int(config.crop_size * config.resize_para),
                                              int(cropped_frame.size[1] * (config.crop_size * config.resize_para) /
                                                  cropped_frame.size[0])))
        # print(resized_frame.size)

        # 旋转图像
        rotated_frame = resized_frame.rotate(round(rotate_degree))

        # 使用当前 offset_y 和 offset 处理图像
        new_img = get_newimg(rotated_frame, round(offset_y), round(offset), config.background_color)
        # new_img.show()
        img = get_filled(new_img, config.background_color)
        return img

    # 使用线程池并行处理帧，保持顺序
    with ThreadPoolExecutor() as executor:
        processed_frames = list(executor.map(process_frame, enumerate(frames)))

    return processed_frames


def afterprocess_frames(frames, config):
    """将所有帧旋转固定角度"""

    def process_frame(args):
        i, frame = args
        # 获取图片尺寸
        width, height = frame.size
        # print(width, height)
        # 计算图片的中心坐标，中心向上偏移 20 像素
        center_x, center_y = width // 2, height // 2 - 20

        # 设置截取区域的大小（默认为300x300）
        left = center_x - config.crop_size // 2
        top = center_y - config.crop_size // 2
        right = center_x + config.crop_size // 2
        bottom = center_y + config.crop_size // 2

        # 裁剪图片
        cropped_frame = frame.crop((left, top, right, bottom))

        # 放大图片
        resized_frame = cropped_frame.resize((int(config.crop_size * config.resize_para),
                                              int(cropped_frame.size[1] * (config.crop_size * config.resize_para) /
                                                  cropped_frame.size[0])))
        rotated_frame = resized_frame.rotate(round(config.rotate_end))  # 使用 rotate_end 作为固定角度

        # 使用固定 offset_y 和 offset 处理图像
        new_img = get_newimg(rotated_frame, config.offset_y_end, config.offset_end, config.background_color)
        img = get_filled(new_img, config.background_color)
        return img

    # 使用线程池并行处理帧，保持顺序
    with ThreadPoolExecutor() as executor:
        rotated_frames = list(executor.map(process_frame, enumerate(frames)))

    return rotated_frames


def play_gif(frames, end_frames, mode='destroy', gif_interval=30, stay_time=1000):
    """播放帧数据"""
    global current_root

    root = tk.Toplevel()
    # 获取屏幕大小
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # 设置窗口大小为屏幕大小
    root.geometry(f"{screen_width}x{screen_height}+0+0")

    # 去掉窗口的边框
    root.overrideredirect(True)

    # 窗口置顶
    root.wm_attributes("-topmost", True)

    # 创建一个 Canvas 组件
    canvas = tk.Canvas(root, width=screen_width, height=screen_height)
    canvas.pack()

    # 定义一个函数来处理 ESC 键的退出事件
    def on_escape(event=None):
        root.quit()  # 退出主事件循环
        root.destroy()  # 销毁窗口

    # 绑定 ESC 键事件
    root.bind('<Escape>', on_escape)

    # 定义一个标志变量，表示是否播放完 frames
    is_frames_finished = False

    def update_frame(frame_index):
        """更新帧数据"""
        nonlocal is_frames_finished

        if not is_frames_finished:
            # 播放 frames
            if frame_index < len(frames):
                # 更新图像
                image_tk = ImageTk.PhotoImage(frames[frame_index])
                canvas.create_image(screen_width // 2, screen_height // 2, image=image_tk)
                canvas.image = image_tk  # 保持引用，防止被垃圾回收
                root.after(gif_interval, update_frame, frame_index + 1)  # 更新下一帧
            else:
                # frames 播放完毕，切换到 origin_frames
                is_frames_finished = True
                update_frame(0)  # 从第 0 帧开始播放 origin_frames
        else:
            # 播放 origin_frames
            if frame_index < len(frames):
                # 更新图像
                image_tk = ImageTk.PhotoImage(end_frames[frame_index])
                canvas.create_image(screen_width // 2, screen_height // 2, image=image_tk)
                canvas.image = image_tk  # 保持引用，防止被垃圾回收
                root.after(gif_interval, update_frame, frame_index + 1)  # 更新下一帧
            else:
                # origin_frames 播放完毕，重新开始
                root.after(gif_interval, update_frame, 0)  # 循环播放
                if mode == 'destroy':
                    root.after(stay_time, root.destroy)  # 5秒后自动关闭窗口
                elif mode == 'stay':
                    pass

    # 开始播放 GIF
    update_frame(0)  # 从第 0 帧开始播放

    # 使窗口全屏并显示
    root.mainloop()


def get_user_input():
    """获取用户输入的起始位置、结束位置和速度等级"""
    print("请输入以下参数：")
    start_position = input("起始位置（left/mid/right）：").strip().lower()
    end_position = input("结束位置（left/mid/right）：").strip().lower()
    speed_level = int(input("速度等级（1: 低速, 2: 中速, 3: 高速）：") or 2)

    return start_position, end_position, speed_level


def get_config(start_position, end_position):
    """根据位置（left/mid/right）返回对应的 FrameConfig"""
    config = FrameConfig()

    if start_position == "left":
        config.offset_y_start = 480
        config.offset_start = 500
        config.rotate_start = 63.5
    elif start_position == "mid":
        config.offset_y_start = 600
        config.offset_start = 25
        config.rotate_start = 90
    elif start_position == "right":
        config.offset_y_start = 480
        config.offset_start = -450
        config.rotate_start = 120.5

    if end_position == "left":
        config.offset_y_end = 480
        config.offset_end = 500
        config.rotate_end = 63.5
    elif end_position == "mid":
        config.offset_y_end = 600
        config.offset_end = 25
        config.rotate_end = 90
    elif end_position == "right":
        config.offset_y_end = 480
        config.offset_end = -450
        config.rotate_end = 120.5
    return config


def stop_gif():
    """强制关闭当前播放的 GIF"""
    global current_root
    if current_root:
        current_root.destroy()
        current_root = None


def process_and_play(start_position, end_position, speed_level, mode='destroy', folder_path='./笑脸/'):
    """
    处理并播放帧数据，支持指定起始位置、结束位置和速度等级。

    参数:
        start_position (str): 起始位置（left/mid/right）。
        end_position (str): 结束位置（left/mid/right）。
        speed_level (int): 速度等级（1、2 或 3）。
        folder_path (str): 图片文件夹路径。
    """
    # 根据速度等级设置 step 和 gif_interval
    if speed_level == 1:
        step = 1
        gif_interval = 15
    elif speed_level == 2:
        step = 2
        gif_interval = 30
    elif speed_level == 3:
        step = 2
        gif_interval = 1

    # 获取起始位置和结束位置的配置
    conf = get_config(start_position, end_position)

    # 设置 step 和 gif_interval
    conf.step = step
    conf.gif_interval = gif_interval

    # 加载帧图像
    frames = load_frames(folder_path, step=step)

    # 预处理帧数据（从起始位置到结束位置）
    processed_frames = preprocess_frames(frames, conf)
    afterprocess_frame = afterprocess_frames(frames, conf)
    # 播放 GIF
    play_gif(processed_frames, afterprocess_frame, mode, gif_interval=gif_interval, stay_time=conf.stay_time)


if __name__ == '__main__':
    while True:
        try:
            # 获取用户输入的起始位置、结束位置和速度等级
            start_position, end_position, speed_level = get_user_input()

            # # 处理并播放动画
            # process_thread = threading.Thread(target=process_and_play, args=(
            #     start_position, end_position, speed_level, 'destroy'))
            # process_thread.start()
            # #
            # process_thread.join()
            process_and_play(start_position, end_position, speed_level, mode='stay', folder_path='./笑脸/')
        # except Exception as e:
        #     print(f"发生错误：{e}")
        #     continue
        except:
            pass
