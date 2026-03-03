## 服务器无法访问 GitHub 的解决方案

### 方法 1：上传 zip 文件到服务器（推荐）

1. 将本地的 zip 文件上传到服务器：
```bash
# 在本地 Windows 执行
scp "C:\Users\As\OneDrive\Desktop\个人资料\astrbot_plugin_pixiv.zip" root@your-server:/tmp/
```

2. 在 AstrBot 插件市场界面：
   - 点击 "+ 安装"
   - 选择 "从本地安装" 或 "上传文件"
   - 选择服务器上的 `/tmp/astrbot_plugin_pixiv.zip`

### 方法 2：手动解压安装

```bash
# SSH 到服务器
ssh root@your-server

# 上传后解压到插件目录
cd /path/to/astrbot/data/plugins
unzip /tmp/astrbot_plugin_pixiv.zip -d astrbot_plugin_pixiv

# 安装依赖
pip3 install pixivpy3 aiohttp

# 配置插件
cd astrbot_plugin_pixiv
cp config.example.json config.json
nano config.json  # 填入 refresh_token

# 重启 AstrBot
systemctl restart astrbot
```

### 方法 3：配置代理

如果服务器有代理，在 AstrBot 配置中添加代理设置，然后再从 GitHub 安装。
