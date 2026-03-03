"""
AstrBot Pixiv 插件
支持查看 Pixiv 图片和小说
"""
import os
import asyncio
from typing import List, Dict, Any
from astrbot.api.star import Context, Star, register
from astrbot.api.event import AstrMessageEvent
from pixivpy3 import AppPixivAPI
import json

@register("pixiv", "Pixiv 图片和小说查看插件", "1.0.0", "LunarTheresa")
class PixivPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.api = AppPixivAPI()
        self.config = {}
        self.is_logged_in = False

    async def on_load(self):
        """插件加载时调用"""
        # 加载配置
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.context.logger.warning("Pixiv 插件配置文件不存在，请创建 config.json")
            return

        # 登录 Pixiv
        try:
            refresh_token = self.config.get("refresh_token", "")
            if refresh_token and refresh_token != "YOUR_PIXIV_REFRESH_TOKEN_HERE":
                self.api.auth(refresh_token=refresh_token)
                self.is_logged_in = True
                self.context.logger.info("Pixiv 插件登录成功")
            else:
                self.context.logger.warning("未配置 Pixiv refresh_token")
        except Exception as e:
            self.context.logger.error(f"Pixiv 登录失败: {e}")

    async def on_message(self, event: AstrMessageEvent):
        """处理消息"""
        message = event.message_str.strip()

        if not self.is_logged_in:
            if message.startswith("/pixiv"):
                await event.reply("Pixiv 插件未登录，请配置 refresh_token")
            return

        # 搜索图片
        if message.startswith("/pixiv "):
            keyword = message[7:].strip()
            await self.search_illust(event, keyword, r18=False)

        # 搜索图片（包含 R18）
        elif message.startswith("/pixiv-r18 "):
            keyword = message[11:].strip()
            await self.search_illust(event, keyword, r18=True)

        # 搜索小说
        elif message.startswith("/pixiv-novel "):
            keyword = message[13:].strip()
            await self.search_novel(event, keyword, r18=False)

        # 搜索小说（包含 R18）
        elif message.startswith("/pixiv-novel-r18 "):
            keyword = message[17:].strip()
            await self.search_novel(event, keyword, r18=True)

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

    async def search_illust(self, event: AstrMessageEvent, keyword: str, r18: bool = False):
        """搜索插画"""
        try:
            await event.reply(f"正在搜索插画: {keyword}...")

            result = self.api.search_illust(keyword, search_target='partial_match_for_tags')

            if not result.illusts:
                await event.reply("未找到相关插画")
                return

            # 过滤结果
            illusts = result.illusts[:10]  # 限制返回数量
            if not r18:
                illusts = [i for i in illusts if i.x_restrict == 0]

            if not illusts:
                await event.reply("未找到符合条件的插画")
                return

            # 构建消息
            msg = f"找到 {len(illusts)} 个结果:\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += f"{idx}. {illust.title}\n"
                msg += f"   作者: {illust.user.name}\n"
                msg += f"   ID: {illust.id}\n"
                msg += f"   标签: {', '.join([tag.name for tag in illust.tags[:5]])}\n"
                msg += f"   链接: https://www.pixiv.net/artworks/{illust.id}\n"
                if illust.x_restrict > 0:
                    msg += f"   ⚠️ R-18\n"
                msg += "\n"

            msg += "使用 /pixiv-detail <ID> 查看详情"
            await event.reply(msg)

        except Exception as e:
            self.context.logger.error(f"搜索插画失败: {e}")
            await event.reply(f"搜索失败: {str(e)}")

    async def search_novel(self, event: AstrMessageEvent, keyword: str, r18: bool = False):
        """搜索小说"""
        try:
            await event.reply(f"正在搜索小说: {keyword}...")

            result = self.api.search_novel(keyword, search_target='partial_match_for_tags')

            if not result.novels:
                await event.reply("未找到相关小说")
                return

            # 过滤结果
            novels = result.novels[:10]
            if not r18:
                novels = [n for n in novels if n.x_restrict == 0]

            if not novels:
                await event.reply("未找到符合条件的小说")
                return

            # 构建消息
            msg = f"找到 {len(novels)} 个结果:\n\n"
            for idx, novel in enumerate(novels, 1):
                msg += f"{idx}. {novel.title}\n"
                msg += f"   作者: {novel.user.name}\n"
                msg += f"   ID: {novel.id}\n"
                msg += f"   字数: {novel.text_length}\n"
                msg += f"   标签: {', '.join([tag.name for tag in novel.tags[:5]])}\n"
                msg += f"   链接: https://www.pixiv.net/novel/show.php?id={novel.id}\n"
                if novel.x_restrict > 0:
                    msg += f"   ⚠️ R-18\n"
                msg += "\n"

            await event.reply(msg)

        except Exception as e:
            self.context.logger.error(f"搜索小说失败: {e}")
            await event.reply(f"搜索失败: {str(e)}")

    async def get_ranking(self, event: AstrMessageEvent, mode: str = "day", r18: bool = False):
        """获取排行榜"""
        try:
            await event.reply(f"正在获取排行榜 ({mode})...")

            result = self.api.illust_ranking(mode=mode)

            if not result.illusts:
                await event.reply("未找到排行榜数据")
                return

            illusts = result.illusts[:10]

            msg = f"排行榜 ({mode}) 前 {len(illusts)} 名:\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += f"{idx}. {illust.title}\n"
                msg += f"   作者: {illust.user.name}\n"
                msg += f"   ID: {illust.id}\n"
                msg += f"   链接: https://www.pixiv.net/artworks/{illust.id}\n"
                if illust.x_restrict > 0:
                    msg += f"   ⚠️ R-18\n"
                msg += "\n"

            await event.reply(msg)

        except Exception as e:
            self.context.logger.error(f"获取排行榜失败: {e}")
            await event.reply(f"获取排行榜失败: {str(e)}")

    async def get_illust_detail(self, event: AstrMessageEvent, illust_id: str):
        """获取作品详情"""
        try:
            await event.reply(f"正在获取作品详情: {illust_id}...")

            result = self.api.illust_detail(illust_id)
            illust = result.illust

            if not illust:
                await event.reply("未找到该作品")
                return

            msg = f"作品详情:\n\n"
            msg += f"标题: {illust.title}\n"
            msg += f"作者: {illust.user.name}\n"
            msg += f"ID: {illust.id}\n"
            msg += f"类型: {illust.type}\n"
            msg += f"创建时间: {illust.create_date}\n"
            msg += f"浏览数: {illust.total_view}\n"
            msg += f"收藏数: {illust.total_bookmarks}\n"
            msg += f"标签: {', '.join([tag.name for tag in illust.tags])}\n"
            msg += f"链接: https://www.pixiv.net/artworks/{illust.id}\n"

            if illust.x_restrict > 0:
                msg += f"⚠️ R-18 内容\n"

            if illust.caption:
                msg += f"\n简介: {illust.caption[:200]}...\n"

            await event.reply(msg)

        except Exception as e:
            self.context.logger.error(f"获取作品详情失败: {e}")
            await event.reply(f"获取作品详情失败: {str(e)}")

    async def get_recommend(self, event: AstrMessageEvent, r18: bool = False):
        """获取推荐作品"""
        try:
            await event.reply("正在获取推荐作品...")

            result = self.api.illust_recommended()

            if not result.illusts:
                await event.reply("未找到推荐作品")
                return

            illusts = result.illusts[:10]
            if not r18:
                illusts = [i for i in illusts if i.x_restrict == 0]

            if not illusts:
                await event.reply("未找到符合条件的推荐作品")
                return

            msg = f"推荐作品 ({len(illusts)} 个):\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += f"{idx}. {illust.title}\n"
                msg += f"   作者: {illust.user.name}\n"
                msg += f"   ID: {illust.id}\n"
                msg += f"   链接: https://www.pixiv.net/artworks/{illust.id}\n"
                if illust.x_restrict > 0:
                    msg += f"   ⚠️ R-18\n"
                msg += "\n"

            await event.reply(msg)

        except Exception as e:
            self.context.logger.error(f"获取推荐作品失败: {e}")
            await event.reply(f"获取推荐作品失败: {str(e)}")

