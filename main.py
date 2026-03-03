"""
AstrBot Pixiv 插件 - 无需 Token 版本
使用第三方 API，支持搜索、排行榜、推荐等功能
"""
from astrbot.api.event import AstrMessageEvent
from astrbot.api.star import Context, Star, register
import httpx
import asyncio

@register("pixiv", "Pixiv 图片和小说查看插件（无需Token）", "2.0.0", "LunarTheresa")
class PixivPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        # 使用多个第三方 API
        self.api_base = "https://api.obfs.dev/api/pixiv"  # 主 API
        self.yuki_api = "https://pixiv.yuki.sh/api"  # 备用 API
        self.client = None

    async def on_load(self):
        """插件加载时调用"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        self.client = httpx.AsyncClient(timeout=30.0, headers=headers)
        self.context.logger.info("Pixiv 插件已加载（无需Token）")

    async def on_message(self, event: AstrMessageEvent):
        """处理消息"""
        message = event.message_str.strip()

        # 搜索插画
        if message.startswith("/pixiv "):
            keyword = message[7:].strip()
            await self.search_illust(event, keyword, r18=False)

        # 搜索插画（包含 R18）
        elif message.startswith("/pixiv-r18 "):
            keyword = message[11:].strip()
            await self.search_illust(event, keyword, r18=True)

        # 获取排行榜
        elif message.startswith("/pixiv-rank"):
            parts = message.split()
            mode = parts[1] if len(parts) > 1 else "day"
            await self.get_ranking(event, mode, r18=False)

        # 获取排行榜（R18）
        elif message.startswith("/pixiv-rank-r18"):
            parts = message.split()
            mode = parts[1] if len(parts) > 1 else "day_r18"
            await self.get_ranking(event, mode, r18=True)

        # 获取作品详情
        elif message.startswith("/pixiv-detail "):
            illust_id = message[14:].strip()
            await self.get_illust_detail(event, illust_id)

        # 获取推荐作品
        elif message == "/pixiv-recommend":
            await self.get_recommend(event, r18=False)

        # 获取推荐作品（R18）
        elif message == "/pixiv-recommend-r18":
            await self.get_recommend(event, r18=True)

        # 随机图片
        elif message == "/pixiv-random":
            await self.get_random(event, r18=False)

        # 随机图片（R18）
        elif message == "/pixiv-random-r18":
            await self.get_random(event, r18=True)

    async def search_illust(self, event: AstrMessageEvent, keyword: str, r18: bool = False):
        """搜索插画"""
        try:
            await event.reply(f"正在搜索插画: {keyword}...")

            url = f"{self.api_base}/search"
            params = {"word": keyword, "mode": "partial_match_for_tags"}

            resp = await self.client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

            if not data.get("illusts"):
                await event.reply("未找到相关插画")
                return

            illusts = data["illusts"][:10]
            if not r18:
                illusts = [i for i in illusts if i.get("x_restrict", 0) == 0]

            if not illusts:
                await event.reply("未找到符合条件的插画")
                return

            msg = f"找到 {len(illusts)} 个结果:\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += f"{idx}. {illust.get('title', '无标题')}\n"
                msg += f"   作者: {illust.get('user', {}).get('name', '未知')}\n"
                msg += f"   ID: {illust.get('id')}\n"
                tags = [tag.get('name', '') for tag in illust.get('tags', [])[:5]]
                msg += f"   标签: {', '.join(tags)}\n"
                msg += f"   链接: https://www.pixiv.net/artworks/{illust.get('id')}\n"
                if illust.get("x_restrict", 0) > 0:
                    msg += f"   ⚠️ R-18\n"
                msg += "\n"

            msg += "使用 /pixiv-detail <ID> 查看详情"
            await event.reply(msg)

        except Exception as e:
            self.context.logger.error(f"搜索插画失败: {e}")
            await event.reply(f"搜索失败，请稍后重试")

    async def get_ranking(self, event: AstrMessageEvent, mode: str = "day", r18: bool = False):
        """获取排行榜"""
        try:
            await event.reply(f"正在获取排行榜 ({mode})...")

            url = f"{self.api_base}/rank"
            params = {"mode": mode}

            resp = await self.client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

            if not data.get("illusts"):
                await event.reply("未找到排行榜数据")
                return

            illusts = data["illusts"][:10]

            msg = f"排行榜 ({mode}) 前 {len(illusts)} 名:\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += f"{idx}. {illust.get('title', '无标题')}\n"
                msg += f"   作者: {illust.get('user', {}).get('name', '未知')}\n"
                msg += f"   ID: {illust.get('id')}\n"
                msg += f"   链接: https://www.pixiv.net/artworks/{illust.get('id')}\n"
                if illust.get("x_restrict", 0) > 0:
                    msg += f"   ⚠️ R-18\n"
                msg += "\n"

            await event.reply(msg)

        except Exception as e:
            self.context.logger.error(f"获取排行榜失败: {e}")
            await event.reply(f"获取排行榜失败，请稍后重试")

    async def get_illust_detail(self, event: AstrMessageEvent, illust_id: str):
        """获取作品详情"""
        try:
            await event.reply(f"正在获取作品详情: {illust_id}...")

            # 使用 yuki API 获取详情
            url = f"{self.yuki_api}/illust"
            params = {"id": illust_id}

            resp = await self.client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

            if not data.get("success") or not data.get("data"):
                await event.reply("未找到该作品")
                return

            illust = data["data"]

            msg = f"作品详情:\n\n"
            msg += f"标题: {illust.get('title', '无标题')}\n"
            msg += f"作者: {illust.get('user', {}).get('name', '未知')}\n"
            msg += f"ID: {illust.get('id')}\n"
            msg += f"浏览数: {illust.get('total_view', 0)}\n"
            msg += f"收藏数: {illust.get('total_bookmarks', 0)}\n"
            tags = illust.get('tags', [])
            msg += f"标签: {', '.join(tags)}\n"
            msg += f"链接: https://www.pixiv.net/artworks/{illust.get('id')}\n"

            if illust.get("x_restrict", 0) > 0:
                msg += f"⚠️ R-18 内容\n"

            await event.reply(msg)

        except Exception as e:
            self.context.logger.error(f"获取作品详情失败: {e}")
            await event.reply(f"获取作品详情失败，请稍后重试")

    async def get_recommend(self, event: AstrMessageEvent, r18: bool = False):
        """获取推荐作品"""
        try:
            await event.reply("正在获取推荐作品...")

            url = f"{self.api_base}/recommend"

            resp = await self.client.get(url)
            resp.raise_for_status()
            data = resp.json()

            if not data.get("illusts"):
                await event.reply("未找到推荐作品")
                return

            illusts = data["illusts"][:10]
            if not r18:
                illusts = [i for i in illusts if i.get("x_restrict", 0) == 0]

            if not illusts:
                await event.reply("未找到符合条件的推荐作品")
                return

            msg = f"推荐作品 ({len(illusts)} 个):\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += f"{idx}. {illust.get('title', '无标题')}\n"
                msg += f"   作者: {illust.get('user', {}).get('name', '未知')}\n"
                msg += f"   ID: {illust.get('id')}\n"
                msg += f"   链接: https://www.pixiv.net/artworks/{illust.get('id')}\n"
                if illust.get("x_restrict", 0) > 0:
                    msg += f"   ⚠️ R-18\n"
                msg += "\n"

            await event.reply(msg)

        except Exception as e:
            self.context.logger.error(f"获取推荐作品失败: {e}")
            await event.reply(f"获取推荐作品失败，请稍后重试")

    async def get_random(self, event: AstrMessageEvent, r18: bool = False):
        """获取随机图片"""
        try:
            await event.reply("正在获取随机图片...")

            url = f"{self.yuki_api}/recommend"
            params = {"type": "json", "proxy": "pixiv.yuki.sh"}

            resp = await self.client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

            if not data.get("success") or not data.get("data"):
                await event.reply("获取随机图片失败")
                return

            illust = data["data"]

            msg = f"随机图片:\n\n"
            msg += f"标题: {illust.get('title', '无标题')}\n"
            msg += f"作者: {illust.get('user', {}).get('name', '未知')}\n"
            msg += f"ID: {illust.get('id')}\n"
            tags = illust.get('tags', [])
            msg += f"标签: {', '.join(tags[:5])}\n"
            msg += f"链接: https://www.pixiv.net/artworks/{illust.get('id')}\n"

            await event.reply(msg)

        except Exception as e:
            self.context.logger.error(f"获取随机图片失败: {e}")
            await event.reply(f"获取随机图片失败，请稍后重试")

    async def terminate(self):
        """插件卸载时调用"""
        if self.client:
            await self.client.aclose()
        self.context.logger.info("Pixiv 插件已卸载")
