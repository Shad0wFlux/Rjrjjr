import re, requests, time, sys, os, random
from os import path
from concurrent.futures import ThreadPoolExecutor, as_completed
from user_agent import generate_user_agent

RED = '\033[1;31m'
GREEN = '\033[2;32m'
RESET = '\033[0m'

expected_response = '"status_code":0,"status_msg":"Thanks for your feedback"'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def format_proxy(proxy):
    proxy = proxy.strip()
    if not (proxy.startswith("http://") or proxy.startswith("https://") or 
            proxy.startswith("socks5://") or proxy.startswith("socks4://")):
        return "http://" + proxy
    return proxy

TEST_URL = "https://httpbin.org/ip"
PROXY_TIMEOUT = 1
MAX_THREADS = 400

def check_proxy(proxy_url):
    formatted = format_proxy(proxy_url)
    proxies = {"http": formatted, "https": formatted}
    try:
        response = requests.get(TEST_URL, proxies=proxies, timeout=PROXY_TIMEOUT)
        if response.status_code == 200:
            return proxy_url, True
    except Exception:
        pass
    return proxy_url, False

def check_proxies_concurrently(proxy_list):
    working = []
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_proxy = {executor.submit(check_proxy, p): p for p in proxy_list}
        for future in as_completed(future_to_proxy):
            proxy, status = future.result()
            if status:
                working.append(format_proxy(proxy))
    return working

def show_report_menu():
    clear_screen()
    print(f"""
TikTok Reporter Tool v1.0
By Shadow

[1] - Report Content
[2] - Spam or Harassment
[3] - Under 13
[4] - Fake Information - Alias
[5] - Hate Speech
[6] - Pornographic
[7] - Terrorism Organizations
[8] - Self Harm
[9] - Harassment or Bullying
[10] - Violence
[11] - Random Reports
[12] - Random Reports with Proxies
[13] - Frauds And Scams
[14] - Dangerous and Challenges Acts
[15] - Report Spam
    """)
    try:
        option = int(input(f"[?] Choose report type (1-15): "))
        if option not in range(1, 16):
            print(f"{RED}Invalid option selected!{RESET}")
            time.sleep(1.5)
            return show_report_menu()
        return option
    except ValueError:
        print(f"{RED}Please enter a valid number!{RESET}")
        time.sleep(1.5)
        return show_report_menu()

def main():
    clear_screen()
    print(f"""
TikTok Reporter Tool v1.0
By Shadow
Instagram: @EK6Q
Telegram : t.me/nusrc
    """)

    option = show_report_menu()

    random_mode = option in [11, 12]
    proxy_mode = option == 12

    option_mapping = {
        11: None,
        12: None,
        13: 14,
        14: 15,
        15: 16
    }
    
    report_type = option_mapping.get(option, option) if not random_mode else None

    clear_screen()

    print(f"SESSION SETUP")
    use_file = input(f"[?] Load session IDs from file? (Y/N): ").strip().lower()
    sessions = []
    
    if use_file == 'y':
        fixed_file = "sessions.txt"
        if not path.isfile(fixed_file):
            print(f"{RED}[!] Session file '{fixed_file}' not found!{RESET}")
            sys.exit(0)
        with open(fixed_file, 'r', encoding='utf-8') as f:
            for line in f:
                s = line.strip()
                if s:
                    sessions.append(s)
        print(f"{GREEN}[+] Loaded {len(sessions)} sessions from file.{RESET}")
    else:
        try:
            num = int(input(f"[?] How many session IDs to enter? : "))
        except ValueError:
            print(f"{RED}[!] Please enter a valid number{RESET}")
            sys.exit(0)
        for i in range(num):
            s = input(f"[+] Enter session ID #{i+1}: ")
            sessions.append(s.strip())

    working_proxies = []
    if proxy_mode:
        print(f"PROXY SETUP")
        proxy_file = input(f"[?] Enter proxy file path: ").strip()
        if not path.isfile(proxy_file):
            print(f"{RED}[!] Proxy file '{proxy_file}' not found!{RESET}")
            sys.exit(0)
        proxy_list = []
        with open(proxy_file, 'r', encoding='utf-8') as pf:
            for line in pf:
                p = line.strip()
                if p:
                    proxy_list.append(p)
        if not proxy_list:
            print(f"{RED}[!] No proxies loaded from file!{RESET}")
            sys.exit(0)
        print(f"{GREEN}[*] Checking {len(proxy_list)} proxies. Please wait...{RESET}")
        working_proxies = check_proxies_concurrently(proxy_list)
        if not working_proxies:
            print(f"{RED}[!] No working proxies found!{RESET}")
            sys.exit(0)
        else:
            print(f"{GREEN}[+] {len(working_proxies)} working proxies found.{RESET}")

    print(f"SESSION VALIDATION")
    check_url = ('https://api16-normal-c-alisg.tiktokv.com/passport/account/info/v2/'
                 '?scene=normal&multi_login=1&account_sdk_source=app&passport-sdk-version=19&'
                 'os_api=25&device_type=A5010&ssmix=a&manifest_version_code=2018093009&dpi=191&'
                 'carrier_region=JO&uoo=1&region=US&app_name=musical_ly&version_name=7.1.2&'
                 'timezone_offset=28800&ts=1628767214&ab_version=7.1.2&residence=SA&'
                 'cpu_support64=false&current_region=JO&ac2=wifi&ac=wifi&app_type=normal&'
                 'host_abi=armeabi-v7a&channel=googleplay&update_version_code=2018093009&'
                 '_rticket=1628767221573&device_platform=android&iid=7396386396296286392&'
                 'build_number=7.1.2&locale=en&op_region=SA&version_code=200705&'
                 'timezone_name=Asia%2FShanghai&cdid=f61ca549-c9ee-450b-90da-8854423b74e7&'
                 'openudid=3e5afbd3f6dde322&sys_region=US&device_id=7296396296396396393&'
                 'app_language=en&resolution=576*1024&device_brand=OnePlus&language=en&'
                 'os_version=7.1.2&aid=1233&mcc_mnc=2947')
    base_headers = {
        'Host': 'api16-normal-c-alisg.tiktokv.com',
        'Accept-Encoding': 'gzip, deflate',
        'User-Agent': generate_user_agent()
    }

    valid_sessions_file = "valid_sessions.txt"
    valid_session_count = 0
    expired_session_count = 0
    checked_valid_sessions = []

    print(f"{GREEN}[*] Validating {len(sessions)} sessions...{RESET}")
    for s in sessions:
        h = base_headers.copy()
        h['Cookie'] = 'sessionid=' + s
        try:
            resp = requests.get(check_url, headers=h, timeout=1)
        except Exception as e:
            print(f"{RED}[!] Error checking session {s[:8]}...: {e}{RESET}")
            continue
        if '"session expired, please sign in again"' in resp.text:
            expired_session_count += 1
            print(f"{RED}[×] Session expired: {s[:8]}...{RESET}")
        elif 'user_id' in resp.text:
            valid_session_count += 1
            checked_valid_sessions.append(s)
            print(f"{GREEN}[✓] Session valid: {s[:8]}...{RESET}")
    
    if not checked_valid_sessions:
        print(f"{RED}[!] No valid sessions found!{RESET}")
        sys.exit(0)
    sessions = checked_valid_sessions

    print(f"[i] Valid sessions: {valid_session_count} | Expired sessions: {expired_session_count}")
    with open(valid_sessions_file, 'w', encoding='utf-8') as f:
        for sess in sessions:
            f.write(sess + "\n")
    print(f"{GREEN}[✓] Valid sessions saved to {valid_sessions_file}{RESET}")
    time.sleep(1)

    clear_screen()
    print(f"TARGET SETUP")
    username = input(f"[?] Enter target username: ").strip()
    
    head = {
        'Host': 'www.tiktok.com',
        'User-Agent': generate_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Te': 'trailers',
        'Connection': 'close',
    }
    
    print(f"{GREEN}[*] Fetching user ID for @{username}...{RESET}")
    req = requests.get(f'https://www.tiktok.com/@{username}?lang=en', headers=head)
    try:
        target_ID = re.findall(r'"user":{"id":"(.*?)"', req.text)[0]
        print(f"{GREEN}[✓] User ID found: {target_ID}{RESET}")
    except:
        print(f"{RED}[!] User not found or banned!{RESET}")
        sys.exit(0)
    
    reports_per_session = 1
    if len(sessions) > 1:
        try:
            reports_per_session = int(input(f"[?] How many reports per session? : "))
            if reports_per_session < 1:
                reports_per_session = 1
        except ValueError:
            print(f"{RED}[!] Invalid input. Using 1 report per session.{RESET}")
            reports_per_session = 1
    
    try:
        sleep_time = int(input(f"[?] Enter sleep time between reports (seconds): "))
        if sleep_time < 0:
            sleep_time = 0
    except ValueError:
        print(f"{RED}[!] Invalid input. Using 5 seconds as default.{RESET}")
        sleep_time = 5

    def get_report_params(r_type, target_ID, session):
        base_url = 'https://www.tiktok.com/aweme/v1/aweme/feedback/'
        common = ("?aid=1233&app_name=tiktok_web&device_platform=web_mobile"
                  "&region=SA&priority_region=SA&os=ios&"
                  "cookie_enabled=true&screen_width=375&screen_height=667&"
                  "browser_language=en-US&browser_platform=iPhone&"
                  "browser_name=Mozilla&browser_version=5.0+(iPhone;+CPU+iPhone+OS+15_1+like+Mac+OS+X)+"
                  "AppleWebKit/605.1.15+(KHTML,+like+Gecko)+InspectBrowser&"
                  "browser_online=true&app_language=ar&timezone_name=Asia%2FRiyadh&"
                  "is_page_visible=true&focus_state=true&is_fullscreen=false")
        params = {
            1: {"reason": "399", "reporter_id": "7024230440182809606", "device_id": "7008218736944907778"},
            2: {"reason": "310", "reporter_id": "27568146", "device_id": "7008218736944907778"},
            3: {"reason": "317", "reporter_id": "27568146", "device_id": "7008218736944907778"},
            4: {"reason": "3142", "reporter_id": "6955107540677968897", "device_id": "7034110346035136001"},
            5: {"reason": "306", "reporter_id": "6955107540677968897", "device_id": "7034110346035136001"},
            6: {"reason": "308", "reporter_id": "310430566162530304", "device_id": "7034110346035136001"},
            7: {"reason": "3011", "reporter_id": "310430566162530304", "device_id": "7034110346035136001"},
            8: {"reason": "3052", "reporter_id": "310430566162530304", "device_id": "7034110346035136001"},
            9: {"reason": "3072", "reporter_id": "310430566162530304", "device_id": "7034110346035136001"},
            10: {"reason": "303", "reporter_id": "310430566162530304", "device_id": "7034110346035136001"},
            14: {"reason": "9004", "reporter_id": "7242379992225940485", "device_id": "7449373206865561094"},
            15: {"reason": "90064", "reporter_id": "7242379992225940485", "device_id": "7449373206865561094"},
            16: {"reason": "9010", "reporter_id": "7242379992225940485", "device_id": "7449373206865561094"}
        }
        p = params.get(r_type)
        url = (f"{base_url}{common}&reason={p['reason']}&report_type=user"
               f"&object_id={target_ID}&owner_id={target_ID}&target={target_ID}"
               f"&reporter_id={p['reporter_id']}&current_region=SA")
        rep_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Cookie': 'sessionid=' + session,
            'Host': 'www.tiktok.com',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': generate_user_agent()
        }
        data = {
            "object_id": target_ID,
            "owner_id": target_ID,
            "report_type": "user",
            "target": target_ID
        }
        return url, rep_headers, data

    def get_random_report_type():
        return random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 14, 15, 16])

    def send_report(session, report_url, headers, data, proxies=None):
        try:
            rep = requests.post(report_url, headers=headers, data=data, proxies=proxies, timeout=5)
            success = expected_response not in rep.text
            return success, session
        except Exception:
            return False, session

    clear_screen()
    print(f"""
TikTok Report Attack Started

Target: @{username} ID: {target_ID[:8]}...
Sessions: {len(sessions)} Reports/Session: {reports_per_session}
Report Type: {report_type if not random_mode else "Random"}
    """)

    successful_reports = 0
    failed_reports = 0
    total_reports = 0
    
    try:
        while True:
            for session in sessions:
                for _ in range(reports_per_session):
                    current_r_type = get_random_report_type() if random_mode else report_type
                    url_report, headers_rep, data_rep = get_report_params(current_r_type, target_ID, session)
                    if proxy_mode and working_proxies:
                        proxy_addr = random.choice(working_proxies)
                        proxies = {"http": proxy_addr, "https": proxy_addr}
                    else:
                        proxies = None
                        
                    success, curr_session = send_report(session, url_report, headers_rep, data_rep, proxies=proxies)
                    
                    if success:
                        successful_reports += 1
                    else:
                        failed_reports += 1
                    total_reports += 1
                    
                    clear_screen()
                    print(f"""
TikTok Report Attack Running

Target: @{username} ID: {target_ID[:8]}...

Process Statistics
Successful reports: {successful_reports}
Failed reports: {failed_reports}
Session: {curr_session[:8]}...
Total: {total_reports}
                    """)
                    
                    time.sleep(sleep_time)
                
    except KeyboardInterrupt:
        print(f"\n[!] Attack interrupted by user.")
        print(f"{GREEN}[+] Final Report: Success: {successful_reports} | Failed: {failed_reports} | Total: {total_reports}{RESET}")
        sys.exit(0)

if __name__ == "__main__":
    main()