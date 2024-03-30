# 幻塔小工具 
## 界面 
<img src="https://github.com/Mommm233/Fantasy-Tower-Tools/blob/main/img/ui.png" width="400px">

## 功能 
自动拾取+钓鱼+修改部分GameUserSettings.ini文件内容
## 打包 
pyinstaller --uac-admin --icon=img\\fle.jpg --name=幻塔小工具 ./src/app.py ./src/changeconfig.py ./src/controlf.py ./src/controlfish.py ./src/identify.py --noconsole  
幻塔小工具文件夹要有_internal、img、platforms(从幻塔小工具\_internal\PyQt5\Qt5\plugins\platforms剪切到幻塔小工具\)、config.json、幻塔小工具.exe
