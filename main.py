import discord
import random
import emoji
import asyncio

TOKEN = 'YourToken'  # ここにトークン

intents = discord.Intents.all()
client = discord.Client(intents=intents)

mess = None
Player1 = None
Player2 = None
Choicemess = None
player_data = {"Player1": None, "Player2": None}
battle_running = False


async def start_game(message):
    global mess
    mess = await message.channel.send("ゲームを開始します。参加プレイヤーはこのメッセージにリアクションしてください。")


async def handle_battle(message):
    global Choicemess
    if Player1 is None or Player2 is None:
        await message.channel.send("プレイヤーが揃ってません。")
        return

    await message.channel.send("クラスを選択します。")

    async def class_select(player, player_key):
        global Choicemess, player_data
        Choicemess = await message.channel.send(f"{player.mention} はクラスを選択してください。")
        await Choicemess.add_reaction("\N{Crossed Swords}")
        await Choicemess.add_reaction("\N{Magic Wand}")
        await Choicemess.add_reaction("\N{Bow and Arrow}")

        def check(reaction, user):
            return (user == player and reaction.message.id == Choicemess.id and
                    str(reaction.emoji) in ["\N{Crossed Swords}", "\N{Magic Wand}", "\N{Bow and Arrow}"]) # 修正箇所

        try:
            reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
            if str(reaction.emoji) == "\N{Magic Wand}":
                player_data[player_key] = {"hp": 70, "attack": 50, "df": 10, "cr": 0.3, "class": "魔法使い"}
                await message.channel.send("魔法使いが選択されました。")
            elif str(reaction.emoji) == "\N{Crossed Swords}":
                player_data[player_key] = {"hp": 100, "attack": 30, "df": 20, "cr": 0.3, "class": "戦士"}
                await message.channel.send("戦士が選択されました。")
            elif str(reaction.emoji) == "\N{Bow and Arrow}":
                player_data[player_key] = {"hp": 90, "attack": 35, "df": 15, "cr": 0.3, "class": "狩人"}
                await message.channel.send("狩人が選択されました。")

        except asyncio.TimeoutError:
            await message.channel.send(f"{player.mention} クラス選択の時間が切れました。")
            # タイムアウト時の処理

    await class_select(Player1, "Player1")
    if player_data["Player1"] is not None:
        await class_select(Player2, "Player2")

    if player_data["Player1"] and player_data["Player2"]:
        await message.channel.send("バトルを開始します。")
        await battle(message, Player1, Player2, player_data["Player1"].copy(), player_data["Player2"].copy())
        player_data["Player1"] = None
        player_data["Player2"] = None



async def battle(message, player1, player2, player1_data, player2_data):
    battle_running = True
    turn = 1
    turn_message = None

    # 先攻後攻を決定
    if random.random() < 0.5:
        attacker = player1
        defender = player2
        attacker_data = player1_data
        defender_data = player2_data
        await message.channel.send(f"{player1.mention} が先攻です。")
    else:
        attacker = player2
        defender = player1
        attacker_data = player2_data
        defender_data = player1_data
        await message.channel.send(f"{player2.mention} が先攻です。")

    while player1_data["hp"] > 0 and player2_data["hp"] > 0 and battle_running:
        await asyncio.sleep(1)
        await message.channel.send(f"## ターン {turn}\n-")

        # 攻撃側のターン
        turn_message = await message.channel.send(f"{attacker.mention} のターンです。行動を選択してください: 👊 (攻撃), 🔯 (スキル)")
        await turn_message.add_reaction("👊")
        await turn_message.add_reaction("🔯")

        def check(reaction, user):
            return user == attacker and str(reaction.emoji) in ["👊", "🔯"] and reaction.message == turn_message

        try:
            reaction, _ = await client.wait_for('reaction_add', timeout=30.0, check=check)

            if str(reaction.emoji) == "👊":
                # if attacker_data["class"] == "戦士":
                #     await play_source("sensi_at.mp3",Player1)
                # elif attacker_data["class"] == "魔法使い":
                #     await play_source("mahou_at.mp3",Player1) 
                # elif attacker_data["class"] == "狩人":
                #     await play_source("kariudo_at.mp3",Player1)
                multiplier = random.uniform(0.8, 1.2)
                if random.random() < attacker_data["cr"]:
                    damage = max(0, int((attacker_data["attack"] * multiplier)))
                    defender_data["hp"] -= damage
                    await message.channel.send(f"クリティカルヒット！ {attacker.mention} が {defender.mention} に {damage} のダメージ！")
                else:
                    damage = max(0, int((attacker_data["attack"] - defender_data["df"]) * multiplier))
                    defender_data["hp"] -= damage
                await message.channel.send(f"{attacker.mention} が {defender.mention} に {damage} のダメージ！")

            elif str(reaction.emoji) == "🔯":
                if attacker_data["class"] == "戦士":
                    attack_boost = random.randint(5, 15)
                    attacker_data["attack"] += attack_boost
                    # await play_source("sensi_skil.mp3",Player1)
                    await message.channel.send(f"{attacker.mention} は攻撃力を {attack_boost} 上げた！")
                elif attacker_data["class"] == "魔法使い":
                    multiplier = random.uniform(0.8, 1.2)
                    attack = attacker_data["attack"] - 10
                    damage = int((attack - defender_data["df"]) * multiplier)
                    defender_data["hp"] -= damage
                    attacker_data["hp"] += int(damage /2)
                    # await play_source("mahou_skil.mp3",Player1)
                    await message.channel.send(f"{attacker.mention} が {defender.mention} に {damage} のダメージ！")
                    await message.channel.send(f"{attacker.mention}の体力が{int(damage/2)}回復した!")
                elif attacker_data["class"] == "狩人":
                    multiplier = random.uniform(0.8, 1.2)
                    attack = attacker_data["attack"] - 10
                    damage = int((attack - defender_data["df"]) * multiplier)
                    defender_data["hp"] -= damage
                    downDf = int(random.uniform(5, 7))
                    defender_data["df"] -= downDf
                    # await play_source("kariudo_skil.mp3",Player1)
                    await message.channel.send(f"{attacker.mention} が {defender.mention} に {damage} のダメージ！")
                    await message.channel.send(f"{defender.mention}の防御力が{downDf}下がった!")
        except asyncio.TimeoutError:
            await message.channel.send("時間切れです。")

        if defender_data["hp"] <= 0:  # 攻撃を受けた側のHPが0以下になった場合
            # await play_source("win.mp3",Player1)
            await message.channel.send(f"## {defender.mention} は倒れた！")
            await message.channel.send(f"# {attacker.mention} の勝利！")
            battle_running = False
            return
        

        # 攻撃側と防御側を交代
        attacker, defender = defender, attacker
        attacker_data, defender_data = defender_data, attacker_data

        await message.channel.send(f"{player1.mention} HP: {player1_data['hp']}, {player2.mention} HP: {player2_data['hp']}\n-")
        turn += 1



@client.event
async def on_ready():
    print('ログインしました')
    await client.change_presence(activity=discord.Game(name="バトル！"))


@client.event
async def on_message(message):
    if message.author.bot:
        return

    global battle_running,Player1, Player2

    if message.content == '/start':
        Player1 = None
        Player2 = None
        player_data = {"Player1": None, "Player2": None} 
        await start_game(message)
    elif message.content == '/helpjob':
        embed = discord.Embed(title="職業一覧", description="各職業の説明です。", color=0x00ff00)

        embed.add_field(name=":crossed_swords:戦士", value="HPが高く、防御力も高い。スキルで攻撃力を上げることができる。", inline=False)
        embed.add_field(name=":magic_wand:魔法使い", value="攻撃力が高く、スキルで敵のHPを吸収できる。", inline=False)
        embed.add_field(name=":bow_and_arrow:狩人", value="攻撃力と防御力のバランスが取れた職業。スキルで相手の防御力を下げることができる。", inline=False)
        await message.channel.send(embed=embed)
    elif message.content == '/commands':
        embed = discord.Embed(title="コマンド一覧", color=0x00ff00)

        embed.add_field(name="/start", value="ゲーム開始", inline=False)
        embed.add_field(name="/end", value="バトル強制終了", inline=False)
        embed.add_field(name="/helpjob", value="職業についての詳細説明", inline=False)
        await message.channel.send(embed=embed)       
    elif message.content == '/end':
        if battle_running:
            battle_running = False
            await message.channel.send("バトルを終了します。")
            Player1 = None
            Player2 = None
            player_data = {"Player1": None, "Player2": None}
        else:
            await message.channel.send("バトルは実行されていません。")
    elif message.content == '/join':
        if message.author.voice and message.author.voice.channel:
            await message.author.voice.channel.connect()
        else:
            await message.channel.send("ボイスチャンネルに参加していません。")
    elif message.content == "/leave":
        if message.guild.voice_client:
            await message.guild.voice_client.disconnect()
        else:
            await message.channel.send("ボイスチャンネルに接続していません。")
    elif message.content == "/playerPrint":
        await message.channel.send(f"Player1: {Player1}, Player2: {Player2}")



@client.event
async def on_reaction_add(reaction, user):
    global mess, Player1, Player2

    if mess is not None and reaction.message.id == mess.id and not user.bot:
        if Player1 is None:
            Player1 = user
            await reaction.message.channel.send(f"Player1は{user.mention}です")
        elif Player2 is None: #and user != Player1:
            Player2 = user
            await reaction.message.channel.send(f"Player2は{user.mention}です")
            await reaction.message.channel.send("プレイヤーが揃いました。")
            await handle_battle(reaction.message)

# #音再生
# async def play_source(file, member: discord.Member, volume=0.5):
#     # メンバーがボイスチャンネルに参加しているか確認
#     if member.voice is None:
#         return

#     # ボイスチャットのクライアントが接続されているか確認
#     if member.guild.voice_client is None:
#         # ボイスチャンネルに接続されていない場合
#         channel = member.voice.channel
#         await channel.connect()
    
#     # FFmpegを使って音源を作成
#     source = discord.FFmpegPCMAudio(file)
#     # 音量設定
#     source = discord.PCMVolumeTransformer(source, volume=volume)

#     # 音源を再生
#     voice_client = member.guild.voice_client
#     if voice_client.is_playing():
#         voice_client.stop()  # すでに再生中の場合、停止する
#     voice_client.play(source)

client.run(TOKEN)
