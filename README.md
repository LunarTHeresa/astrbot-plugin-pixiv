# AstrBot Pixiv 插件（官方API版）

一个用于 AstrBot 的 Pixiv 插件，使用**官方 Pixiv API**，功能稳定可靠。

## 功能特性

✅ 搜索 Pixiv 插画（稳定）
✅ 查看排行榜（支持日榜、周榜、月榜、R18榜）
✅ 获取推荐作品（稳定）
✅ 查看作品详情（稳定）
✅ 灵活的 R18 内容过滤（过滤/允许/仅R18）
✅ 直接发送图片到聊天
✅ 使用官方 API，稳定可靠

## 安装

### 方法 1：从 GitHub 安装（推荐）

在 AstrBot 插件市场输入：
```
https://github.com/LunarTHeresa/astrbot-plugin-pixiv
```

### 方法 2：本地安装

1. 下载插件文件
2. 在 AstrBot 插件市场选择"从本地安装"
3. 上传 zip 文件

## 配置

### 获取 Refresh Token

**必须配置 refresh_token 才能使用插件！**

#### 方法一：使用 gppt 工具（推荐）

```bash
pip install gppt
gppt
```

按照提示登录 Pixiv 账号，自动获取 refresh_token。

#### 方法二：手动获取

1. 打开浏览器开发者工具（F12）
2. 访问 Pixiv 登录页面
3. 登录后在 Network 中找到 refresh_token
4. 详细教程：[GET_TOKEN.md](./GET_TOKEN.md)

#### 方法三：参考官方教程

访问 https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362

获取到 token 后，在 AstrBot WebUI 的插件配置中填写。

### 配置选项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `refresh_token` | Pixiv API 认证令牌（必填） | 无 |
| `r18_mode` | R18内容过滤模式 | "过滤 R18" |
| `return_count` | 每次返回的图片数量 (1-10) | 1 |
| `proxy` | 代理地址（可选） | 无 |

### R18 过滤模式

- **过滤 R18**（默认）：不显示任何 R18 内容
- **允许 R18**：显示所有内容（包括 R18）
- **仅 R18**：只显示 R18 内容

## 使用指令

### 搜索插画
```
/pixiv <关键词>
```
示例：`/pixiv 初音ミク`

搜索插画，根据 R18 设置自动过滤内容

### 查看排行榜
```
/pixiv-rank [模式]
```
示例：
- `/pixiv-rank` - 日榜
- `/pixiv-rank week` - 周榜
- `/pixiv-rank month` - 月榜

可用模式：`day`, `week`, `month`, `day_male`, `day_female`

**R18 排行榜**：
- 如果设置为"仅 R18"模式，会自动使用 R18 排行榜
- 可用模式：`day_r18`, `week_r18`

### 推荐作品
```
/pixiv-recommend
```
获取推荐作品，根据 R18 设置自动过滤

### 查看作品详情
```
/pixiv-detail <作品ID>
```
示例：`/pixiv-detail 123456789`

根据作品ID查看详情并获取图片

### 帮助信息
```
/pixiv-help
```
查看使用帮助和当前配置

## 指令速查表

| 功能 | 指令 | 说明 |
|------|------|------|
| 搜索插画 | `/pixiv <关键词>` | 根据R18设置过滤 |
| 排行榜 | `/pixiv-rank [模式]` | 支持多种模式 |
| 推荐作品 | `/pixiv-recommend` | 根据R18设置过滤 |
| 作品详情 | `/pixiv-detail <ID>` | 查看指定作品 |
| 帮助 | `/pixiv-help` | 查看帮助信息 |

## 技术说明

本插件使用以下技术：

### 官方 Pixiv API
- 使用 `pixivpy3` 库（官方 API 的 Python 封装）
- 需要 `refresh_token` 进行认证
- 稳定可靠，功能完整

### 特点
- ✅ 使用官方 API，稳定性高
- ✅ 支持完整的 R18 过滤功能
- ✅ 直接发送图片到聊天
- ✅ 完善的错误处理
- ✅ 异步操作，性能优秀

## 优点

- ✅ 使用官方 API，稳定可靠
- ✅ 功能完整，支持搜索、排行榜、推荐
- ✅ 灵活的 R18 内容控制
- ✅ 图片直接发送，无需手动点击链接
- ✅ 支持代理配置

## 注意事项

1. **必须配置 refresh_token** 才能使用插件
2. refresh_token 需要定期更新（通常几个月）
3. 如果遇到认证失败，请检查 token 是否过期
4. 建议配置代理以提高访问速度

## 更新日志

### v3.0.0
- 完全重写，使用官方 Pixiv API
- 使用 `pixivpy3` 库替代第三方 API
- 添加灵活的 R18 过滤模式（过滤/允许/仅R18）
- 移除循环请求机制，直接使用官方 API 过滤
- 提高稳定性和可靠性
- 需要配置 refresh_token

### v2.2.0
- R18指令保证返回真正的R18内容
- 循环请求机制（最多10次）

### v2.1.1
- 使用第三方 API（无需 token）

## 许可证

MIT License

## 致谢

- [pixivpy3](https://github.com/upbit/pixivpy) - 提供官方 API 封装
- [Pixiv](https://www.pixiv.net/) - 提供官方 API
