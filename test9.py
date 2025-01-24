import queue
from pyttsx3 import init
import wave
import json
from vosk import Model, KaldiRecognizer
import pyaudio
import webrtcvad
import threading
from pydub import AudioSegment
import time
import serial
import serial.tools.list_ports
from tkinter import Tk, Label
from PIL import Image, ImageTk

from ImageDistortion.forTest import process_and_play, stop_gif

task_queue = queue.Queue()
VAD_aggressiveness = 3  # VAD 灵敏度，取值范围为 0-3，数值越大越灵敏
buffer_duration = 1  # 缓冲时间（秒）
wakeup_word = "小鹿 小鹿"  # 唤醒词

# 加载 Vosk 模型
model_path = "vosk-model-cn-0.22"  # 请根据你的模型路径进行修改
model = Model(model_path)

# 定义一个全局变量用于存储位置信息
global_position = None

# 定义一个全局变量用于记录串口读取到的特定数字
last_received_data = None

recognize_result = None

# 定义一个全局变量用于记录是否已经处理过图片显示
image_shown = False

# 图片名称和串口读取数字的映射
success_image_mapping = {
    3: "smile3",
    4: "smile4",
    5: "smile5",
    6: "smile6",
    7: "smile7"
}

failure_image_mapping = {
    3: "q3",
    4: "q4",
    5: "q5",
    6: "q6",
    7: "q7"
}


def record_audio(filename="user_input.wav"):
    """ 录制用户音频并保存，使用 VAD 优化录音 """
    # recognizer = sr.Recognizer()
    audio_data = []
    vad = webrtcvad.Vad(VAD_aggressiveness)  # 在函数内部定义 VAD 对象

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=320)
    print("开始录音")

    last_speech_time = time.time()
    post_speech_silence_duration = 2  # 增加录音后静音检测时段
    post_speech_detected = False

    while True:
        chunk = stream.read(320, exception_on_overflow=False)  # 使用 20ms 的帧大小
        if vad.is_speech(chunk, 16000):
            audio_data.append(chunk)
            last_speech_time = time.time()
            post_speech_detected = False  # 重置
        else:
            if time.time() - last_speech_time > buffer_duration and not post_speech_detected:
                post_speech_detected = True
                post_speech_time = time.time()  # 记录静音开始的时间
            if post_speech_detected and time.time() - post_speech_time > post_speech_silence_duration:
                break
            else:
                audio_data.append(chunk)  # 保留非语音帧

    stream.stop_stream()
    stream.close()
    p.terminate()

    try:
        audio = AudioSegment(
            data=b''.join(audio_data),
            sample_width=p.get_sample_size(pyaudio.paInt16),
            frame_rate=16000,
            channels=1
        )
        audio.export(filename, format="wav")
        print("录音保存成功！")
    except Exception as e:
        print(f"保存录音失败！ {e}")


def recognize_speech_from_file(filename):
    """ 从文件中识别语音（使用Vosk） """
    wf = wave.open(filename, "rb")
    recognizer = KaldiRecognizer(model, wf.getframerate())

    while True:
        data = wf.readframes(2000)  # 减少每次读取的帧数
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            if result['text']:
                return result['text']

    final_result = json.loads(recognizer.FinalResult())
    if final_result['text']:
        return final_result['text']

    return "无法理解你的话"


def speak(text):
    """ 将文本转换为语音并播放（离线） """
    engine = init()
    engine.say(text)
    engine.runAndWait()


def detect_wakeup_word():
    """ 使用 Vosk 模型检测唤醒词 """
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=3200)

    recognizer = KaldiRecognizer(model, 16000)
    speak("我在听着")

    try:
        while True:
            data = stream.read(3200, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                # print(result)
                if result['text'] and wakeup_word in result['text']:
                    speak("在呢")
                    return True
            else:
                partial_result = json.loads(recognizer.PartialResult())
                if partial_result['partial'] and wakeup_word in partial_result['partial']:
                    speak("在呢")
                    return True
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


def position(port):
    global global_position, last_received_data
    ser = serial.Serial(port, baudrate=1000000, timeout=1)

    while True:
        # 接收数据
        data = ser.read(1)
        hex_data = data.hex()
        if hex_data == '55':
            data1 = ser.read(1)
            hex_data1 = data1.hex()
            if hex_data1 == 'aa':
                pos = ser.read(1)
                hex_pos = pos.hex()
                hex_pos_num = eval("0x" + hex_pos)
                if hex_pos_num >= 0x80:
                    hex_pos_num = hex_pos_num - 0x80
                else:
                    hex_pos_num = hex_pos_num

                last_received_data = hex_pos_num
                print(f"记录到串口数据: {hex_pos_num}")
            else:
                continue
        else:
            continue


def process_user_input():
    global global_position, recognize_result, image_shown

    record_audio_thread = threading.Thread(target=record_audio, args=("user_input.wav",))
    record_audio_thread.start()
    record_audio_thread.join()
    global_position = last_received_data

    speak("收到")
    print("global_position:", global_position)
    recognize_result = recognize_and_respond("user_input.wav")


def process_tasks():
    """在主线程中处理任务"""
    while True:
        task, args = task_queue.get()  # 从队列中获取任务和参数
        if task == "stop_gif":
            stop_gif()
        elif task == "show_gif":
            start_position, end_position, speed_level, mode = args  # 解包参数
            process_thread = threading.Thread(target=process_and_play, args=(
                start_position, end_position, speed_level, mode, './ImageDistortion/笑脸/',), daemon=True)
            process_thread.start()
        task_queue.task_done()


def recognize_and_respond(filename):
    user_input = recognize_speech_from_file(filename)
    print(f"输入识别结果: {user_input}")

    # 检查用户的输入
    if "打开 车窗" in user_input:
        speak("好的，我来给你通通风")
        return True
    elif "播放 音乐" in user_input:
        speak("不嫌弃的话，让我来唱首歌给你听吧")
        return True
    elif "定速 巡航" in user_input:
        speak("我来匀速奔跑")
        return True
    else:
        speak("我没有理解您的命令")
        return False


# def show_image_based_on_result(recognize_result):
#     global global_position, image_shown
#     if global_position is not None:
#         # print("last_data:", last_received_data)
#         if recognize_result:  # 识别成功
#             if not image_shown:
#                 show_gif(global_position)
#                 # show_image(success_image_mapping[last_received_data])
#                 image_shown = True  # 标记图片已显示
#             else:
#                 print("图片已显示，不再重复显示")
#         else:  # 识别失败
#             if not image_shown:
#                 pass
#                 # show_gif(last_received_data)
#                 # show_image(failure_image_mapping[last_received_data])
#                 # image_shown = True  # 标记图片已显示
#             else:
#                 print("图片已显示，不再重复显示")
#         global_position = None  # 重置状态
#         image_shown = False  # 重置图片显示标志
#     else:
#         if not recognize_result:
#             print("没有记录到串口数据，但识别失败")


def show_image(image_name):
    """ 显示指定名称的图片，使用tkinter和Pillow实现 """
    global image_shown

    def show_image_window(image_name):
        global image_shown
        root = Tk()
        root.title("图片显示")
        img_path = f"{image_name}.jpg"  # 图片文件的路径
        try:
            img = Image.open(img_path)
            img = ImageTk.PhotoImage(img)
            label = Label(root, image=img)
            label.pack()
            print(f"显示图片: {img_path}")
            root.after(5000, root.destroy)  # 5秒后自动关闭窗口
        except Exception as e:
            print(f"无法显示图片: {e}")
        root.mainloop()

    if not image_shown:
        image_shown = True
        threading.Thread(target=show_image_window, args=(image_name,)).start()
#

# 如何关闭窗口

# 正常显示mid
def show_gif():
    # 2,3,4 LEFT  5,6,7 MID 8,9,10 RIGHT
    global global_position, image_shown, recognize_result

    while True:
        if global_position is None:
            start_position, end_position, speed_level = "mid", "mid", 1
            # 处理并播放动画
            # task_queue.put(("show_gif", (start_position, end_position, speed_level, 'stay')))
            # print("thread start")
            process_and_play(start_position, end_position, speed_level, mode='stay', folder_path='./ImageDistortion/笑脸/')
            global_position = 0
        else:
            # print("res:", recognize_result)
            time.sleep(0.1)
            if recognize_result:  # 识别成功
                if not image_shown:
                    task_queue.put(("stop_gif", None))
                    # process_thread.join()
                    if global_position in range(2, 6):
                        start_position, end_position, speed_level = "mid", "left", 1
                    elif global_position in range(6, 7):
                        start_position, end_position, speed_level = "mid", "mid", 1
                    elif global_position in range(7, 11):
                        start_position, end_position, speed_level = "mid", "right", 1
                    print(start_position, end_position, speed_level)
                    # task_queue.put(("show_gif", (start_position, end_position, speed_level, 'stay')))
                    # process_thread = threading.Thread(target=process_and_play, args=(
                    #     start_position, end_position, speed_level, 'destroy', './ImageDistortion/笑脸/',))
                    # process_thread.start()
                    process_and_play(start_position, end_position, speed_level, mode='destroy',
                                     folder_path='./ImageDistortion/笑脸/')
                    image_shown = True  # 标记图片已显示
                else:
                    print("图片已显示，不再重复显示")
            else:  # 识别失败
                if image_shown:
                    print("图片已显示，不再重复显示")
            # global_position = None  # 重置状态
            recognize_result = None
            image_shown = False  # 重置图片显示标志


def main():
    task_thread = threading.Thread(target=process_tasks, daemon=True)
    task_thread.start()

    gif_thread = threading.Thread(target=show_gif, daemon=True)
    gif_thread.start()

    # 启动串口通信线程
    position_thread = threading.Thread(target=position, args=("COM14",), daemon=True)
    position_thread.start()

    while True:
        if detect_wakeup_word():
            process_user_input()
            time.sleep(2)  # 等待图片显示后继续


# 六种情况 分别调用出来
if __name__ == "__main__":
    main()
