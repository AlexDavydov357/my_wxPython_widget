# import pika
# import sys
#
import winsound
# import ctypes
# from ctypes import windll, Structure, c_long, byref  # windows only
# import threading as th
# import time, datetime
# import pickle
import os
# import wx
#
# import cv2
# import math
# import tkinter
import numpy as np
# import random
# from glob import glob
# from numba import jit, njit
#
#
# from docx.shared import Pt
# from docx.shared import Mm
# from docx.shared import RGBColor
# from docx.enum.text import WD_ALIGN_PARAGRAPH
# from docx.oxml import OxmlElement, ns
# from matplotlib.colors import LinearSegmentedColormap
# import matplotlib as mpl
# import matplotlib.pyplot as plt
# import matplotlib.ticker as ticker
# import serial
# from sklearn.cluster import KMeans



# mpl.use('Agg')

def resource_path2(relative_path):
    if os.path.exists(relative_path):
        return relative_path
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    _path = os.path.join(base_path, relative_path.split('/')[-1])
    if os.path.exists(_path):
        return _path
    return ''

def _round(val: float) -> int:
    '''Округляет до целого, переводит в int'''
    return int(round(val, 0))

def dev_config_reader():
    curr_list = []
    #     if not os.path.exists('config/'):
    if not os.path.isdir('config'):
        os.makedirs('config')
    file_name = 'config/config.csv'
    try:
        if not os.path.exists(file_name):
            restore_file_name = resource_path('config.csv')
            import shutil
            shutil.copy(restore_file_name, file_name)
        f = open(file_name, encoding='utf-8')
        try:
            curr_list = [x.strip('\n') for x in f.readlines()]
        finally:
            f.close()
    except FileNotFoundError:
        warning_dialog(f"файл конфигурации {file_name}, не найден!")
        print(f"файл {file_name} не найден")
        sys.exit()
    except Exception as e:  # любые другие ошибки
        warning_dialog(f"файл конфигурации {file_name}, не найден!")
        print(f'Неожиданная ошибка: {e}')
    return curr_list



def InfoMessageBox(text, show_time, style=0, sound=1):
    sound_ls = ['SystemExclamation', 'SystemHand']
    title = ('АСЕССОР: Уведомление!').encode('cp1251')  # cp1251
    if sound:
        winsound.PlaySound(sound_ls[style], winsound.SND_ASYNC)  # SystemExclamation

    def killer(title, show_time):
        time.sleep(show_time)
        wd = ctypes.windll.user32.FindWindowA(0, title)
        ctypes.windll.user32.SendMessageA(wd, 0x0010, 0, 0)

    th.Thread(target=killer, args=(title, show_time)).start()

    MB_SYSTEMMODAL = 0x00001000
    MB_ICONINFORMATION = 0x00000040
    ctypes.windll.user32.MessageBoxA(0, text.encode('cp1251'), title, MB_SYSTEMMODAL | MB_ICONINFORMATION)

def configWriter(config, path='config/config.csv'):
    time_string = f"# последнее обновление файла [{getTimeString()}]\n"
    try:
        with open(path, 'w', encoding='utf-8') as f:
            for line in config:
                if line[:5] == '-----':
                    break
                f.write("%s\n" % line)
            f.write("%s\n" % '-------------------------------------------------')
            f.write("%s\n" % time_string)

    except:
        msg = f'Запись {path} не удалась!'
        print(msg)
        InfoMessageBox(msg, 5)


def fig2rgb_array(fig, depth=4):
    fig.canvas.draw()
    if depth == 3:
        buf = fig.canvas.tostring_rgb()
    else:
        buf = fig.canvas.tostring_argb()
    ncols, nrows = fig.canvas.get_width_height()
    return np.frombuffer(buf, dtype=np.uint8).reshape(nrows, ncols, depth)


def val_checker(val):
    print(f"val_checker: {val} {val.count('.')}")
    if val == '.' or val == '0':
        return '0.'
    elif val.count('.') > 1:
        return '0.'  # val[:-1]
    else:
        return val

