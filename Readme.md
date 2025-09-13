使用yolov11训练的烟云十六声-丝竹雅韵 ai演奏机器人，非外挂

前置条件
1、目前仅适用于烟云十六声PC版，分辨率为1920*1080
2、本程序运行在独立电脑上，不在游戏电脑中运行，因此你需要两台电脑
3、本项目通过 ms2131 采集卡对显示器的内容进行采集，也可以通过固定摄像头进行采集
4、本项目通过 ch0329 usb串口键盘对目标电脑进行操作

注1：电脑不能太差，可以通过-sp ture进行预览，如果fps低于30就不太好用了
注2：ms2131采集卡（环出），在拼夕夕36元购入
注3：ch0329串口键盘（双usb口），在淘宝16元购入

运行参数
options:
  -h, --help            show this help message and exit
  -kp KBMS_PORT, --kbms_port KBMS_PORT
                        键盘端口号
  -ci CAMERA_INDEX, --camera_index CAMERA_INDEX
                        摄像头索引
  -sp SCREEN, --screen SCREEN
                        显示检测窗口
  -lg LOG, --log LOG    启用日志记录
  -cw CAP_WIDTH, --CAP_WIDTH CAP_WIDTH
                        采集宽度
  -ch CAP_HEIGHT, --CAP_HEIGHT CAP_HEIGHT
                        采集高度
  -cf CAP_FPS, --CAP_FPS CAP_FPS
                        采集帧率


目前的问题
1、ch0329不能单独控制按键抬起
2、模型仅训练了300轮，还不够准确

2025/9/14 by youkai
