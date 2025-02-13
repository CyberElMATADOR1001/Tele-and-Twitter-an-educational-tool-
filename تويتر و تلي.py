from telethon import TelegramClient, errors
from telethon.tl.functions.channels import InviteToChannelRequest
import tweepy
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Back, Style, init
import sys
import os

# تهيئة colorama للألوان
init(autoreset=True)

# إعدادات API العامة
api_id = 17221716
api_hash = "e4c25110a83ef5a990c841df77a75951"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_banner():
    clear_screen()
    banner = f"""
{Fore.RED}
╔══════════════════════════════════════════════════════════════╗
{Fore.YELLOW}║                      Tools El Matador                        ║
{Fore.RED}╚══════════════════════════════════════════════════════════════╝
{Fore.CYAN}║                    حقوق؛ El Matador                         ║
{Fore.GREEN}║       صَلِّ عَلَىٰ سَيِّدِنَا مُحَمَّدٍ صلى الله عليه وسلم        ║
{Fore.RED}╚══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
"""
    print(banner)

async def main():
    display_banner()
    platform = input(f"{Fore.YELLOW}[+] اختر المنصة:\n{Fore.CYAN}1. تليجرام\n2. تويتر\n\n{Fore.GREEN}اختيارك (1/2): {Style.RESET_ALL}")

    if platform == '1':
        await handle_telegram()
    elif platform == '2':
        await handle_twitter()
    else:
        print(f"{Fore.RED}[!] اختيار غير صحيح{Style.RESET_ALL}")

async def handle_telegram():
    display_banner()
    phone = input(f"{Fore.YELLOW}[+] أدخل رقم الهاتف مع كود الدولة (مثال: +20xxxxxxxxxx): {Style.RESET_ALL}")
    client = TelegramClient('session', api_id, api_hash)
    
    try:
        await client.connect()
        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            code = input(f"{Fore.CYAN}[+] أدخل الكود: {Style.RESET_ALL}")
            await client.sign_in(phone, code)

        source = input(f"{Fore.YELLOW}[+] أدخل معرف المجموعة المصدر: {Style.RESET_ALL}")
        target = input(f"{Fore.YELLOW}[+] أدخل معرف المجموعة الهدف: {Style.RESET_ALL}")

        print(f"{Fore.CYAN}[+] جاري البحث عن الأعضاء...{Style.RESET_ALL}")
        members = await client.get_participants(source)
        print(f"{Fore.GREEN}[+] تم العثور على {len(members)} عضو. جاري النقل...{Style.RESET_ALL}")

        failed = 0
        for idx, member in enumerate(members, 1):
            try:
                await client(InviteToChannelRequest(target, [member]))
                print(f"{Fore.GREEN}[+] ({idx}/{len(members)}) تمت إضافة: {member.id}{Style.RESET_ALL}")
                await asyncio.sleep(2)
                failed = 0
            except errors.UserPrivacyRestrictedError:
                print(f"{Fore.RED}[!] خصوصية العضو {member.id} تمنع الإضافة{Style.RESET_ALL}")
                failed += 1
            except Exception as e:
                print(f"{Fore.RED}[!] خطأ: {e}{Style.RESET_ALL}")
                failed += 1
                if failed >= 3:
                    print(f"{Fore.RED}[!] توقف بسبب كثرة الأخطاء{Style.RESET_ALL}")
                    break
                await self_heal(client, phone)

        print(f"{Fore.GREEN}[+] اكتملت العملية بنجاح!{Style.RESET_ALL}")

    finally:
        await client.disconnect()

async def handle_twitter():
    display_banner()
    api_key = input(f"{Fore.YELLOW}[+] أدخل Twitter API Key: {Style.RESET_ALL}")
    api_secret = input(f"{Fore.YELLOW}[+] أدخل Twitter API Secret: {Style.RESET_ALL}")
    access_token = input(f"{Fore.YELLOW}[+] أدخل Access Token: {Style.RESET_ALL}")
    access_secret = input(f"{Fore.YELLOW}[+] أدخل Access Token Secret: {Style.RESET_ALL}")
    source_user = input(f"{Fore.YELLOW}[+] أدخل اسم المستخدم المصدر: {Style.RESET_ALL}")
    
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, sync_twitter_transfer,
                                 api_key, api_secret,
                                 access_token, access_secret,
                                 source_user)

def sync_twitter_transfer(api_key, api_secret, access_token, access_secret, source_user):
    try:
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_secret)
        api = tweepy.API(auth, wait_on_rate_limit=True)

        print(f"{Fore.CYAN}[+] جاري جلب المتابعين...{Style.RESET_ALL}")
        followers = []
        for user in tweepy.Cursor(api.get_followers, screen_name=source_user).items():
            followers.append(user.screen_name)
        
        print(f"{Fore.GREEN}[+] تم العثور على {len(followers)} متابع. جاري البدء...{Style.RESET_ALL}")
        
        for idx, follower in enumerate(followers, 1):
            try:
                if not api.get_friendship(screen_name=follower)[0].is_following:
                    api.create_friendship(screen_name=follower)
                    print(f"{Fore.GREEN}[{idx}/{len(followers)}] تم متابعة: {follower}{Style.RESET_ALL}")
                    time.sleep(60)
                else:
                    print(f"{Fore.CYAN}[{idx}/{len(followers)}] مستخدم {follower} مفعلاً بالفعل{Style.RESET_ALL}")
            except tweepy.TweepError as e:
                print(f"{Fore.RED}[!] خطأ في {follower}: {e}{Style.RESET_ALL}")
                if "429" in str(e):
                    print(f"{Fore.YELLOW}[!] تم اكتشاف Rate Limit، انتظار 15 دقيقة...{Style.RESET_ALL}")
                    time.sleep(900)
            except Exception as e:
                print(f"{Fore.RED}[!] خطأ غير متوقع: {e}{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}[!] فشل العملية: {e}{Style.RESET_ALL}")

async def self_heal(client, phone):
    try:
        print(f"{Fore.YELLOW}[*] محاولة إصلاح ذاتي...{Style.RESET_ALL}")
        await client.reconnect()
        if not await client.is_user_authorized():
            await client.send_code_request(phone)
            new_code = input(f"{Fore.CYAN}[+] أدخل الكود الجديد: {Style.RESET_ALL}")
            await client.sign_in(phone, new_code)
        print(f"{Fore.GREEN}[+] تمت استعادة الاتصال بنجاح{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] فشل الإصلاح: {e}{Style.RESET_ALL}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] تم إيقاف البرنامج بواسطة المستخدم{Style.RESET_ALL}")
        sys.exit(0)