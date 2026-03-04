"""
AstrBot Pixiv Plugin - ByPassSniApi
"""
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import asyncio
from pixivpy3 import ByPassSniApi, AppPixivAPI, PixivError
from typing import Dict, Any, Optional

DEFAULT_TOKEN = "PsamcKHObWOhaTvoA3CsMOM-a_3xBIRJeirDr08VuHU"


@register("pixiv", "Pixiv Plugin", "3.2.1", "LunarTheresa")
class PixivPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.proxy = ""
        self.return_count = 1
        self.refresh_token = DEFAULT_TOKEN
        self.authenticated = False
        self.api = None
        try:
            cfg = self.context.get_config()
            if cfg:
                self.refresh_token = cfg.get("refresh_token", "") or DEFAULT_TOKEN
                self.return_count = cfg.get("return_count", 1)
                self.proxy = cfg.get("proxy", "")
        except Exception:
            pass

    def _create_api(self):
        if self.proxy:
            logger.info("Pixiv: proxy mode " + self.proxy)
            return AppPixivAPI(proxies={"https": self.proxy})
        logger.info("Pixiv: ByPassSniApi mode")
        api = ByPassSniApi()
        hosts = api.require_appapi_hosts()
        if hosts:
            logger.info("Pixiv: DoH resolved -> " + str(hosts))
        else:
            logger.warning("Pixiv: DoH failed, using known IP")
            api.hosts = "https://210.140.131.188"
        return api

    async def initialize(self):
        if not self.refresh_token:
            logger.error("Pixiv: no refresh_token configured")
            return
        try:
            self.api = await asyncio.to_thread(self._create_api)
            await asyncio.to_thread(self.api.auth, refresh_token=self.refresh_token)
            self.authenticated = True
            logger.info("Pixiv: authenticated, user_id=" + str(self.api.user_id))
        except PixivError as e:
            logger.error("Pixiv auth failed: " + str(e))
        except Exception as e:
            logger.error("Pixiv init failed: " + str(e), exc_info=True)

    def _format_illust(self, illust):
        msg = "Title: " + illust.get("title", "N/A") + "\n"
        msg += "Author: " + illust.get("user", {}).get("name", "N/A") + "\n"
        msg += "ID: " + str(illust.get("id")) + "\n"
        tags = [t.get("name", "") for t in illust.get("tags", [])[:5]]
        if tags:
            msg += "Tags: " + ", ".join(tags) + "\n"
        msg += "URL: https://www.pixiv.net/artworks/" + str(illust.get("id")) + "\n"
        if illust.get("x_restrict", 0) > 0:
            msg += "R-18\n"
        return msg

    def _get_image_url(self, illust):
        meta = illust.get("meta_single_page", {})
        if meta.get("original_image_url"):
            return meta["original_image_url"]
        pages = illust.get("meta_pages", [])
        if pages:
            return pages[0].get("image_urls", {}).get("original")
        urls = illust.get("image_urls", {})
        return urls.get("large") or urls.get("medium")

    def _check_auth(self, event):
        if not self.authenticated:
            return event.plain_result("Pixiv not authenticated, check refresh_token")
        return None

    @filter.command("pixiv")
    async def pixiv_search(self, event: AstrMessageEvent):
        err = self._check_auth(event)
        if err:
            yield err
            return
        args = event.message_str.strip().split(maxsplit=1)
        if len(args) < 2:
            yield event.plain_result("/pixiv <keyword>")
            return
        keyword = args[1]
        try:
            yield event.plain_result("Searching: " + keyword + "...")
            result = await asyncio.to_thread(
                self.api.search_illust, keyword,
                search_target="partial_match_for_tags"
            )
            if not result or not result.get("illusts"):
                yield event.plain_result("No results found")
                return
            illusts = [i for i in result["illusts"][:20] if i.get("x_restrict", 0) == 0]
            if not illusts:
                yield event.plain_result("No non-R18 results")
                return
            illusts = illusts[:self.return_count]
            msg = "Found " + str(len(illusts)) + " results:\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += str(idx) + ". " + self._format_illust(illust) + "\n"
            yield event.plain_result(msg)
            for illust in illusts:
                url = self._get_image_url(illust)
                if url:
                    yield event.image_result(url)
        except Exception as e:
            logger.error("Search failed: " + str(e), exc_info=True)
            yield event.plain_result("Search failed: " + str(e)[:80])

    @filter.command("pixiv-rank")
    async def pixiv_rank(self, event: AstrMessageEvent):
        err = self._check_auth(event)
        if err:
            yield err
            return
        args = event.message_str.strip().split()
        mode = args[1] if len(args) > 1 else "day"
        try:
            yield event.plain_result("Getting ranking (" + mode + ")...")
            result = await asyncio.to_thread(self.api.illust_ranking, mode=mode)
            if not result or not result.get("illusts"):
                yield event.plain_result("No ranking data")
                return
            illusts = [i for i in result["illusts"][:20] if i.get("x_restrict", 0) == 0]
            if not illusts:
                yield event.plain_result("No non-R18 works")
                return
            illusts = illusts[:self.return_count]
            msg = "Ranking (" + mode + "):\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += str(idx) + ". " + self._format_illust(illust) + "\n"
            yield event.plain_result(msg)
            for illust in illusts:
                url = self._get_image_url(illust)
                if url:
                    yield event.image_result(url)
        except Exception as e:
            logger.error("Ranking failed: " + str(e), exc_info=True)
            yield event.plain_result("Ranking failed: " + str(e)[:80])

    @filter.command("pixiv-recommend")
    async def pixiv_recommend(self, event: AstrMessageEvent):
        err = self._check_auth(event)
        if err:
            yield err
            return
        try:
            yield event.plain_result("Getting recommendations...")
            result = await asyncio.to_thread(self.api.illust_recommended)
            if not result or not result.get("illusts"):
                yield event.plain_result("No recommendations")
                return
            illusts = [i for i in result["illusts"][:20] if i.get("x_restrict", 0) == 0]
            if not illusts:
                yield event.plain_result("No non-R18 recommendations")
                return
            illusts = illusts[:self.return_count]
            msg = "Recommendations:\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += str(idx) + ". " + self._format_illust(illust) + "\n"
            yield event.plain_result(msg)
            for illust in illusts:
                url = self._get_image_url(illust)
                if url:
                    yield event.image_result(url)
        except Exception as e:
            logger.error("Recommend failed: " + str(e), exc_info=True)
            yield event.plain_result("Recommend failed: " + str(e)[:80])

    @filter.command("pixiv-detail")
    async def pixiv_detail(self, event: AstrMessageEvent):
        err = self._check_auth(event)
        if err:
            yield err
            return
        args = event.message_str.strip().split()
        if len(args) < 2:
            yield event.plain_result("/pixiv-detail <illust_id>")
            return
        illust_id = args[1]
        if not illust_id.isdigit():
            yield event.plain_result("ID must be a number")
            return
        try:
            yield event.plain_result("Getting illust " + illust_id + "...")
            result = await asyncio.to_thread(self.api.illust_detail, int(illust_id))
            if not result or not result.get("illust"):
                yield event.plain_result("Illust not found")
                return
            illust = result["illust"]
            yield event.plain_result(self._format_illust(illust))
            url = self._get_image_url(illust)
            if url:
                yield event.image_result(url)
        except Exception as e:
            logger.error("Detail failed: " + str(e), exc_info=True)
            yield event.plain_result("Detail failed: " + str(e)[:80])

    @filter.command("pixiv-r18")
    async def pixiv_search_r18(self, event: AstrMessageEvent):
        err = self._check_auth(event)
        if err:
            yield err
            return
        args = event.message_str.strip().split(maxsplit=1)
        if len(args) < 2:
            yield event.plain_result("/pixiv-r18 <keyword>")
            return
        keyword = args[1]
        try:
            yield event.plain_result("Searching R18: " + keyword + "...")
            result = await asyncio.to_thread(
                self.api.search_illust, keyword,
                search_target="partial_match_for_tags"
            )
            if not result or not result.get("illusts"):
                yield event.plain_result("No results")
                return
            illusts = [i for i in result["illusts"][:30] if i.get("x_restrict", 0) > 0]
            if not illusts:
                yield event.plain_result("No R18 content found")
                return
            illusts = illusts[:self.return_count]
            msg = "R18 results (" + str(len(illusts)) + "):\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += str(idx) + ". " + self._format_illust(illust) + "\n"
            yield event.plain_result(msg)
            for illust in illusts:
                url = self._get_image_url(illust)
                if url:
                    yield event.image_result(url)
        except Exception as e:
            logger.error("R18 search failed: " + str(e), exc_info=True)
            yield event.plain_result("Search failed: " + str(e)[:80])

    @filter.command("pixiv-rank-r18")
    async def pixiv_rank_r18(self, event: AstrMessageEvent):
        err = self._check_auth(event)
        if err:
            yield err
            return
        args = event.message_str.strip().split()
        mode = args[1] if len(args) > 1 else "day"
        if not mode.endswith("_r18"):
            mode = mode + "_r18"
        try:
            yield event.plain_result("Getting R18 ranking (" + mode + ")...")
            result = await asyncio.to_thread(self.api.illust_ranking, mode=mode)
            if not result or not result.get("illusts"):
                yield event.plain_result("No R18 ranking data")
                return
            illusts = result["illusts"][:self.return_count]
            msg = "R18 Ranking (" + mode + "):\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += str(idx) + ". " + self._format_illust(illust) + "\n"
            yield event.plain_result(msg)
            for illust in illusts:
                url = self._get_image_url(illust)
                if url:
                    yield event.image_result(url)
        except Exception as e:
            logger.error("R18 ranking failed: " + str(e), exc_info=True)
            yield event.plain_result("R18 ranking failed: " + str(e)[:80])

    @filter.command("pixiv-recommend-r18")
    async def pixiv_recommend_r18(self, event: AstrMessageEvent):
        err = self._check_auth(event)
        if err:
            yield err
            return
        try:
            yield event.plain_result("Getting R18 recommendations...")
            result = await asyncio.to_thread(self.api.illust_recommended)
            if not result or not result.get("illusts"):
                yield event.plain_result("No recommendations")
                return
            illusts = [i for i in result["illusts"][:30] if i.get("x_restrict", 0) > 0]
            if not illusts:
                yield event.plain_result("No R18 recommendations")
                return
            illusts = illusts[:self.return_count]
            msg = "R18 Recommendations:\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += str(idx) + ". " + self._format_illust(illust) + "\n"
            yield event.plain_result(msg)
            for illust in illusts:
                url = self._get_image_url(illust)
                if url:
                    yield event.image_result(url)
        except Exception as e:
            logger.error("R18 recommend failed: " + str(e), exc_info=True)
            yield event.plain_result("R18 recommend failed: " + str(e)[:80])

    @filter.command("pixiv-help")
    async def pixiv_help(self, event: AstrMessageEvent):
        auth_status = "OK" if self.authenticated else "Not authenticated"
        mode = "Proxy: " + self.proxy if self.proxy else "ByPassSniApi"
        msg = "Pixiv Plugin Help\n\n"
        msg += "/pixiv <keyword> - Search\n"
        msg += "/pixiv-rank [day/week/month] - Ranking\n"
        msg += "/pixiv-recommend - Recommend\n"
        msg += "/pixiv-detail <ID> - Detail\n"
        msg += "/pixiv-r18 <keyword> - R18 Search\n"
        msg += "/pixiv-rank-r18 [day/week] - R18 Ranking\n"
        msg += "/pixiv-recommend-r18 - R18 Recommend\n\n"
        msg += "Auth: " + auth_status + "\n"
        msg += "Count: " + str(self.return_count) + "\n"
        msg += "Mode: " + mode
        yield event.plain_result(msg)

    async def terminate(self):
        logger.info("Pixiv plugin unloaded")
