from curl_cffi import requests
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, hashlib, time, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Kivanet:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Language": "en",
            "Origin": "https://app.kivanet.com",
            "Priority": "u=1, i",
            "Referer": "https://app.kivanet.com/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://app.kivanet.com"
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.access_tokens = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Claim {Fore.BLUE + Style.BRIGHT}Kiva Network - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_accounts(self):
        filename = "accounts.json"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File {filename} Not Found.{Style.RESET_ALL}")
                return

            with open(filename, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            return []
    
    async def load_proxies(self, use_proxy_choice: bool):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                response = await asyncio.to_thread(requests.get, "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text")
                response.raise_for_status()
                content = response.text
                with open(filename, 'w') as f:
                    f.write(content)
                self.proxies = [line.strip() for line in content.splitlines() if line.strip()]
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, email):
        if email not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[email] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[email]

    def rotate_proxy_for_account(self, email):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[email] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def mask_account(self, account):
        if "@" in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"
        
    def encoded_hex(self, text: bytes) -> str:
        md5 = hashlib.md5()
        md5.update(text)
        return md5.hexdigest()
        
    def encode_password(self, password):
        encoded_pass = self.encoded_hex(password.encode('utf-8'))
        return encoded_pass
    
    def generate_sign_payload(self):
        keys = "klj90)sadsjfdjskfjkdd*&*&34434434346fjdskfjO"
        timestamp = int(time.time() * 1000)
        try:
            data  = keys + str(timestamp)
            encoded_data = self.encoded_hex(data.encode('utf-8'))
            auth = ''.join(sorted(encoded_data))
            
            payload = {
                "isTg":"1",
                "auth":auth,
                "timestamp":timestamp
            }

            return payload
        except Exception as e:
            raise Exception(f"Generate Req Payload Failed: {str(e)}")

    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Proxyscrape Free Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run With Private Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Run Without Proxy{Style.RESET_ALL}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "With Proxyscrape Free" if choose == 1 else 
                        "With Private" if choose == 2 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        rotate = False
        if choose in [1, 2]:
            while True:
                rotate = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return choose, rotate
    
    async def check_connection(self, proxy=None):
        try:
            response = await asyncio.to_thread(requests.get, url=self.BASE_API, headers={}, proxy=proxy, timeout=30, impersonate="chrome110", verify=False)
            response.raise_for_status()
            return True
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Connection Not 200 OK {Style.RESET_ALL}"
            )
        return None
        
    async def user_login(self, email: str, password: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/user/login"
        data = json.dumps({"email":email, "password":self.encode_password(password)})
        headers = {
            **self.headers,
            "Authorization": "",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxy=proxy, timeout=120, impersonate="chrome110", verify=False)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Login Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
        
    async def user_info(self, email: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/user/getSignInfo"
        data = json.dumps({"isTg":"1"})
        headers = {
            **self.headers,
            "Authorization": self.access_tokens[email],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxy=proxy, timeout=120, impersonate="chrome110", verify=False)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Balance   :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} GET Earned PTS Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
            
    async def start_mining(self, email: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/user/sign"
        data = json.dumps(self.generate_sign_payload())
        headers = {
            **self.headers,
            "Authorization": self.access_tokens[email],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxy=proxy, timeout=120, impersonate="chrome110", verify=False)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Mining    :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Not Started {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
        
    async def task_lists(self, email: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/task/getTaskList"
        data = json.dumps({"status":1})
        headers = {
            **self.headers,
            "Authorization": self.access_tokens[email],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxy=proxy, timeout=120, impersonate="chrome110", verify=False)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Task Lists:{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} GET Lists Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
        
    async def do_tasks(self, email: str, task_id: str, title: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/api/task/doTask"
        data = json.dumps({"id":task_id})
        headers = {
            **self.headers,
            "Authorization": self.access_tokens[email],
            "Content-Length": str(len(data)),
            "Content-Type": "application/json",
        }
        for attempt in range(retries):
            try:
                response = await asyncio.to_thread(requests.post, url=url, headers=headers, data=data, proxy=proxy, timeout=120, impersonate="chrome110", verify=False)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN + Style.BRIGHT}    ->{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} {title} {Style.RESET_ALL}"
                    f"{Fore.RED + Style.BRIGHT}Not Completed{Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}"
                )

        return None
            
    async def process_check_connection(self, email: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            )

            is_valid = await self.check_connection(proxy)
            if is_valid:
                return True
            
            if rotate_proxy:
                proxy = self.rotate_proxy_for_account(email)
                await asyncio.sleep(5)
                continue

            return False

    async def process_user_login(self, email: str, password: str, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(email, use_proxy, rotate_proxy)
        if is_valid:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None
            
            login = await self.user_login(email, password, proxy)
            if login and login.get("state"):
                self.access_tokens[email] = login["object"]

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} Login Success {Style.RESET_ALL}"
                )
                return True
                
            return False
            
    async def process_accounts(self, email: str, password: str, use_proxy: bool, rotate_proxy: bool):
        logined = await self.process_user_login(email, password, use_proxy, rotate_proxy)
        if logined:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None
            
            user = await self.user_info(email, proxy)
            if user and user.get("state"):
                balance = user.get("object").get("allAccount", 0)

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Balance   :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {balance} {Style.RESET_ALL}"
                )

            mining = await self.start_mining(email, proxy)
            if mining and mining.get("state"):
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Mining    :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} Started {Style.RESET_ALL}"
                )
                
            task_lists = await self.task_lists(email, proxy)
            if task_lists and task_lists.get("state"):
                tasks = task_lists.get("object", [])

                if tasks:
                    self.log(f"{Fore.CYAN+Style.BRIGHT}Task Lists:{Style.RESET_ALL}")

                    for task in tasks:
                        if task:
                            task_id = task.get("id")
                            title = task.get("taskName")
                            reward = task.get("speedAdd")

                            complete = await self.do_tasks(email, task_id, title, proxy)
                            if complete:
                                self.log(
                                    f"{Fore.CYAN + Style.BRIGHT}    ->{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} {title} {Style.RESET_ALL}"
                                    f"{Fore.GREEN + Style.BRIGHT}Is Completed{Style.RESET_ALL}"
                                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                                    f"{Fore.CYAN + Style.BRIGHT}Reward{Style.RESET_ALL}"
                                    f"{Fore.WHITE + Style.BRIGHT} +{reward}% {Style.RESET_ALL}"
                                )
                else:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Task Lists:{Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT} No Available {Style.RESET_ALL}"
                    )
    
    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts:
                self.log(f"{Fore.RED + Style.BRIGHT}No Accounts Loaded.{Style.RESET_ALL}")
                return
            
            use_proxy_choice, rotate_proxy = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            while True:
                use_proxy = False
                if use_proxy_choice in [1, 2]:
                    use_proxy = True

                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )

                if use_proxy:
                    await self.load_proxies(use_proxy_choice)
                
                separator = "=" * 20
                for idx, account in enumerate(accounts, start=1):
                    if account:
                        email = account["Email"]
                        password = account["Password"]
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {idx} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}Of{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {len(accounts)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )

                        if not "@" in email or not password:
                            self.log(
                                f"{Fore.CYAN+Style.BRIGHT}Status    :{Style.RESET_ALL}"
                                f"{Fore.RED+Style.BRIGHT} Invalid Account Data {Style.RESET_ALL}"
                            )
                            continue
                            
                        await self.process_accounts(email, password, use_proxy, rotate_proxy)
                        await asyncio.sleep(3)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*50)
                seconds = 12 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}All Accounts Have Been Processed.{Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        bot = Kivanet()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Kiva Network - BOT{Style.RESET_ALL}                                       "                              
        )