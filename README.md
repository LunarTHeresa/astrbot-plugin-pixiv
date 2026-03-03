# AstrBot Pixiv 插件（无需Token版）

一个用于 AstrBot 的 Pixiv 插件，**无需 refresh_token**，使用第三方 API 实现所有功能。

## 功能特性

✅ 搜索 Pixiv 插画
✅ 查看排行榜
✅ 获取推荐作品
✅ 查看作品详情
✅ 随机图片
✅ 支持 R18 内容（单独指令）
✅ **无需登录，无需配置**

## 安装

### 方法 1：从 GitHub 安装

在 AstrBot 插件市场输入：
```
https://github.com/LunarTHeresa/astrbot-plugin-pixiv
```

### 方法 2：本地安装

1. 下载插件文件
2. 在 AstrBot 插件市场选择"从本地安装"
3. 上传 zip 文件

## 使用指令

### 普通内容指令

#### 搜索插画
```
/pixiv <关键词>
```
示例：`/pixiv 风景`

#### 查看排行榜
```
/pixiv-rank [模式]
```
示例：
- `/pixiv-rank` - 日榜
- `/pixiv-rank week` - 周榜
- `/pixiv-rank month` - 月榜

可用模式：`day`, `week`, `month`, `day_male`, `day_female`

#### 获取推荐作品
```
/pixiv-recommend
```

#### 随机图片
```
/pixiv-random
```

#### 查看作品详情
```
/pixiv-detail <作品ID>
```
示例：`/pixiv-detail 123456789`

---

### R18 内容指令

⚠️ **警告：以下指令会返回 R18 内容**

#### 搜索插画（含 R18）
```
/pixiv-r18 <关键词>
```

#### R18 排行榜
```
/pixiv-rank-r18 [模式]
```
可用模式：`day_r18`, `week_r18`, `day_male_r18`, `day_female_r18`

#### 推荐作品（含 R18）
```
/pixiv-recommend-r18
```

#### 随机图片（含 R18）
```
/pixiv-random-r18
```

---

## 指令速查表

| 功能 | 普通指令 | R18 指令 |
|------|---------|---------|
| 搜索插画 | `/pixiv <关键词>` | `/pixiv-r18 <关键词>` |
| 排行榜 | `/pixiv-rank [模式]` | `/pixiv-rank-r18 [模式]` |
| 推荐作品 | `/pixiv-recommend` | `/pixiv-recommend-r18` |
| 随机图片 | `/pixiv-random` | `/pixiv-random-r18` |
| 作品详情 | `/pixiv-detail <ID>` | 同左 |

## 技术说明

本插件使用以下第三方 API：
- `api.obfs.dev` - 主要 API（搜索、排行榜、推荐）
- `pixiv.yuki.sh` - 备用 API（作品详情、随机图片）

**优点：**
- 无需 Pixiv 账号
- 无需 refresh_token
- 安装即用，零配置
- 稳定可靠

**注意事项：**
1. 依赖第三方 API 服务可用性
2. 部分功能可能受 API 限制
3. 搜索结果默认限制为 10 条

## 更新日志

### v2.0.0
- 重写插件，使用第三方 API
- 移除 refresh_token 依赖
- 新增随机图片功能
- 优化错误处理

### v1.0.x
- 初始版本（需要 token）

## 许可证

MIT License

## 致谢

- [pixiv.yuki.sh](https://pixiv.yuki.sh) - 提供图床服务
- [api.obfs.dev](https://api.obfs.dev) - 提供 Pixiv API 代理
