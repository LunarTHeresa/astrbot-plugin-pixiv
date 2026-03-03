# 如何获取 Pixiv Refresh Token

## 方法一：使用 gppt（推荐，最简单）

### 1. 安装 gppt 工具

```bash
pip install gppt
```

### 2. 运行获取命令

```bash
gppt
```

### 3. 按照提示操作

1. 会自动打开浏览器
2. 登录你的 Pixiv 账号
3. 登录成功后，工具会自动获取 refresh_token
4. 复制显示的 refresh_token

---

## 方法二：手动获取（通过浏览器）

### 1. 准备工作

- 安装 Chrome 或 Firefox 浏览器
- 确保能访问 Pixiv（可能需要代理）

### 2. 获取步骤

#### 使用 Chrome：

1. 打开 Chrome 浏览器
2. 按 `F12` 打开开发者工具
3. 切换到 `Network`（网络）标签
4. 访问 https://app-api.pixiv.net/web/v1/login
5. 登录你的 Pixiv 账号
6. 在 Network 标签中找到 `login` 请求
7. 查看响应内容，找到 `refresh_token` 字段
8. 复制 refresh_token 的值

#### 使用 Firefox：

1. 打开 Firefox 浏览器
2. 按 `F12` 打开开发者工具
3. 切换到 `网络` 标签
4. 访问 https://app-api.pixiv.net/web/v1/login
5. 登录你的 Pixiv 账号
6. 在网络标签中找到 `login` 请求
7. 查看响应，找到 `refresh_token`
8. 复制 refresh_token 的值

---

## 方法三：使用 Python 脚本

### 1. 创建获取脚本

创建文件 `get_token.py`：

```python
from pixivpy3 import AppPixivAPI

api = AppPixivAPI()

# 替换为你的 Pixiv 用户名和密码
username = "your_username"
password = "your_password"

try:
    api.login(username, password)
    print(f"Refresh Token: {api.refresh_token}")
except Exception as e:
    print(f"登录失败: {e}")
```

### 2. 运行脚本

```bash
python get_token.py
```

### 3. 复制显示的 refresh_token

---

## 方法四：使用在线工具

访问以下网站，按照说明获取：
- https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362

---

## 注意事项

1. **refresh_token 是敏感信息**，不要分享给他人
2. **token 会过期**，通常几个月后需要重新获取
3. **保存好 token**，避免频繁获取
4. 如果提示"认证失败"，说明 token 已过期，需要重新获取

---

## 配置到插件

获取到 refresh_token 后：

1. 打开 AstrBot WebUI
2. 进入"插件管理"
3. 找到 Pixiv 插件
4. 点击"配置"
5. 在 `refresh_token` 字段粘贴你的 token
6. 保存并重启插件

---

## 常见问题

### Q: 提示"登录失败"怎么办？
A: 检查用户名和密码是否正确，确保能正常访问 Pixiv。

### Q: 需要代理吗？
A: 如果你所在地区无法直接访问 Pixiv，需要配置代理。

### Q: token 多久过期？
A: 通常几个月，过期后重新获取即可。

### Q: 可以用别人的 token 吗？
A: 不建议，token 绑定账号，使用别人的 token 可能导致账号问题。
