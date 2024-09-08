import aiohttp
import asyncio
from datetime import datetime, timedelta

# Send a rich Discord embed notification
async def send_discord_embed(webhook_url, username, status, game_name=None, elapsed_time=None):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    status_icons = {
        "online but not in a game": "🟢",
        "in a game": "🎮",
        "in Roblox Studio": "🛠️"
    }

    color = {
        "online but not in a game": 0x00FF00,  # Green
        "in a game": 0x3498DB,  # Blue
        "in Roblox Studio": 0xF1C40F  # Yellow
    }.get(status, 0xFFFFFF)  # White as default

    embed = {
        "title": f"{status_icons.get(status, '')} {username}'s Status Update",
        "color": color,
        "fields": [
            {"name": "Status", "value": f"**{status}**", "inline": True},
            {"name": "Date and Time", "value": f"**{current_time}**", "inline": True}
        ],
        "footer": {
            "text": "grave on top faggots",
            "icon_url": "https://files.catbox.moe/5a89mn.jpg"  
        }
    }

    if game_name:
        embed["fields"].append({"name": "Game", "value": f"**{game_name}**", "inline": False})

    if elapsed_time:
        embed["fields"].append({"name": "Elapsed Time", "value": f"**{elapsed_time}**", "inline": True})

    data = {"embeds": [embed]}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=data) as response:
                if response.status == 204:
                    print(f"Successfully sent embed for {username}")
                else:
                    response_text = await response.text()
                    print(f"Failed to send embed for {username}: {response.status}, {response_text}")
    except Exception as e:
        print(f"Exception occurred while sending embed for {username}: {e}")

# Fetches Roblox user IDs based on usernames
async def get_user_ids(usernames, roblox_cookie):
    url = 'https://users.roblox.com/v1/usernames/users'
    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'.ROBLOSECURITY={roblox_cookie}',
    }
    data = {"usernames": usernames, "excludeBannedUsers": True}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    user_data = await response.json()
                    return {user['requestedUsername']: user['id'] for user in user_data['data']}
                else:
                    print(f"Error fetching User IDs: {response.status}")
                    return {}
    except Exception as e:
        print(f"Exception occurred while fetching User IDs: {e}")
        return {}

# Fetches the presence (status) of a list of Roblox users
async def get_user_presence(user_ids, roblox_cookie):
    url = 'https://presence.roblox.com/v1/presence/users'
    headers = {
        'Content-Type': 'application/json',
        'Cookie': f'.ROBLOSECURITY={roblox_cookie}',
    }
    data = {"userIds": user_ids}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    presence_data = await response.json()
                    return presence_data['userPresences']
                else:
                    print(f"Error fetching user presence: {response.status}")
                    return []
    except Exception as e:
        print(f"Exception occurred while fetching user presence: {e}")
        return []

# Retrieves the name of a game from its ID
async def get_game_name(game_id, roblox_cookie):
    url = f'https://games.roblox.com/v1/games/{game_id}'
    headers = {'Cookie': f'.ROBLOSECURITY={roblox_cookie}'}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    game_data = await response.json()
                    return game_data.get('name', 'Unknown Game')
                else:
                    print(f"Error fetching game name: {response.status}")
                    return 'Unknown Game'
    except Exception as e:
        print(f"Exception occurred while fetching game name: {e}")
        return 'Unknown Game'

# Main function to track users' statuses and send updates
async def track_users(usernames, webhook_url, roblox_cookie):
    user_ids = await get_user_ids(usernames, roblox_cookie)
    last_statuses = {username: None for username in usernames}
    status_timestamps = {username: None for username in usernames}

    while True:
        presences = await get_user_presence(list(user_ids.values()), roblox_cookie)
        current_time = datetime.now()

        for presence in presences:
            username = next(key for key, value in user_ids.items() if value == presence['userId'])
            current_status = presence['userPresenceType']
            game_id = presence.get('placeId', None)

            if current_status == 0:
                continue  # Skip offline users
            elif current_status == 1:
                status_text = "online but not in a game"
                game_name = None
            elif current_status == 2:
                status_text = "in a game"
                game_name = await get_game_name(game_id, roblox_cookie) if game_id else None
            elif current_status == 3:
                status_text = "in Roblox Studio"
                game_name = None

            # Check if the status or game has changed
            last_status = last_statuses[username]
            if last_status != (status_text, game_name):
                elapsed_time = None
                if status_timestamps[username]:
                    elapsed_time = str(current_time - status_timestamps[username]).split('.')[0]
                status_timestamps[username] = current_time

                await send_discord_embed(webhook_url, username, status_text, game_name, elapsed_time)
                last_statuses[username] = (status_text, game_name)

        await asyncio.sleep(10)  # Adjust this interval based on the number of users

# Run the tracking process
async def main():
    usernames = [
        "lerizclavie", "latiaspokem",
    ]
    webhook_url = "https://discord.com/api/webhooks/1282318908094808085/Xv-DTURVZwYhJRt1Y6lg9siNDMCxYfGHvodUaDg61XDKE8g9kQu7ZhgoTT2Y6wwwM5iP" # Replace with your Discord webhook URL
    roblox_cookie = "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_B510206599B897383CCFA5AEAEE7BA8CB1A8AA9AA6E04E65B3557833D2DE5B670B1C0A409B2E8C518FACAFB152B10FF6E02589165C6CEE04FEB69824813E76BFAA5129729EBE301B3C8A99DB848E28DFDD5851EEBE659416B60E8745EC495AED8891ABD53002A2D61B73D2BF4347985827EC88BCED7AECCA5C57CDCCE804CB5D48D8AAC5442342983D8E44FE4BF4F54B8D1A5E3F88B94D8F62B8D66DAE14950BB215A85062D8055CC89EBAD1FFFC53EC81BED4520E1FED96F21A8989129D92B6337335E2C6225025876B27FB629BA7D495F3CF1A4200BC3CB51718C6FFFCC09FF2A4FA73E0E2F2C1486CB2C25C97D5EBB5C22C88E41A2EA3A1441A5F28466AA0D7D1D268F1DAA9B08593E6537937240B6BA529A97F0464F81B021C1E87F875F46815C7E683150C45C7FA0EFE1B109C98C4658CA1EAE087357283728F5E2076E0C47C8E00C17DE86364734D5ECBB1521EF79515EF2E39FEBC200C4950862C95E3B582933E6714B7A20EF4BA66AF8DCF504F2DF8BCA568227C58DB05077BDF0479A1BFFFC87684C6F7E0C362EF553759396E6560AFDDDB87D1C95D0A25A7BE039198212727DCCF63B5558A73AE82631DEC83BEADAF8368907DBB647B56B2FB8C7217156EDE26FED0295690DE97437E14770C141FE234FFE859F3BEFA173E374D0FAC89F90617F3022CE33CC95876C639739241F712F6B0107BC88CF2CCACB5A2AB322DE6845E3D88CD55C29BA09EB7BDCA01CED3CD93C7F7A3D53D99B2BBC59BB4701B41DBF6C30F428FAF7991B3C6B31B43F0209417B0344736D53A99A3C03A6C29598FDC723D671246CAFC09DE3173AAC973B6B3C40A555D53556F375765E7EEEBADB11946F16099D8E2803FE0A865CDF50737FF7C6121545D9DEEAB5929D902B48C2F45DD1F01037577A651274B9364834264B7"  # Replace with your .ROBLOSECURITY cookie

    await track_users(usernames, webhook_url, roblox_cookie)

# Execute the main function
if __name__ == "__main__":
    asyncio.run(main())
