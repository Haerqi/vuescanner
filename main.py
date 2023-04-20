import PySimpleGUI as sg
import requests
import re
import datetime
import os
import threading



layout = [
[
[sg.Text('请输入app.js的链接：'), sg.Input(key='-LINK-'), sg.Button('获取路径'), sg.Button('追加获取路径'),
sg.Text('请输入测试链接：'), sg.Input(key='-TEST-LINK-'), sg.Button('状态码测试'), sg.Button('响应体测试')]
],

[sg.HorizontalSeparator()],
[sg.Multiline(size=(90, 30), key='-OUTPUT-'), sg.Multiline(size=(90, 30), key='-RESPONSE-')],
[sg.Button('保存测试日志')]
]

window = sg.Window('vue未授权接口扫描器 by j0phe', layout)

def get_paths(link):
    try:
        response = requests.get(link,verify=False)
        paths = re.findall(r'path:"(.*?)"', response.text)
        # 给paths中的每个元素加上换行
        paths = [path + '\n' for path in paths]
        return paths
    except Exception as e:
        now = datetime.datetime.now()
        filename = os.path.join('error', now.strftime('%Y-%m-%d %H-%M-%S') + '.error.log')
        with open(filename, 'w') as f:
            f.write(str(e))
        sg.popup_error(str(e))
        return []

def test_paths(paths, test_link,stauts_code=True):
    for i in paths:
        try:
            if stauts_code != True:
                # 响应体测试
                response = requests.get(test_link + i, verify=False)
                window['-RESPONSE-'].update(
                window['-RESPONSE-'].get() + '\n请求' + test_link + i + '\n响应体：' + response.text + '\n')
                continue
            else:
                response = requests.get(test_link + i, verify=False)
                window['-RESPONSE-'].update(
                window['-RESPONSE-'].get() + '\n请求' + test_link + i + '\n状态码：' + str(response.status_code) + '\n' + '响应体大小：' + str(len(response.text)) + '\n')
        except Exception as e:
            now = datetime.datetime.now()
            filename = os.path.join('error', now.strftime('%Y-%m-%d %H-%M-%S') + '.error.log')
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(str(e))
            sg.popup_error(str(e))

def save_response(response):
    now = datetime.datetime.now()
    filename = now.strftime('%Y-%m-%d %H-%M-%S') + '.log'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(response)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    if event == '获取路径' or event == '追加获取路径':
        link = values['-LINK-']
        paths = get_paths(link)
    if event == '获取路径':
        if paths == []:
            window['-OUTPUT-'].update('未获取到路径！')
            continue
        window['-OUTPUT-'].update(''.join(paths))
    else:
        window['-OUTPUT-'].update(window['-OUTPUT-'].get() + '' + ''.join(paths))
    if event == '状态码测试' or event == '响应体测试':
        if values['-TEST-LINK-'] == '':
            sg.popup_error('测试链接不能为空！')
            continue
        paths = window['-OUTPUT-'].get().split('\n')
        # 如果paths中的元素第一个字符是/，则去掉
        paths = [path[1:] if path.startswith('/') else path for path in paths]
        # 如果paths中的元素为''，则删除
        paths = [path for path in paths if path != '']
        if event == '响应体测试':
            threading.Thread(target=test_paths, args=(paths, values['-TEST-LINK-'], False)).start()
        else:
            threading.Thread(target=test_paths, args=(paths, values['-TEST-LINK-'])).start()
    if event == '保存测试日志':
        save_response(values['-RESPONSE-'])

window.close()