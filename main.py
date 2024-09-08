import aiohttp
import asyncio
from datetime import datetime, timedelta
import webserver

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
        "lerizclavie", "latiaspokem", "Lune_Jana", "nolplay355", "progamer142517251", "trixieccp", "ooANARCHY", 
    ]
    webhook_url = "https://discord.com/api/webhooks/1282318908094808085/Xv-DTURVZwYhJRt1Y6lg9siNDMCxYfGHvodUaDg61XDKE8g9kQu7ZhgoTT2Y6wwwM5iP" # Replace with your Discord webhook URL
    roblox_cookie = "_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_B34C34E09C1F07A22DE1883E7339740DD19449D8628C6D2796FD65E94B5ED79A5956175F2C399CD8130FB4E7CC55C414B37880BF09F786F1A8F7EE1EFA6D3A957379F4DD8D3E05E1EFFF489FC7806776B409DC3DF439091DAC4AE96F39F830E15389A2848F53B063073B84DE9AF8A613CB68111F52A2C8A13CE065789868F44000305BF4A662393BED9582658FAA53298D88CAD82B42829939C3C4494D09B6F8DD17BCBBA20C3D72FCAC0CA67750BD3EEDBA9B96842E597126DEE5D240E51C8E0DD9828ECF83315B89E41503B8DD2BFC071108DA505FDD3FDC4CE521422CF9189E2B153F9723BE9E20FB7076160789A5AC56E9245B6EADAFCA8061DBB08477C53859FFD5BAB1EF2C81F071F5DC10FEDF5047F846A06911B932AFE9D88AF47189ADD5EFAE1BECE32C5D8FE177ABAB74B0DD563B32A7128F72B897A25E8929998004C0CB1D159B1CAE79187D24470E1672412B7A984060C4DC57F3079203C0DE0CE4EE0B10887EA8AE90C42A7CDBB9282126A5F36D9A915C0FC599A39CA81C178F57B9BA81C847EECA7142F0E12DE313BEAB898B69C8DF386CE359B626E4E0CA82C5716C81490DA95BA78B48372EB7BDE6572D570D28574F76FFE2F4447E13C87FDBDC5FD2731373FB607B6FB3D973DB81413F6BB6EF092661D608DAA323AD71D108B81659F9ABA8FB6E2BAA5766366917BFB508C2590A263E8BE4D306828D8450027B7FD2E93A9428EADAD34CAFA0B87186544AD22A77C05880B0E340209D000C84C7DE0B6BB004117F681595A020AC6DA03D31F970667C8E35DEE547C33B8589309DB86437E6721C7BDAB0A749E9705318B9C70D6BF11436766D645029D5F617EA27265377B0FDB3579DD81D9F49ED33D21ED62BE98A74029A8188E3A5DC0E8C6317E616"  # Replace with your .ROBLOSECURITY cookie

    await track_users(usernames, webhook_url, roblox_cookie)


webserver.keep_alive()
# Execute the main function
if __name__ == "__main__":
    asyncio.run(main())
