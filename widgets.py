"""my_any_ctrl.widgets
Модуль, содержащий пользовательские виджеты для wxPython.
"""
import wx
import wx.lib.buttons as btn
from utils_.common_utils import (val_checker, _round, InfoMessageBox, configWriter, dev_config_reader, fig2rgb_array,
                                 resource_path2, post_slider_event)
import winsound
from utils_.embed_images import _ok, _infinity_big
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np
import threading as th
import time

# ----------------------------------------------------------------------
#  Глобальные константы
# ----------------------------------------------------------------------
key_sound = resource_path2("config/key_sound.wav")

__all__ = [
    "Buble_size_Pref",
    "MyStaticBox",
    "MOG_Pref",
    "PopUPField",
    "MySliderCtrl",
    "MyKnobSpinCtrl",
    "MyRadioButton",
    "MyButton",
    "MyDisplay",
    "MyGauge2",
    "MyGauge",
    "MySpinCtrl",
    "PopUPKeyboard",
    "TouchSpinCtrl",
    "TouchBtn",
    "TouchPanel",
    "XDAV",
]


class Buble_size_Pref(wx.MiniFrame):
    """ Вслпвающая панелья с полями ввода для настройки параметров пузырей """
    def __init__(self, parent, pos=wx.DefaultPosition, size=(250, 300), style=wx.DEFAULT_FRAME_STYLE):
        title = 'Настройки Параметров пузырей'
        wx.MiniFrame.__init__(self, parent, -1, title, pos, size, style)
        self.parent = parent  # videoPanel
        self.conf_data = parent.conf_data
        self.min_w = parent.min_w_bub  # минимальная ширина пузыря
        self.min_h = parent.min_h_bub  # минимальная высота пузыря
        self.max_w = parent.max_w_bub  # максимальная ширина пузыря
        self.max_h = parent.max_h_bub  # максимальная высота пузыря

        self.panel = panel = wx.Panel(self, -1)
        blankSizer = wx.BoxSizer(wx.VERTICAL)
        min_w_bs = wx.StaticBoxSizer(wx.StaticBox(panel, label='Мин. Ширина:'), wx.VERTICAL)
        min_h_bs = wx.StaticBoxSizer(wx.StaticBox(panel, label='Мин. Высота:'), wx.VERTICAL)

        max_w_bs = wx.StaticBoxSizer(wx.StaticBox(panel, label='Макс. Ширина:'), wx.VERTICAL)
        max_h_bs = wx.StaticBoxSizer(wx.StaticBox(panel, label='Макс. Высота:'), wx.VERTICAL)

        self.Items()

        min_w_bs.Add(self.min_w_bub, flag=wx.EXPAND | wx.ALL, border=5)
        min_h_bs.Add(self.min_h_bub, flag=wx.EXPAND | wx.ALL, border=5)
        max_w_bs.Add(self.max_w_bub, flag=wx.EXPAND | wx.ALL, border=5)
        max_h_bs.Add(self.max_h_bub, flag=wx.EXPAND | wx.ALL, border=5)
        h_box1 = wx.BoxSizer(wx.HORIZONTAL)
        h_box2 = wx.BoxSizer(wx.HORIZONTAL)
        h_box1.Add(min_w_bs, flag=wx.ALL, border=5)
        h_box1.Add(min_h_bs, flag=wx.ALL, border=5)
        blankSizer.Add(h_box1, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        h_box2.Add(max_w_bs, flag=wx.ALL, border=5)
        h_box2.Add(max_h_bs, flag=wx.ALL, border=5)
        blankSizer.Add(h_box2, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        blankSizer.Add(self.save_btn, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        blankSizer.Add(self.btnCn, flag=wx.ALIGN_CENTER | wx.ALL, border=5)

        panel.SetSizer(blankSizer)
        self.BindItems()
        self.Layout()

    def BindItems(self):
        # self.Bind(wx.EVT_BUTTON, self.OnCloseMe, self.button)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.btnCn.Bind(wx.EVT_BUTTON, self.OnCloseWindow)
        self.save_btn.Bind(wx.EVT_BUTTON, self.SaveOffset)

    def GetParams(self):
        return (self.min_w_bub.GetValue(), self.min_h_bub.GetValue(), self.max_h_bub.GetValue(),
                self.max_w_bub.GetValue())

    def Items(self):

        self.min_w_bub = MySpinCtrl(self.panel, name='min_w', font_size=14, type='int', style=wx.BORDER_SUNKEN)
        self.min_w_bub.SetToolTip('Количество кадров для обучения детектора (больше - лучше) ')
        self.min_w_bub.SetRange(1, 100)
        self.min_w_bub.SetValue(self.min_w)

        self.min_h_bub = MySpinCtrl(self.panel, name='varThreshold', font_size=14, type='int',
                                       style=wx.BORDER_SUNKEN)
        self.min_h_bub.SetToolTip(
            'Порог, ниже которого модель будет считать объект неподвижным, малые значения - много ложных срабатываний')
        self.min_h_bub.SetRange(1, 100)
        self.min_h_bub.SetMinSize((60, -1))
        self.min_h_bub.SetValue(self.min_h)

        self.max_w_bub = MySpinCtrl(self.panel, name='kernel_size', font_size=14, type='int', style=wx.BORDER_SUNKEN)
        self.max_w_bub.SetToolTip(
            'Размер ядра фильтра. Меньше - больше шум, больше - меньше шум. Оптимальное значение 5')
        self.max_w_bub.SetRange(2, 300)
        self.max_w_bub.SetMinSize((60, -1))
        self.max_w_bub.SetValue(self.max_w)

        self.max_h_bub = MySpinCtrl(self.panel, name='kernel_size', font_size=14, type='int', style=wx.BORDER_SUNKEN)
        self.max_h_bub.SetToolTip(
            'Количество проходов фильтра. Для обнаружения мелких пузырьков оптимально значение 0')
        self.max_h_bub.SetRange(2, 300)
        self.max_h_bub.SetMinSize((60, -1))
        self.max_h_bub.SetValue(self.max_h)

        self.save_btn = btn.ThemedGenBitmapTextButton(self.panel, wx.ID_OK, _ok.GetBitmap(),
                                                      "Сохранить настройки", size=(170, 36))
        self.save_btn.SetUseFocusIndicator(False)

        self.btnCn = wx.Button(self.panel, wx.ID_CANCEL, label='Закрыть', size=(170, 30))

    def OnCloseWindow(self, event):
        self.Destroy()

    def SaveOffset(self, e):

        min_w = self.min_w_bub.GetValue()
        min_h = self.min_h_bub.GetValue()
        max_w = self.max_w_bub.GetValue()
        max_h = self.max_h_bub.GetValue()

        self.conf_data[10] = f'предельные_размеры_пузыря: {min_w} {min_h} {max_w} {max_h}'
        self.parent.min_w_bub = min_w
        self.parent.min_h_bub = min_h
        self.parent.max_w_bub = max_w
        self.parent.max_h_bub = max_h

        configWriter(self.conf_data)
        self.Destroy()


class MyStaticBox(wx.StaticBoxSizer):
    """ Статический бокс с возможностью изменения шрифта, лэйбла и контролем размера
    param
    parent: panel
    label: str
    font_size: int
    size: wx.Size
    orient: wx.HORIZONTAL or wx.VERTICAL
    """
    def __init__(self, parent, label='', font_size=None, size=wx.DefaultSize, orient=wx.HORIZONTAL):
        self.box = wx.StaticBox(parent, label=label, size=size)
        if font_size is not None:
            self.SetFont(font_size)
        wx.StaticBoxSizer.__init__(self, self.box, orient)

    def SetFont(self, font_size):
        self.box.SetFont(wx.Font(wx.FontInfo(font_size)))

    def SetLabel(self, label):
        self.box.SetLabel(label)

    def SetMinSize(self, size):
        self.box.SetMinSize(size)


class MOG_Pref(wx.MiniFrame):
    """ Вслывающая панель с полями ввода для настройки параметров MOG фильтра """
    def __init__(self, parent, pos=wx.DefaultPosition, size=(300, 400), style=wx.DEFAULT_FRAME_STYLE):
        title = 'Настройки MOG детектора'
        wx.MiniFrame.__init__(self, parent, -1, title, pos, size, style)
        self.parent = parent  # videoPanel

        self.panel = panel = wx.Panel(self, -1)
        blankSizer = wx.BoxSizer(wx.VERTICAL)
        sb_hist = wx.StaticBoxSizer(wx.StaticBox(panel, label='Кол-во кадров:'), wx.VERTICAL)
        sb_thresh = wx.StaticBoxSizer(wx.StaticBox(panel, label='Порог:'), wx.VERTICAL)

        sb_kernel = wx.StaticBoxSizer(wx.StaticBox(panel, label='Размер ядра:'), wx.VERTICAL)
        sb_iter = wx.StaticBoxSizer(wx.StaticBox(panel, label='Итераций:'), wx.VERTICAL)

        self.Items()

        sb_hist.Add(self.history, flag=wx.EXPAND | wx.ALL, border=5)
        sb_thresh.Add(self.varThreshold, flag=wx.EXPAND | wx.ALL, border=5)
        sb_kernel.Add(self.kernel_size, flag=wx.EXPAND | wx.ALL, border=5)
        sb_iter.Add(self.iterations, flag=wx.EXPAND | wx.ALL, border=5)
        h_box1 = wx.BoxSizer(wx.HORIZONTAL)
        h_box2 = wx.StaticBoxSizer(wx.StaticBox(panel, label='Настройка фильтра:'), wx.HORIZONTAL)
        h_box1.Add(sb_hist, flag=wx.ALL, border=5)
        h_box1.Add(sb_thresh, flag=wx.ALL, border=5)
        blankSizer.Add(h_box1, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        h_box2.Add(sb_kernel, flag=wx.ALL, border=5)
        h_box2.Add(sb_iter, flag=wx.ALL, border=5)
        blankSizer.Add(h_box2, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        blankSizer.Add(self.filtering, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        blankSizer.Add(self.detectShadows, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        blankSizer.Add(self.save_btn, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        blankSizer.Add(self.btnCn, flag=wx.ALIGN_CENTER | wx.ALL, border=5)

        panel.SetSizer(blankSizer)
        self.BindItems()
        self.Layout()

    def BindItems(self):
        # self.Bind(wx.EVT_BUTTON, self.OnCloseMe, self.button)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.btnCn.Bind(wx.EVT_BUTTON, self.OnCloseWindow)
        self.save_btn.Bind(wx.EVT_BUTTON, self.SaveOffset)

    def Items(self):
        self.filtering = wx.CheckBox(self.panel, -1, "Применять фильтрацию шума")
        if self.parent.filtering_MOG:
            self.filtering.SetValue(True)
        self.detectShadows = wx.CheckBox(self.panel, -1, "Учитывать блики")
        if self.parent.detectShadow_MOG:
            self.detectShadows.SetValue(True)
        self.detectShadows.SetToolTip(
            'Включение данного параметра может привести к ложным срабатываниям. Необходимо тестирование')

        self.history = MySpinCtrl(self.panel, name='history', font_size=14, type='int', style=wx.BORDER_SUNKEN)
        self.history.SetToolTip('Количество кадров для обучения детектора (больше - лучше) ')
        self.history.SetRange(1, 1000)
        self.history.SetValue(self.parent.history_MOG)

        self.varThreshold = MySpinCtrl(self.panel, name='varThreshold', font_size=14, type='int',
                                       style=wx.BORDER_SUNKEN)
        self.varThreshold.SetToolTip(
            'Порог, ниже которого модель будет считать объект неподвижным, малые значения - много ложных срабатываний')
        self.varThreshold.SetRange(1, 255)
        self.varThreshold.SetValue(self.parent.threshold_MOG)
        self.varThreshold.SetMinSize((60, -1))
        """ varianceThreshold (float)
        Что делает: Порог для удаления из модели Гауссианов, которые имеют дисперсию (разброс), меньшую чем этот порог. Гауссианы с низкой дисперсией считаются «статичными» и могут быть удалены, чтобы упростить модель.
        Диапазон: Положительное вещественное число (> 0). Типичные значения: 0.5–10.0.
        Контекст:
        Малые значения: Удаляются только очень «узкие» Гауссианы, модель становится сложнее.
        Большие значения: Удаляются многие Гауссианы, модель упрощается, но может хуже описывать детали (например, мелкие пузырьки).
        Рекомендация: Значение 2.0–5.0 является безопасным для большинства задач. """

        self.kernel_size = MySpinCtrl(self.panel, name='kernel_size', font_size=14, type='int', style=wx.BORDER_SUNKEN)
        self.kernel_size.SetToolTip(
            'Размер ядра фильтра. Меньше - больше шум, больше - меньше шум. Оптимальное значение 5')
        self.kernel_size.SetRange(1, 20)
        self.kernel_size.SetValue(self.parent.kernel_MOG)
        self.kernel_size.SetMinSize((60, -1))

        self.iterations = MySpinCtrl(self.panel, name='kernel_size', font_size=14, type='int', style=wx.BORDER_SUNKEN)
        self.iterations.SetToolTip(
            'Количество проходов фильтра. Для обнаружения мелких пузырьков оптимально значение 0')
        self.iterations.SetRange(0, 5)
        self.iterations.SetValue(self.parent.iter_MOG)
        self.iterations.SetMinSize((60, -1))

        self.save_btn = btn.ThemedGenBitmapTextButton(self.panel, wx.ID_OK, _ok.GetBitmap(),
                                                      "Сохранить настройки", size=(170, 36))
        self.save_btn.SetUseFocusIndicator(False)

        self.btnCn = wx.Button(self.panel, wx.ID_CANCEL, label='Закрыть', size=(170, 30))

    def OnCloseWindow(self, event):
        self.Destroy()

    def SaveOffset(self, e):
        self.conf_data = dev_config_reader()
        self.parent.filtering_MOG = self.filtering.GetValue()
        self.parent.detectShadow_MOG = self.detectShadows.GetValue()
        self.parent.history_MOG = self.history.GetValue()
        self.parent.threshold_MOG = self.varThreshold.GetValue()
        self.parent.kernel_MOG = self.kernel_size.GetValue()
        self.parent.iter_MOG = self.iterations.GetValue()

        self.conf_data[25] = f'фильтрация_маски: {1 if self.filtering.GetValue() else 0}  # filtering'
        self.conf_data[26] = f'detectShadows: {1 if self.detectShadows.GetValue() else 0} # работа с бликами '
        self.conf_data[
            27] = f'history: {self.history.GetValue()}    # настройка для алгоритмов детекции сколько кадров нужно для обучения модели на фоне, больше лучше'
        self.conf_data[28] = f'varThreshold_MOG2 {self.varThreshold.GetValue()}'
        self.conf_data[29] = f'kernel_MOG: {self.kernel_size.GetValue()}'
        self.conf_data[30] = f'iteration_MOG: {self.iterations.GetValue()}'
        configWriter(self.conf_data)
        self.Destroy()


class PopUPField(wx.Frame):  # miniframe не теряет фокус при открытии
    """ Всплывающее окно с полем ввода
    """
    def __init__(self, parent, mainParent, color, size=(150, 100)):  #
        self.focuskill_flag = False
        wx.MiniFrame.__init__(self, parent, -1, '', size=size, style=wx.BORDER_DOUBLE | wx.FRAME_FLOAT_ON_PARENT)
        # parent.display.CenterOnParent(wx.BOTH)
        x, y = parent.display.GetScreenPosition()
        self.SetPosition((x - 50, y - 40))  # parent.display.GetPosition())

        self.parent = parent
        self.mainParent = mainParent
        self.shit_count = 0
        self.val_mem = parent.value
        self.max_value = parent.max_value
        self.min_value = parent.min_value
        self.name = parent.name
        self.type = parent.type

        self.panel = wx.Panel(self, -1)
        self.SetBgColor(color)  # наследуем цвет панели от родителя
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        # mainSizer.Add(self.vbox, proportion=0, flag=wx.ALIGN_CENTER)

        self.display = wx.TextCtrl(self.panel, -1,
                                   style=wx.NO_BORDER | wx.TE_PROCESS_ENTER | wx.TE_CENTER | wx.TE_RICH2)
        self.display.SetBackgroundColour(color)
        self.display.SetFont(wx.Font(30, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.display.Bind(wx.EVT_CHAR, self.blockNonNumber)
        self.Bind(wx.EVT_TEXT_ENTER, self.TextEnter)
        self.display.Bind(wx.EVT_KILL_FOCUS, self.FocusKill)
        self.display.Bind(wx.EVT_SET_FOCUS, self.FocusSet)
        self.panel.Bind(wx.EVT_SET_FOCUS, self.FocusPanSet)
        self.panel.Bind(wx.EVT_KILL_FOCUS, self.FocusPanKill)
        # self.Bind(wx.EVT_SIZE, self.OnSize)

        mainSizer.Add((1, 1), proportion=1, flag=wx.EXPAND)
        mainSizer.Add(self.display, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        mainSizer.Add((1, 1), proportion=1, flag=wx.EXPAND)

        self.panel.SetSizerAndFit(mainSizer)
        self.Layout()
        self.Show()

    def FocusPanKill(self, e):
        print('FocusPanKill')

    def FocusPanSet(self, e):
        print('FocusPanSet')

    def blockNonNumber(self, event):
        key = event.GetKeyCode()
        cur_val = ''
        print('blockNonNumber: ', key, 'cur_field_name: ', self.name, chr(key))
        allowed_sym = [44, 46, '\t', 8, 127, 315, 317]  # , 314, 316]  # точка, таб, bcksp 8, del 127, влево, вправо

        if key == 13:  # Ввод
            event.Skip()

        elif key == 27:  # Esc
            self.parent.SetValue(self.val_mem)
            self.Destroy()
            return

        if chr(key) == ',':
            self.display.SetValue(
                f'{self.display.GetValue()[-1]}.')  # обновяем значение в поле после замены запятой на точку
            return

        if '.' in self.display.GetValue() and key == 46:
            return
        # разрешаем все цифры
        if ord('0') <= key <= ord('9') or key in allowed_sym:
            if key in [8, 127, 315, 317]:  # 314 316
                cur_val = val_checker(self.display.GetValue())
            else:
                cur_val = val_checker(self.display.GetValue() + chr(key))

            print(f'blockNonNumber: {cur_val}')
            if key == 315 or key == 317:
                self.btn_up_down_ctrl(key)
                return
            if cur_val:
                if key != 315 or key != 317:
                    if float(cur_val) > self.parent.max_value:
                        print(f'PlaySound 1: {cur_val}')
                        winsound.PlaySound("SystemExclamation", winsound.SND_ASYNC)
                        self.display.SetValue(str(self.parent.max_value))
                        return
                    # if float(cur_val) < self.parent.min_value:
                    #     print(f'PlaySound 2: {cur_val}')
                    #     winsound.PlaySound("SystemExclamation", winsound.SND_ASYNC)
                    #     self.display.SetValue(str(self.parent.min_value))
                    #     return

            event.Skip()
        else:
            self.shit_count += 1
            if self.shit_count > 5:
                InfoMessageBox('Прекратите вводить с клавиатуры всякое дерьмо!\n'
                               'Для воода допустимы только цифры и точка!', 5, sound=True)
                self.shit_count = 0

    def play_sound(self, path_to_sound):
        # print('play_sound')
        try:
            winsound.PlaySound(path_to_sound, winsound.SND_ASYNC)
        except:
            pass

    def btn_up_down_ctrl(self, key):
        """ Код 315 стрелка вверх"""
        cur_val = 0
        increment = 0
        if key == 315:  # стрелка вверх
            increment = self.parent.increment
        elif key == 317:  # стрелка вниз
            increment = self.parent.increment * -1

        if self.display.GetValue() == '':
            cur_val = self.parent.value
        else:
            cur_val = float(self.display.GetValue())

        cur_val += increment
        if cur_val > self.parent.max_value:
            cur_val = self.parent.max_value
            print(f'PlaySound 1: {cur_val}')
            winsound.PlaySound("SystemExclamation", winsound.SND_ASYNC)
        elif cur_val <= self.parent.min_value:
            cur_val = self.parent.min_value
            print(f'PlaySound 2: {cur_val}')
            winsound.PlaySound("SystemExclamation", winsound.SND_ASYNC)

        # Присваиваем значение в конце
        self.display.SetValue(str(cur_val))

    def FocusKill(self, e=None):
        # print('FocusKill', time.time() - self.life_time )
        # if time.time() - self.life_time > 0.5:
        #     print('FocusKill')
        self.Destroy()
        e.Skip()

    def FocusSet(self, e=None):
        print('FocusSet')
        e.Skip()

    def OnSize(self, e=None):
        self.panel.Layout()
        # self.Layout()
        e.Skip()

    def SetBgColor(self, color):
        if isinstance(color, str):
            self.panel.SetBackgroundColour(color)
        elif isinstance(color, tuple):
            self.panel.SetBackgroundColour(wx.Colour(color))
        else:
            self.panel.SetBackgroundColour(color)

    def TextEnter(self, e=None):
        print('TextEnter:', self.display.GetValue())
        self.focuskill_flag = False

        try:
            if len(self.display.GetValue()) > 1:
                if self.display.GetValue()[0] == '0' and self.display.GetValue()[1] != '.':
                    cur_val = round(float('0.' + self.display.GetValue()[1:]), 1)
                else:
                    cur_val = round(float(self.display.GetValue()), 1)
            else:
                cur_val = round(float(self.display.GetValue()), 1)
        except:
            cur_val = self.val_mem

        cur_val = self.min_value if cur_val < self.min_value else cur_val
        cur_val = self.max_value if cur_val > self.max_value else cur_val

        self.parent.SetValue(cur_val)
        self.Destroy()


class MySliderCtrl(wx.Panel):
    def __init__(self, parent, name='', label='', font_size=wx.DefaultSize, color=wx.WHITE, type='float', style_panel=wx.NO_BORDER,
                 style_slider=None, orient='H', bmp=None, bmp_pos='right', drop=False, null=False):
        """Универсальное поле ввода с индикатором и слайдером
        style_panel: wx.NO_BORDER, wx.SUNKEN_BORDER, wx.RAISED_BORDER, wx.SIMPLE_BORDER
        style_slider: wx.SL_HORIZONTAL, wx.SL_VERTICAL, wx.SL_TICKS, wx.SL_AUTOTICKS, wx.SL_LABELS, wx.SL_LEFT, wx.SL_RIGHT, wx.SL_BOTH
        type: 'int' - 1 or 'float' - 0.1 позволяет задать шаг для float
        orient: 'H' or 'V' ориентация слайдера H - горизонтальная V - вертикальная
        bmp: wx.Bitmap или None - иконка может располагаться left, right, top, bottom по умолчанию right
        Флаг self.drop - для активации пункта выпадающего меню - сбросить значения к исходным
        Флаг self.null - для активации пункта выпадающего меню - обнулить значение
        """
        wx.Panel.__init__(self, parent=parent, id=-1, style=style_panel)
        self.tooltip = ''
        self.parent = parent
        self.name = name
        self.label = label
        self.color = color
        self.value = self.default_value = 0
        self.mem_value = 0
        self.icon = None
        # список доступных шагов (по‑умолчанию – стандартный набор)
        self._inc_items = [1, 5, 10, 25, 50, 100]
        if type == 'float':
            self._inc_items = [0.01, 0.05, 0.1, 1.0, 5.0, 10.0]
        # словарь id → шаг, будет построен в `Menu()`
        self._inc_dict = {}

        if type == 'int':
            self.max_value = 100
        else:
            self.max_value = 1000
        self.orientation = 1 if orient == 'H' else 0
        self.min_value = 0
        self.type = type
        self.increment = self._inc_items[0]  # шаг

        self.popup_win = None
        self.drop = drop  # флаг для активации пункта выпадающего меню
        self.null = null
        self.scale = 1 # масштаб пересчета значения слайдера в реальное значение
        # self.SetBackgroundColour(wx.BLACK)

        # self.display = wx.TextCtrl(self, -1, '0', style=wx.TE_PROCESS_ENTER | wx.TE_CENTER, size=(75, -1), name='display')
        # self.display = wx.StaticText(self, -1, label=f'{self.label}: 0', name='display')
        # self.display.SetMinSize((30, -1))
        # self.display.SetFont(wx.Font(wx.FontInfo(font_size)))
        if bmp is not None:
            self.icon = wx.StaticBitmap(self, -1, bmp)


        if orient == 'H':
            self.slider = wx.Slider(self, -1, self.value, self.min_value, self.max_value,
                                    name=self.name, style=wx.SL_HORIZONTAL|style_slider)
            self.display = wx.TextCtrl(self, -1, f'{self.label}: 100', style=wx.TE_READONLY|wx.SUNKEN_BORDER|wx.TE_CENTER)
            self.display.SetFont(wx.Font(wx.FontInfo(font_size)))
            self.display.SetMinSize((200, -1))
            sizer = wx.BoxSizer(wx.HORIZONTAL)
            hbox = wx.BoxSizer(wx.HORIZONTAL)
            if bmp is not None and bmp_pos == 'left':
                hbox.Add(self.icon, flag=wx.ALIGN_CENTER)
            hbox2 = wx.BoxSizer(wx.HORIZONTAL)
            hbox2.Add(self.display, 1, flag=wx.EXPAND)
            hbox2.SetMinSize((70,-1))
            hbox.Add(hbox2, flag=wx.EXPAND|wx.RIGHT, border=5)
            hbox.Add(self.slider, proportion=1)
            if bmp is not None and bmp_pos == 'right':
                hbox.Add(self.icon, flag=wx.ALIGN_CENTER)
            sizer.Add(hbox, proportion=1, flag=wx.EXPAND)
        else:
            #self.gate_name = wx.StaticText(self, -1, label=self.label, name='gate_name', style=wx.ALIGN_CENTER)
            self.display = wx.StaticText(self, -1, label='3', name='display', style=wx.ALIGN_CENTER)
            self.display.SetFont(wx.Font(wx.FontInfo(font_size)))
            self.slider = wx.Slider(self, -1, self.value, self.min_value, self.max_value, name=self.name,
                                    style=wx.SL_VERTICAL|wx.SL_INVERSE|style_slider)
            self.slider.SetFont(wx.Font(wx.FontInfo(1)))
            sizer = wx.BoxSizer(wx.VERTICAL)
            if bmp is not None and bmp_pos == 'top':
                sizer.Add(self.icon, flag=wx.ALIGN_CENTER)
            sizer.Add(self.display, flag=wx.ALIGN_CENTER)
            sizer.Add(self.slider, proportion=1, flag=wx.ALIGN_CENTER)
            if bmp is not None and bmp_pos == 'bottom':
                sizer.Add(self.icon, flag=wx.ALIGN_CENTER)

            self.slider.Bind(wx.EVT_SLIDER, self._forward_slider_event)  # проброс события слайдера в родителя
            # sizer1.Add(sizer)

        self._recalc_range_for_float()
        self.SetSizer(sizer)
        self.Layout()

        self.Menu()
        self.slider.Bind(wx.EVT_SLIDER, self.val_ctrl)
        self.slider.Bind(wx.EVT_MOUSEWHEEL, self.MouseWheel)
        self.slider.Bind(wx.EVT_RIGHT_UP, self.right_m_down)
        self.display.Bind(wx.EVT_RIGHT_UP, self.right_m_down)


    def _adjust_display_width(self, max_int_val: int):
        """
        Вспомогательный метод для изменения ширины поля display.
        Выбирает минимальный размер `display` в зависимости от количества
        цифр в максимальном значении. Работает как для int, так и для float.
        """
        # количество цифр в целой части (для float‑режима уже масштабировано)
        digits = len(str(abs(max_int_val)))
        # простая эвристика: 7‑10 пикселей на цифру + небольшие отступы
        width = max(30, digits * 8 + 20)
        self.display.SetMinSize((width, -1))

    def _forward_slider_event(self, event):
        """
        Прокидывает событие EVT_SLIDER от внутреннего wx.Slider наружу.
        После этого любой объект, который привязал обработчик к
        экземпляру MySliderCtrl, получит событие.
        """
        # Генерируем то же самое событие, но с источником = self
        # (это позволяет использовать обычный Bind на панели)
        wx.PostEvent(self, event)
        # Если кто‑то ещё хочет обработать событие у самого слайдера,
        # пропускаем его дальше по иерархии.
        event.Skip()

    # ----------------------------------------------------------------------
    # 1. Внутренний помощник – перевод «логического» диапазона в целый
    # ----------------------------------------------------------------------
    def _float_to_int(self, val: float) -> int:
        """
        Преобразует значение, которое пользователь видит (float),
        в целое, которое реально хранит wx.Slider.

        Для float‑режима масштаб = 10ⁿ, где n – количество знаков
        после запятой у текущего шага (self.increment).
        """
        scale = 10 ** self._float_precision()
        return int(round(val * scale))

    def _int_to_float(self, val: int) -> float:
        """
        Обратное преобразование: из целого, полученного от wx.Slider,
        в «логическое» float‑значение.
        """
        scale = 10 ** self._float_precision()
        return round(val / scale, self._float_precision())

    def _float_precision(self) -> int:
        """
        Возвращает количество знаков после запятой, которое требуется
        для представления текущего шага (self.increment).
        Пример: 0.1 → 1, 0.01 → 2, 1 → 0.
        """
        # self.increment всегда кратен 10⁻n, поэтому достаточно посчитать
        # сколько нулей после запятой.
        s = f'{self.increment:.10f}'.rstrip('0')
        if '.' in s:
            return len(s.split('.')[1])
        return 0

    def SetTickFreq(self, freq):
        """ Устанавливает частоту меток на слайдере
        Пример: для диапазаона 0-255 частота 127 означает метки на 0, 127, 255"""
        self.slider.SetTickFreq(freq)

    def Menu(self):
        """
        Создаёт (или пересоздаёт) контекстное меню.
        Список пунктов берётся из ``self._inc_items``.
        Если в списке только один элемент – меню не создаётся
        (только пункт «Закрыть» и, при необходимости, «Обнулить»).
        """
        self.ctx_menu = ctx = wx.Menu(style=wx.MENU_TEAROFF)

        # очистим старый словарь id → шаг
        self._inc_dict.clear()

        if self.drop:
            ctx.Append(338, "Сбросить", kind=wx.ITEM_NORMAL)
            self.Bind(wx.EVT_MENU, self.Drop2Default, id=338)

        if self.null:
            ctx.Append(337, "Обнулить", kind=wx.ITEM_NORMAL)
            self.Bind(wx.EVT_MENU, self.SetNull, id=337)


        # если вариантов больше одного – формируем пункты‑радиокнопки
        if len(self._inc_items) > 1:
            if self.drop or self.null:
                ctx.AppendSeparator()
            for idx, step in enumerate(self._inc_items, start=331):
                ctx.Append(idx, str(step), kind=wx.ITEM_RADIO)
                self._inc_dict[idx] = step
            ctx.AppendSeparator()
            ctx.Append(wx.ID_ANY, "Закрыть", kind=wx.ITEM_NORMAL)


        if self.type == 'float':
            self.Bind(wx.EVT_MENU, self._set_increment, id=331, id2=336)
        else:
            self.Bind(wx.EVT_MENU, self._set_increment, id=331, id2=336)

    def Drop2Default(self, e=None):
        """ Приводит значение к исходному """
        self.mem_value = self.value
        self.SetValue(self.default_value)
        post_slider_event(self)


    def menu_add_drop_to_zero(self):
        """Добавляет пункт меню для обнуления значения"""
        self.drop = True
        self.Menu()

    def MouseWheel(self, e: wx.MouseEvent = None) -> None:
        """
        Обрабатывает вращение колёсика мыши.
        Работает одинаково в int‑ и float‑режимах, без «скачков».
        """
        # --------------------------------------------------------------
        # 1. Сколько «щелчков» было в этом событии?
        #    120 → один щелчок вперёд, -120 → один назад,
        #    240 → два вперёд и т.д.
        # --------------------------------------------------------------
        wheel_steps = e.GetWheelRotation() // 120  # целочисленное деление сохраняет знак
        if wheel_steps == 0:  # иногда бывает 0 (медленное вращение)
            e.Skip()
            return

        # --------------------------------------------------------------
        # 2. Текущее значение «внутри» слайдера (целое)
        # --------------------------------------------------------------
        cur_int = self.slider.GetValue()  # уже в целых, которые понимает wx.Slider

        # --------------------------------------------------------------
        # 3. Вычисляем шаг в том же масштабе, что и слайдер
        # --------------------------------------------------------------
        if self.type == 'float':
            # шаг в целых (например, 0.1 → 1, 0.01 → 1, 5.0 → 5)
            step_int = self._float_to_int(self.increment)

            # новое целое значение
            new_int = cur_int + wheel_steps * step_int

            # ограничиваем диапазоном, чтобы не выйти за пределы
            new_int = max(self.min_value, min(self.max_value, new_int))

            # Устанавливаем новое значение через SetValue (которая сделает обратный перевод)
            self.SetValue(self._int_to_float(new_int))
        else:
            # int‑режим – шаг уже целый
            step_int = int(self.increment)  # гарантируем int
            new_int = cur_int + wheel_steps * step_int
            new_int = max(self.min_value, min(self.max_value, new_int))
            self.SetValue(new_int)

        # --------------------------------------------------------------
        # 4. Пропускаем событие дальше, если кто‑то ещё хочет его обработать
        # --------------------------------------------------------------
        e.Skip()

    def MouseWheel_old(self, e=None):
        direction = e.GetWheelRotation() // 120  # направление
        print(f'MouseWheel value: {self.value} {direction * self.increment} {direction} {self.increment}')
        if direction == 0:  # иногда бывает 0 (например, при очень медленном вращении)
            if e is not None:
                e.Skip()
            return
        # 2. Текущее «логическое» значение (float или int)
        cur_val = self.slider.GetValue()
        if self.type == 'float':
            cur_val = self._int_to_float(cur_val)  # переводим в float

        # 3. Вычисляем шаг в том же масштабе, что и значение
        #    Для float‑режима переводим шаг в целое, иначе оставляем как есть
        if self.type == 'float':
            step_int = self._float_to_int(self.increment)  # шаг в целых
            new_val_int = cur_val * (10 ** self._float_precision()) + direction * step_int
            # Приводим к целому, чтобы не было «плавающих» остатков
            new_val_int = int(round(new_val_int))
            # 4. Устанавливаем новое значение через SetValue (которая сама сделает обратный перевод)
            self.SetValue(self._int_to_float(new_val_int))
        else:
            # int‑режим – шаг уже целый
            new_val = cur_val + direction * self.increment
            self.SetValue(new_val)

        if e is not None:
            e.Skip()

    def SetLabel(self, label):
        """ Устанавливает текст к слайдеру"""
        self.display.SetLabel(label)
        self.display.Layout()


    def _recalc_range_for_float(self):
        """
        Вспомогательная функция – пересчёт диапазона для float‑режима
        Пересчитывает min/max‑значения с учётом текущей точности
        (self.increment).  Сохраняет «логический» диапазон в атрибутах
        _logical_min/_logical_max и обновляет wx.Slider.
        """
        # количество знаков после запятой у шага
        prec = self._float_precision()

        # масштаб = 10**prec
        self.scale = scale = 10 ** prec

        # логический диапазон (то, что видит пользователь)
        lo_min = getattr(self, "_logical_min", self.min_value)
        lo_max = getattr(self, "_logical_max", self.max_value)

        # переводим в целый диапазон, который понимает wx.Slider
        self.min_value = int(round(lo_min * scale))
        self.max_value = int(round(lo_max * scale))

        # сохраняем логический диапазон для последующего использования
        self._logical_min = lo_min
        self._logical_max = lo_max

        # применяем к слайдеру
        self.slider.SetRange(self.min_value, self.max_value)

        # подгоняем ширину поля вывода (чтобы не «обрезать» большие числа)
        self._adjust_display_width(self.max_value)

        # если текущее значение уже находится за пределами нового диапазона –
        # корректируем его
        if self.value < lo_min:
            self.SetValue(lo_min)
        elif self.value > lo_max:
            self.SetValue(lo_max)

    def _set_increment(self, e):
        """
        Обработчик пункта контекстного меню (EVT_MENU).  Получает id
        выбранного пункта и меняет шаг `self.increment`.  После
        изменения шага вызывается `_recalc_range_for_float`, если тип
        контролa – float.
        """
        step = self._inc_dict.get(e.GetId())
        if step is None:                     # неизвестный пункт – игнорируем
            return

        self.increment = step
        self.display.SetToolTip(f'{self.tooltip}, шаг: {self.increment}')
        self.slider.SetToolTip(f'{self.tooltip}, шаг: {self.increment}')

        # При float‑режиме меняется точность, поэтому пересчитываем диапазон
        if self.type == 'float':
            self._recalc_range_for_float()

    def SetIncrement(self, inc_list: list[float | int] | int | float) -> None:
        """
        Задаёт набор шагов инкремента, которые будут отображаться в контекстном меню.
        * inc_list – список от 0 до 6 чисел (int/float). или int/float --> в список
          Если список пустой – оставляем текущий набор [0.1, 1, 5, 10, 50, 100]
          Если в списке один элемент – меню будет отключено (только один вариант).
        После вызова меню будет перестроено.
        """
        if isinstance(inc_list, (int, float)):
            inc_list = [float(inc_list)]


        if not inc_list:                     # пустой список – ничего не меняем
            return

        # оставляем только первые 6 элементов и приводим к типу float
        self._inc_items = [float(v) for v in inc_list[:6]]

        self.increment = self._inc_items[0]
        # пересоздаём меню, чтобы отразить новые варианты
        self.Menu()
        # При float‑режиме меняем масштаб диапазона

        if self.type == 'float':
            self._recalc_range_for_float()


    def SetValue(self, val: int | float, set_as_default=False):
        """
         Устанавливает текущее значение и синхронно обновляет слайдер
         и текстовое поле. При float‑режиме значение переводится в целое.
         Флаг `set_as_default` – устанавливает значение как «по‑умолчанию» для сброса и возврата к нему.
         """
        self.value = float(val)
        self.mem_value = self.value
        if set_as_default:
            self.default_value = self.value

        if self.orientation:
            self.SetLabel(f'{self.label}: {self.round_val(val)}')
        else:
            self.SetLabel(str(self.round_val(val)))

        # Устанавливаем значение в слайдере (внутреннее целое)
        if self.type == 'float':
            self.slider.SetValue(self._float_to_int(self.value))
        else:
            self.slider.SetValue(int(self.value))
        self.val_ctrl()
        self.Layout()

    def SetNull(self, e=None):
        """ Устанавливает значение в 0 """
        self.SetValue(0)
        post_slider_event(self)

    def SetMinSize(self, size):
        """Устанавливает минимальный размер панели и переразмещает дочерние окна."""
        # вызываем оригинальный метод из wx.Window
        super().SetMinSize(size)
        # обновляем компоновку, если размеры изменились
        self.Layout()

    def SetToolTip(self, tip):
        self.display.SetToolTip(tip)
        self.slider.SetToolTip(tip)
        self.tooltip = tip
        if self.icon is not None:
            self.icon.SetToolTip(tip)

    def GetValue(self):
        return self.round_val(self.value)

    def GetMemValue(self):
        return self.mem_value

    def SetMax(self, val: int|float):
        """Устанавливает верхнюю границу диапазона."""
        self.max_value = int(val)
        if self.type == 'float':
            self.max_value = self._float_to_int(val)
        self.slider.SetMax(self.max_value)
        self._adjust_display_width(self.max_value)

    def SetMin(self, val: int|float):
        """Устанавливает только нижнюю границу диапазона."""
        self.min_value = val
        if self.type == 'float':
            self.min_value = self._float_to_int(val)
        self.slider.SetMin(self.min_value)

    def SetRange(self, min_val: int|float=-1000, max_val: int|float=1000):
        """ Устанавливает диапазон значений для слайдера
        min_val: int или float, max_val: int или float"""
        # Сохраняем «логический» диапазон (для отображения пользователю)
        self._logical_min = min_val
        self._logical_max = max_val

        if self.type == 'float':
            # масштабируем диапазон к целым числам
            self.min_value = self._float_to_int(min_val)
            self.max_value = self._float_to_int(max_val)
        else:
            self.min_value = int(min_val)
            self.max_value = int(max_val)

        # Подгоняем размер поля отображения в зависимости от ширины max‑значения
        self._adjust_display_width(self.max_value)

        self.slider.SetRange(self.min_value, self.max_value)
        self.val_ctrl()          # обновляем отображаемое значение
        self.Layout()

    def right_m_down(self, e):
        self.PopupMenu(self.ctx_menu)

    def round_val(self, val):
        if self.type == 'float':
            return round(float(val), 1)
        else:
            return _round(val)

    def val_ctrl(self, e=None):
        """
        Обработчик изменения положения ползунка.
        Преобразует целое значение слайдера в «логическое» значение
        (float, если требуется) и обновляет отображение.
        """

        cur_val = self.slider.GetValue()
        if self.type == 'float':
            cur_val = self._int_to_float(cur_val)

        self.mem_value = self.value
        self.value = cur_val
        if self.orientation:
            # print(f'val_ctrl {self.name} {self.value}')
            self.SetLabel(f'{self.label}: {self.round_val(cur_val)}')
        else:
            self.SetLabel(f'{self.round_val(cur_val)}')
        self.slider.Layout()
        self.Layout()
        if e is not None:
            e.Skip()

class MyKnobSpinCtrl(wx.Panel):
    def __init__(self, parent, name='', font_size=12, color=wx.WHITE, type='float', style=wx.BORDER_SIMPLE):
        """Универсальное поле ввода с кнопками и  крутилкой"""
        wx.Panel.__init__(self, parent=parent, id=-1, style=wx.NO_BORDER)
        self.tooltip = ''
        self.parent = parent
        self.name = name
        self.color = color
        self.value = 0.0
        self.mem_value = 0.0
        self.max_value = 10000000
        self.min_value = -10000000
        self.type = type
        self.increment = 0.1
        self.popup_win = None
        self.drop = False  # флаг для активации пункта выпадающего меню
        self.knob_active = False  # флаг для активации крутилки

        self.knob_active = False
        # self.SetBackgroundColour(wx.BLACK)

        # self.display = wx.TextCtrl(self, -1, '0', style=wx.TE_PROCESS_ENTER | wx.TE_CENTER, size=(75, -1), name='display')
        self.Panel = wx.Panel(self, style=style)
        self.Panel.SetBackgroundColour(color)
        self.display = wx.StaticText(self.Panel, -1, label='0.0')
        self.display.SetFont(wx.Font(wx.FontInfo(font_size)))
        if self.type == 'float':
            self.display.SetLabel('0.0')
        else:
            self.display.SetLabel('0')

        self.display.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        # self.Panel.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)

        self.spin_btn = wx.SpinButton(self, -1, style=wx.SP_VERTICAL | wx.BORDER_RAISED, size=(22, 28))
        self.spin_btn.Bind(wx.EVT_SPIN_UP, self.val_ctrl)
        self.spin_btn.Bind(wx.EVT_SPIN_DOWN, self.val_ctrl)
        self.spin_btn.SetMin(-10000000)
        self.spin_btn.SetMax(10000000)

        sizer = wx.BoxSizer(wx.VERTICAL)
        hbox_lv1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox_lv2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add((1, 1), 1, wx.EXPAND)
        hbox.Add(self.display, flag=wx.ALIGN_CENTER)
        hbox.Add((1, 1), 1, wx.EXPAND)
        self.Panel.SetSizer(hbox)
        hbox_lv1.Add(self.Panel, proportion=1, flag=wx.EXPAND)
        hbox_lv1.Add(self.spin_btn)

        self.knob = KC.KnobCtrl(self, -1, size=(70, 70))
        self.knob.SetAngularRange(-45, 225)
        minvalue = self.knob.GetMinValue()
        maxvalue = self.knob.GetMaxValue()
        therange = 10  # количество мелких делений
        tickrange = range(minvalue, maxvalue + 1, therange)
        self.knob.SetTags(tickrange)
        self.knob.SetValue(0)
        self.knob.SetBoundingColour(wx.BLACK)
        self.Bind(KC.EVT_KC_ANGLE_CHANGED, self.KnobAngleChanged, self.knob)

        self.val_min_txt = wx.StaticText(self, -1, f'{self.min_value}')
        self.val_max_txt = wx.StaticText(self, -1, f'{self.max_value}')
        hbox_lv2.Add(self.val_min_txt)
        hbox_lv2.Add((1, 1), proportion=1, flag=wx.EXPAND)
        hbox_lv2.Add(self.val_max_txt)

        self.knob.Bind(wx.EVT_ENTER_WINDOW, self.KnobOn)
        self.knob.Bind(wx.EVT_MOUSEWHEEL, self.MouseWheel)
        self.knob.Bind(wx.EVT_LEAVE_WINDOW, self.Knob_off)
        # self.knob2.Bind(wx.EVT_LEFT_UP, self.knob2_release)

        sizer.Add(hbox_lv1, flag=wx.EXPAND)
        sizer.Add((1, 2), flag=wx.EXPAND)
        sizer.Add(self.knob, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        sizer.Add(hbox_lv2, flag=wx.EXPAND)
        self.SetSizer(sizer)

        self.Menu()
        self.Panel.Bind(wx.EVT_RIGHT_UP, self.right_m_down)
        self.spin_btn.Bind(wx.EVT_RIGHT_UP, self.right_m_down)
        self.display.Bind(wx.EVT_RIGHT_UP, self.right_m_down)

    def Menu(self):
        self.ctx_menu = ctx = wx.Menu(style=wx.MENU_TEAROFF)
        # self.ctx_menu.SetTitle("Шаг")
        if self.type == 'float':
            ctx.Append(331, "0.1", kind=wx.ITEM_RADIO)
        ctx.Append(332, "1", kind=wx.ITEM_RADIO)
        ctx.Append(333, "5", kind=wx.ITEM_RADIO)
        ctx.Append(334, "10", kind=wx.ITEM_RADIO)
        ctx.Append(335, "50", kind=wx.ITEM_RADIO)
        ctx.Append(336, "100", kind=wx.ITEM_RADIO)
        ctx.AppendSeparator()
        ctx.Append(wx.ID_ANY, "Закрыть", kind=wx.ITEM_NORMAL)
        if self.drop:
            ctx.Append(337, "Обнулить", kind=wx.ITEM_NORMAL)
        if self.type == 'float':
            self.Bind(wx.EVT_MENU, self._set_increment, id=331, id2=336)
        else:
            self.Bind(wx.EVT_MENU, self._set_increment, id=332, id2=336)
        self.Bind(wx.EVT_MENU, self.SetNull, id=337)

    def menu_add_drop_to_zero(self):
        """Добавляет пункт меню для обнуления значения"""
        self.drop = True
        self.Menu()

    def MouseWheel(self, e):
        if self.knob_active:
            val = round(e.GetWheelRotation() / 120, 0)  # шаг крутилки 1
            self.SetValue(self.value + self.increment * val)

    def KnobOn(self, e):
        self.knob_active = True
        # print('KnobOn2', self.knob2_active)
        e.Skip()

    def Knob_off(self, e):
        self.knob_active = False
        # print('Knob_off2', self.knob2_active)
        e.Skip()

    def _set_increment(self, e):
        inc_dic = {331: 0.1, 332: 1, 333: 5, 334: 10, 335: 50, 336: 100}
        print(f'_set_increment {e.GetId()}, {inc_dic[e.GetId()]}')
        self.increment = inc_dic[e.GetId()]
        # self.ctx_menu.Check(id=e.GetId(), check=True)
        self.display.SetToolTip(f'{self.tooltip}, шаг: {self.increment}')
        self.spin_btn.SetToolTip(f'{self.tooltip}, шаг: {self.increment}')
        self.Panel.SetToolTip(f'{self.tooltip}, шаг: {self.increment}')

    def SetValue(self, val):
        self.mem_value = self.value
        self.value = float(val)
        self.display.SetLabel(str(self.round_val(val)))
        self.spin_btn.SetValue(int(self.value))
        self.val_ctrl()

    def SetNull(self, e=None):
        self.SetValue(0)

    def SetMinSize(self, size):
        self.Panel.SetMinSize(size)
        self.Panel.Layout()

    def SetToolTip(self, tip):
        self.display.SetToolTip(tip)
        self.spin_btn.SetToolTip(tip)
        self.Panel.SetToolTip(tip)
        self.tooltip = tip

    def GetValue(self):
        return self.round_val(self.value)

    def GetMemValue(self):
        return self.mem_value

    def SetMax(self, val):
        self.max_value = val
        self.spin_btn.SetMax(val)
        self.val_max_txt.SetLabel(str(val))

    def SetMin(self, val):
        self.min_value = val
        self.spin_btn.SetMin(val)
        self.val_min_txt.SetLabel(str(val))

    def SetRange(self, min_val=-1000, max_val=1000):
        self.min_value = min_val
        self.max_value = max_val
        self.val_min_txt.SetLabel(str(min_val))
        self.val_max_txt.SetLabel(str(max_val))
        self.val_ctrl()

    def OnLeftDown(self, e=None):
        print(f'OnLeftDown {self.name} {self.value}')
        # self.display.SetLabel('')
        self.popup_win = PopUPField(self, self.parent, color=self.color)
        # self.popup_win.Show()
        e.Skip()

    def right_m_down(self, e):
        self.PopupMenu(self.ctx_menu)

    def KnobAngleChanged(self, e):
        # print(f'KnobAngleChanged Range: {e.GetValue()}')
        value = e.GetValue() / 100
        total_range = self.max_value - self.min_value

        newVal = round(total_range * value, 1) + self.min_value

        self.display.SetLabel(str(self.round_val(newVal)))
        self.spin_btn.SetValue(int(newVal))
        self.value = self.round_val(newVal)
        self.Panel.Layout()
        # e.Skip()

    def round_val(self, val):
        if self.type == 'float':
            return round(float(val), 1)
        else:
            return _round(val)

    def val_ctrl(self, e=None):
        direction = 0
        if e is not None:  # управление инкрементом
            if 10064 < e.GetEventType() < 10067:
                direction = 1 if e.GetEventType() == 10065 else -1

        val = self.value + self.increment * direction
        val = val if val < self.max_value else self.max_value
        val = val if val >= self.min_value else self.min_value
        self.mem_value = self.value
        self.value = val
        self.display.SetLabel(str(self.round_val(val)))

        total_range = self.max_value - self.min_value
        knob_val = (val - self.min_value) / total_range * 100
        self.knob.SetValue(knob_val)
        self.knob.Layout()
        self.Panel.Layout()
        if e is not None:
            e.Skip()



class MyRadioButton(wx.Panel):
    def __init__(self, parent, mainParent, color=wx.WHITE, num_btn=3, orient='H', style=wx.NO_BORDER, radio=False,
                 label=None,
                 btn_size=(48,35)):
        """Универсальное поле ввода с радио кнопками """
        wx.Panel.__init__(self, parent=parent, id=-1, size=wx.DefaultSize, style=style)

        self.Panel = wx.Panel(self, style=style)
        self.parent = mainParent

        if label is None:
            label = [f"btn_{i}" for i in range(num_btn)]

        self.btn_list = btn_list = [btn.GenToggleButton(self.Panel, -1, label[i],
                                                        size=btn_size, name=f'{i+1}') for i in range(num_btn)]

        font = wx.Font(wx.FontInfo(9).Bold())
        [_btn.SetFont(font) for _btn in btn_list]

        sizer = wx.BoxSizer(wx.VERTICAL)
        btn_list[0].SetValue(True)
        btn_list[0].SetForegroundColour(wx.GREEN)

        if orient == 'H':
            szbox = wx.BoxSizer(wx.HORIZONTAL)
            for n, _btn in enumerate(btn_list):
                border = 5 if n > 0 else 2
                szbox.Add(_btn, proportion=0, flag=wx.EXPAND|wx.LEFT, border=border)
        else:
            szbox = wx.BoxSizer(wx.VERTICAL)
            [szbox.Add(_btn, proportion=0, flag=wx.EXPAND | wx.TOP, border=5) for _btn in btn_list]

        [_btn.SetUseFocusIndicator(False) for _btn in btn_list]
        [_btn.Bind(wx.EVT_RIGHT_UP, self.PopUpMenu) for _btn in btn_list]
        if radio:
            [_btn.Bind(wx.EVT_BUTTON, self.radio_func) for _btn in btn_list]

        self.Panel.SetSizer(szbox)
        sizer.Add(self.Panel) #, proportion=0, flag=wx.EXPAND)
        self.SetSizer(sizer)

    def radio_func(self, e):
        cur_btn = e.GetEventObject()
        [_btn.SetValue(False) for _btn in self.btn_list]
        [_btn.SetForegroundColour(wx.BLACK) for _btn in self.btn_list]
        cur_btn.SetValue(True)
        cur_btn.SetForegroundColour(wx.GREEN)

    def GetBtn(self):
        """Возвращает имя активной кнопки в радио режиме"""
        for _btn in self.btn_list:
            if _btn.GetValue():
                return _btn.GetName()

    def GetBtnState(self):
        """Возвращает список состояний кнопок в порядке нумерации"""
        #for _btn in self.btn_list:
        return [True if _btn.GetValue() else False for _btn in self.btn_list]



    def PopUpMenu_btn_1(self):
        self.ctx_menu = ctx_menu = wx.Menu()
        # ctx_menu.Append(300, 'Настроойки шумоподавления')
        ctx_menu.Append(300, 'Настройки детектора')
        ctx_menu.AppendSeparator()
        ctx_menu.Append(654, 'Скрыть меню')

        # self.Bind(wx.EVT_MENU, self.filtering_pref, id=300)
        self.Bind(wx.EVT_MENU, self.mog2_pref, id=300)
        self.Bind(wx.EVT_MENU, self.zzz, id=654)
        self.PopupMenu(self.ctx_menu)
        self.ctx_menu.Destroy()

    def PopUpMenu_btn_2(self):
        self.ctx_menu = ctx_menu = wx.Menu()
        # ctx_menu.Append(300, 'Настроойки шумоподавления')
        ctx_menu.Append(301, 'Настройки детектора')
        ctx_menu.AppendSeparator()
        ctx_menu.Append(654, 'Скрыть меню')

        # self.Bind(wx.EVT_MENU, self.filtering_pref, id=300)
        self.Bind(wx.EVT_MENU, self.xdav_pref, id=301)
        self.Bind(wx.EVT_MENU, self.zzz, id=654)
        self.PopupMenu(self.ctx_menu)
        self.ctx_menu.Destroy()

    def mog2_pref(self, e):
        win = MOG_Pref(self.parent.videoPanel)
        win.CenterOnParent(wx.BOTH)
        win.Show(True)

    def xdav_pref(self, e):
        self.parent.videoPanel.x_dav_win = XDAV(self.parent.videoPanel)
        self.parent.videoPanel.x_dav_win.CenterOnParent(wx.BOTH)
        self.parent.videoPanel.x_dav_win.Show(True)

    def PopUpMenu(self, e=None):
        obj = e.GetEventObject()
        if obj.GetName() == '1':
            self.PopUpMenu_btn_1()
        if obj.GetName() == '3':
            self.PopUpMenu_btn_2()


    def SetToolTip(self, num_btn, tip):
        self.btn_list[num_btn-1].SetToolTip(tip)

    def zzz(self, e):
        pass


class MyButton(wx.Panel):
    def __init__(self, parent, name='', font_size=12, panel_color=wx.NullColour, style=wx.BORDER_RAISED,
                 size=wx.DefaultSize, text=['',''], text_color=wx.BLACK, is_toggle=False, bind_id=123):
        """Универсальная кнопка """
        wx.Panel.__init__(self, parent=parent, id=-1, size=size, style=wx.NO_BORDER)
        self.tooltip = ''
        self.parent = parent
        self.ID = bind_id
        self.name = name
        self.value = False
        self.mem_value = 0.0
        self.text = text
        self.is_toggle = is_toggle
        self.font_size = font_size
        self.text_color = text_color
        self.panel_color = panel_color
        self.build_panel(style, text=text)
        # self.btnEvent = wx.PyCommandEvent(wx.wxEVT_BUTTON, id=123)
        # self.btnEvent.SetEventObject(self.Panel)


    def build_panel(self, style, bg_color=wx.NullColour, text=['',''], textBG=wx.NullColour):
        self.Panel = wx.Panel(self, style=style)
        self.Panel.SetBackgroundColour(bg_color)
        # self.Panel.SetBackgroundColour(self.panel_color)
        self.textWX = [wx.StaticText(self.Panel, -1, label=f'{txt}') for txt in text]
        self.SetFont(size=16, bold=True)
        self.SetTextColor(self.text_color)
        self.SetTextBGColor(textBG)

        if self.is_toggle:
            self.Panel.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
            [txt.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown) for txt in self.textWX]
        else:
            self.Panel.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
            self.Panel.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
            [txt.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown) for txt in self.textWX]

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add((1, 1), 1, wx.EXPAND)

        [self.vbox.Add(text, flag=wx.ALIGN_CENTER) for text in self.textWX]
        self.vbox.Add((1, 1), 1, wx.EXPAND)
        self.Panel.SetSizer(self.vbox)
        self.sizer.Add(self.Panel, proportion=1, flag=wx.EXPAND)
        self.SetSizer(self.sizer)


    def OnLeftDown(self, e):
        print('OnLeftDown')
        self.sizer.Clear()
        self.vbox.Clear()
        if self.is_toggle:
            self.value = not self.value
            if self.value:
                text = ['ОТМЕНИТЬ', 'ВКЛЮЧЕНИЕ']
                self.build_panel(wx.BORDER_SUNKEN, bg_color='#FFFEA0', text=text)
            else:
                text = ['ВКЛЮЧИТЬ','РЕНТГЕН']
                self.build_panel(wx.BORDER_RAISED, text=text)
        else:
            self.value = True
            self.build_panel(wx.BORDER_SUNKEN)
        self.Layout()
        #wx.PostEvent(self.parent, self.btnEvent)
        wx.PostEvent(self.parent, wx.CommandEvent(wx.wxEVT_BUTTON, id=123))
        # self.Panel.Refresh()
        e.Skip()

    def OnLeftUp(self, e):
        print('OnLeftUp')
        self.sizer.Clear()
        self.value = False
        # self.Panel.Destroy()
        self.build_panel(wx.BORDER_RAISED)
        self.Layout()
        # self.Panel.Refresh()
        e.Skip()

    def SetTextColor(self, color):
        [item.SetForegroundColour(color) for item in self.textWX]
        self.Layout()

    def SetText(self, text):
        print(f'SetText: {text}')
        [item.SetLabel(text[n]) for n, item in enumerate(self.textWX)]
        self.Panel.Refresh()
        self.Layout()

    def SetFont(self, size=14, bold=False):
        if bold:
            [item.SetFont(wx.Font(wx.FontInfo(self.font_size)).Bold()) for item in self.textWX]
        else:
            [item.SetFont(wx.Font(wx.FontInfo(self.font_size))) for item in self.textWX]


    def SetValue(self, val):
        self.value = val
        self.Layout()

    def SetTextBGColor(self, color):
        for item in self.textWX:
            item.SetBackgroundColour(color)
        self.Refresh()


    def SetBackgroundColour(self, color):
        self.panel_color = color
        self.Panel.SetBackgroundColour(color)

    def SetMinSize(self, size):
        self.Panel.SetMinSize(size)
        self.Panel.Layout()

    def SetToolTip(self, tip):
        [item.SetToolTip(tip) for item in self.textWX]
        self.Panel.SetToolTip(tip)
        self.tooltip = tip

    def GetValue(self):
        return self.value




class MyDisplay(wx.Panel):
    def __init__(self, parent, name='', font_size=12, panel_color=wx.NullColour, type='float', style=wx.BORDER_SIMPLE,
                 size=wx.DefaultSize):
        """Универсальный дисплей для отображения текстоой информации """
        wx.Panel.__init__(self, parent=parent, id=-1, size=size, style=wx.NO_BORDER)
        self.tooltip = ''
        self.parent = parent
        self.name = name
        self.value = 0.0
        self.mem_value = 0.0
        self.max_value = 10000000
        self.min_value = -10000000
        self.type = type
        self.increment = 0.1
        self.drop = False  # флаг для активации пункта выпадающего меню

        # self.display = wx.TextCtrl(self, -1, '0', style=wx.TE_PROCESS_ENTER | wx.TE_CENTER, size=(75, -1), name='display')
        self.Panel = wx.Panel(self, style=style)
        self.Panel.SetBackgroundColour(panel_color)
        self.display = wx.StaticText(self.Panel, -1, label=f'{self.value}')
        if self.type == 'float':
            self.display.SetLabel('0.0')
        elif self.type == 'str':
            self.display.SetLabel('')
        else:
            self.display.SetLabel('0')
        # self.display.SetBackgroundColour(color)
        self.display.SetFont(wx.Font(wx.FontInfo(font_size)))


        sizer = wx.BoxSizer(wx.HORIZONTAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add((1, 1), 1, wx.EXPAND)
        hbox.Add(self.display, flag=wx.ALIGN_CENTER)
        hbox.Add((1, 1), 1, wx.EXPAND)
        self.Panel.SetSizer(hbox)
        sizer.Add(self.Panel, proportion=1, flag=wx.EXPAND)
        self.SetSizer(sizer)

    def SetFont(self, size):
        self.display.SetFont(wx.Font(wx.FontInfo(size)))


    def SetValue(self, val, pre_fix='', post_fix=''):
        if self.type == 'str':
            self.display.SetLabel(str(val))
        else:
            self.mem_value = self.value
            self.value = float(val)
            self.display.SetLabel(f"{pre_fix}{self.round_val(val)}{post_fix}")
        self.Layout()


    def SetNull(self, e=None):
        self.SetValue(0)

    def SetDisplayColor(self, color):
        self.display.SetForegroundColour(color)

    def SetPanelColor(self, color):
        self.Panel.SetBackgroundColour(color)

    def SetMinSize(self, size):
        self.Panel.SetMinSize(size)
        self.Panel.Layout()

    def SetToolTip(self, tip):
        self.display.SetToolTip(tip)
        self.Panel.SetToolTip(tip)
        self.tooltip = tip

    def GetValue(self):
        return self.round_val(self.value)

    def SetMax(self, val):
        self.max_value = val

    def SetMin(self, val):
        self.min_value = val

    def SetRange(self, min_val=-1000, max_val=1000):
        self.min_value = min_val
        self.max_value = max_val

    def round_val(self, val):
        if self.type == 'float':
            return round(float(val), 1)
        elif self.type == 'int':
            return _round(val)
        else:
            return val

class MyGauge2(wx.Panel):
    def __init__(self, parent, width=10, height=1, start_color='#7FFF00', end_color='#FF0000', bg_color='#c0c0c0',
                 edgecolor='none', linewidth=0, fontSZ=9, style=wx.BORDER_SIMPLE):
        wx.Panel.__init__(self, parent, -1, style=style|wx.FULL_REPAINT_ON_RESIZE)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        """ цвет от зеленого к красному """
        self.parent = parent
        self.start_color = start_color
        self.end_color = end_color
        self.bg_color = bg_color
        self.max_value = 100
        self.width = width
        self.height = height
        self.edgecolor = edgecolor
        self.linewidth = linewidth
        self.get_gauge()
        self.gauge_img = None
        self.fontSZ = fontSZ
        self.SetVal() # инициализируем изображение
        self.SetMinSize((100, 10))

    def _relValue(self, val):
        # print(val, self.max_value, val/self.max_value * 100)
        return val/self.max_value


    def get_gauge(self):
        """Строит основу для прогресс бара"""
        self.fig, self.ax = plt.subplots(figsize=(self.width / 5, self.height / 5))

        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(-self.height / 2, self.height / 2)
        self.ax.axis('off')  # Скрыть оси
        # создаем градиент
        self.cmap = LinearSegmentedColormap.from_list('grad', [self.start_color, self.end_color])

        # 1. Рисуем пустой фон того же цвета start_color (чтобы не было дыр), но без краев
        self.ax.fill_betweenx([-self.height / 2, self.height / 2], 0, self.width, color=self.bg_color,
                         edgecolor=self.edgecolor, linewidth=self.linewidth)

        self.fig.canvas.draw()
        self.axBackground = self.fig.canvas.copy_from_bbox(self.ax.bbox)
        # plt.close(fig)

    def OnPaint(self, e):
        dc = wx.PaintDC(self)
        dc.Clear()
        x, y = self.GetSize()
        posx, posy = 0, 0
        # height, width = self.grid_img.shape[:2]
        # bitmap = wx.Bitmap.FromBuffer(width, height, self.grid_img)
        img = self.gauge_img.ConvertToImage()

        img = img.Scale(x, y, wx.IMAGE_QUALITY_HIGH)
        # self.bmp = wx.Bitmap(img)
        dc.DrawBitmap(wx.Bitmap(img), posx, posy)


    def SetRange(self, max_val):
        self.max_value = max_val

    def SetVal(self, val=0, array=False):
        value = self._relValue(val)
        pct_text = f"{(value * 100):.1f}%"

        patch = Rectangle((0, -self.height/2), value * self.width,
                            self.height,
                            facecolor=self.cmap(value), # Цвет зависит от значения (зеленый -> красный)
                            edgecolor= 'none',      # Без внутренней обводки
                            linewidth=0
                        )

        # Вычисляем центр активной части для центрирования текста по прогрессу
        center_x = self.width / 2

        txt_a = self.ax.text(
            center_x,
            0,  # Y=0 - центр высоты оси
            pct_text,
            ha='center',  # Центрирование по горизонтали
            va='center',  # Центрирование по вертикали
            color='#333333',  # Темный цвет текста
            fontsize=self.fontSZ,
            fontweight='normal',
            bbox=dict(boxstyle="round,pad=0.3", facecolor="None", edgecolor="none", alpha=0.99)
            # Белая подложка для читаемости
        )
        rect = self.ax.add_patch(patch)
        self.fig.canvas.restore_region(self.axBackground)

        self.ax.draw_artist(rect)
        self.ax.draw_artist(txt_a)
        self.fig.canvas.blit(self.ax.bbox)
        img = np.array(self.fig.canvas.buffer_rgba(), dtype=np.uint8)[:, :, :3]
        img = img[_round(3*self.height):_round(-1*self.height),
              _round(25*self.width/10):_round(-20*self.width/10)].astype(np.uint8)  # y | x
        height, width = img.shape[:2]
        self.gauge_img = wx.Bitmap.FromBuffer(width, height, img)
        self.Refresh()

class MyGauge:
    def __init__(self, parent, width=10, height=1, start_color='#7FFF00', end_color='#FF0000', bg_color='#c0c0c0',
                 edgecolor='none', linewidth=0):
        """ Прогресс бар с цветным градиентом от зеленого к красному и процентом заполнения """
        self.parent = parent
        self.start_color = start_color
        self.end_color = end_color
        self.bg_color = bg_color
        self.max_value = 100
        self.width = width
        self.height = height
        self.edgecolor = edgecolor
        self.linewidth = linewidth
        self.get_gauge()

    def _relValue(self, val):
        # print(val, self.max_value, val/self.max_value * 100)
        return val/self.max_value


    def get_gauge(self):
        """Строит основу для прогресс бара"""
        self.fig, self.ax = plt.subplots(figsize=(self.width / 5, self.height / 5))

        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(-self.height / 2, self.height / 2)
        self.ax.axis('off')  # Скрыть оси
        # создаем градиент
        self.cmap = LinearSegmentedColormap.from_list('grad', [self.start_color, self.end_color])

        # 1. Рисуем пустой фон того же цвета start_color (чтобы не было дыр), но без краев
        self.ax.fill_betweenx([-self.height / 2, self.height / 2], 0, self.width, color=self.bg_color,
                         edgecolor=self.edgecolor, linewidth=self.linewidth)

        self.fig.canvas.draw()
        self.axBackground = self.fig.canvas.copy_from_bbox(self.ax.bbox)
        # plt.close(fig)

    def reDraw_gauge(self, val=0, array=False):
        value = self._relValue(val)
        pct_text = f"{(value * 100):.1f}%"

        patch = Rectangle((0, -self.height/2), value * self.width,
                            self.height,
                            facecolor=self.cmap(value), # Цвет зависит от значения (зеленый -> красный)
                            edgecolor= 'none',      # Без внутренней обводки
                            linewidth=0
                        )


        # Вычисляем центр активной части для центрирования текста по прогрессу
        center_x = self.width / 2

        txt_a = self.ax.text(
            center_x,
            0,  # Y=0 - центр высоты оси
            pct_text,
            ha='center',  # Центрирование по горизонтали
            va='center',  # Центрирование по вертикали
            color='#333333',  # Темный цвет текста
            fontsize=9,
            fontweight='normal',
            bbox=dict(boxstyle="round,pad=0.3", facecolor="None", edgecolor="none", alpha=0.99)
            # Белая подложка для читаемости
        )
        rect = self.ax.add_patch(patch)
        self.fig.canvas.restore_region(self.axBackground)

        self.ax.draw_artist(rect)
        self.ax.draw_artist(txt_a)
        self.fig.canvas.blit(self.ax.bbox)
        img = np.array(self.fig.canvas.buffer_rgba(), dtype=np.uint8)[:, :, :3]
        img = img[3:-3, 25:-20].astype(np.uint8)  # y | x

        if array:
            return img
        height, width = img.shape[:2]
        return wx.Bitmap.FromBuffer(width, height, img)

class MySpinCtrl(wx.Panel):
    def __init__(self, topParent=None, panel=None, name='', font_size=12, color=wx.WHITE, type='float',
                 style=wx.BORDER_SIMPLE, size=wx.DefaultSize,
                 touch_keyboard=False,
                 show_infinity=False):
        """Универсальное поле ввода с кнопками или всплывающей клавиатурой"""
        wx.Panel.__init__(self, parent=panel, id=-1, size=size, style=wx.NO_BORDER)
        self.on_display = False
        self.tooltip = ''
        self.parent = topParent
        self.touch_keyboard = touch_keyboard
        self.name = name
        self.color = color
        self.value = 0.0
        self.mem_value = 0.0
        self.max_value = 10000000
        self.min_value = -10000000
        self.type = type
        self.increment = 0.1
        self.drop = False  # флаг для активации пункта выпадающего меню
        self.show_infinity = show_infinity  # показывать ли бесконечность

        # self.display = wx.TextCtrl(self, -1, '0', style=wx.TE_PROCESS_ENTER | wx.TE_CENTER, size=(75, -1), name='display')
        self.Panel = wx.Panel(self, style=style)
        self.Panel.SetBackgroundColour(color)
        self.display = wx.StaticText(self.Panel, -1, label=f'{self.value}')
        if self.type == 'float':
            self.display.SetLabel('0.0')
        else:
            self.display.SetLabel('0')

        self.infinityImg = wx.StaticBitmap(self.Panel, wx.ID_ANY, _infinity_big.GetBitmap())
        self.infinityImg.SetToolTip("Бесконечная экспозиция!")
        self.infinityImg.Hide()
        # self.nullImg = wx.Bitmap.FromRGBA(100, 60, 255, 255, 255, alpha=1)

        # self.display.SetBackgroundColour(color)
        self.display.SetFont(wx.Font(wx.FontInfo(font_size)))
        self.display.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.infinityImg.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        # self.nullImg.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Panel.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.btn_up = btn.GenBitmapButton(self, -1, bitmap=wx.Bitmap('images/arrow_up_16.png'), name='1') #, size=(100, 22))
        self.btn_up.SetUseFocusIndicator(False)
        self.btn_down = btn.GenBitmapButton(self, -1, bitmap=wx.Bitmap('images/arrow_down_16.png'), name='-1') #, size=(100, 22))
        self.btn_down.SetUseFocusIndicator(False)
        self.btn_up.Bind(wx.EVT_BUTTON, self.val_ctrl)
        self.btn_up.Bind(wx.EVT_LEFT_DOWN, self.left_m_down)
        self.btn_up.Bind(wx.EVT_LEFT_UP, self.left_m_up)
        self.btn_down.Bind(wx.EVT_BUTTON, self.val_ctrl)
        self.btn_down.Bind(wx.EVT_LEFT_DOWN, self.left_m_down)
        self.btn_down.Bind(wx.EVT_LEFT_UP, self.left_m_up)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add((1, 1), 1, wx.EXPAND)
        hbox.Add(self.display, flag=wx.ALIGN_CENTER)
        hbox.Add(self.infinityImg, flag=wx.ALIGN_CENTER)
        hbox.Add((1, 1), 1, wx.EXPAND)
        self.Panel.SetSizer(hbox)
        sizer.Add(self.Panel, proportion=1, flag=wx.EXPAND)
        self.btn_box = wx.BoxSizer(wx.VERTICAL)
        self.btn_box.Add(self.btn_up, proportion=1, flag=wx.EXPAND)
        self.btn_box.Add(self.btn_down, proportion=1, flag=wx.EXPAND)
        sizer.Add(self.btn_box, flag=wx.EXPAND)
        self.SetSizer(sizer)

        self.Menu()
        self.Panel.Bind(wx.EVT_RIGHT_UP, self.right_m_down)
        self.btn_up.Bind(wx.EVT_RIGHT_UP, self.right_m_down)
        self.display.Bind(wx.EVT_RIGHT_UP, self.right_m_down)

        self.display.Bind(wx.EVT_ENTER_WINDOW, self.DisplayOn_Off)
        self.display.Bind(wx.EVT_MOUSEWHEEL, self.MouseWheel)
        self.display.Bind(wx.EVT_LEAVE_WINDOW, self.DisplayOn_Off)
        if self.show_infinity:
            self.SetValue(0) # для отображения бесконечности

    def counter_flow(self, direction):
        time.sleep(0.5)
        while self.left_is_down:
            self.val_ctrl(direction=direction)
            time.sleep(0.1)


    def left_m_down(self, e):
        self.left_is_down = True
        direction = int(e.GetEventObject().GetName())
        if self.value > 0 and direction == -1:
            th.Thread(target=self.counter_flow, args=(direction,)).start()
        elif self.value < self.max_value and direction == 1:
            th.Thread(target=self.counter_flow, args=(direction,)).start()
        e.Skip()

    def left_m_up(self, e):
        self.left_is_down = False
        e.Skip()

    def DisplayOn_Off(self, e):
        self.on_display = not self.on_display

    def Menu(self):
        self.ctx_menu = ctx = wx.Menu(style=wx.MENU_TEAROFF)
        # self.ctx_menu.SetTitle("Шаг")
        if self.type == 'float':
            ctx.Append(331, "0.1", kind=wx.ITEM_RADIO)
        ctx.Append(332, "1", kind=wx.ITEM_RADIO)
        if self.max_value > 5:
            ctx.Append(333, "5", kind=wx.ITEM_RADIO)
            if self.max_value > 10:
                ctx.Append(334, "10", kind=wx.ITEM_RADIO)
                if self.max_value > 50:
                    ctx.Append(335, "50", kind=wx.ITEM_RADIO)
                    if self.max_value > 100:
                        ctx.Append(336, "100", kind=wx.ITEM_RADIO)
        ctx.AppendSeparator()
        ctx.Append(wx.ID_ANY, "Закрыть", kind=wx.ITEM_NORMAL)
        if self.drop:
            ctx.Append(337, "Обнулить", kind=wx.ITEM_NORMAL)
        if self.type == 'float':
            self.Bind(wx.EVT_MENU, self._set_increment, id=331, id2=336)
        else:
            self.Bind(wx.EVT_MENU, self._set_increment, id=332, id2=336)
        self.Bind(wx.EVT_MENU, self.SetNull, id=337)

    def menu_add_drop_to_zero(self):
        """Добавляет пункт меню для обнуления значения"""
        self.drop = True
        self.Menu()

    def MouseWheel(self, e):
        if self.on_display:
            val = round(e.GetWheelRotation() / 120, 0)  # шаг крутилки 1
            self.SetValue(self.value + self.increment * val)

    def SetFont(self, size=20):
        self.display.SetFont(wx.Font(wx.FontInfo(size)))
        self.Layout()

    def SetNull(self, e=None):
        self.SetValue(0)

    def SetMinSizePanel(self, size):
        self.Panel.SetMinSize(size)
        self.Panel.Layout()

    def SetMinSizeBtn(self, size):
        self.btn_box.SetMinSize(size)
        self.Layout()

    def SetBgColor(self, color):
        self.color = color
        if isinstance(color, str):
            self.Panel.SetBackgroundColour(color)
        elif isinstance(color, tuple):
            self.Panel.SetBackgroundColour(wx.Colour(color))
        else:
            self.Panel.SetBackgroundColour(color)

    def SSH(self, minW=100, minH=50, maxW=200, maxH=100):
        ''' SetSizeHints '''
        self.SetSizeHints(minW=minW, minH=minH, maxW=maxW, maxH=maxH)

    def SetToolTip(self, tip):
        self.display.SetToolTip(tip)
        self.btn_up.SetToolTip(tip)
        self.btn_down.SetToolTip(tip)
        self.Panel.SetToolTip(tip)
        self.tooltip = tip

    def GetValue(self):
        return self.round_val(self.value)

    def _set_increment(self, e):
        inc_dic = {331: 0.1, 332: 1, 333: 5, 334: 10, 335: 50, 336: 100}
        print(f'_set_increment {e.GetId()}, {inc_dic[e.GetId()]}')
        self.increment = inc_dic[e.GetId()]
        # self.ctx_menu.Check(id=e.GetId(), check=True)
        self.display.SetToolTip(f'{self.tooltip}, шаг: {self.increment}')
        self.btn_up.SetToolTip(f'{self.tooltip}, шаг: {self.increment}')
        self.btn_down.SetToolTip(f'{self.tooltip}, шаг: {self.increment}')
        self.Panel.SetToolTip(f'{self.tooltip}, шаг: {self.increment}')

    def SetMax(self, val):
        self.max_value = val

    def SetMin(self, val):
        self.min_value = val

    def SetRange(self, min_val=-1000, max_val=1000):
        self.min_value = min_val
        self.max_value = max_val

    def OnLeftDown(self, e=None):
        print(f'OnLeftDown {self.name} {self.value}')
        if self.touch_keyboard:
            self.popup_win = PopUPKeyboard(self, self.parent, color=self.color)
            self.popup_win.Show()
        else:
            self.popup_win = PopUPField(self, self.parent, color=self.color)
        e.Skip()

    def right_m_down(self, e):
        self.PopupMenu(self.ctx_menu)

    def round_val(self, val, forced_round=False):
        if self.type == 'float' and not forced_round:
            return round(float(val), 1)
        else:
            return _round(val)

    def SetValue(self, val, forced_round=False):
        print(f'SetValue {val}')
        self.mem_value = self.value
        self.value = float(val)
        self.display.SetLabel(str(self.round_val(val, forced_round=forced_round)))
        if self.value == 0 and self.show_infinity:
            self.infinityImg.Show()
            self.display.Hide()
            # self.Panel.Layout()
        else:
            self.infinityImg.Hide()
            self.display.Show()
            # self.Panel.Layout()

    def val_ctrl(self, e=None, direction=0):
        if e is not None:  # управление инкрементом
            direction = int(e.GetEventObject().GetName())

        self.increment = 1 if (self.type == 'int' and self.increment < 1) else self.increment

        # print('val_ctrl', self.max_value, self.min_value, self.value, self.increment, direction)
        val = self.value + self.increment * direction
        val = val if val < self.max_value else self.max_value
        val = val if val >= self.min_value else self.min_value
        if val != self.value:
            self.SetValue(val)
        else:
            self.left_is_down = False # прерываем цикл spinBtn
            # self.play_sound("SystemExclamation")

        self.Panel.Layout()
        if e is not None:
            e.Skip()

    def play_sound(self, path_to_sound):
        # print('play_sound')
        try:
            winsound.PlaySound(path_to_sound, winsound.SND_ASYNC)
        except:
            pass


class PopUPKeyboard(wx.MiniFrame):
    """ Всплывающее окно с клавиатурой для тачскрина"""
    def __init__(self, parent, mainParent, color, pos=wx.DefaultPosition, size=(500,600)):  #
        self.focuskill_flag = True
        title = 'Asessor X-ray: Введите величину'
        wx.MiniFrame.__init__(self, parent, -1, title, pos, size, style=wx.BORDER_DOUBLE | wx.FRAME_FLOAT_ON_PARENT)

        x, y, w, h = mainParent.GetScreenRect()
        xc = x + w // 2  - 250
        yc = y + h // 2 - 300
        self.SetPosition((xc, yc))

        self.parent = parent
        self.mainParent = mainParent
        self.shit_count = 0
        self.val_mem = parent.value
        self.name = parent.name
        self.color = color

        self.panel = wx.Panel(self, -1)
        self.Items()
        self.SetBgColor(wx.BLACK)  # наследуем цвет панели от родителя
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        gbs = wx.GridBagSizer(vgap=5, hgap=4)


        # self.Bind(wx.EVT_SIZE, self.OnSize)

        mainSizer.Add(gbs, proportion=1, flag=wx.EXPAND)
        # mainSizer.Add(self.display, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        # mainSizer.Add((1, 1), proportion=1, flag=wx.EXPAND)
        gbs.Add(self.display, pos=(0, 0), span=(1, 4), flag=wx.EXPAND)

        gbs.Add(self.key7, pos=(1, 0), flag=wx.EXPAND)
        gbs.Add(self.key8, pos=(1, 1), flag=wx.EXPAND)
        gbs.Add(self.key9, pos=(1, 2), flag=wx.EXPAND)
        gbs.Add(self.key_del, pos=(1, 3), flag=wx.EXPAND)
        gbs.Add(self.key4, pos=(2, 0), flag=wx.EXPAND)
        gbs.Add(self.key5, pos=(2, 1), flag=wx.EXPAND)
        gbs.Add(self.key6, pos=(2, 2), flag=wx.EXPAND)
        gbs.Add(self.key_enter, pos=(2, 3), span=(3, 1), flag=wx.EXPAND)

        gbs.Add(self.key1, pos=(3, 0), flag=wx.EXPAND)
        gbs.Add(self.key2, pos=(3, 1), flag=wx.EXPAND)
        gbs.Add(self.key3, pos=(3, 2), flag=wx.EXPAND)
        gbs.Add(self.key0, pos=(4, 0), span=(1,2), flag=wx.EXPAND)
        gbs.Add(self.key_dot, pos=(4, 2), flag=wx.EXPAND)

        for i in range(0, 5):
            gbs.AddGrowableRow(i)
        for i in range(4):
            gbs.AddGrowableCol(i)

        self.panel.SetSizerAndFit(mainSizer)
        self.Layout()
        self.display.SetFocus()

    def Items(self):
        self.key_dot = TouchBtn(self.panel, self, name='.')
        self.key_dot.SSH()
        self.key0 = TouchBtn(self.panel, self, name='0')
        self.key0.SSH()
        self.key1 = TouchBtn(self.panel, self, name='1')
        self.key1.SSH()
        self.key2 = TouchBtn(self.panel, self, name='2')
        self.key2.SSH()
        self.key3 = TouchBtn(self.panel, self, name='3')
        self.key3.SSH()
        self.key4 = TouchBtn(self.panel, self, name='4')
        self.key4.SSH()
        self.key5 = TouchBtn(self.panel, self, name='5')
        self.key5.SSH()
        self.key6 = TouchBtn(self.panel, self, name='6')
        self.key6.SSH()
        self.key7 = TouchBtn(self.panel, self, name='7')
        self.key7.SSH()
        self.key8 = TouchBtn(self.panel, self, name='8')
        self.key8.SSH()
        self.key9 = TouchBtn(self.panel, self, name='9')
        self.key9.SSH()
        self.key_del = TouchBtn(self.panel, self, name='<<<')
        self.key_del.SSH(minW=65)
        self.key_enter = TouchBtn(self.panel, self, name='Ввод')
        self.key_enter.SSH(minW=65)

        #self.display = wx.TextCtrl(self.panel, -1, style=wx.BORDER_RAISED| wx.TE_CENTER| wx.TE_READONLY)
        self.display = wx.Panel(self.panel)
        self.display.SetBackgroundColour('#00007f')
        self.display.SetFont(wx.Font(30, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
        self.display_text = wx.StaticText(self.display, -1, '')
        self.display_text.SetForegroundColour('#fdfd02')
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add((1,1), 1, wx.EXPAND)
        vbox.Add(self.display_text, 0, flag=wx.ALIGN_CENTER)
        vbox.Add((1, 1), 1, wx.EXPAND)
        self.display.SetSizer(vbox)
        #self.display.Bind(wx.EVT_KILL_FOCUS, self.FocusKill)

    def blockNonNumber(self, event):
        print('blockNonNumber')
        key = event.GetKeyCode()
        if key == 13:  # Ввод
            self.TextEnter()

        elif key == 27:  # Esc
            self.parent.SetValue(self.val_mem)
            self.Destroy()
            return

    def FocusKill(self, e=None):
        print(f'FocusKill {self.val_mem} {self.mainParent.appInFocusFlag}, {self.focuskill_flag}')
        if self.mainParent.appInFocusFlag and self.focuskill_flag:
            print(f'FocusKill_2 {self.val_mem}')
            self.parent.SetValue(self.val_mem)
            self.Destroy()

    def play_sound(self, path_to_sound):
        # print('play_sound')
        try:
            winsound.PlaySound(path_to_sound, winsound.SND_ASYNC)
        except:
            pass


    def OnSize(self, e=None):
        self.panel.Layout()
        # self.Layout()
        e.Skip()

    def SetBgColor(self, color):
        if isinstance(color, str):
            self.panel.SetBackgroundColour(color)
        elif isinstance(color, tuple):
            self.panel.SetBackgroundColour(wx.Colour(color))
        else:
            self.panel.SetBackgroundColour(color)

    def TextEnter(self):
        text = self.display_text.GetLabel()
        print('TextEnter:', text, self.name)
        self.focuskill_flag = False

        if len(text) > 1:
            if text[0] == '0' and text[1] != '.' and '.' not in text:
                text = f'0.{text[1:]}'
        elif text == '.':
            text = 0.0
        elif not text:
            text = self.val_mem
        try:
            cur_val = round(float(text), 1)
        except:
            cur_val = self.val_mem

        print('TextEnter2 cur_val: ', cur_val)
        if self.name == 'set_voltage':
            if cur_val < self.mainParent.kVmin:
                cur_val = self.mainParent.kVmin
            elif cur_val > self.mainParent.kVmax:
                cur_val = self.mainParent.kVmax
            print('TextEnter touch_pan_MA cur_val: ', cur_val)
            self.mainParent.touch_pan_MA.SetValue(self.mainParent.get_Amps_norm(curVoltage=cur_val))
        if self.name == 'set_amper':
            cur_val = self.mainParent.get_Amps_norm(curAmper=cur_val)
            # self.mainParent.touch_pan_MA.SetValue(tuned_Amper)
            # self.display.SetValue(str(tuned_Amper))

        elif self.name == 'set_timer':
            if self.mainParent.min_sec_btn.GetValue() or self.mainParent.min_sec_btn2.GetValue():
                cur_val = round(cur_val, 1)
                print('TextEnter3 cur_val: ', cur_val)
            else:
                cur_val = _round(cur_val)
                print('TextEnter4 cur_val: ', cur_val)

        self.parent.SetValue(cur_val)
        self.Destroy()


class TouchSpinCtrl(wx.Panel):
    def __init__(self, topParent=None, panel=None, name='', font_size=12, color=wx.WHITE, type='float',
                 style=wx.BORDER_SIMPLE,
                 size=wx.DefaultSize):
        """Универсальное поле ввода с кнопками для тачскрина"""
        wx.Panel.__init__(self, parent=panel, id=-1, size=size, style=wx.NO_BORDER)
        self.on_display = False
        self.tooltip = ''
        self.parent = topParent
        self.name = name
        self.color = color
        self.value = 0.0
        self.mem_value = 0.0
        self.max_value = 10000000
        self.min_value = -10000000
        self.type = type
        self.increment = 0.1
        self.drop = False  # флаг для активации пункта выпадающего меню

        # self.display = wx.TextCtrl(self, -1, '0', style=wx.TE_PROCESS_ENTER | wx.TE_CENTER, size=(75, -1), name='display')
        self.Panel = wx.Panel(self, style=style)
        self.Panel.SetBackgroundColour(color)
        self.display = wx.StaticText(self.Panel, -1, label=f'{self.value}')
        if self.type == 'float':
            self.display.SetLabel('0.0')
        else:
            self.display.SetLabel('0')
        # self.display.SetBackgroundColour(color)
        self.display.SetFont(wx.Font(wx.FontInfo(font_size)))
        self.display.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        # self.Panel.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.btn_up = btn.GenBitmapButton(self, -1, bitmap=wx.Bitmap('images/arrow_up_16.png'), name='1') #, size=(100, 22))
        self.btn_up.SetUseFocusIndicator(False)
        self.btn_down = btn.GenBitmapButton(self, -1, bitmap=wx.Bitmap('images/arrow_down_16.png'), name='-1') #, size=(100, 22))
        self.btn_down.SetUseFocusIndicator(False)
        self.btn_up.Bind(wx.EVT_BUTTON, self.val_ctrl)
        self.btn_up.Bind(wx.EVT_LEFT_DOWN, self.left_m_down)
        self.btn_up.Bind(wx.EVT_LEFT_UP, self.left_m_up)
        self.btn_down.Bind(wx.EVT_BUTTON, self.val_ctrl)
        self.btn_down.Bind(wx.EVT_LEFT_DOWN, self.left_m_down)
        self.btn_down.Bind(wx.EVT_LEFT_UP, self.left_m_up)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add((1, 1), 1, wx.EXPAND)
        hbox.Add(self.display, flag=wx.ALIGN_CENTER)
        hbox.Add((1, 1), 1, wx.EXPAND)
        self.Panel.SetSizer(hbox)
        sizer.Add(self.Panel, proportion=1, flag=wx.EXPAND)
        self.btn_box = wx.BoxSizer(wx.VERTICAL)
        self.btn_box.Add(self.btn_up, proportion=1, flag=wx.EXPAND)
        self.btn_box.Add(self.btn_down, proportion=1, flag=wx.EXPAND)
        sizer.Add(self.btn_box, flag=wx.EXPAND)
        self.SetSizer(sizer)

        self.Menu()
        self.Panel.Bind(wx.EVT_RIGHT_UP, self.right_m_down)
        self.btn_up.Bind(wx.EVT_RIGHT_UP, self.right_m_down)
        self.display.Bind(wx.EVT_RIGHT_UP, self.right_m_down)

        self.display.Bind(wx.EVT_ENTER_WINDOW, self.DisplayOn_Off)
        self.display.Bind(wx.EVT_MOUSEWHEEL, self.MouseWheel)
        self.display.Bind(wx.EVT_LEAVE_WINDOW, self.DisplayOn_Off)

    def counter_flow(self, direction):
        time.sleep(0.5)
        while self.left_is_down:
            self.val_ctrl(direction=direction)
            time.sleep(0.1)


    def left_m_down(self, e):
        self.left_is_down = True
        th.Thread(target=self.counter_flow, args=(int(e.GetEventObject().GetName()),)).start()
        e.Skip()

    def left_m_up(self, e):
        self.left_is_down = False
        e.Skip()

    def DisplayOn_Off(self, e):
        self.on_display = not self.on_display

    def Menu(self):
        self.ctx_menu = ctx = wx.Menu(style=wx.MENU_TEAROFF)
        # self.ctx_menu.SetTitle("Шаг")
        if self.type == 'float':
            ctx.Append(331, "0.1", kind=wx.ITEM_RADIO)
        ctx.Append(332, "1", kind=wx.ITEM_RADIO)
        if self.max_value > 5:
            ctx.Append(333, "5", kind=wx.ITEM_RADIO)
            if self.max_value > 10:
                ctx.Append(334, "10", kind=wx.ITEM_RADIO)
                if self.max_value > 50:
                    ctx.Append(335, "50", kind=wx.ITEM_RADIO)
                    if self.max_value > 100:
                        ctx.Append(336, "100", kind=wx.ITEM_RADIO)
        ctx.AppendSeparator()
        ctx.Append(wx.ID_ANY, "Закрыть", kind=wx.ITEM_NORMAL)
        if self.drop:
            ctx.Append(337, "Обнулить", kind=wx.ITEM_NORMAL)
        if self.type == 'float':
            self.Bind(wx.EVT_MENU, self._set_increment, id=331, id2=336)
        else:
            self.Bind(wx.EVT_MENU, self._set_increment, id=332, id2=336)
        self.Bind(wx.EVT_MENU, self.SetNull, id=337)

    def menu_add_drop_to_zero(self):
        """Добавляет пункт меню для обнуления значения"""
        self.drop = True
        self.Menu()

    def MouseWheel(self, e):
        if self.on_display:
            val = round(e.GetWheelRotation() / 120, 0)  # шаг крутилки 1
            self.SetValue(self.value + self.increment * val)

    def SetFont(self, size=20):
        self.display.SetFont(wx.Font(wx.FontInfo(size)))
        self.Layout()

    def SetNull(self, e=None):
        self.SetValue(0)

    def SetMinSizePanel(self, size):
        self.Panel.SetMinSize(size)
        self.Panel.Layout()

    def SetMinSizeBtn(self, size):
        self.btn_box.SetMinSize(size)
        self.Layout()

    def SetBgColor(self, color):
        self.color = color
        if isinstance(color, str):
            self.Panel.SetBackgroundColour(color)
        elif isinstance(color, tuple):
            self.Panel.SetBackgroundColour(wx.Colour(color))
        else:
            self.Panel.SetBackgroundColour(color)

    def SSH(self, minW=100, minH=50, maxW=200, maxH=100):
        ''' SetSizeHints '''
        self.SetSizeHints(minW=minW, minH=minH, maxW=maxW, maxH=maxH)

    def SetToolTip(self, tip):
        self.display.SetToolTip(tip)
        self.btn_up.SetToolTip(tip)
        self.btn_down.SetToolTip(tip)
        self.Panel.SetToolTip(tip)
        self.tooltip = tip

    def GetValue(self):
        return self.round_val(self.value)

    def _set_increment(self, e):
        inc_dic = {331: 0.1, 332: 1, 333: 5, 334: 10, 335: 50, 336: 100}
        print(f'_set_increment {e.GetId()}, {inc_dic[e.GetId()]}')
        self.increment = inc_dic[e.GetId()]
        # self.ctx_menu.Check(id=e.GetId(), check=True)
        self.display.SetToolTip(f'{self.tooltip}, шаг: {self.increment}')
        self.btn_up.SetToolTip(f'{self.tooltip}, шаг: {self.increment}')
        self.btn_down.SetToolTip(f'{self.tooltip}, шаг: {self.increment}')
        self.Panel.SetToolTip(f'{self.tooltip}, шаг: {self.increment}')

    def SetMax(self, val):
        self.max_value = val

    def SetMin(self, val):
        self.min_value = val

    def SetRange(self, min_val=-1000, max_val=1000):
        self.min_value = min_val
        self.max_value = max_val

    def OnLeftDown(self, e=None):
        print(f'OnLeftDown {self.name} {self.value}')
        self.popup_win = PopUPField(self, self.parent, color=self.color)
        e.Skip()

    def right_m_down(self, e):
        self.PopupMenu(self.ctx_menu)

    def round_val(self, val):
        if self.type == 'float':
            return round(float(val), 1)
        else:
            return _round(val)


    def SetValue(self, val):
        self.mem_value = self.value
        self.value = float(val)
        self.display.SetLabel(str(self.round_val(val)))
        # self.spin_btn.SetValue(int(self.value))
        # self.val_ctrl()

    def val_ctrl(self, e=None, direction=0):
        if e is not None:  # управление инкрементом
            direction = int(e.GetEventObject().GetName())

        self.increment = 1 if (self.type == 'int' and self.increment < 1) else self.increment

        # print('val_ctrl', self.max_value, self.min_value, self.value, self.increment, direction)
        val = self.value + self.increment * direction
        val = val if val < self.max_value else self.max_value
        val = val if val >= self.min_value else self.min_value
        self.mem_value = self.value
        self.value = val
        self.display.SetLabel(str(self.round_val(val)))
        self.Panel.Layout()
        if e is not None:
            e.Skip()




class TouchBtn(wx.Panel):
    """ Сенсорная кнопка """
    def __init__(self, parent=None, topParent=None, name='', bmp=None):
        wx.Panel.__init__(self, parent, id=-1, style=wx.BORDER_RAISED | wx.NO_FULL_REPAINT_ON_RESIZE)
        # self.SetSizeHints(minW=100, minH=50, maxW=200, maxH=100)
        self.parent = topParent
        self.fix_val_flag = False
        self.write_position = 50 # позиция в которую будет производится запись
        self.preffix = 'TouchPanel' # заголовок записи в конфиг
        self.name = name
        self.color = wx.BLACK #'#D7E4F2'
        self.bmp = bmp
        # self.Bind(wx.EVT_LEFT_DOWN, self.OnTouchBtn)
        # self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        # self.Bind(wx.EVT, self.OnEnter)
        self.value = 0.0
        self.value_mem = 0.0

        self.key_name = wx.StaticText(self, label=self.name)
        if name == '.':
            self.key_name.SetFont(wx.Font(wx.FontInfo(50)))
        else:
            self.key_name.SetFont(wx.Font(wx.FontInfo(25)))
        self.key_name.SetForegroundColour('#fdfd02')
        obj_list = [self.key_name, self]

        [obj.Bind(wx.EVT_LEFT_DOWN, self.OnTouchBtn) for obj in obj_list]
        [obj.Bind(wx.EVT_LEFT_DCLICK, self.OnTouchBtn) for obj in obj_list]
        [obj.Bind(wx.EVT_LEFT_UP, self.OnLeftUp) for obj in obj_list]

        main_box = wx.BoxSizer(wx.VERTICAL)
        # main_box = wx.StaticBoxSizer(wx.StaticBox(self, label=''), wx.VERTICAL)
        main_box.Add((1, 1), 1, flag=wx.EXPAND)
        main_box.Add(self.key_name, flag=wx.ALIGN_CENTER)
        main_box.Add((1, 1), 1, flag=wx.EXPAND)

        self.SetSizer(main_box)

    def OnTouchBtn(self, e=None):
        self.SetBackgroundColour(wx.WHITE)
        self.key_name.SetForegroundColour(wx.BLACK)
        self.Refresh()
        cur_txt = self.parent.display_text.GetLabel()
        print(f"OnTouchBtn {self.name} {cur_txt}, {cur_txt.find('.')}")
        self.play_sound(key_sound)
        if self.name == '<<<':
            if cur_txt:
                self.parent.display_text.SetLabel(cur_txt[:-1])
            else:
                winsound.PlaySound("SystemExclamation", winsound.SND_ASYNC)
        elif self.name == 'Ввод':
            self.parent.TextEnter()
        else:
            if cur_txt:
                if cur_txt[0] == '0' and self.name == '0':
                    winsound.PlaySound("SystemExclamation", winsound.SND_ASYNC)
                    return
                if cur_txt[-1] == '.' and self.name == '.':
                    winsound.PlaySound("SystemExclamation", winsound.SND_ASYNC)
                    return
                if self.name == '.' and cur_txt.find('.') > 0:
                    winsound.PlaySound("SystemExclamation", winsound.SND_ASYNC)
                    return
            self.parent.display_text.SetLabel(f'{cur_txt}{self.name}')

    def OnLeftUp(self, e=None):
        print(f'OnLeftUp {self.value}')
        self.SetBackgroundColour(wx.BLACK)
        self.key_name.SetForegroundColour('#fdfd02')
        self.Refresh()
        # th.Thread(target=self.flowUP, daemon=True).start()

    def flowUP(self):
        print('flowUP')
        self.SetBackgroundColour(wx.BLACK)
        self.key_name.SetForegroundColour('#fdfd02')
        self.Refresh()

    def play_sound(self, path_to_sound):
        # print('play_sound')
        try:
            winsound.PlaySound(path_to_sound, winsound.SND_ASYNC)
        except:
            pass


    def SSH(self, minW=55, minH=55, maxW=200, maxH=100):
        ''' SetSizeHints '''
        self.SetSizeHints(minW=minW, minH=minH, maxW=maxW, maxH=maxH)

    def SetBgColor(self, color):
        self.color = color
        if isinstance(color, str):
            self.SetBackgroundColour(color)
        elif isinstance(color, tuple):
            self.SetBackgroundColour(wx.Colour(color))
        else:
            self.SetBackgroundColour(color)

class TouchPanel(wx.Panel):
    """ Сенсорная панель """
    def __init__(self, parent=None, topParent=None, name=''):
        wx.Panel.__init__(self, parent, id=-1, style=wx.BORDER_RAISED | wx.NO_FULL_REPAINT_ON_RESIZE)
        # self.SetSizeHints(minW=100, minH=50, maxW=200, maxH=100)
        self.parent = topParent
        self.fix_val_flag = False
        self.write_position = 50 # позиция в которую будет производится запись
        self.preffix = 'TouchPanel' # заголовок записи в конфиг
        self.conf_data = topParent.conf_data
        self.name = name
        self.color = '#D7E4F2'
        # self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        # self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        # self.Bind(wx.EVT, self.OnEnter)
        self.value = 0.0
        self.value_mem = 0.0
        self.show_infinity = False

        self.display_Val = wx.StaticText(self, -1, '0.0')
        self.SetFont()

        self.infinityImg = wx.StaticBitmap(self, wx.ID_ANY, _infinity_big.GetBitmap())
        self.infinityImg.SetToolTip("Бесконечная экспозиция!")
        self.infinityImg.Hide()
        obj_list = [self.infinityImg, self.display_Val, self]

        [obj.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown) for obj in obj_list]
        [self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp) for obj in obj_list]

        main_box = wx.BoxSizer(wx.VERTICAL)
        # main_box = wx.StaticBoxSizer(wx.StaticBox(self, label=''), wx.VERTICAL)
        main_box.Add((1, 1), 1, flag=wx.EXPAND)
        main_box.Add(self.infinityImg, flag=wx.ALIGN_CENTER)
        main_box.Add(self.display_Val, flag=wx.ALIGN_CENTER)
        main_box.Add((1, 1), 1, flag=wx.EXPAND)

        self.SetSizer(main_box)

    def OnLeftDown(self, e=None):
        print(f'OnLeftDown {self.name} {self.value}')
        self.display_Val.SetLabel('')
        if self.show_infinity:
            self.infinityImg.Hide()
        if self.parent.touch_screen_use.IsChecked():
            self.popup_win = PopUPField(self, self.parent, color=self.color)
            self.popup_win.Show()
        else:
            self.popup_win = PopUPKeyboard(self, self.parent, color=self.color)
            self.popup_win.Show()


    def OnLeftUp(self, e=None):
        self.display_Val.SetLabel(f'{self.value:.1f}')
        if self.show_infinity:
            self.infinityImg.Show()

    def SSH(self, minW=100, minH=50, maxW=200, maxH=100):
        ''' SetSizeHints '''
        self.SetSizeHints(minW=minW, minH=minH, maxW=maxW, maxH=maxH)
    def SetBgColor(self, color):
        self.color = color
        if isinstance(color, str):
            self.SetBackgroundColour(color)
        elif isinstance(color, tuple):
            self.SetBackgroundColour(wx.Colour(color))
        else:
            self.SetBackgroundColour(color)

    def SetFont(self, size=20):
        self.display_Val.SetFont(wx.Font(wx.FontInfo(size)))
        self.Layout()

    def SetValue(self, val, forced_round=False):
        try:
            val = float(val)
        except:
            val = 0
        # print(f'SetValue {self.name} {val}')
        # try:
        #     val = round(float(val), 1)
        #     if self.name == 'set_timer':
        #         val = _round(val)
        # except:
        #     val = self.value
        if self.fix_val_flag:
            self.conf_data[self.write_position] = f'{self.preffix} {val}'
            writer_conf(self.conf_data)

        if val == 0.0:
            self.value = 0.0
            if self.show_infinity:
                self.infinityImg.Show()
                self.display_Val.Hide()
                self.display_Val.SetLabel('0.0')

            if self.name == 'set_timer':
                self.display_Val.SetLabel(f'{0}')
            else:
                self.display_Val.SetLabel('0.0')
        else:
            self.value = val
            self.infinityImg.Hide()
            self.display_Val.Show()
            if self.name == 'set_timer' and not self.parent.min_sec_btn.GetValue() or not self.parent.min_sec_btn2.GetValue():
                self.display_Val.SetLabel(f'{val}')
            else:
                if forced_round:
                    self.display_Val.SetLabel(f'{_round(val)}')
                else:
                    self.display_Val.SetLabel(f'{val:.1f}')
            #
            # if self.show_infinity and not self.display_Val.IsShown():

        self.Layout()

    def GetValue(self):
        return self.value

class XDAV(wx.MiniFrame):
    """ Панель для настройки фильтра X-DAV """
    def __init__(self, parent, pos=wx.DefaultPosition, size=(350, 280), style=wx.DEFAULT_FRAME_STYLE):
        title = 'Настройки фильтра X-DAV'
        wx.MiniFrame.__init__(self, parent, -1, title, pos, size, style)
        self.parent = parent  # videoPanel

        self.panel = panel = wx.Panel(self, -1)
        blankSizer = wx.BoxSizer(wx.VERTICAL)
        self.Items()
        sb_H1 = wx.StaticBoxSizer(wx.StaticBox(panel, label='Hue:'), wx.VERTICAL)
        sb_H1.Add(self.h_lower, flag=wx.EXPAND | wx.LEFT| wx.RIGHT, border=5)
        sb_S1 = wx.StaticBoxSizer(wx.StaticBox(panel, label='Sat:'), wx.VERTICAL)
        sb_S1.Add(self.s_lower, flag=wx.EXPAND | wx.LEFT| wx.RIGHT, border=5)
        sb_V1 = wx.StaticBoxSizer(wx.StaticBox(panel, label='Value:'), wx.VERTICAL)
        sb_V1.Add(self.v_lower, flag=wx.EXPAND | wx.LEFT| wx.RIGHT, border=5)

        sb_H2 = wx.StaticBoxSizer(wx.StaticBox(panel, label='Hue:'), wx.VERTICAL)
        sb_H2.Add(self.h_upper, flag=wx.EXPAND | wx.LEFT| wx.RIGHT, border=5)
        sb_S2 = wx.StaticBoxSizer(wx.StaticBox(panel, label='Sat:'), wx.VERTICAL)
        sb_S2.Add(self.s_upper, flag=wx.EXPAND | wx.LEFT| wx.RIGHT, border=5)
        sb_V2 = wx.StaticBoxSizer(wx.StaticBox(panel, label='Value:'), wx.VERTICAL)
        sb_V2.Add(self.v_upper, flag=wx.EXPAND | wx.LEFT| wx.RIGHT, border=5)


        h_box1 = wx.StaticBoxSizer(wx.StaticBox(panel, label='Нижняя граница диапазона:'), wx.HORIZONTAL)
        h_box2 = wx.StaticBoxSizer(wx.StaticBox(panel, label='Верхняя граница диапазона:'), wx.HORIZONTAL)
        h_box1.Add(sb_H1, flag=wx.ALL, border=5)
        h_box1.Add(sb_S1, flag=wx.ALL, border=5)
        h_box1.Add(sb_V1, flag=wx.ALL, border=5)

        h_box2.Add(sb_H2, flag=wx.ALL, border=5)
        h_box2.Add(sb_S2, flag=wx.ALL, border=5)
        h_box2.Add(sb_V2, flag=wx.ALL, border=5)

        blankSizer.Add(h_box1, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        blankSizer.Add(h_box2, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        blankSizer.Add(hbox, flag=wx.ALIGN_CENTER) # | wx.ALL, border=5)
        hbox.Add(self.save_btn, flag=wx.ALIGN_CENTER) # | wx.ALL, border=5)
        hbox.Add(self.btnCn, flag=wx.ALIGN_CENTER)   #wx.BOTTOM, border=5)

        panel.SetSizer(blankSizer)
        self.BindItems()
        self.Layout()

    def BindItems(self):
        # self.Bind(wx.EVT_BUTTON, self.OnCloseMe, self.button)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.btnCn.Bind(wx.EVT_BUTTON, self.OnCloseWindow)
        self.save_btn.Bind(wx.EVT_BUTTON, self.SaveOffset)


    def h_lover_update(self, e):
        self.panel.h_lower = self.h_lower.GetValue()

    def Items(self):

        self.h_lower = MySpinCtrl(self.panel, name='h_lower', font_size=14, type='int', style=wx.BORDER_SUNKEN)
        self.h_lower.SetToolTip('Цветовой тон, оттенок который нас интересует диапазон от 0 до 179')
        self.h_lower.SetRange(0, 179)
        self.h_lower.SetValue(self.parent.h_lower)
        self.h_lower.SetMinSize((50, -1))


        self.s_lower = MySpinCtrl(self.panel, name='s_lower', font_size=14, type='int', style=wx.BORDER_SUNKEN)
        self.s_lower.SetToolTip('Насыщенность или яркость цвета от 0 до 255, где 0 - отсутствие цвета, 255 - максимально насыщенный цвет')
        self.s_lower.SetRange(0, 255)
        self.s_lower.SetValue(self.parent.s_lower)
        self.s_lower.SetMinSize((50, -1))

        self.v_lower = MySpinCtrl(self.panel, name='s_lower', font_size=14, type='int', style=wx.BORDER_SUNKEN)
        self.v_lower.SetToolTip('Насыщенность или яркость цвета от 0 до 255, где 0 - отсутствие цвета, 255 - максимально насыщенный цвет')
        self.v_lower.SetRange(0, 255)
        self.v_lower.SetValue(self.parent.v_lower)
        self.v_lower.SetMinSize((50, -1))

        self.h_upper = MySpinCtrl(self.panel, name='h_lower', font_size=14, type='int', style=wx.BORDER_SUNKEN)
        self.h_upper.SetToolTip('Цветовой тон, оттенок который нас интересует диапазон от 0 до 179')
        self.h_upper.SetRange(0, 179)
        self.h_upper.SetValue(self.parent.h_upper)
        self.h_upper.SetMinSize((50, -1))

        self.s_upper = MySpinCtrl(self.panel, name='s_lower', font_size=14, type='int', style=wx.BORDER_SUNKEN)
        self.s_upper.SetToolTip('Насыщенность или яркость цвета от 0 до 255, где 0 - отсутствие цвета, 255 - максимально насыщенный цвет')
        self.s_upper.SetRange(0, 255)
        self.s_upper.SetValue(self.parent.s_upper)
        self.s_upper.SetMinSize((50, -1))

        self.v_upper = MySpinCtrl(self.panel, name='s_lower', font_size=14, type='int', style=wx.BORDER_SUNKEN)
        self.v_upper.SetToolTip('Насыщенность или яркость цвета от 0 до 255, где 0 - отсутствие цвета, 255 - максимально насыщенный цвет')
        self.v_upper.SetRange(0, 255)
        self.v_upper.SetValue(self.parent.v_upper)
        self.v_upper.SetMinSize((50, -1))




        self.save_btn = btn.ThemedGenBitmapTextButton(self.panel, wx.ID_OK, _ok.GetBitmap(),
                                                      "Сохранить настройки", size=(170, 38))
        self.save_btn.SetUseFocusIndicator(False)

        self.btnCn = wx.Button(self.panel, wx.ID_CANCEL, label='Закрыть', size=(70, 36))

    def GetParams(self):
        return (self.h_lower.GetValue(), self.s_lower.GetValue(), self.v_lower.GetValue(),
                self.h_upper.GetValue(), self.s_upper.GetValue(), self.v_upper.GetValue())

    def OnCloseWindow(self, event):
        self.Destroy()

    def SaveOffset(self, e):
        self.conf_data = dev_config_reader()
        self.parent.h_lower = self.h_lower.GetValue()
        self.parent.s_lower = self.s_lower.GetValue()
        self.parent.v_lower = self.v_lower.GetValue()
        self.parent.h_upper = self.h_upper.GetValue()
        self.parent.s_upper = self.s_upper.GetValue()
        self.parent.v_upper = self.v_upper.GetValue()
        print()

        self.conf_data[32] = f'h_lower: {self.h_lower.GetValue()}'
        self.conf_data[33] = f's_lower: {self.s_lower.GetValue()}'
        self.conf_data[34] = f'v_lower: {self.v_lower.GetValue()}'
        self.conf_data[35] = f'h_upper: {self.h_upper.GetValue()}'
        self.conf_data[36] = f's_upper: {self.s_upper.GetValue()}'
        self.conf_data[37] = f'v_upper: {self.v_upper.GetValue()}'
        configWriter(self.conf_data)
        self.Destroy()

