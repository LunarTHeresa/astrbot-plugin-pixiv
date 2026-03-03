# 使用指南

## 快速开始

### 1. 获取 Refresh Token

访问以下链接，按照教程获取你的 refresh_token：
https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362

### 2. 配置插件

在 AstrBot WebUI 中：
1. 进入"插件管理"
2. 找到 Pixiv 插件
3. 点击"配置"
4. 填写 `refresh_token`
5. 选择 R18 过滤模式
6. 保存并重启插件

### 3. 开始使用

```bash
# 搜索插画
/pixiv 初音ミク

# 查看排行榜
/pixiv-rank

# 获取推荐
/pixiv-recommend

# 查看作品详情
/pixiv-detail 123456789

# 查看帮助
/pixiv-help
```

## R18 模式说明

### 过滤 R18（默认）
- 不显示任何 R18 内容
- 适合公共群聊使用

### 允许 R18
- 显示所有内容（包括 R18）
- 搜索和推荐会包含 R18 内容

### 仅 R18
- 只显示 R18 内容
- 排行榜自动切换到 R18 榜
- 搜索和推荐只返回 R18 作品

## 常见问题

### Q: 提示"未认证"怎么办？
A: 检查是否正确配置了 refresh_token，并重启插件。

### Q: 提示"认证失败"怎么办？
A: refresh_token 可能已过期，需要重新获取。

### Q: 如何提高访问速度？
A: 配置代理（proxy），例如：`http://127.0.0.1:7890`

### Q: 为什么搜索结果很少？
A: 可能被 R18 过滤了，可以调整 R18 模式为"允许 R18"。

### Q: 如何一次获取多张图片？
A: 修改配置中的 `return_count`，最大支持 10 张。

## 技术支持

如有问题，请访问：
https://github.com/LunarTHeresa/astrbot-plugin-pixiv/issues
