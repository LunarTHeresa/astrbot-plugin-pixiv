# AstrBot Pixiv 插件（官方API版）

一个用于 AstrBot 的 Pixiv 插件，使用**官方 Pixiv API**，功能稳定可靠。

## 功能特性

✅ 搜索 Pixiv 插画（稳定）
✅ 查看排行榜（支持日榜、周榜、月榜、R18榜）
✅ 获取推荐作品（稳定）
✅ 查看作品详情（稳定）
✅ 分离的常规和 R18 指令
✅ 直接发送图片到聊天
✅ 使用官方 API，稳定可靠
✅ 内置代理支持

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

### 已内置配置

插件已经内置以下配置，**无需额外配置即可使用**：

- ✅ **refresh_token**：已内置
- ✅ **代理设置**：默认 `http://127.0.0.1:7897`（Clash Verge）
- ✅ **返回数量**：默认 1 张

如需修改，可在插件配置中覆盖默认值。

### 获取自己的 Refresh Token（可选）

如果想使用自己的 token：

1. 下载脚本：
```bash
curl -O https://gist.githubusercontent.com/ZipFile/c9ebedb224406f4f11845ab700124362/raw/pixiv_auth.py
```

2. 运行脚本：
```bash
python pixiv_auth.py login
```

3. 按照提示登录 Pixiv，获取 refresh_token

4. 在插件配置中填写你的 token

详细教程：https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362

## 使用指令

### 常规指令（过滤 R18 内容）

#### 搜索插画
```
/pixiv <关键词>
```
示例：`/pixiv 初音ミク`

搜索插画，自动过滤 R18 内容

#### 查看排行榜
```
/pixiv-rank [模式]
```
示例：
- `/pixiv-rank` - 日榜
- `/pixiv-rank week` - 周榜
- `/pixiv-rank month` - 月榜

可用模式：`day`, `week`, `month`, `day_male`, `day_female`

#### 推荐作品
```
/pixiv-recommend
```
获取推荐作品，自动过滤 R18 内容

#### 查看作品详情
```
/pixiv-detail <作品ID>
```
示例：`/pixiv-detail 123456789`

根据作品ID查看详情并获取图片

### R18 专用指令（只返回 R18 内容）

#### 搜索 R18 插画
```
/pixiv-r18 <关键词>
```
示例：`/pixiv-r18 初音ミク`

搜索插画，**只返回 R18 内容**

#### R18 排行榜
```
/pixiv-rank-r18 [模式]
```
示例：
- `/pixiv-rank-r18` - R18 日榜
- `/pixiv-rank-r18 week` - R18 周榜

可用模式：`day`, `week`

#### R18 推荐作品
```
/pixiv-recommend-r18
```
获取推荐作品，**只返回 R18 内容**

### 帮助信息
```
/pixiv-help
```
查看使用帮助和当前配置

## 指令速查表

| 功能 | 常规指令（过滤R18） | R18指令（仅R18） |
|------|-------------------|-----------------|
| 搜索插画 | `/pixiv <关键词>` | `/pixiv-r18 <关键词>` |
| 排行榜 | `/pixiv-rank [模式]` | `/pixiv-rank-r18 [模式]` |
| 推荐作品 | `/pixiv-recommend` | `/pixiv-recommend-r18` |
| 作品详情 | `/pixiv-detail <ID>` | - |
| 帮助 | `/pixiv-help` | - |

## 配置选项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `refresh_token` | Pixiv API 认证令牌 | 已内置 |
| `return_count` | 每次返回的图片数量 (1-10) | 1 |
| `proxy` | 代理地址 | `http://127.0.0.1:7897` |

## 技术说明

本插件使用以下技术：

### 官方 Pixiv API
- 使用 `pixivpy3` 库（官方 API 的 Python 封装）
- 需要 `refresh_token` 进行认证
- 稳定可靠，功能完整

### R18 内容处理
- **常规指令**：通过 `x_restrict == 0` 过滤 R18 内容
- **R18 指令**：通过 `x_restrict > 0` 只返回 R18 内容
- **R18 排行榜**：直接使用官方 `day_r18`, `week_r18` 排行榜

### 特点
- ✅ 使用官方 API，稳定性高
- ✅ 分离常规和 R18 指令，使用更灵活
- ✅ 直接发送图片到聊天
- ✅ 完善的错误处理
- ✅ 异步操作，性能优秀
- ✅ 内置代理支持

## 优点

- ✅ 使用官方 API，稳定可靠
- ✅ 功能完整，支持搜索、排行榜、推荐
- ✅ R18 指令保证返回 R18 内容
- ✅ 图片直接发送，无需手动点击链接
- ✅ 内置代理配置，开箱即用
- ✅ 无需配置，安装即用

## 注意事项

1. **代理配置**：默认使用 `http://127.0.0.1:7897`（Clash Verge），如果你的代理端口不同，请在配置中修改
2. **Token 过期**：内置的 refresh_token 可能会过期，过期后需要重新获取
3. **请求频率**：官方 API 有请求频率限制，请勿频繁请求
4. **R18 内容**：R18 指令只在设置允许的情况下使用，请遵守当地法律法规

## 更新日志

### v3.0.1
- 添加专门的 R18 指令（`/pixiv-r18`, `/pixiv-rank-r18`, `/pixiv-recommend-r18`）
- 常规指令默认过滤 R18 内容
- R18 指令保证只返回 R18 内容
- 内置代理配置（Clash Verge 7897 端口）
- 内置 refresh_token，无需配置即可使用

### v3.0.0
- 完全重写，使用官方 Pixiv API
- 使用 `pixivpy3` 库替代第三方 API
- 添加灵活的 R18 过滤模式
- 移除循环请求机制，直接使用官方 API 过滤
- 提高稳定性和可靠性

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
