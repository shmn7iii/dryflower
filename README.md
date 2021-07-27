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
import dryflower

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)


@client.event
async def on_message_delete(message):
    if message.content.startswith("$BSDL:"):
        await dryflower.disable(message)


@client.event
async def on_message(message):
    if message.author.bot:
        if message.content != "〆":
            return

    # bosyu
    if message.content.startswith("!dr"):
        bs = dryflower.Bosyu(message)
        await bs.generate()

    # sime
    if message.content.startswith("〆"):
        if message.reference is not None:
            referenced_message = await message.channel.fetch_message(message.reference.message_id)
            if dryflower.check_bosyu(referenced_message):
                bs = dryflower.Bosyu(referenced_message)
                await bs.sime(referenced_message)

    # syuugou
    if message.content.startswith("集合"):
        if message.reference is not None:
            referenced_message = await message.channel.fetch_message(message.reference.message_id)
            if dryflower.check_bosyu(referenced_message) or dryflower.check_bosyu_sime(referenced_message):
                bs = dryflower.Bosyu(referenced_message)
                await bs.syuugou(referenced_message)


@client.event
async def on_raw_reaction_add(payload):
    message = await channel.fetch_message(payload.message_id)
    member = payload.member

    if member.bot:
        return

    if dryflower.check_bosyu(message):
        bs = dryflower.Bosyu(message)
        await bs.add_reaction(member)


@client.event
async def on_raw_reaction_remove(payload):
    message = await channel.fetch_message(payload.message_id)
    member = guild.get_member(payload.user_id)

    if member.bot:
        return

    if dryflower.check_bosyu(message):
        bs = dryflower.Bosyu(message)
        await bs.remove_reaction(member)
        

client.run("TOKEN")
```

## もっと詳しく

[Wikiページ](https://github.com/shmn7iii/dryflower/wiki)をご覧ください。
