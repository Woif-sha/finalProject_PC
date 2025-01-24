import os
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from PIL import Image, ImageTk

# 中->右  # 中->左
# 左->右  # 右->左


# 速度等级 1 2 3  慢>>快
# 起始位置
# 终止位置
# 图片文件夹路径

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
        print(f"加载文件: {frame_path}")  # 打印文件路径

        # 如果文件存在，加载图像并预处理
        if os.path.exists(frame_path):
            frame = Image.open(frame_path)
            # 预处理：填充颜色
            frame = get_filled(frame)
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

        # 旋转图像
        rotated_frame = frame.rotate(round(rotate_degree))

        # 使用当前 offset_y 和 offset 处理图像
        new_img = get_newimg(rotated_frame, round(offset_y), round(offset), config.background_color)
        img = get_filled(new_img, config.background_color)
        return img

    # 使用线程池并行处理帧，保持顺序
    with ThreadPoolExecutor() as executor:
        processed_frames = list(executor.map(process_frame, enumerate(frames)))

    return processed_frames


def rotate_frames(frames, config):
    """将所有帧旋转固定角度"""

    def process_frame(args):
        i, frame = args
        # 旋转图像
        rotated_frame = frame.rotate(round(config.rotate_end))  # 使用 rotate_end 作为固定角度

        # 使用固定 offset_y 和 offset 处理图像
        new_img = get_newimg(rotated_frame, config.offset_y_end, config.offset_end, config.background_color)
        img = get_filled(new_img, config.background_color)
        return img

    # 使用线程池并行处理帧，保持顺序
    with ThreadPoolExecutor() as executor:
        rotated_frames = list(executor.map(process_frame, enumerate(frames)))

    return rotated_frames


def play_gif(frames, origin_frames, gif_interval=30):
    """播放两组帧数据（frames 和 origin_frames）"""
    root = tk.Tk()

    # 获取屏幕大小
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    # 设置窗口大小为屏幕大小
    root.geometry(f"{screen_width}x{screen_height}+0+0")

    # 去掉窗口的边框
    root.overrideredirect(True)

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
                # root.after(gif_interval, update_frame, 0)  # 循环播放
                # frames 播放完毕，切换到 origin_frames
                is_frames_finished = True
                update_frame(0)  # 从第 0 帧开始播放 origin_frames
        else:
            # 播放 origin_frames
            if frame_index < len(origin_frames):
                # 更新图像
                image_tk = ImageTk.PhotoImage(origin_frames[frame_index])
                canvas.create_image(screen_width // 2, screen_height // 2, image=image_tk)
                canvas.image = image_tk  # 保持引用，防止被垃圾回收
                root.after(gif_interval, update_frame, frame_index + 1)  # 更新下一帧
            else:
                # origin_frames 播放完毕，重新开始
                root.after(gif_interval, update_frame, 0)  # 循环播放

    # 开始播放 GIF
    update_frame(0)  # 从第 0 帧开始播放

    # 使窗口全屏并显示
    root.mainloop()


if __name__ == '__main__':
    # 初始化配置
    left = FrameConfig()
    left.offset_y_start = 600  # y 方向起始偏移
    left.offset_y_end = 480  # y 方向结束偏移

    # x 方向偏移
    left.offset_start = 25  # x 方向起始偏移
    left.offset_end = 500  # x 方向结束偏移

    # 旋转角度
    left.rotate_start = 90  # 起始旋转角度
    left.rotate_end = 66.5  # 结束旋转角度

    # 加载帧图像
    frames = load_frames('笑脸/', step=left.step)

    # 预处理帧数据
    processed_frames = preprocess_frames(frames, left)

    # 旋转帧数据
    rotated_frames = rotate_frames(frames, left)

    # 播放 GIF
    play_gif(processed_frames, rotated_frames, gif_interval=left.gif_interval)

    right = FrameConfig()
    right.offset_y_start = 600  # y 方向起始偏移
    right.offset_y_end = 500  # y 方向结束偏移

    # x 方向偏移
    right.offset_start = 25  # x 方向起始偏移
    right.offset_end = -450  # x 方向结束偏移

    # 旋转角度
    right.rotate_start = 90  # 起始旋转角度
    right.rotate_end = 113.5  # 结束旋转角度

    # 加载帧图像
    frames = load_frames('笑脸/', step=right.step)

    # 预处理帧数据
    processed_frames = preprocess_frames(frames, right)

    # 旋转帧数据
    rotated_frames = rotate_frames(frames, right)

    # 播放 GIF
    play_gif(processed_frames, rotated_frames, gif_interval=right.gif_interval)

