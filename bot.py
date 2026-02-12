from highrise import BaseBot, User
import re

# -------------------------
# STORAGE
# -------------------------
VIP_USERS = set()
MUSIC_QUEUE = []

# -------------------------
# EMOTES
# -------------------------
BASIC_EMOTES = {
    "wave": "wave",
    "laidback": "laidback",
    "punch": "punch",
    "smooch": "smooch",
}

ADVANCED_EMOTES = {
    "dance": "dance",
    "worm": "worm",
    "dab": "dab",
    "floss": "floss",
    "spin": "spin",
    "celebrate": "celebrate",
}

URL_REGEX = re.compile(r"https?://\S+")

# -------------------------
# PERMISSIONS
# -------------------------
def can_control(user: User):
    return user.role in ("owner", "moderator") or user.id in VIP_USERS


class HighriseRoomBot(BaseBot):

    async def on_ready(self):
        await self.highrise.send_channel(
            "👋 FindABrat.Bot online! Type !help for commands."
        )

    async def on_chat(self, user: User, message: str):
        msg = message.lower().strip()

        # ------------------------
        # HELP
        # ------------------------
        if msg == "!help":
            await self.highrise.send_channel(
                "📜 Commands:\n"
                "Regular: !wave !laidback !punch !smooch\n"
                "VIP+: !dance !dab !worm !spin\n"
                "Target: !emote @username (VIP/mod/owner)\n"
                "Music: !play <song/link> (VIP)\n"
                "!queue\n"
                "Mods: !addvip !removevip !skip !clearqueue"
            )
            return

        # ------------------------
        # TARGETED EMOTES
        # ------------------------
        if msg.startswith("!") and "@" in msg:
            parts = msg.split()
            if len(parts) < 2:
                return

            cmd = parts[0][1:]
            target_name = parts[1][1:]

            if cmd not in BASIC_EMOTES and cmd not in ADVANCED_EMOTES:
                return

            if not can_control(user):
                await self.highrise.send_channel(
                    f"❌ {user.username}, you can't control others."
                )
                return

            room_users = await self.highrise.get_room_users()
            for u in room_users.content:
                if u.username.lower() == target_name.lower():
                    emote = BASIC_EMOTES.get(cmd) or ADVANCED_EMOTES.get(cmd)
                    await self.highrise.send_emote(emote, u.id)
                    await self.highrise.send_channel(
                        f"✨ {u.username} did {cmd}! (by {user.username})"
                    )
                    return
            return

        # ------------------------
        # BASIC SELF EMOTES
        # ------------------------
        if msg.startswith("!"):
            cmd = msg[1:]
            if cmd in BASIC_EMOTES:
                await self.highrise.send_emote(BASIC_EMOTES[cmd], user.id)
                return

        # ------------------------
        # ADVANCED SELF EMOTES
        # ------------------------
        if msg.startswith("!"):
            cmd = msg[1:]
            if cmd in ADVANCED_EMOTES:
                if not can_control(user):
                    await self.highrise.send_channel(
                        f"❌ {user.username}, this emote is restricted."
                    )
                    return
                await self.highrise.send_emote(ADVANCED_EMOTES[cmd], user.id)
                return

        # ------------------------
        # MUSIC REQUEST (VIP)
        # ------------------------
        if msg.startswith("!play "):
            if user.id not in VIP_USERS:
                await self.highrise.send_channel(
                    "🎵 Music requests are VIP-only."
                )
                return

            song = message[6:].strip()
            link = None
            match = URL_REGEX.search(song)
            if match:
                link = match.group()

            MUSIC_QUEUE.append({
                "user": user.username,
                "request": song,
                "link": link
            })

            await self.highrise.send_channel(
                f"🎶 Added to queue:\n{song}\nRequested by {user.username}"
            )
            return

        # ------------------------
        # SHOW QUEUE
        # ------------------------
        if msg == "!queue":
            if not MUSIC_QUEUE:
                await self.highrise.send_channel("📭 Music queue is empty.")
                return

            text = "🎵 Music Queue:\n"
            for i, item in enumerate(MUSIC_QUEUE, start=1):
                text += f"{i}. {item['request']} — {item['user']}\n"

            await self.highrise.send_channel(text)
            return

        # ------------------------
        # MOD COMMANDS
        # ------------------------
        if msg.startswith("!addvip "):
            if user.role not in ("owner", "moderator"):
                return

            target = message.split(" ", 1)[1]
            users = await self.highrise.get_room_users()
            for u in users.content:
                if u.username.lower() == target.lower():
                    VIP_USERS.add(u.id)
                    await self.highrise.send_channel(
                        f"⭐ {u.username} is now VIP! (by {user.username})"
                    )
                    return

        if msg.startswith("!removevip "):
            if user.role not in ("owner", "moderator"):
                return

            target = message.split(" ", 1)[1]
            users = await self.highrise.get_room_users()
            for u in users.content:
                if u.username.lower() == target.lower():
                    VIP_USERS.discard(u.id)
                    await self.highrise.send_channel(
                        f"❌ {u.username} is no longer VIP."
                    )
                    return

        if msg == "!skip":
            if user.role not in ("owner", "moderator"):
                return

            if MUSIC_QUEUE:
                skipped = MUSIC_QUEUE.pop(0)
                await self.highrise.send_channel(
                    f"⏭ Skipped: {skipped['request']}"
                )

        if msg == "!clearqueue":
            if user.role not in ("owner", "moderator"):
                return

            MUSIC_QUEUE.clear()
            await self.highrise.send_channel("🗑 Music queue cleared.")
