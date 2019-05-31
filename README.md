# lrcGenerater

这是一个用于获取已经下载的歌曲 从网易云服务器获取 对应lrc文件的工具
说明：此工具需要Chrome浏览器，并且需要下载对应驱动
驱动下载地址： http://chromedriver.storage.googleapis.com/index.html

使用
1.打开lrcGenerater.py文件
2.设置 endList 这是需要匹配的歌曲文件格式
3.设置 chromeDriver 这是chrome浏览器驱动文件所在路径
4.设置 localDir  这是歌曲所在的路径，也是lrc文件保存路径
5.python3 ./lrcGenerater.py 

安装
pip install selenium requests