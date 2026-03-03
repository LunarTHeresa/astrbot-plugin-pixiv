"""
AstrBot Pixiv 插件 - 无需 Token 版本
使用第三方 API，支持搜索、排行榜、推荐等功能
"""
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import httpx

@register("pixiv", "Pixiv 图片和小说查看插件（无需Token）", "2.0.4", "LunarTheresa")
class PixivPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.api_base = "https://api.obfs.dev/api/pixiv"
        self.yuki_api = "https://pixiv.yuki.sh/api"
        self.client = None

    async def initialize(self):
        """初始化：创建复用的 httpx 异步客户端"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            headers=headers,
            follow_redirects=True
        )
        logger.info("Pixiv 插件已加载（无需Token）")

    @filter.command("pixiv")
    async def pixiv_search(self, event: AstrMessageEvent):
        """搜索插画"""
        message = event.message_str.strip()
        args = message.split()

        if len(args) < 2:
            yield event.plain_result("请输入搜索关键词：/pixiv <关键词>")
            return

        keyword = " ".join(args[1:])

        try:
            yield event.plain_result(f"正在搜索插画: {keyword}...")

            url = f"{self.api_base}/search"
            params = {"word": keyword, "mode": "partial_match_for_tags"}

            resp = await self.client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

            if not data.get("illusts"):
                yield event.plain_result("未找到相关插画")
                return

            illusts = [i for i in data["illusts"][:10] if i.get("x_restrict", 0) == 0]

            if not illusts:
                yield event.plain_result("未找到符合条件的插画")
                return

            msg = f"找到 {len(illusts)} 个结果:\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += f"{idx}. {illust.get('title', '无标题')}\n"
                msg += f"   作者: {illust.get('user', {}).get('name', '未知')}\n"
                msg += f"   ID: {illust.get('id')}\n"
                tags = [tag.get('name', '') for tag in illust.get('tags', [])[:5]]
                msg += f"   标签: {', '.join(tags)}\n"
                msg += f"   链接: https://www.pixiv.net/artworks/{illust.get('id')}\n\n"

            msg += "使用 /pixiv-detail <ID> 查看详情"
            yield event.plain_result(msg)

        except Exception as e:
            logger.error(f"搜索插画失败: {e}")
            yield event.plain_result(f"搜索失败，请稍后重试")

    @filter.command("pixiv-r18")
    async def pixiv_search_r18(self, event: AstrMessageEvent):
        """搜索插画（R18）"""
        message = event.message_str.strip()
        args = message.split()

        if len(args) < 2:
            yield event.plain_result("请输入搜索关键词：/pixiv-r18 <关键词>")
            return

        keyword = " ".join(args[1:])

        try:
            yield event.plain_result(f"正在搜索插画: {keyword}...")

            url = f"{self.api_base}/search"
            params = {"word": keyword, "mode": "partial_match_for_tags"}

            resp = await self.client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

            if not data.get("illusts"):
                yield event.plain_result("未找到相关插画")
                return

            illusts = data["illusts"][:10]

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
            yield event.plain_result(msg)

        except Exception as e:
            logger.error(f"搜索插画失败: {e}")
            yield event.plain_result(f"搜索失败，请稍后重试")

    @filter.command("pixiv-rank")
    async def pixiv_rank(self, event: AstrMessageEvent):
        """排行榜"""
        message = event.message_str.strip()
        args = message.split()
        mode = args[1] if len(args) > 1 else "day"

        try:
            yield event.plain_result(f"正在获取排行榜 ({mode})...")

            url = f"{self.api_base}/rank"
            params = {"mode": mode}

            resp = await self.client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

            if not data.get("illusts"):
                yield event.plain_result("未找到排行榜数据")
                return

            illusts = data["illusts"][:10]

            msg = f"排行榜 ({mode}) 前 {len(illusts)} 名:\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += f"{idx}. {illust.get('title', '无标题')}\n"
                msg += f"   作者: {illust.get('user', {}).get('name', '未知')}\n"
                msg += f"   ID: {illust.get('id')}\n"
                msg += f"   链接: https://www.pixiv.net/artworks/{illust.get('id')}\n\n"

            yield event.plain_result(msg)

        except Exception as e:
            logger.error(f"获取排行榜失败: {e}")
            yield event.plain_result(f"获取排行榜失败，请稍后重试")

    @filter.command("pixiv-rank-r18")
    async def pixiv_rank_r18(self, event: AstrMessageEvent):
        """排行榜（R18）"""
        message = event.message_str.strip()
        args = message.split()
        mode = args[1] if len(args) > 1 else "day_r18"

        try:
            yield event.plain_result(f"正在获取排行榜 ({mode})...")

            url = f"{self.api_base}/rank"
            params = {"mode": mode}

            resp = await self.client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

            if not data.get("illusts"):
                yield event.plain_result("未找到排行榜数据")
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

            yield event.plain_result(msg)

        except Exception as e:
            logger.error(f"获取排行榜失败: {e}")
            yield event.plain_result(f"获取排行榜失败，请稍后重试")

    @filter.command("pixiv-detail")
    async def pixiv_detail(self, event: AstrMessageEvent):
        """作品详情"""
        message = event.message_str.strip()
        args = message.split()

        if len(args) < 2:
            yield event.plain_result("请输入作品ID：/pixiv-detail <ID>")
            return

        illust_id = args[1]

        try:
            yield event.plain_result(f"正在获取作品详情: {illust_id}...")

            url = f"{self.yuki_api}/illust"
            params = {"id": illust_id}

            resp = await self.client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

            if not data.get("success") or not data.get("data"):
                yield event.plain_result("未找到该作品")
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

            yield event.plain_result(msg)

        except Exception as e:
            logger.error(f"获取作品详情失败: {e}")
            yield event.plain_result(f"获取作品详情失败，请稍后重试")

    @filter.command("pixiv-recommend")
    async def pixiv_recommend(self, event: AstrMessageEvent):
        """推荐作品"""
        try:
            yield event.plain_result("正在获取推荐作品...")

            url = f"{self.api_base}/recommend"

            resp = await self.client.get(url)
            resp.raise_for_status()
            data = resp.json()

            if not data.get("illusts"):
                yield event.plain_result("未找到推荐作品")
                return

            illusts = [i for i in data["illusts"][:10] if i.get("x_restrict", 0) == 0]

            if not illusts:
                yield event.plain_result("未找到符合条件的推荐作品")
                return

            msg = f"推荐作品 ({len(illusts)} 个):\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += f"{idx}. {illust.get('title', '无标题')}\n"
                msg += f"   作者: {illust.get('user', {}).get('name', '未知')}\n"
                msg += f"   ID: {illust.get('id')}\n"
                msg += f"   链接: https://www.pixiv.net/artworks/{illust.get('id')}\n\n"

            yield event.plain_result(msg)

        except Exception as e:
            logger.error(f"获取推荐作品失败: {e}")
            yield event.plain_result(f"获取推荐作品失败，请稍后重试")

    @filter.command("pixiv-recommend-r18")
    async def pixiv_recommend_r18(self, event: AstrMessageEvent):
        """推荐作品（R18）"""
        try:
            yield event.plain_result("正在获取推荐作品...")

            url = f"{self.api_base}/recommend"

            resp = await self.client.get(url)
            resp.raise_for_status()
            data = resp.json()

            if not data.get("illusts"):
                yield event.plain_result("未找到推荐作品")
                return

            illusts = data["illusts"][:10]

            msg = f"推荐作品 ({len(illusts)} 个):\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += f"{idx}. {illust.get('title', '无标题')}\n"
                msg += f"   作者: {illust.get('user', {}).get('name', '未知')}\n"
                msg += f"   ID: {illust.get('id')}\n"
                msg += f"   链接: https://www.pixiv.net/artworks/{illust.get('id')}\n"
                if illust.get("x_restrict", 0) > 0:
                    msg += f"   ⚠️ R-18\n"
                msg += "\n"

            yield event.plain_result(msg)

        except Exception as e:
            logger.error(f"获取推荐作品失败: {e}")
            yield event.plain_result(f"获取推荐作品失败，请稍后重试")

    @filter.command("pixiv-random")
    async def pixiv_random(self, event: AstrMessageEvent):
        """随机图片"""
        try:
            yield event.plain_result("正在获取随机图片...")

            url = f"{self.yuki_api}/recommend"
            params = {"type": "json", "proxy": "pixiv.yuki.sh"}

            resp = await self.client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

            if not data.get("success") or not data.get("data"):
                yield event.plain_result("获取随机图片失败")
                return

            illust = data["data"]

            msg = f"随机图片:\n\n"
            msg += f"标题: {illust.get('title', '无标题')}\n"
            msg += f"作者: {illust.get('user', {}).get('name', '未知')}\n"
            msg += f"ID: {illust.get('id')}\n"
            tags = illust.get('tags', [])
            msg += f"标签: {', '.join(tags[:5])}\n"
            msg += f"链接: https://www.pixiv.net/artworks/{illust.get('id')}\n"

            yield event.plain_result(msg)

        except Exception as e:
            logger.error(f"获取随机图片失败: {e}")
            yield event.plain_result(f"获取随机图片失败，请稍后重试")

    @filter.command("pixiv-random-r18")
    async def pixiv_random_r18(self, event: AstrMessageEvent):
        """随机图片（R18）"""
        try:
            yield event.plain_result("正在获取随机图片...")

            url = f"{self.yuki_api}/recommend"
            params = {"type": "json", "proxy": "pixiv.yuki.sh"}

            resp = await self.client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

            if not data.get("success") or not data.get("data"):
                yield event.plain_result("获取随机图片失败")
                return

            illust = data["data"]

            msg = f"随机图片:\n\n"
            msg += f"标题: {illust.get('title', '无标题')}\n"
            msg += f"作者: {illust.get('user', {}).get('name', '未知')}\n"
            msg += f"ID: {illust.get('id')}\n"
            tags = illust.get('tags', [])
            msg += f"标签: {', '.join(tags[:5])}\n"
            msg += f"链接: https://www.pixiv.net/artworks/{illust.get('id')}\n"
            if illust.get("x_restrict", 0) > 0:
                msg += f"⚠️ R-18 内容\n"

            yield event.plain_result(msg)

        except Exception as e:
            logger.error(f"获取随机图片失败: {e}")
            yield event.plain_result(f"获取随机图片失败，请稍后重试")

    async def terminate(self):
        """插件卸载时调用"""
        if self.client and not self.client.is_closed:
            try:
                await self.client.aclose()
                logger.info("已关闭 httpx 异步客户端")
            except Exception as e:
                logger.error(f"关闭客户端失败：{str(e)}")
        logger.info("Pixiv 插件已卸载")
