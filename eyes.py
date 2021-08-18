from time import sleep
import threading
import unicodedata
import winsound

import uiautomation as ui #サードパーティ uiautomation
from uisoup import uisoup #サードパーティ MSAA
import pyttsx3 #サードパーティ 読み上げ
import wx #サードパーティ GUI
import  mouse #サードパーティ マウス関連
import keyboard #サードパーティ キーボード関連


class MainFrame(wx.Frame): #wxPythonの設定
    def __init__(self):
        wx.Frame.__init__(self,None,-1,"EyEs",size=(800,200))
        self.panel = wx.Panel(self,wx.ID_ANY)
        self.panel.SetBackgroundColour("#FFFFFF")
        self.text = wx.StaticText(self.panel,wx.ID_ANY,"ここにテキストが表示されます",style=wx.TE_CENTER)
        font = wx.Font(40, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)
        self.text.SetFont(font)
        layout = wx.BoxSizer(wx.VERTICAL)
        layout.Add(self.text,wx.CENTER)
        self.panel.SetSizer(layout)

    def text_change(self,text): #テキストを変える
        self.text.SetLabel(text)

def get_mouse(): #マウスの位置を取得
    global old_pos
    new_pos = mouse.get_position()
    if new_pos != old_pos: #前回拾った座標と違ったらget_by_uiを実行する
        old_pos = new_pos
        get_by_ui(old_pos[0],old_pos[1])

def get_by_ui(x,y): #uiautomationを利用して情報を取得する
    global old_elems_ui
    global old_elems_msaa
    try:
        new_elems_ui = ui.ControlFromPoint(x,y) #ここで取得
        if new_elems_ui.Name != old_elems_ui.Name and new_elems_ui.Name != '': #前回の情報と異なり、値が入ってたら...
            old_elems_ui = new_elems_ui
            if old_elems_ui.Name != old_elems_msaa: #前回のMSAAと比べる
                print("ui-----" + str(old_elems_ui.Name) + "/")
                speak(str(old_elems_ui.Name)) #話す
        else:
            get_by_msaa(x,y) #Falseだったらget_by_msaaを実行する
    except:
        get_by_msaa(x,y)

def get_by_msaa(x,y): #MSAAを利用して情報を取得する
    global old_elems_ui
    global old_elems_msaa_list
    global old_elems_msaa
    try:
        new_elems_msaa = uisoup.get_object_by_coordinates(x,y) #ここで取得
        new_elems_msaa_list = []

        get_value_key_list =['acc_role_name','acc_name','acc_value'] #色々付いてくるのでこの3つだけを取得する
        ''''''
        for key in get_value_key_list:
            try:
                elem = getattr(new_elems_msaa,key)
                new_elems_msaa_list.append(elem)
            except:
                new_elems_msaa_list.append('')
        if new_elems_msaa_list != old_elems_msaa_list and new_elems_msaa_list[1] != '': #前回の情報と異なり、値が入ってたら...
            old_elems_msaa_list = new_elems_msaa_list
            
            if old_elems_msaa_list[0] == "txt": #テキストオブジェクトだったら...
                old_elems_msaa = old_elems_msaa_list[2]
            else:
                old_elems_msaa = old_elems_msaa_list[1]
            if old_elems_msaa != old_elems_ui.Name: #前回のuiautomationと比べる
                print("msaa---" + str(old_elems_msaa) + "/")
                speak(str(old_elems_msaa))
    except:
        pass
        
def speak(text): #話す
    pass

    global engine
    global layout
    engine.save_to_file(text, "sound/output.mp3") #ここで音声ファイルを書き込む
    engine.runAndWait()
    winsound.PlaySound("sound/output.mp3",winsound.SND_ASYNC) #再生する
    #frame.text.SetLabel(text_count(text))

    frame.text_change(text_count(text)) #GUIに書き込む（その前に自動改行を実行する）

def text_count(text): #自動改行
    c = 0
    text_list = list()
    for w in text:
        if unicodedata.east_asian_width(w) in "FWA":
            c += 2
        else:
            c += 1
        text_list.append(w)
        if c >= 34:
            text_list.append("\n")
            c = 0
    text = "".join(text_list)

    return text

def key_speak(): #押したキーを通知する
    global old_key
    global engine
    count = 0
    engine2 = pyttsx3.init() #初期化
    while True:
        new_key = keyboard.read_key() #押されたキーを取得
        if new_key != old_key:
            old_key = new_key
            engine2.save_to_file(old_key, "sound/output_key.mp3")
            engine2.runAndWait()
            winsound.PlaySound("sound/output_key.mp3",winsound.SND_ASYNC)
        elif count >= 1:
            old_key = ""
        new_key = ""
        count += 1
        sleep(0.1)

def main():
    while True:
        get_mouse()
        sleep(0.1)
        
if __name__ == "__main__":
    old_pos = mouse.get_position() 
    old_elems_ui = ui.ControlFromPoint(old_pos[0],old_pos[1])
    old_elems_msaa_list = []
    old_elems_msaa = ""
    old_key = ""
    engine = pyttsx3.init() #初期化
    app = wx.App(False) #GUI作成
    frame = MainFrame() #GUIの中身を作る
    frame.Show()
    thread1 = threading.Thread(target=main) #別スレッドで実行
    thread1.setDaemon(True)
    thread1.start()
    thread2 = threading.Thread(target=key_speak) #別スレッドで実行
    thread2.setDaemon(True)
    thread2.start()
    app.MainLoop() #GUIループ
