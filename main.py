"""
AstrBot Pixiv 插件 - 无需 Token 版本
使用第三方 API，支持搜索、排行榜、推荐等功能
"""
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
import asyncio
import httpx

@register("pixiv", "Pixiv 图片和小说查看插件（无需Token）", "2.1.0", "LunarTheresa")
class PixivPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.api_base = "https://api.obfs.dev/api/pixiv"
        self.yuki_api = "https://pixiv.yuki.sh/api"
        self.client = None
        self.background_task = None
        # 域名替换规则
        self.old_domain = "pixiv.yuki.sh"
        self.new_domain = "i.yuki.sh"
        self.heartbeat_url = "https://blog.yuki.sh"

    async def initialize(self):
        """初始化：创建复用的 httpx 异步客户端"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": f"https://{self.old_domain}/",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
        }
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            headers=headers,
            follow_redirects=False
        )
        self.background_task = asyncio.create_task(self._heartbeat())
        logger.info("Pixiv 插件已加载（无需Token）")

    async def _heartbeat(self):
        """后台心跳任务，检测yuki.sh服务可用性"""
        while True:
            try:
                await asyncio.sleep(300)
                try:
                    resp = await self.client.head(
                        self.heartbeat_url,
                        timeout=httpx.Timeout(10.0)
                    )
                    resp.raise_for_status()
                    logger.debug("Pixiv插件心跳正常")
                except httpx.HTTPStatusError as e:
                    logger.warning(f"Pixiv插件心跳检测异常：yuki.sh 返回状态码 {e.response.status_code}")
                except httpx.TimeoutException:
                    logger.warning("Pixiv插件心跳检测超时：连接yuki.sh超时")
                except httpx.ConnectError:
                    logger.warning("Pixiv插件心跳检测失败：无法连接到yuki.sh")
                except Exception as e:
                    logger.warning(f"Pixiv插件心跳检测异常：{str(e)}")
            except asyncio.CancelledError:
                logger.debug("Pixiv插件心跳已终止")
                break

    def _replace_domain(self, url: str) -> str:
        """统一替换URL中的域名：pixiv.yuki.sh → i.yuki.sh"""
        if url and self.old_domain in url:
            new_url = url.replace(self.old_domain, self.new_domain)
            logger.debug(f"URL域名替换：{url} → {new_url}")
            return new_url
        return url

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

            illusts = [i for i in data["illusts"][:5] if i.get("x_restrict", 0) == 0]

            if not illusts:
                yield event.plain_result("未找到符合条件的插画")
                return

            msg = f"找到 {len(illusts)} 个结果:\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += f"{idx}. {illust.get('title', '无标题')}\n"
                msg += f"   作者: {illust.get('user', {}).get('name', '未知')}\n"
                msg += f"   ID: {illust.get('id')}\n"
                tags = [tag.get('name', '') for tag in illust.get('tags', [])[:5]]
                msg += f"   标签: {', '.join(tags)}\n\n"

            msg += "使用 /pixiv-detail <ID> 查看详情和图片"
            yield event.plain_result(msg)

        except httpx.HTTPStatusError as e:
            logger.error(f"搜索HTTP错误 {e.response.status_code}：{str(e)}")
            if e.response.status_code == 530:
                yield event.plain_result("搜索服务暂时不可用（api.obfs.dev 返回530错误），请稍后重试或使用 /pixiv-random 获取随机图片")
            else:
                yield event.plain_result(f"搜索失败（状态码：{e.response.status_code}），请稍后重试")
        except httpx.TimeoutException:
            yield event.plain_result("搜索请求超时，请检查网络或稍后再试")
        except httpx.ConnectError:
            yield event.plain_result("搜索服务连接失败，请检查网络或稍后再试")
        except Exception as e:
            logger.error(f"搜索插画失败: {e}", exc_info=True)
            yield event.plain_result(f"搜索失败：{str(e)[:50]}...")

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

            illusts = data["illusts"][:5]

            msg = f"找到 {len(illusts)} 个结果:\n\n"
            for idx, illust in enumerate(illusts, 1):
                msg += f"{idx}. {illust.get('title', '无标题')}\n"
                msg += f"   作者: {illust.get('user', {}).get('name', '未知')}\n"
                msg += f"   ID: {illust.get('id')}\n"
                tags = [tag.get('name', '') for tag in illust.get('tags', [])[:5]]
                msg += f"   标签: {', '.join(tags)}\n"
                if illust.get("x_restrict", 0) > 0:
                    msg += f"   ⚠️ R-18\n"
                msg += "\n"

            msg += "使用 /pixiv-detail <ID> 查看详情和图片"
            yield event.plain_result(msg)

        except httpx.HTTPStatusError as e:
            logger.error(f"搜索HTTP错误 {e.response.status_code}：{str(e)}")
            if e.response.status_code == 530:
                yield event.plain_result("搜索服务暂时不可用（api.obfs.dev 返回530错误），请稍后重试或使用 /pixiv-random-r18 获取随机图片")
            else:
                yield event.plain_result(f"搜索失败（状态码：{e.response.status_code}），请稍后重试")
        except httpx.TimeoutException:
            yield event.plain_result("搜索请求超时，请检查网络或稍后再试")
        except httpx.ConnectError:
            yield event.plain_result("搜索服务连接失败，请检查网络或稍后再试")
        except Exception as e:
            logger.error(f"搜索插画失败: {e}", exc_info=True)
            yield event.plain_result(f"搜索失败：{str(e)[:50]}...")

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

        except httpx.HTTPStatusError as e:
            logger.error(f"排行榜HTTP错误 {e.response.status_code}：{str(e)}")
            if e.response.status_code == 530:
                yield event.plain_result("排行榜服务暂时不可用（api.obfs.dev 返回530错误），请稍后重试或使用 /pixiv-random 获取随机图片")
            else:
                yield event.plain_result(f"获取排行榜失败（状态码：{e.response.status_code}），请稍后重试")
        except httpx.TimeoutException:
            yield event.plain_result("排行榜请求超时，请检查网络或稍后再试")
        except httpx.ConnectError:
            yield event.plain_result("排行榜服务连接失败，请检查网络或稍后再试")
        except Exception as e:
            logger.error(f"获取排行榜失败: {e}", exc_info=True)
            yield event.plain_result(f"获取排行榜失败：{str(e)[:50]}...")

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

        except httpx.HTTPStatusError as e:
            logger.error(f"排行榜HTTP错误 {e.response.status_code}：{str(e)}")
            if e.response.status_code == 530:
                yield event.plain_result("排行榜服务暂时不可用（api.obfs.dev 返回530错误），请稍后重试或使用 /pixiv-random-r18 获取随机图片")
            else:
                yield event.plain_result(f"获取排行榜失败（状态码：{e.response.status_code}），请稍后重试")
        except httpx.TimeoutException:
            yield event.plain_result("排行榜请求超时，请检查网络或稍后再试")
        except httpx.ConnectError:
            yield event.plain_result("排行榜服务连接失败，请检查网络或稍后再试")
        except Exception as e:
            logger.error(f"获取排行榜失败: {e}", exc_info=True)
            yield event.plain_result(f"获取排行榜失败：{str(e)[:50]}...")

    @filter.command("pixiv-detail")
    async def pixiv_detail(self, event: AstrMessageEvent):
        """作品详情（使用 yuki.sh API）"""
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

            url = f"{self.yuki_api}/illust"
            params = {"id": illust_id}

            resp = await self.client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

            if not data.get("success") or not data.get("data"):
                yield event.plain_result("未找到该作品")
                return

            illust = data["data"]
            user = illust.get("user", {})

            # 处理描述字段
            description = illust.get("description", "无")

            msg = f"作品详情 (ID: {illust['id']})\n"
            msg += f"标题：{illust.get('title', '无标题')}\n"
            msg += f"作者：{user.get('name', '未知')} (ID: {user.get('id', '未知')} | 账号：{user.get('account', '未知')})\n"
            msg += f"描述：{description}\n"
            msg += f"标签：{', '.join(illust.get('tags', []))}\n"
            msg += f"链接：https://www.pixiv.net/artworks/{illust.get('id')}"

            if illust.get("x_restrict", 0) > 0:
                msg += f"\n⚠️ R-18 内容"

            yield event.plain_result(msg)

            # 发送图片
            urls = illust.get("urls", {})
            original_url = urls.get("original")

            if original_url:
                image_url = self._replace_domain(original_url)
                yield event.image_result(image_url)
            else:
                yield event.plain_result("该作品为R-18内容，违反平台规则")

        except httpx.HTTPStatusError as e:
            logger.error(f"获取详情HTTP错误 {e.response.status_code}：{str(e)}")
            if e.response.status_code == 404:
                yield event.plain_result("作品不存在或已被删除")
            elif e.response.status_code == 401:
                yield event.plain_result("找不到指定id的图片")
            elif e.response.status_code == 403:
                yield event.plain_result("访问被拒绝，可能是IP限制")
            else:
                yield event.plain_result(f"获取作品详情失败（状态码：{e.response.status_code}），请稍后重试")
        except httpx.TimeoutException:
            yield event.plain_result("请求超时，请检查网络或稍后再试")
        except httpx.ConnectError:
            yield event.plain_result("连接失败，请检查网络或API服务是否可用")
        except KeyError as e:
            logger.error(f"数据解析错误：{str(e)}")
            yield event.plain_result(f"数据解析错误，缺少字段：{str(e)}")
        except Exception as e:
            logger.error(f"获取作品详情失败: {e}", exc_info=True)
            yield event.plain_result(f"获取作品详情失败：{str(e)[:50]}...")

    @filter.command("pixiv-recommend")
    async def pixiv_recommend(self, event: AstrMessageEvent):
        """推荐作品（使用yuki.sh API）"""
        try:
            yield event.plain_result("正在获取推荐作品...")

            url = f"{self.yuki_api}/recommend"
            params = {"type": "json", "proxy": "pixiv.yuki.sh"}

            resp = await self.client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

            if not data.get("success") or not data.get("data"):
                yield event.plain_result("获取推荐作品失败")
                return

            illust = data["data"]

            # 检查是否为R18内容
            if illust.get("x_restrict", 0) > 0:
                yield event.plain_result("该作品为R-18内容，请使用 /pixiv-recommend-r18")
                return

            msg = f"推荐作品:\n\n"
            msg += f"标题: {illust.get('title', '无标题')}\n"
            msg += f"作者: {illust.get('user', {}).get('name', '未知')}\n"
            msg += f"ID: {illust.get('id')}\n"
            tags = illust.get('tags', [])
            msg += f"标签: {', '.join(tags[:5])}\n"
            msg += f"链接: https://www.pixiv.net/artworks/{illust.get('id')}\n"

            yield event.plain_result(msg)

            # 发送图片
            urls = illust.get("urls", {})
            image_url = urls.get("original") or urls.get("regular")
            if image_url:
                # 替换域名以提高访问速度
                image_url = image_url.replace(self.old_domain, self.new_domain)
                yield event.image_result(image_url)
            else:
                yield event.plain_result("无法获取图片URL")

        except httpx.HTTPStatusError as e:
            logger.error(f"推荐HTTP错误 {e.response.status_code}：{str(e)}")
            yield event.plain_result(f"获取推荐作品失败（状态码：{e.response.status_code}），请稍后重试")
        except httpx.TimeoutException:
            yield event.plain_result("推荐请求超时，请检查网络或稍后再试")
        except httpx.ConnectError:
            yield event.plain_result("推荐服务连接失败，请检查网络或稍后再试")
        except Exception as e:
            logger.error(f"获取推荐作品失败: {e}", exc_info=True)
            yield event.plain_result(f"获取推荐作品失败：{str(e)[:50]}...")

    @filter.command("pixiv-recommend-r18")
    async def pixiv_recommend_r18(self, event: AstrMessageEvent):
        """推荐作品（R18，使用yuki.sh API）"""
        try:
            yield event.plain_result("正在获取推荐作品...")

            url = f"{self.yuki_api}/recommend"
            params = {"type": "json", "proxy": "pixiv.yuki.sh"}

            resp = await self.client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

            if not data.get("success") or not data.get("data"):
                yield event.plain_result("获取推荐作品失败")
                return

            illust = data["data"]

            msg = f"推荐作品:\n\n"
            msg += f"标题: {illust.get('title', '无标题')}\n"
            msg += f"作者: {illust.get('user', {}).get('name', '未知')}\n"
            msg += f"ID: {illust.get('id')}\n"
            tags = illust.get('tags', [])
            msg += f"标签: {', '.join(tags[:5])}\n"
            msg += f"链接: https://www.pixiv.net/artworks/{illust.get('id')}\n"
            if illust.get("x_restrict", 0) > 0:
                msg += f"⚠️ R-18 内容\n"

            yield event.plain_result(msg)

            # 发送图片
            urls = illust.get("urls", {})
            image_url = urls.get("original") or urls.get("regular")
            if image_url:
                # 替换域名以提高访问速度
                image_url = image_url.replace(self.old_domain, self.new_domain)
                yield event.image_result(image_url)
            else:
                yield event.plain_result("无法获取图片URL")

        except httpx.HTTPStatusError as e:
            logger.error(f"推荐HTTP错误 {e.response.status_code}：{str(e)}")
            yield event.plain_result(f"获取推荐作品失败（状态码：{e.response.status_code}），请稍后重试")
        except httpx.TimeoutException:
            yield event.plain_result("推荐请求超时，请检查网络或稍后再试")
        except httpx.ConnectError:
            yield event.plain_result("推荐服务连接失败，请检查网络或稍后再试")
        except httpx.TimeoutException:
            yield event.plain_result("推荐请求超时，请检查网络或稍后再试")
        except httpx.ConnectError:
            yield event.plain_result("推荐服务连接失败，请检查网络或稍后再试")
        except Exception as e:
            logger.error(f"获取推荐作品失败: {e}", exc_info=True)
            yield event.plain_result(f"获取推荐作品失败：{str(e)[:50]}...")

    @filter.command("pixiv-random")
    async def pixiv_random(self, event: AstrMessageEvent):
        """随机图片（使用 yuki.sh API）"""
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

            # 检查是否为R18内容
            if illust.get("x_restrict", 0) > 0:
                yield event.plain_result("该作品为R-18内容，请使用 /pixiv-random-r18")
                return

            user = illust.get("user", {})
            tags = illust.get('tags', [])

            msg = f"随机图片\n"
            msg += f"标题：{illust.get('title', '无标题')}\n"
            msg += f"作者：{user.get('name', '未知')} (ID: {user.get('id', '未知')})\n"
            msg += f"标签：{', '.join(tags[:5])}\n"
            msg += f"链接：https://www.pixiv.net/artworks/{illust.get('id')}"

            yield event.plain_result(msg)

            # 发送图片
            urls = illust.get("urls", {})
            original_url = urls.get("original")

            if original_url:
                image_url = self._replace_domain(original_url)
                yield event.image_result(image_url)
            else:
                yield event.plain_result("无法获取图片URL")

        except httpx.HTTPStatusError as e:
            logger.error(f"随机图片HTTP错误 {e.response.status_code}：{str(e)}")
            if e.response.status_code == 404:
                yield event.plain_result("API地址可能已变更或资源不存在")
            elif e.response.status_code == 403:
                yield event.plain_result("访问被拒绝，可能是IP限制")
            else:
                yield event.plain_result(f"获取随机图片失败（状态码：{e.response.status_code}），请稍后重试")
        except httpx.TimeoutException:
            yield event.plain_result("请求超时，请检查网络或稍后再试")
        except httpx.ConnectError:
            yield event.plain_result("连接失败，请检查网络或API服务是否可用")
        except KeyError as e:
            logger.error(f"数据解析错误：{str(e)}")
            yield event.plain_result(f"数据解析错误，缺少字段：{str(e)}")
        except Exception as e:
            logger.error(f"获取随机图片失败: {e}", exc_info=True)
            yield event.plain_result(f"获取随机图片失败：{str(e)[:50]}...")

    @filter.command("pixiv-random-r18")
    async def pixiv_random_r18(self, event: AstrMessageEvent):
        """随机图片（R18，使用 yuki.sh API）"""
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
            user = illust.get("user", {})
            tags = illust.get('tags', [])

            msg = f"随机图片\n"
            msg += f"标题：{illust.get('title', '无标题')}\n"
            msg += f"作者：{user.get('name', '未知')} (ID: {user.get('id', '未知')})\n"
            msg += f"标签：{', '.join(tags[:5])}\n"
            msg += f"链接：https://www.pixiv.net/artworks/{illust.get('id')}"

            if illust.get("x_restrict", 0) > 0:
                msg += f"\n⚠️ R-18 内容"

            yield event.plain_result(msg)

            # 发送图片
            urls = illust.get("urls", {})
            original_url = urls.get("original")

            if original_url:
                image_url = self._replace_domain(original_url)
                yield event.image_result(image_url)
            else:
                yield event.plain_result("无法获取图片URL")

        except httpx.HTTPStatusError as e:
            logger.error(f"随机图片HTTP错误 {e.response.status_code}：{str(e)}")
            if e.response.status_code == 404:
                yield event.plain_result("API地址可能已变更或资源不存在")
            elif e.response.status_code == 403:
                yield event.plain_result("访问被拒绝，可能是IP限制")
            else:
                yield event.plain_result(f"获取随机图片失败（状态码：{e.response.status_code}），请稍后重试")
        except httpx.TimeoutException:
            yield event.plain_result("请求超时，请检查网络或稍后再试")
        except httpx.ConnectError:
            yield event.plain_result("连接失败，请检查网络或API服务是否可用")
        except KeyError as e:
            logger.error(f"数据解析错误：{str(e)}")
            yield event.plain_result(f"数据解析错误，缺少字段：{str(e)}")
        except Exception as e:
            logger.error(f"获取随机图片失败: {e}", exc_info=True)
            yield event.plain_result(f"获取随机图片失败：{str(e)[:50]}...")

    async def terminate(self):
        """插件卸载时调用"""
        if self.client and not self.client.is_closed:
            try:
                await self.client.aclose()
                logger.info("已关闭 httpx 异步客户端")
            except Exception as e:
                logger.error(f"关闭客户端失败：{str(e)}")

        if self.background_task and not self.background_task.done():
            self.background_task.cancel()
            try:
                await self.background_task
            except asyncio.CancelledError:
                pass
            logger.info("已终止后台心跳任务")

        logger.info("Pixiv 插件已卸载")
