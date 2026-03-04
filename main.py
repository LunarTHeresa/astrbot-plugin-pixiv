"""
AstrBot Pixiv 插件 - 使用官方 API (pixivpy3)
需要配置 refresh_token，支持搜索、排行榜、推荐等功能
分离常规指令和 R18 指令
"""
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import asyncio
from pixivpy3 import AppPixivAPI, PixivError
from typing import Dict, Any, Optional

# 默认配置
DEFAULT_TOKEN = "PsamcKHObWOhaTvoA3CsMOM-a_3xBIRJeirDr08VuHU"
DEFAULT_PROXY = "http://127.0.0.1:7897"

@register("pixiv", "Pixiv 图片查看插件（官方API）", "3.1.0", "LunarTheresa")
class PixivPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.config = self._load_config()
        self.refresh_token = self.config.get("refresh_token", "") or DEFAULT_TOKEN
        self.return_count = self.config.get("return_count", 1)
        self.proxy = self.config.get("proxy", "") or DEFAULT_PROXY
        self.authenticated = False

        # 在构造函数中传入代理（这是 pixivpy3 正确的代理设置方式）
        if self.proxy:
            self.api = AppPixivAPI(proxies={'https': self.proxy})
        else:
            self.api = AppPixivAPI()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        try:
            return self.context.get_config()
        except Exception:
            return {}

    async def initialize(self):
        """初始化：认证 Pixiv API"""
        if not self.refresh_token:
            logger.error("Pixiv 插件：未配置 refresh_token，请在插件配置中填写")
            return

        try:
            await asyncio.to_thread(self.api.auth, refresh_token=self.refresh_token)
            self.authenticated = True
            logger.info(f"Pixiv 插件已加载（官方API）- 用户ID: {self.api.user_id}")
            if self.proxy:
                logger.info(f"Pixiv 插件：使用代理 {self.proxy}")
        except PixivError as e:
            logger.error(f"Pixiv API 认证失败: {e}")
            logger.error("请检查 refresh_token 是否正确")
        except Exception as e:
            logger.error(f"Pixiv 插件初始化失败: {e}", exc_info=True)

    def _format_illust(self, illust: dict) -> str:
        """格式化作品信息"""
        msg = f"标题: {illust.get('title', '无标题')}\n"
        msg += f"作者: {illust.get('user', {}).get('name', '未知')}\n"
        msg += f"ID: {illust.get('id')}\n"
        tags = [t.get('name', '') for t in illust.get('tags', [])[:5]]
        if tags:
            msg += f"标签: {', '.join(tags)}\n"
        msg += f"链接: https://www.pixiv.net/artworks/{illust.get('id')}\n"
        if illust.get("x_restrict", 0) > 0:
            msg += "R-18\n"
        return msg

    def _get_image_url(self, illust: dict) -> Optional[str]:
        """获取图片URL"""
        meta = illust.get("meta_single_page", {})
        if meta.get("original_image_url"):
            return meta["original_image_url"]
        pages = illust.get("meta_pages", [])
        if pages:
            return pages[0].get("image_urls", {}).get("original")
        urls = illust.get("image_urls", {})
        return urls.get("large") or urls.get("medium")

    def _check_auth(self, event):
        """检查认证状态"""
        if not self.authenticated:
            return event.plain_result("Pixiv 插件未认证，请检查 refresh_token 配置")
        return None

    # ========== 常规指令（过滤 R18） ==========

    @filter.command("pixiv")
    async def pixiv_search(self, event: AstrMessageEvent):
        """搜索插画（过滤R18）"""
        err = self._check_auth(event)
        if err:
            yield err
            return

        args = event.message_str.strip().split(maxsplit=1)
        if len(args) < 2:
            yield event.plain_result("用法：/pixiv <关键词>")
            return

        keyword = args[1]
        try:
            yield event.plain_result(f"正在搜索: {keyword}...")
            result = await asyncio.to_thread(
                self.api.search_illust, keyword,
                search_target='partial_match_for_tags'
            )
            if not result or not result.get("illusts"):
                yield event.plain_result("未找到相关插画")
                return

            # 过滤 R18
            illusts = [i for i in result["illusts"][:20] if i.get("x_restrict", 0) == 0]
            if not illusts:
                yield event.plain_result("未找到非R18插画")
                return

            illusts = illusts[:self.return_count]
            msg = f"找到 {len(illusts)} 个结果:\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += f"{idx}. {self._format_illust(illust)}\n"
            yield event.plain_result(msg)

            for illust in illusts:
                url = self._get_image_url(illust)
                if url:
                    yield event.image_result(url)

        except PixivError as e:
            yield event.plain_result(f"搜索失败: {e}")
        except Exception as e:
            logger.error(f"搜索失败: {e}", exc_info=True)
            yield event.plain_result(f"搜索失败：{str(e)[:80]}")

    @filter.command("pixiv-rank")
    async def pixiv_rank(self, event: AstrMessageEvent):
        """排行榜（过滤R18）"""
        err = self._check_auth(event)
        if err:
            yield err
            return

        args = event.message_str.strip().split()
        mode = args[1] if len(args) > 1 else "day"

        try:
            yield event.plain_result(f"正在获取排行榜 ({mode})...")
            result = await asyncio.to_thread(self.api.illust_ranking, mode=mode)
            if not result or not result.get("illusts"):
                yield event.plain_result("未找到排行榜数据")
                return

            # 过滤 R18
            illusts = [i for i in result["illusts"][:20] if i.get("x_restrict", 0) == 0]
            if not illusts:
                yield event.plain_result("未找到非R18作品")
                return

            illusts = illusts[:self.return_count]
            msg = f"排行榜 ({mode}):\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += f"{idx}. {self._format_illust(illust)}\n"
            yield event.plain_result(msg)

            for illust in illusts:
                url = self._get_image_url(illust)
                if url:
                    yield event.image_result(url)

        except PixivError as e:
            yield event.plain_result(f"获取排行榜失败: {e}")
        except Exception as e:
            logger.error(f"获取排行榜失败: {e}", exc_info=True)
            yield event.plain_result(f"获取排行榜失败：{str(e)[:80]}")

    @filter.command("pixiv-recommend")
    async def pixiv_recommend(self, event: AstrMessageEvent):
        """推荐作品（过滤R18）"""
        err = self._check_auth(event)
        if err:
            yield err
            return

        try:
            yield event.plain_result("正在获取推荐作品...")
            result = await asyncio.to_thread(self.api.illust_recommended)
            if not result or not result.get("illusts"):
                yield event.plain_result("获取推荐作品失败")
                return

            # 过滤 R18
            illusts = [i for i in result["illusts"][:20] if i.get("x_restrict", 0) == 0]
            if not illusts:
                yield event.plain_result("未找到非R18推荐作品")
                return

            illusts = illusts[:self.return_count]
            msg = "推荐作品:\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += f"{idx}. {self._format_illust(illust)}\n"
            yield event.plain_result(msg)

            for illust in illusts:
                url = self._get_image_url(illust)
                if url:
                    yield event.image_result(url)

        except PixivError as e:
            yield event.plain_result(f"获取推荐失败: {e}")
        except Exception as e:
            logger.error(f"获取推荐失败: {e}", exc_info=True)
            yield event.plain_result(f"获取推荐失败：{str(e)[:80]}")

    @filter.command("pixiv-detail")
    async def pixiv_detail(self, event: AstrMessageEvent):
        """作品详情"""
        err = self._check_auth(event)
        if err:
            yield err
            return

        args = event.message_str.strip().split()
        if len(args) < 2:
            yield event.plain_result("用法：/pixiv-detail <作品ID>")
            return

        illust_id = args[1]
        if not illust_id.isdigit():
            yield event.plain_result("作品ID必须是数字")
            return

        try:
            yield event.plain_result(f"正在获取作品 {illust_id}...")
            result = await asyncio.to_thread(self.api.illust_detail, int(illust_id))
            if not result or not result.get("illust"):
                yield event.plain_result("未找到该作品")
                return

            illust = result["illust"]
            msg = f"作品详情:\n\n{self._format_illust(illust)}"
            yield event.plain_result(msg)

            url = self._get_image_url(illust)
            if url:
                yield event.image_result(url)

        except PixivError as e:
            yield event.plain_result(f"获取详情失败: {e}")
        except Exception as e:
            logger.error(f"获取详情失败: {e}", exc_info=True)
            yield event.plain_result(f"获取详情失败：{str(e)[:80]}")

    # ========== R18 专用指令（只返回 R18） ==========

    @filter.command("pixiv-r18")
    async def pixiv_search_r18(self, event: AstrMessageEvent):
        """搜索 R18 插画"""
        err = self._check_auth(event)
        if err:
            yield err
            return

        args = event.message_str.strip().split(maxsplit=1)
        if len(args) < 2:
            yield event.plain_result("用法：/pixiv-r18 <关键词>")
            return

        keyword = args[1]
        try:
            yield event.plain_result(f"正在搜索 R18 插画: {keyword}...")
            result = await asyncio.to_thread(
                self.api.search_illust, keyword,
                search_target='partial_match_for_tags'
            )
            if not result or not result.get("illusts"):
                yield event.plain_result("未找到相关插画")
                return

            # 只返回 R18
            illusts = [i for i in result["illusts"][:30] if i.get("x_restrict", 0) > 0]
            if not illusts:
                yield event.plain_result("未找到 R18 内容")
                return

            illusts = illusts[:self.return_count]
            msg = f"R18 搜索结果 ({len(illusts)}):\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += f"{idx}. {self._format_illust(illust)}\n"
            yield event.plain_result(msg)

            for illust in illusts:
                url = self._get_image_url(illust)
                if url:
                    yield event.image_result(url)

        except PixivError as e:
            yield event.plain_result(f"搜索失败: {e}")
        except Exception as e:
            logger.error(f"R18搜索失败: {e}", exc_info=True)
            yield event.plain_result(f"搜索失败：{str(e)[:80]}")

    @filter.command("pixiv-rank-r18")
    async def pixiv_rank_r18(self, event: AstrMessageEvent):
        """R18 排行榜（直接使用官方 R18 榜单，保证全是 R18）"""
        err = self._check_auth(event)
        if err:
            yield err
            return

        args = event.message_str.strip().split()
        mode = args[1] if len(args) > 1 else "day"

        # 确保使用 R18 排行榜模式
        if not mode.endswith("_r18"):
            mode = mode + "_r18"

        try:
            yield event.plain_result(f"正在获取 R18 排行榜 ({mode})...")
            result = await asyncio.to_thread(self.api.illust_ranking, mode=mode)
            if not result or not result.get("illusts"):
                yield event.plain_result("未找到 R18 排行榜数据")
                return

            # R18 排行榜本身就全是 R18，无需再过滤
            illusts = result["illusts"][:self.return_count]

            msg = f"R18 排行榜 ({mode}):\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += f"{idx}. {self._format_illust(illust)}\n"
            yield event.plain_result(msg)

            for illust in illusts:
                url = self._get_image_url(illust)
                if url:
                    yield event.image_result(url)

        except PixivError as e:
            yield event.plain_result(f"获取R18排行榜失败: {e}")
        except Exception as e:
            logger.error(f"获取R18排行榜失败: {e}", exc_info=True)
            yield event.plain_result(f"获取R18排行榜失败：{str(e)[:80]}")

    @filter.command("pixiv-recommend-r18")
    async def pixiv_recommend_r18(self, event: AstrMessageEvent):
        """R18 推荐作品"""
        err = self._check_auth(event)
        if err:
            yield err
            return

        try:
            yield event.plain_result("正在获取 R18 推荐作品...")
            result = await asyncio.to_thread(self.api.illust_recommended)
            if not result or not result.get("illusts"):
                yield event.plain_result("获取推荐作品失败")
                return

            # 只返回 R18
            illusts = [i for i in result["illusts"][:30] if i.get("x_restrict", 0) > 0]
            if not illusts:
                yield event.plain_result("未找到 R18 推荐作品")
                return

            illusts = illusts[:self.return_count]
            msg = "R18 推荐作品:\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += f"{idx}. {self._format_illust(illust)}\n"
            yield event.plain_result(msg)

            for illust in illusts:
                url = self._get_image_url(illust)
                if url:
                    yield event.image_result(url)

        except PixivError as e:
            yield event.plain_result(f"获取R18推荐失败: {e}")
        except Exception as e:
            logger.error(f"获取R18推荐失败: {e}", exc_info=True)
            yield event.plain_result(f"获取R18推荐失败：{str(e)[:80]}")

    # ========== 帮助 ==========

    @filter.command("pixiv-help")
    async def pixiv_help(self, event: AstrMessageEvent):
        """帮助信息"""
        auth_status = "已认证" if self.authenticated else "未认证"
        msg = f"""Pixiv 插件使用帮助

常规指令（过滤R18）：
/pixiv <关键词> - 搜索插画
/pixiv-rank [模式] - 排行榜 (day/week/month)
/pixiv-recommend - 推荐作品
/pixiv-detail <ID> - 作品详情

R18 专用指令（只返回R18）：
/pixiv-r18 <关键词> - 搜索R18插画
/pixiv-rank-r18 [模式] - R18排行榜 (day/week)
/pixiv-recommend-r18 - R18推荐作品

当前状态：
- 认证: {auth_status}
- 返回数量: {self.return_count}
- 代理: {self.proxy or '未使用'}"""
        yield event.plain_result(msg)

    async def terminate(self):
        """插件卸载时调用"""
        logger.info("Pixiv 插件已卸载")
