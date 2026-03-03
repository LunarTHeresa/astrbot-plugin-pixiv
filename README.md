# AstrBot Pixiv 插件

一个用于 AstrBot 的 Pixiv 插件，支持搜索和查看 Pixiv 的图片和小说。

## 功能特性

- 🔍 搜索 Pixiv 插画和小说
- 📊 查看排行榜
- 💡 获取推荐作品
- 📖 查看作品详情
- 🔞 支持 R18 内容（单独指令）

## 安装

1. 将插件文件夹放入 AstrBot 的插件目录

2. 安装依赖：
   
   ```bash
   pip install -r requirements.txt
   ```

3. 配置 `config.json` 文件

## 配置说明

编辑 `config.json` 文件：

```json
{
  "refresh_token": "YOUR_PIXIV_REFRESH_TOKEN_HERE",
  "proxy": "",
  "language": "zh-cn"
}
```

### 获取 Refresh Token

1. 访问 https://github.com/eggplants/get-pixivpy-token
2. 按照说明获取你的 Pixiv refresh_token
3. 将 token 填入 config.json

或者使用以下 Python 脚本获取：

```python
from pixivpy3 import AppPixivAPI

api = AppPixivAPI()
api.login("your_username", "your_password")
print(api.refresh_token)
```

## 使用指令

### 普通内容指令

#### 搜索插画

```
/pixiv <关键词>
```

示例：`/pixiv 风景`

搜索指定关键词的插画作品（不包含 R18）

#### 搜索小说

```
/pixiv-novel <关键词>
```

示例：`/pixiv-novel 恋爱`

搜索指定关键词的小说作品（不包含 R18）

#### 查看排行榜

```
/pixiv-rank [模式]
```

示例：

- `/pixiv-rank` - 日榜
- `/pixiv-rank week` - 周榜
- `/pixiv-rank month` - 月榜

可用模式：

- `day` - 日榜（默认）
- `week` - 周榜
- `month` - 月榜
- `day_male` - 男性向日榜
- `day_female` - 女性向日榜

#### 获取推荐作品

```
/pixiv-recommend
```

获取系统推荐的插画作品（不包含 R18）

#### 查看作品详情

```
/pixiv-detail <作品ID>
```

示例：`/pixiv-detail 123456789`

查看指定 ID 的作品详细信息

---

### R18 内容指令

⚠️ **警告：以下指令会返回 R18 内容，请确保在合适的环境下使用**

#### 搜索插画（含 R18）

```
/pixiv-r18 <关键词>
```

示例：`/pixiv-r18 关键词`

搜索插画，包含 R18 内容

#### 搜索小说（含 R18）

```
/pixiv-novel-r18 <关键词>
```

示例：`/pixiv-novel-r18 关键词`

搜索小说，包含 R18 内容

#### 查看 R18 排行榜

```
/pixiv-rank-r18 [模式]
```

示例：

- `/pixiv-rank-r18` - R18 日榜
- `/pixiv-rank-r18 week` - R18 周榜

可用模式：

- `day_r18` - R18 日榜（默认）
- `week_r18` - R18 周榜
- `day_male_r18` - R18 男性向日榜
- `day_female_r18` - R18 女性向日榜

#### 获取推荐作品（含 R18）

```
/pixiv-recommend-r18
```

获取推荐作品，包含 R18 内容

---

## 指令速查表

| 功能   | 普通指令                 | R18 指令                   |
| ---- | -------------------- | ------------------------ |
| 搜索插画 | `/pixiv <关键词>`       | `/pixiv-r18 <关键词>`       |
| 搜索小说 | `/pixiv-novel <关键词>` | `/pixiv-novel-r18 <关键词>` |
| 排行榜  | `/pixiv-rank [模式]`   | `/pixiv-rank-r18 [模式]`   |
| 推荐作品 | `/pixiv-recommend`   | `/pixiv-recommend-r18`   |
| 作品详情 | `/pixiv-detail <ID>` | 同左                       |

## 注意事项

1. **登录要求**：使用前必须配置有效的 refresh_token
2. **API 限制**：Pixiv API 有访问频率限制，请勿频繁调用
3. **R18 内容**：R18 相关指令需要谨慎使用，确保符合当地法律法规
4. **网络环境**：部分地区可能需要配置代理才能访问 Pixiv
5. **结果数量**：为避免刷屏，搜索结果默认限制为 10 条

## 代理配置

如果需要使用代理，在 `config.json` 中配置：

```json
{
  "refresh_token": "YOUR_TOKEN",
  "proxy": "http://127.0.0.1:7890"
}
```

然后在代码中添加代理支持（需要修改 main.py）：

```python
if self.config.get("proxy"):
    self.api.set_additional_headers({'Proxy': self.config.get("proxy")})
```

## 常见问题

### Q: 提示"未登录"怎么办？

A: 检查 config.json 中的 refresh_token 是否正确配置

### Q: 搜索结果为空？

A: 可能是关键词问题，或者该关键词下没有符合条件的作品

### Q: 无法访问 Pixiv？

A: 部分地区需要配置代理，请在 config.json 中设置 proxy 字段

### Q: R18 指令没有返回内容？

A: 确保你的 Pixiv 账号已开启 R18 内容显示权限

## 开发者信息

- 基于 pixivpy3 库开发
- 支持 AstrBot 框架
- 遵循 Pixiv 使用条款

## 许可证

MIT License

## 更新日志

### v1.0.0

- 初始版本
- 支持搜索插画和小说
- 支持排行榜和推荐
- 支持 R18 内容单独指令
