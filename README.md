# AstrBot Pixiv 插件（无需Token版）

一个用于 AstrBot 的 Pixiv 插件，**无需 refresh_token**，使用第三方 API 实现所有功能。

## 功能特性

✅ 搜索 Pixiv 插画
✅ 查看排行榜
✅ 获取推荐作品（**稳定可用，直接发送图片**）
✅ 查看作品详情（**稳定可用，直接发送图片**）
✅ 随机图片（**稳定可用，直接发送图片**）
✅ 支持 R18 内容（单独指令）
✅ **无需登录，无需配置**

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

## 使用指令

### ✅ 稳定可用的指令（推荐使用）

这些指令使用 `pixiv.yuki.sh` API，**稳定可靠，会直接发送图片**：

#### 随机图片
```
/pixiv-random
```
获取一张随机图片（过滤R18内容）

#### 随机图片（R18）
```
/pixiv-random-r18
```
获取一张随机图片（包含R18内容）

#### 推荐作品
```
/pixiv-recommend
```
获取推荐作品（过滤R18内容）

#### 推荐作品（R18）
```
/pixiv-recommend-r18
```
获取推荐作品（包含R18内容）

#### 查看作品详情
```
/pixiv-detail <作品ID>
```
示例：`/pixiv-detail 123456789`
根据作品ID查看详情并获取图片

---

### ⚠️ 可能不稳定的指令

这些指令使用 `api.obfs.dev` API，**可能返回530错误**，如遇问题请使用上面的稳定指令：

#### 搜索插画
```
/pixiv <关键词>
```
示例：`/pixiv 风景`
搜索插画，返回作品列表（使用 `/pixiv-detail <ID>` 查看图片）

#### 搜索插画（含 R18）
```
/pixiv-r18 <关键词>
```
搜索插画（包含R18内容）

#### 查看排行榜
```
/pixiv-rank [模式]
```
示例：
- `/pixiv-rank` - 日榜
- `/pixiv-rank week` - 周榜
- `/pixiv-rank month` - 月榜

可用模式：`day`, `week`, `month`, `day_male`, `day_female`

#### R18 排行榜
```
/pixiv-rank-r18 [模式]
```
可用模式：`day_r18`, `week_r18`, `day_male_r18`, `day_female_r18`

---

## 指令速查表

| 功能 | 普通指令 | R18 指令 | 稳定性 |
|------|---------|---------|--------|
| 搜索插画 | `/pixiv <关键词>` | `/pixiv-r18 <关键词>` | ⚠️ 可能不稳定 |
| 排行榜 | `/pixiv-rank [模式]` | `/pixiv-rank-r18 [模式]` | ⚠️ 可能不稳定 |
| 推荐作品 | `/pixiv-recommend` | `/pixiv-recommend-r18` | ✅ 稳定，发送图片 |
| 随机图片 | `/pixiv-random` | `/pixiv-random-r18` | ✅ 稳定，发送图片 |
| 作品详情 | `/pixiv-detail <ID>` | 同左 | ✅ 稳定，发送图片 |

## 技术说明

本插件使用以下第三方 API：

### 稳定 API（pixiv.yuki.sh）
用于以下功能：
- ✅ 随机图片（`/pixiv-random`, `/pixiv-random-r18`）
- ✅ 推荐作品（`/pixiv-recommend`, `/pixiv-recommend-r18`）
- ✅ 作品详情（`/pixiv-detail`）

**特点：**
- 稳定可靠
- 直接发送图片到聊天
- 自动域名优化（i.yuki.sh）
- 心跳检测机制

### 不稳定 API（api.obfs.dev）
用于以下功能：
- ⚠️ 搜索功能（`/pixiv`, `/pixiv-r18`）
- ⚠️ 排行榜功能（`/pixiv-rank`, `/pixiv-rank-r18`）

**注意：** 该API可能返回530错误，如遇问题请使用稳定指令。

## 优点

- ✅ 无需 Pixiv 账号
- ✅ 无需 refresh_token
- ✅ 安装即用，零配置
- ✅ 核心功能稳定可靠
- ✅ 图片直接发送，无需手动点击链接

## 注意事项

1. 搜索和排行榜功能依赖 `api.obfs.dev`，可能不稳定
2. 如遇530错误，建议使用 `/pixiv-random` 或 `/pixiv-detail` 等稳定功能
3. 所有稳定功能都会直接发送图片到聊天

## 更新日志

### v2.1.1
- 推荐功能改用稳定的 pixiv.yuki.sh API
- 所有稳定功能现在都会直接发送图片
- 优化错误提示，区分稳定和不稳定功能

### v2.1.0
- 完整重写插件代码
- 添加心跳检测机制
- 域名自动替换优化
- 完善错误处理

### v2.0.x
- 重写插件，使用第三方 API
- 移除 refresh_token 依赖
- 新增随机图片功能

### v1.0.x
- 初始版本（需要 token）

## 许可证

MIT License

## 致谢

- [pixiv.yuki.sh](https://pixiv.yuki.sh) - 提供稳定的图床服务
- [api.obfs.dev](https://api.obfs.dev) - 提供 Pixiv API 代理
