# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""
D:\soft\vse_windows_GPU\vse\Python\python.exe .\run.py "E:\system\待下载\[桜都字幕组][ばにぃうぉ～か～]OVA大好きな母 ＃2 大好きな母の裏側"
嵌套字幕提取的命令行运行
@Author  : hank 
"""

import argparse
import os
import sys
# 提取模块
from backend.main import SubtitleExtractor
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dependencies'))
from threading import Thread
import cv2
import traceback
# import pdb
# reload(sys)
# sys.setdefaultencoding('utf8')

def validate(args):
    """
    Check that the CLI arguments passed to autosub are valid.
    """
    # if not args.source_path:
        # print("请传入你的路径")
        # return False

    return True

def filterFileFun(fileName, *suffix):
    try:
        if isinstance(fileName, str):fileName=fileName
        for nowSuffix in suffix:
            if fileName.endswith("."+nowSuffix):
                return True
    except BaseException as e:
        print(e)
    return False

def main(source_path, shutdown, onceNum):
    """
    运行字幕提取的命令行模式
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-xL', '--xLeft', help="字幕区域x轴左边相对视频的比例,默认.05", type=float, default=.05)
    parser.add_argument('-xW', '--xWidth', help="字幕区域x轴宽度相对视频的比例,默认.9", type=float, default=.9)    
    parser.add_argument('-yT', '--yTop', help="字幕区域y轴上边相对视频的比例,默认.83", type=float, default=.83)    
    parser.add_argument('-yH', '--yHeight', help="字幕区域y轴高度相对视频高度的比例,默认.17", type=float, default=.17)    
    
    args = parser.parse_args()
    if not validate(args):
        return 1
    try:
        allFile = []
        if not os.path.isdir(source_path):
            allFile = [source_path]
        else:
            file_name_lists = []
            for maindir, subdir, file_name_list in os.walk(source_path):
                # print("1:",maindir) #当前主目录
                # print("2:",subdir) #当前主目录下的所有目录
                # print("3:",file_name_list)  #当前主目录下的所有文件
                file_name_lists = file_name_lists + [maindir+"\\"+x for x in file_name_list]
            allFile = [x for x in file_name_lists if filterFileFun(x, "wmv", "avi", "mpeg", "mpg", "rm", "rmvb", "flv", "mp4", "mkv")]
        concurrencyNum = len(allFile) if len(allFile) < onceNum else onceNum
        i = 0
        j = 0
        nowProcessAll = []

        # 字幕区域参数
        for nowFile in allFile:
            print(f"now file:{nowFile}")
            video_cap = cv2.VideoCapture(nowFile)
            if video_cap is None:
                print(f"{nowFile} 读取失败")
                continue
            if not video_cap.isOpened():
                print(f"{nowFile} 打开失败")
                continue
            if os.path.exists(os.path.join(os.path.splitext(nowFile)[0] + '.srt')):
                print(f"{nowFile} 已存在字幕")
                continue
            # 获取视频的高度
            frame_height = video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            # 获取视频的宽度
            frame_width = video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            
            # 字幕区域x轴设置
            xmin = frame_width * args.xLeft
            xmax = xmin + frame_width * args.xWidth
            
            # 字幕区域y轴设置
            ymin = frame_height * args.yTop
            ymax = ymin + frame_height * args.yHeight
            subtitle_area = (ymin, ymax, xmin, xmax)
            se = SubtitleExtractor(nowFile, sub_area=subtitle_area)
            nowProcess = Thread(target=se.run)
            # nowProcess = Thread(target=se.run, daemon=True)
            # nowProcess = Process(target=generate_subtitles, args=(),
                    # kwargs={
                        # 'source_path':nowFile,
                        # 'concurrency':args.concurrency,
                        # 'src_language':args.src_language,
                        # 'dst_language':args.dst_language,
                        # 'api_key':args.api_key,
                        # 'subtitle_file_format':args.format,
                        # 'output':args.output
                    # })
            nowProcess.start()
            nowProcessAll.append(nowProcess)
            i = i+1
            j = j+1
            if i == concurrencyNum or j == len(allFile):
                i = 0
                for nowProcess in nowProcessAll:
                    try:
                        nowProcess.join()
                    except BaseException as e:
                        print(e)
                print(f"----------------Ok----------------------")
                nowProcessAll = []
        print(f"all Ok")
    except BaseException as e:
        print(traceback.print_exc())
        return 1
    finally:
        # 自动关机
        if shutdown:
            print(f"60s after shutdown pc")
            os.system('shutdown -s -t 60')
    
    return 0


# if __name__ == '__main__':
#     sys.exit(main())