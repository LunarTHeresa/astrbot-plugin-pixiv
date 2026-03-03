"""
AstrBot Pixiv 插件 - 使用官方 API
需要配置 refresh_token，支持搜索、排行榜、推荐等功能
"""
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import asyncio
from pixivpy3 import AppPixivAPI, PixivError
from typing import Dict, Any, Optional

@register("pixiv", "Pixiv 图片查看插件（官方API）", "3.0.1", "LunarTheresa")
class PixivPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.api = AppPixivAPI()
        self.config = self._load_config()
        # 默认 refresh_token（可通过配置覆盖）
        self.refresh_token = self.config.get("refresh_token", "PsamcKHObWOhaTvoA3CsMOM-a_3xBIRJeirDr08VuHU")
        self.r18_mode = self.config.get("r18_mode", "过滤 R18")  # 默认过滤 R18
        self.return_count = self.config.get("return_count", 1)
        self.proxy = self.config.get("proxy", "http://127.0.0.1:7897")  # Clash Verge 代理
        self.authenticated = False

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        try:
            return self.context.get_config()
        except:
            return {}

    async def initialize(self):
        """初始化：认证 Pixiv API"""
        if not self.refresh_token:
            logger.error("Pixiv 插件：未配置 refresh_token，请在插件配置中填写")
            logger.error("获取方法：https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362")
            return

        try:
            # 设置代理
            if self.proxy:
                self.api.set_proxy(self.proxy)
                logger.info(f"Pixiv 插件：使用代理 {self.proxy}")

            # 认证
            await asyncio.to_thread(self.api.auth, refresh_token=self.refresh_token)
            self.authenticated = True
            logger.info(f"Pixiv 插件已加载（官方API）- R18模式: {self.r18_mode}")
        except PixivError as e:
            logger.error(f"Pixiv API 认证失败: {e}")
            logger.error("请检查 refresh_token 是否正确")
        except Exception as e:
            logger.error(f"Pixiv 插件初始化失败: {e}", exc_info=True)

    def _filter_r18(self, illusts: list) -> list:
        """根据 R18 模式过滤作品"""
        if self.r18_mode == "允许 R18":
            return illusts
        elif self.r18_mode == "仅 R18":
            return [i for i in illusts if i.get("x_restrict", 0) > 0]
        else:  # "过滤 R18"
            return [i for i in illusts if i.get("x_restrict", 0) == 0]

    def _format_illust_info(self, illust: Dict[str, Any], show_r18_tag: bool = True) -> str:
        """格式化作品信息"""
        msg = f"标题: {illust.get('title', '无标题')}\n"
        msg += f"作者: {illust.get('user', {}).get('name', '未知')}\n"
        msg += f"ID: {illust.get('id')}\n"

        tags = [tag.get('name', '') for tag in illust.get('tags', [])[:5]]
        if tags:
            msg += f"标签: {', '.join(tags)}\n"

        msg += f"链接: https://www.pixiv.net/artworks/{illust.get('id')}\n"

        if show_r18_tag and illust.get("x_restrict", 0) > 0:
            msg += "⚠️ R-18 内容\n"

        return msg

    async def _get_image_url(self, illust: Dict[str, Any]) -> Optional[str]:
        """获取图片URL"""
        if illust.get("meta_single_page"):
            return illust["meta_single_page"].get("original_image_url")
        elif illust.get("meta_pages"):
            return illust["meta_pages"][0]["image_urls"].get("original")
        elif illust.get("image_urls"):
            return illust["image_urls"].get("large") or illust["image_urls"].get("medium")
        return None

    @filter.command("pixiv")
    async def pixiv_search(self, event: AstrMessageEvent):
        """搜索插画"""
        if not self.authenticated:
            yield event.plain_result("Pixiv 插件未认证，请检查配置中的 refresh_token")
            return

        message = event.message_str.strip()
        args = message.split(maxsplit=1)

        if len(args) < 2:
            yield event.plain_result("请输入搜索关键词：/pixiv <关键词>")
            return

        keyword = args[1]

        try:
            yield event.plain_result(f"正在搜索插画: {keyword}...")

            # 调用 Pixiv API 搜索
            result = await asyncio.to_thread(
                self.api.search_illust,
                keyword,
                search_target='partial_match_for_tags'
            )

            if not result or not result.get("illusts"):
                yield event.plain_result("未找到相关插画")
                return

            # 过滤 R18
            illusts = self._filter_r18(result["illusts"][:10])

            if not illusts:
                yield event.plain_result("未找到符合条件的插画（已根据R18设置过滤）")
                return

            # 限制返回数量
            illusts = illusts[:self.return_count]

            msg = f"找到 {len(illusts)} 个结果:\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += f"{idx}. {self._format_illust_info(illust)}\n"

            yield event.plain_result(msg)

            # 发送图片
            for illust in illusts:
                image_url = await self._get_image_url(illust)
                if image_url:
                    yield event.image_result(image_url)

        except PixivError as e:
            logger.error(f"Pixiv API 错误: {e}")
            yield event.plain_result(f"搜索失败: {str(e)}")
        except Exception as e:
            logger.error(f"搜索插画失败: {e}", exc_info=True)
            yield event.plain_result(f"搜索失败：{str(e)[:50]}...")

    @filter.command("pixiv-rank")
    async def pixiv_rank(self, event: AstrMessageEvent):
        """排行榜"""
        if not self.authenticated:
            yield event.plain_result("Pixiv 插件未认证，请检查配置中的 refresh_token")
            return

        message = event.message_str.strip()
        args = message.split()
        mode = args[1] if len(args) > 1 else "day"

        # 根据 R18 模式调整排行榜模式
        if self.r18_mode == "仅 R18":
            if mode == "day":
                mode = "day_r18"
            elif mode == "week":
                mode = "week_r18"

        try:
            yield event.plain_result(f"正在获取排行榜 ({mode})...")

            # 调用 Pixiv API
            result = await asyncio.to_thread(self.api.illust_ranking, mode=mode)

            if not result or not result.get("illusts"):
                yield event.plain_result("未找到排行榜数据")
                return

            # 过滤 R18
            illusts = self._filter_r18(result["illusts"][:20])

            if not illusts:
                yield event.plain_result("未找到符合条件的作品（已根据R18设置过滤）")
                return

            # 限制返回数量
            illusts = illusts[:self.return_count]

            msg = f"排行榜 ({mode}):\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += f"{idx}. {self._format_illust_info(illust)}\n"

            yield event.plain_result(msg)

            # 发送图片
            for illust in illusts:
                image_url = await self._get_image_url(illust)
                if image_url:
                    yield event.image_result(image_url)

        except PixivError as e:
            logger.error(f"Pixiv API 错误: {e}")
            yield event.plain_result(f"获取排行榜失败: {str(e)}")
        except Exception as e:
            logger.error(f"获取排行榜失败: {e}", exc_info=True)
            yield event.plain_result(f"获取排行榜失败：{str(e)[:50]}...")

    @filter.command("pixiv-recommend")
    async def pixiv_recommend(self, event: AstrMessageEvent):
        """推荐作品"""
        if not self.authenticated:
            yield event.plain_result("Pixiv 插件未认证，请检查配置中的 refresh_token")
            return

        try:
            yield event.plain_result("正在获取推荐作品...")

            # 调用 Pixiv API
            result = await asyncio.to_thread(self.api.illust_recommended)

            if not result or not result.get("illusts"):
                yield event.plain_result("获取推荐作品失败")
                return

            # 过滤 R18
            illusts = self._filter_r18(result["illusts"][:20])

            if not illusts:
                yield event.plain_result("未找到符合条件的作品（已根据R18设置过滤）")
                return

            # 限制返回数量
            illusts = illusts[:self.return_count]

            msg = "推荐作品:\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += f"{idx}. {self._format_illust_info(illust)}\n"

            yield event.plain_result(msg)

            # 发送图片
            for illust in illusts:
                image_url = await self._get_image_url(illust)
                if image_url:
                    yield event.image_result(image_url)

        except PixivError as e:
            logger.error(f"Pixiv API 错误: {e}")
            yield event.plain_result(f"获取推荐作品失败: {str(e)}")
        except Exception as e:
            logger.error(f"获取推荐作品失败: {e}", exc_info=True)
            yield event.plain_result(f"获取推荐作品失败：{str(e)[:50]}...")

    @filter.command("pixiv-detail")
    async def pixiv_detail(self, event: AstrMessageEvent):
        """作品详情"""
        if not self.authenticated:
            yield event.plain_result("Pixiv 插件未认证，请检查配置中的 refresh_token")
            return

        message = event.message_str.strip()
        args = message.split()

        if len(args) < 2:
            yield event.plain_result("请输入作品ID：/pixiv-detail <ID>")
            return

        illust_id = args[1]

        if not illust_id.isdigit():
            yield event.plain_result("作品ID必须是数字")
            return

        try:
            yield event.plain_result(f"正在获取作品详情: {illust_id}...")

            # 调用 Pixiv API
            result = await asyncio.to_thread(self.api.illust_detail, illust_id)

            if not result or not result.get("illust"):
                yield event.plain_result("未找到该作品")
                return

            illust = result["illust"]

            # 检查 R18 过滤
            if self.r18_mode == "过滤 R18" and illust.get("x_restrict", 0) > 0:
                yield event.plain_result("该作品为R-18内容，当前设置为过滤R18")
                return
            elif self.r18_mode == "仅 R18" and illust.get("x_restrict", 0) == 0:
                yield event.plain_result("该作品不是R-18内容，当前设置为仅显示R18")
                return

            msg = f"作品详情 (ID: {illust['id']})\n\n"
            msg += self._format_illust_info(illust)

            yield event.plain_result(msg)

            # 发送图片
            image_url = await self._get_image_url(illust)
            if image_url:
                yield event.image_result(image_url)
            else:
                yield event.plain_result("无法获取图片URL")

        except PixivError as e:
            logger.error(f"Pixiv API 错误: {e}")
            yield event.plain_result(f"获取作品详情失败: {str(e)}")
        except Exception as e:
            logger.error(f"获取作品详情失败: {e}", exc_info=True)
            yield event.plain_result(f"获取作品详情失败：{str(e)[:50]}...")

    @filter.command("pixiv-help")
    async def pixiv_help(self, event: AstrMessageEvent):
        """帮助信息"""
        help_msg = """Pixiv 插件使用帮助

基础指令（普通内容）：
/pixiv <关键词> - 搜索插画（过滤R18）
/pixiv-rank [模式] - 查看排行榜（过滤R18）
  模式: day(日榜), week(周榜), month(月榜)
/pixiv-recommend - 获取推荐作品（过滤R18）
/pixiv-detail <ID> - 查看作品详情

R18 专用指令：
/pixiv-r18 <关键词> - 搜索 R18 插画
/pixiv-rank-r18 [模式] - R18 排行榜
  模式: day(日榜), week(周榜)
/pixiv-recommend-r18 - R18 推荐作品

配置说明：
- refresh_token: 必填，用于API认证
- return_count: 每次返回图片数量 (1-10)
- proxy: 代理地址 (默认: http://127.0.0.1:7897)

获取 refresh_token:
https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362

当前设置：
- 返回数量: {return_count}
- 认证状态: {auth_status}
"""
        auth_status = "已认证" if self.authenticated else "未认证"
        yield event.plain_result(help_msg.format(
            return_count=self.return_count,
            auth_status=auth_status
        ))

    @filter.command("pixiv-r18")
    async def pixiv_search_r18(self, event: AstrMessageEvent):
        """搜索插画（R18）"""
        if not self.authenticated:
            yield event.plain_result("Pixiv 插件未认证，请检查配置中的 refresh_token")
            return

        message = event.message_str.strip()
        args = message.split(maxsplit=1)

        if len(args) < 2:
            yield event.plain_result("请输入搜索关键词：/pixiv-r18 <关键词>")
            return

        keyword = args[1]

        try:
            yield event.plain_result(f"正在搜索 R18 插画: {keyword}...")

            # 调用 Pixiv API 搜索
            result = await asyncio.to_thread(
                self.api.search_illust,
                keyword,
                search_target='partial_match_for_tags'
            )

            if not result or not result.get("illusts"):
                yield event.plain_result("未找到相关插画")
                return

            # 只返回 R18 内容
            illusts = [i for i in result["illusts"][:20] if i.get("x_restrict", 0) > 0]

            if not illusts:
                yield event.plain_result("未找到 R18 内容")
                return

            # 限制返回数量
            illusts = illusts[:self.return_count]

            msg = f"找到 {len(illusts)} 个 R18 结果:\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += f"{idx}. {self._format_illust_info(illust)}\n"

            yield event.plain_result(msg)

            # 发送图片
            for illust in illusts:
                image_url = await self._get_image_url(illust)
                if image_url:
                    yield event.image_result(image_url)

        except PixivError as e:
            logger.error(f"Pixiv API 错误: {e}")
            yield event.plain_result(f"搜索失败: {str(e)}")
        except Exception as e:
            logger.error(f"搜索插画失败: {e}", exc_info=True)
            yield event.plain_result(f"搜索失败：{str(e)[:50]}...")

    @filter.command("pixiv-rank-r18")
    async def pixiv_rank_r18(self, event: AstrMessageEvent):
        """R18 排行榜"""
        if not self.authenticated:
            yield event.plain_result("Pixiv 插件未认证，请检查配置中的 refresh_token")
            return

        message = event.message_str.strip()
        args = message.split()
        mode = args[1] if len(args) > 1 else "day_r18"

        # 确保使用 R18 排行榜
        if not mode.endswith("_r18"):
            mode = mode + "_r18"

        try:
            yield event.plain_result(f"正在获取 R18 排行榜 ({mode})...")

            # 调用 Pixiv API
            result = await asyncio.to_thread(self.api.illust_ranking, mode=mode)

            if not result or not result.get("illusts"):
                yield event.plain_result("未找到排行榜数据")
                return

            illusts = result["illusts"][:self.return_count]

            msg = f"R18 排行榜 ({mode}):\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += f"{idx}. {self._format_illust_info(illust)}\n"

            yield event.plain_result(msg)

            # 发送图片
            for illust in illusts:
                image_url = await self._get_image_url(illust)
                if image_url:
                    yield event.image_result(image_url)

        except PixivError as e:
            logger.error(f"Pixiv API 错误: {e}")
            yield event.plain_result(f"获取排行榜失败: {str(e)}")
        except Exception as e:
            logger.error(f"获取排行榜失败: {e}", exc_info=True)
            yield event.plain_result(f"获取排行榜失败：{str(e)[:50]}...")

    @filter.command("pixiv-recommend-r18")
    async def pixiv_recommend_r18(self, event: AstrMessageEvent):
        """R18 推荐作品"""
        if not self.authenticated:
            yield event.plain_result("Pixiv 插件未认证，请检查配置中的 refresh_token")
            return

        try:
            yield event.plain_result("正在获取 R18 推荐作品...")

            # 调用 Pixiv API
            result = await asyncio.to_thread(self.api.illust_recommended)

            if not result or not result.get("illusts"):
                yield event.plain_result("获取推荐作品失败")
                return

            # 只返回 R18 内容
            illusts = [i for i in result["illusts"][:30] if i.get("x_restrict", 0) > 0]

            if not illusts:
                yield event.plain_result("未找到 R18 推荐作品")
                return

            # 限制返回数量
            illusts = illusts[:self.return_count]

            msg = "R18 推荐作品:\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += f"{idx}. {self._format_illust_info(illust)}\n"

            yield event.plain_result(msg)

            # 发送图片
            for illust in illusts:
                image_url = await self._get_image_url(illust)
                if image_url:
                    yield event.image_result(image_url)

        except PixivError as e:
            logger.error(f"Pixiv API 错误: {e}")
            yield event.plain_result(f"获取推荐作品失败: {str(e)}")
        except Exception as e:
            logger.error(f"获取推荐作品失败: {e}", exc_info=True)
            yield event.plain_result(f"获取推荐作品失败：{str(e)[:50]}...")

    async def terminate(self):
        """插件卸载时调用"""
        logger.info("Pixiv 插件已卸载")

