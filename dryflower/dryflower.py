import discord
import datetime
from discord import Button, ButtonStyle, SelectMenu, SelectOption


def getTime():
    dt_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9)))
    month = str(dt_now.month)
    day = str(dt_now.day)
    hour = str(dt_now.hour)
    minute = str(dt_now.minute)
    if len(hour) == 1:
        hour = "0" + hour
    if len(minute) == 1:
        minute = "0" + minute
    return f'{month}/{day} {hour}:{minute}'


def getEmbedFromMessage(message):
    return discord.Embed.from_dict(message.embeds[0].to_dict())


class Bosyu:
    def __init__(self, _message):
        self.message = _message
        self.BSID = getBSID(_message)

        # __init__ の中で async/await できない関係でまず None で初期値設定 -> 使うときに各自で self.getRole() する形に
        self.role = None

        try:
            self.embed = getEmbedFromMessage(_message)
        except:
            self.embed = None

    async def getRole(self, creation=False):
        # まずは探索
        role_name = self.embed.description[:10] + "..."
        roles_in_guild = await self.message.guild.fetch_roles()
        for role in roles_in_guild:
            if role.name == role_name:
                return role
        # なければ
        if creation:
            await self.message.guild.create_role(name=role_name, mentionable=True,
                                                 reason="Created by DryFlower. BSID: " + self.BSID)
            return await self.getRole(False)
        else:
            return None

    async def generate(self):
        contents = self.message.content.split()
        contents.remove("!dr")
        mentions = []
        mentioned_channel = None

        # channel mention
        if len(self.message.channel_mentions) != 0:
            for i in self.message.channel_mentions:
                mentioned_channel = i
                contents.remove(i.mention)

        # member mention
        if len(self.message.mentions) != 0:
            for i in self.message.mentions:
                mentions.append(f"{i.mention}")
                # contents中では<@!21345678>なのにi.mentionでは<@21345678>になるとかいう罠。
                # ちなみにチャンネルメンションはどちらも<@&1234567>になるから多分仕様変更の弊害かなにか
                contents.remove(i.mention[:2] + "!" + i.mention[2:])

        # role mention
        if len(self.message.role_mentions) != 0:
            for i in self.message.role_mentions:
                mentions.append(f"{i.mention}")
                contents.remove(i.mention)

        # @number
        att_max = None
        for i in contents:
            if i.startswith("@"):
                i = i.replace("@", "")
                if i.isdecimal():
                    att_max = i

        # create embed
        em = discord.Embed(title=":mega: 募集", description=" ".join(contents), color=0x00f900)
        em.set_author(name=self.message.author.name, icon_url=self.message.author.avatar_url)
        if att_max is None:
            em.add_field(name=f"参加者 | 0人", value="ｲﾅｲﾖ", inline=False)
        else:
            em.add_field(name=f"参加者 | @{att_max}", value="ｲﾅｲﾖ", inline=False)
        em.set_footer(text=f"$BSID: {self.BSID} | LastEdit: {getTime()}")

        self.embed = em

        # create role
        self.role = await self.getRole(creation=True)

        components = [
            [
                Button(label="🙌  参加",
                       custom_id="hi",
                       style=ButtonStyle.red),
                Button(label="👋  取り消し",
                       custom_id="no",
                       style=ButtonStyle.blurple),
                Button(label="⚙️  管理",
                       custom_id="control",
                       style=ButtonStyle.grey)
            ]
        ]

        # send
        if mentioned_channel is None:
            await self.message.channel.send(" ".join(mentions), embed=em, components=components)
        else:
            await mentioned_channel.send(" ".join(mentions), embed=em, components=components)

    async def add_reaction(self, member):
        await self.reaction_event(True, member)

    async def remove_reaction(self, member):
        await self.reaction_event(False, member)

    async def reaction_event(self, add, member):

        self.role = await self.getRole(creation=False)

        f_value = self.embed.fields[0].value.splitlines()
        value = ""
        f_name = member.name

        # add
        if add:
            if "ｲﾅｲﾖ" in f_value:
                f_value.remove("ｲﾅｲﾖ")
            if not "- " + f_name in f_value:
                f_value.append("- " + f_name)

            # role add
            if self.role is not None:
                await member.add_roles(self.role, reason="Added by DryFlower. BSID: " + self.BSID)

        # remove
        else:
            if "- " + f_name in f_value:
                f_value.remove("- " + f_name)

            if len(f_value) == 0:
                f_value.append("ｲﾅｲﾖ")

            # role remove
            if self.role is not None:
                await member.remove_roles(self.role, reason="Removed by DryFlower. BSID: " + self.BSID)

        for i in f_value:
            value += "\n" + i

        att_max = None
        contents = self.embed.description.split()
        for i in contents:
            if i.startswith("@"):
                i = i.replace("@", "")
                if i.isdecimal():
                    att_max = int(i)

        if "ｲﾅｲﾖ" in f_value:
            att_now = 0
        else:
            att_now = len(f_value)

        if att_max is None:
            name = f"参加者 | {att_now}人"
        else:
            name = f"参加者 | @{att_max - att_now}"

        self.embed.clear_fields()
        self.embed.add_field(name=name, value=value, inline=False)
        self.embed.set_footer(text=f"$BSID: {self.BSID} | LastEdit: {getTime()}")

        check_end = False
        if att_max is not None:
            if att_max - att_now == 0:
                check_end = True

        await self.message.edit(embed=self.embed)
        if check_end:
            await self.sime(self.message)

    async def sime(self, referenced_message):
        members = self.embed.fields[0].value
        er = discord.Embed(title=self.embed.title, description=self.embed.description, color=0xff2600)
        er.set_author(name=self.embed.author.name, icon_url=self.embed.author.icon_url)
        er.add_field(name="参加者 | 〆!!", value=members, inline=False)
        er.set_footer(text=f"&BSID: {self.BSID} | LastEdit: {getTime()}")

        await referenced_message.edit(content="", embed=er)
        await referenced_message.clear_reactions()

    async def syuugou(self, referenced_message):
        self.role = await self.getRole(False)
        await referenced_message.reply(f"{self.role.mention} 集合！！")

    async def disable(self, referenced_message):
        await self.sime(self.message)

        self.role = await self.getRole(creation=False)
        if self.role is not None:
            await self.role.delete(reason="Deleted by DryFlower. BSID: " + str(self.BSID))

        await referenced_message.edit(components=[])


# check if bosyu is enable
def check_bosyu(_message):
    try:
        embed = getEmbedFromMessage(_message)
    except:
        return False
    if embed.footer.text.startswith("$BSID:"):
        return True
    else:
        return False


# check if bosyu is simed
def check_bosyu_sime(_message):
    try:
        embed = getEmbedFromMessage(_message)
    except:
        return False
    if embed.footer.text.startswith("&BSID:"):
        return True
    else:
        return False


def getBSID(message):
    try:
        embed = getEmbedFromMessage(message)
    except:
        # 最初の生成時にしかこっち来ないはず。BSIDは生成用素メッセージのMessageIDを使う。
        return str(message.id)

    return embed.footer.text[7:25]
