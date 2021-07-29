# dryflower.lib

An easy recruiting library.

## 技術仕様

言語: Python-3.9.1

外部ライブラリ: discord.py, datetime

ライセンス: MIT-License

## 使い方
以下のサンプルコードを参考にしてください。DryFlowerBOTと同様の挙動をします。

```Python
import discord
from discord.ext import commands
from discord import Button, ButtonStyle, SelectMenu, SelectOption
import dryflower

# intents
intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix='!', intents=intents)


@client.command()
async def dr(ctx, *args):
    bs = dryflower.Bosyu(ctx.message)
    await bs.generate()


@client.on_click(custom_id="hi")
async def button_press_hi(i: discord.Interaction, button):
    message = i.message
    if dryflower.check_bosyu(message):
        bs = dryflower.Bosyu(message)
        await bs.add_reaction(i.author)
        await i.respond("**参加** を表明しました。", hidden=True)


@client.on_click(custom_id="no")
async def button_press_no(i: discord.Interaction, button):
    message = i.message
    if dryflower.check_bosyu(message):
        bs = dryflower.Bosyu(message)
        await bs.remove_reaction(i.author)
        await i.respond("取り消しました。", hidden=True)


@client.on_click(custom_id="control")
async def button_press_control(i: discord.Interaction, button):
    # if not i.member.guild_permissions.manage_messages:
    #     await i.respond("権限がありません。募集を管理するには「メッセージを管理」権限が必要です。", hidden=True)
    #     return

    # 返信元取得できるようにmessageIDをcustom_idの後ろにくっつける
    components = [
        [
            SelectMenu(custom_id=f"control-select-{i.message.id}", options=[
                SelectOption(emoji='🚥', label='〆', value='sime', description="募集を締め切ります"),
                SelectOption(emoji='📯', label='集合', value='syuugou', description="専用ロールで集合をかけます。"),
                SelectOption(emoji='🗑', label='無効化', value='disable', description="募集を無効化し、ロールを削除します。")
            ],
                       placeholder='🔧 Select action!', max_values=3)
        ]
    ]

    await i.respond("操作を選択してください。", components=components, hidden=True)


@client.event
async def on_selection_select(i: discord.Interaction, select_menu):

    message_id = select_menu.custom_id[-18:]
    message = await i.channel.fetch_message(message_id)
    bs = dryflower.Bosyu(message)
    vals = select_menu.values

    if "syuugou" in vals and "disable" in vals:
        await i.respond("無効な組み合わせです。ロールへのメンション通知と同時に該当ロールが削除されてしまいます。"
                        "「無効化」は募集した企画そのものが終了した後に行うことを推奨しています。", hidden=True)
        return

    if "sime" in vals:
        await bs.sime(message)
        # await i.respond("正常に締め切りました。", hidden=True)
    if "syuugou" in vals:
        await bs.syuugou(message)
        # await i.respond("集合をかけました。", hidden=True)
    if "disable" in vals:
        await bs.disable(message)
        # await i.respond("無効化しました。", hidden=True)

    await i.respond("OK!", hidden=True)

    return


# Botの起動とDiscordサーバーへの接続
client.run(setting.TOKEN)

```

## もっと詳しく

[Wikiページ](https://github.com/shmn7iii/dryflower/wiki)をご覧ください。
