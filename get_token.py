"""
获取 Pixiv Refresh Token 的脚本
运行此脚本获取你的 refresh_token
"""
from pixivpy3 import AppPixivAPI

def get_refresh_token():
    api = AppPixivAPI()

    print("=== Pixiv Refresh Token 获取工具 ===")
    print("请输入你的 Pixiv 账号信息：")

    username = input("用户名/邮箱: ")
    password = input("密码: ")

    try:
        print("\n正在登录...")
        api.login(username, password)

        print("\n✓ 登录成功！")
        print(f"\n你的 Refresh Token 是：")
        print(f"{api.refresh_token}")
        print(f"\n请将此 token 复制到 config.json 的 refresh_token 字段中")

        # 保存到文件
        with open("refresh_token.txt", "w") as f:
            f.write(api.refresh_token)
        print(f"\nToken 已保存到 refresh_token.txt 文件中")

    except Exception as e:
        print(f"\n✗ 登录失败: {e}")
        print("\n提示：")
        print("1. 检查用户名和密码是否正确")
        print("2. 如果在中国大陆，可能需要使用代理")
        print("3. 也可以访问 https://github.com/eggplants/get-pixivpy-token 获取")

if __name__ == "__main__":
    get_refresh_token()
