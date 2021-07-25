import discord
import datetime


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

        try:
            self.embed = getEmbedFromMessage(_message)
        except:
            self.embed = None

    async def generate(self):
        content = self.message.content.replace("!bosyu", "")
        mentions = []
        mentioned_channel = None

        # channel mention
        if len(self.message.channel_mentions) != 0:
            for i in self.message.channel_mentions:
                mentioned_channel = i

        # member mention
        if len(self.message.mentions) != 0:
            for i in self.message.mentions:
                mentions.append(f"{i.mention}")

        # role mention
        if len(self.message.role_mentions) != 0:
            for i in self.message.role_mentions:
                mentions.append(f"{i.mention}")

        # @number
        att_max = None
        contents = content.split()
        for i in contents:
            if i.startswith("@"):
                i = i.replace("@", "")
                if i.isdecimal():
                    att_max = i

        # create embed
        em = discord.Embed(title=":mega: 募集", description=content, color=0x00f900)
        em.set_author(name=self.message.author.name, icon_url=self.message.author.avatar_url)
        if att_max is None:
            em.add_field(name=f"参加者 | 0人", value="ｲﾅｲﾖ", inline=False)
        else:
            em.add_field(name=f"参加者 | @{att_max}", value="ｲﾅｲﾖ", inline=False)
        em.set_footer(text=f"$BSID: {self.BSID} | LastEdit: {getTime()}")

        # create role
        await self.message.guild.create_role(name=self.BSID, mentionable=True,
                                             reason="Created by gigi-bot for bosyu: " + self.BSID)

        # send
        if mentioned_channel is None:
            await self.message.channel.send(*mentions, embed=em)
        else:
            await mentioned_channel.send(*mentions, embed=em)

        # reply for delete
        await self.message.reply(f"$BSDL: {self.BSID} \n:wastebasket: 企画が終わったら or 企画を取り下げたらこの返信を消してね",
                                 mention_author=True)

    async def add_reaction(self, member):
        await self.reaction_event(True, member)

    async def remove_reaction(self, member):
        await self.reaction_event(False, member)

    async def reaction_event(self, add, member):
        roles_in_guild = await self.message.guild.fetch_roles()
        role = None
        for r in roles_in_guild:
            if r.name == self.BSID:
                role = r

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
            if role is not None:
                await member.add_roles(role, reason="Added by gigi-bot for bosyu: " + self.BSID)

        # remove
        else:
            if "- " + f_name in f_value:
                f_value.remove("- " + f_name)

            if len(f_value) == 0:
                f_value.append("ｲﾅｲﾖ")

            # role remove
            if role is not None:
                await member.remove_roles(role, reason="Removed by gigi-bot for bosyu: " + self.BSID)

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
            await self.message.reply("〆")

    async def sime(self, referenced_message):
        members = self.embed.fields[0].value
        er = discord.Embed(title=self.embed.title, description=self.embed.description, color=0xff2600)
        er.set_author(name=self.embed.author.name, icon_url=self.embed.author.icon_url)
        er.add_field(name="参加者 | 〆!!", value=members, inline=False)
        er.set_footer(text=f"&BSID: {self.BSID} | LastEdit: {getTime()}")

        await referenced_message.edit(content="", embed=er)
        await referenced_message.clear_reactions()

    async def syuugou(self, referenced_message):
        roles_in_guild = await referenced_message.guild.fetch_roles()
        role = None
        for r in roles_in_guild:
            if r.name == self.BSID:
                role = r

        await referenced_message.channel.send(f"{role.mention} 集合！！")


async def disable(message):
    BSID = message.content[7:25]
    roles_in_guild = await message.guild.fetch_roles()
    for r in roles_in_guild:
        if r.name == BSID:
            await r.delete(reason="Deleted by gigi-bot for bosyu: " + str(BSID))


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
        return str(message.id)

    return embed.footer.text[7:25]
