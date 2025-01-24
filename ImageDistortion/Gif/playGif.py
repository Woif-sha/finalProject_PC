import sys

import cv2
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from demo import trapezoid_transform

def extract_gif_frames(gif_path):
    frames_list = []
    # 打开GIF文件
    with Image.open(gif_path) as img:
        # 计算GIF中的帧数
        frames = img.n_frames
        for i in range(1,frames):
            img.seek(i)  # 移动到第i帧
            frame = img.copy()  # 获取当前帧的副本，避免后续操作影响原图像
            frame = trapezoid_transform(frame, scale_factor=0.30)
            frames_list.append(frame)
    return frames_list

def save_frames_as_mp4(frames, output_video_path, fps=10, frame_delay=1):
    """
    将帧列表保存为MP4视频文件，并可设置每帧的等待时间（以延长帧显示时长）
    :param frames: 图像帧列表，每个元素是PIL的Image对象
    :param output_video_path: 输出的MP4视频文件路径
    :param fps: 视频帧率，默认为10帧每秒
    :param frame_delay: 每帧的等待时间（即同一帧重复写入次数），默认为1，值越大帧显示时间越长
    """
    height, width = frames[0].size[1], frames[0].size[0]
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
    for frame in frames:
        frame_np = np.array(frame)
        frame_np = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
        for _ in range(frame_delay):
            out.write(frame_np)
    out.release()

def play_gif_frames(frames):
    fig = plt.figure(figsize=(16, 12))
    ims = []
    for frame in frames:
        frame_np = np.array(frame)
        im = plt.imshow(frame_np, animated=True)
        ims.append([im])

    ax = plt.gca()
    # 隐藏坐标轴
    ax.axis('off')

    ani = animation.ArtistAnimation(fig, ims, interval=50, blit=True)
    plt.show()

if __name__ == '__main__':
    gif_path = 'smile.gif'
    output_video_path = "smile.mp4"  # 输出的MP4视频文件路径
    frames = extract_gif_frames(gif_path)
    # 先保存帧为MP4视频
    save_frames_as_mp4(frames, output_video_path)
    print('ok')
    sys.exit()
    while True:
        # play_gif_frames(frames)
        pass