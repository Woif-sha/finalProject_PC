import time
import serial
import serial.tools.list_ports
# --------------------------------------------------------------------------------------------------------

#
# ports_list = list(serial.tools.list_ports.comports())  # 获取所有串口设备实例
# if len(ports_list) <= 0:
#     print("无可用的串口设备！")
# else:
#     print("可用的串口设备如下：")
#     for port in ports_list:  # 依次输出每个设备对应的串口号和描述信息
#         print(list(port)[0], list(port)[1])  # COM4 USB-SERIAL CH340 (COM4)
# --------------------------------------------------------------------------------------------------------

# ser = serial.Serial("COM8", 1000000)  # 打开COM4，将波特率配置为115200，其余参数使用默认值
# if ser.isOpen():  # 判断串口是否成功打开
#     print("串口成功打开")
#     print(ser.name)  # 输出串口号，即COM4
# else:
#     print("串口打开失败")
#
# ser.close()  # 关闭串口
# if ser.isOpen():  # 判断串口是否关闭
#     print("串口未关闭")
# else:
#     print("串口已关闭")
# --------------------------------------------------------------------------------------------------------


def position(port):
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
                    hex_pos_num = hex_pos_num-0x80
                else:
                    hex_pos_num = hex_pos_num
                return hex_pos_num
            else:
                continue
        else:
            continue


def main():
    while True:
        time.sleep(1)
        try:
            pos = position('COM14')  # 修改串口名
            print(pos)
        except Exception as e:
            print(f"程序发生错误: {e}")


if __name__ == '__main__':
    main()
