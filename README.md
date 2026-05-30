# TaskReminder

Windows 本地 GUI 任务提醒工具，使用 PySide6 实现。

## 功能

- 通过日期时间选择控件添加一次性提醒任务
- JSON 持久化保存任务
- 到点后弹窗提醒并显示系统托盘通知
- 关闭窗口时最小化到系统托盘
- 支持注册表 Run 项开机自启
- 支持 PyInstaller 打包为 exe

## 开发运行

```powershell
pip install -r requirements.txt
python main.py
```

## 打包

```powershell
pyinstaller taskreminder.spec
```

打包结果位于 `dist/TaskReminder.exe`。
