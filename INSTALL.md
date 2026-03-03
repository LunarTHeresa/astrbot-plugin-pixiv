# AstrBot Pixiv Plugin

## 快速安装（服务器端）

```bash
# 进入 AstrBot 插件目录
cd /path/to/your/astrbot/plugins

# 克隆或下载插件
git clone <your-repo-url> astrbot_plugin_pixiv
# 或者直接创建文件夹并上传文件

# 安装依赖
pip3 install pixivpy3 aiohttp

# 配置
nano astrbot_plugin_pixiv/config.json
# 填入 refresh_token

# 重启 AstrBot
systemctl restart astrbot  # 或使用你的启动方式
```

## 获取 Refresh Token

由于服务器可能无法直接登录 Pixiv，建议在本地获取 token：

```bash
# 在本地运行
python get_token.py
```

然后将获取的 token 填入服务器上的 config.json

## 检查插件是否加载

```bash
# 查看 AstrBot 日志
tail -f /path/to/astrbot/logs/latest.log

# 应该能看到类似信息：
# [INFO] Pixiv 插件登录成功
```
