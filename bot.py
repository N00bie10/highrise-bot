import asyncio
from highrise import BaseBot, User
from highrise.models.emotes import EmoteId

# ------------------------
# CONFIG
# ------------------------
VIP_USERS = set()        # user IDs with VIP privileges
MUSIC_QUEUE = []         # (username, song) queue

# Basic emotes everyone can use
BASIC_EMOTES = {
    "wave": EmoteId.Wave,
    "punch": EmoteId.Punch,
    "smooch": EmoteId.Smooch,
    "worm": EmoteId.Worm,
    "laidback": EmoteId.Laidback,
}

# Advanced emotes (VIPs/mods/owner)
ADVANCED_EMOTES = {
    "dance": EmoteId.Dance,
    "celebrate": EmoteId.Celebrate,
}

# ------------------------
# HELPER FUNCTIONS
# ------------------------
def can_control(user: User):
    """Check if user can run VIP/advanced commands"""
    # Owner or mod or VIP
    return getattr(user, "is_mod", False) or getattr(user, "is_owner", False) or user.id in VIP_USERS

def parse_target_username(message: str):
    """Extract @username from command if present"""
    parts = message.split(" ", 1)
    if len(parts) < 2:
        return None
    target = parts[1].strip()
    if target.startswith("@"):
        return target[1:]
    return None

# ------------------------
# BOT CLASS
# ------------------------
class HighriseRoomBot(BaseBot):

    async def on_ready(self):
        print("✅ BOT CONNECTED SUCCESSFULLY")

    async def on_chat(self, user: User, message: str):
        msg = message.lower().strip()

        # ------------------------
        # HELP COMMAND
        # ------------------------
        if msg == "!help":
            help_text = (
                "🎮 Commands:\n"
                "Basic emotes: " + ", ".join(BASIC_EMOTES.keys()) + "\n"
                "Advanced emotes (VIP/mods/owner): " + ", ".join(ADVANCED_EMOTES.keys()) + "\n"
                "Music: !play <song> (VIP only)\n"
                "Queue: !queue\n"
                "Give emote to another: !<emote> @username (VIP/mods/owner)"
            )
            await self.highrise.send_channel(help_text)
            return

        # ------------------------
        # EMOTE COMMANDS
        # ------------------------
        if msg.startswith("!"):
            cmd = msg[1:].split(" ")[0]

            # Check if targeting another user
            target_name = parse_target_username(msg)
            target_id = None

            if target_name:
                room_users = await self.highrise.get_room_users()
                for u in room_users.content:
                    if u.username.lower() == target_name.lower():
                        target_id = u.id
                        break
                if not target_id:
                    await self.highrise.send_channel(f"❌ User @{target_name} not found.")
                    return

            # ------------------------
            # BASIC EMOTES
            # ------------------------
            if cmd in BASIC_EMOTES:
                try:
                    if target_id and can_control(user):
                        await self.highrise.send_emote(BASIC_EMOTES[cmd], target_id)
                    else:
                        await self.highrise.send_emote(BASIC_EMOTES[cmd], user.id)
                except Exception as e:
                    await self.highrise.send_channel(f"❌ Error: {e}")
                return

            # ------------------------
            # ADVANCED EMOTES
            # ------------------------
            if cmd in ADVANCED_EMOTES:
                if not can_control(user):
                    await self.highrise.send_channel(f"❌ {user.username}, only VIPs/mods/owner can use this.")
                    return
                try:
                    if target_id:
                        await self.highrise.send_emote(ADVANCED_EMOTES[cmd], target_id)
                    else:
                        await self.highrise.send_emote(ADVANCED_EMOTES[cmd], user.id)
                except Exception as e:
                    await self.highrise.send_channel(f"❌ Error: {e}")
                return

            # ------------------------
            # MUSIC COMMANDS (VIP only)
            # ------------------------
            if cmd == "play":
                if not can_control(user):
                    await self.highrise.send_channel(f"🎵 Music requests are for VIPs/mods/owner only.")
                    return
                song = msg[6:].strip()
                if song:
                    MUSIC_QUEUE.append((user.username, song))
                    await self.highrise.send_channel(f"🎶 Added to queue: {song} (requested by {user.username})")
                return

            if cmd == "queue":
                if not MUSIC_QUEUE:
                    await self.highrise.send_channel("📭 Music queue is empty.")
                    return
                queue_text = "🎵 Music Queue:\n" + "\n".join(
                    f"{i+1}. {s} — {u}" for i, (u, s) in enumerate(MUSIC_QUEUE)
                )
                await self.highrise.send_channel(queue_text)
                return

            # ------------------------
            # VIP MANAGEMENT (Owner only)
            # ------------------------
            if cmd == "addvip":
                if not getattr(user, "is_owner", False):
                    return
                target_name = msg.split(" ", 1)[1]
                room_users = await self.highrise.get_room_users()
                for u in room_users.content:
                    if u.username.lower() == target_name.lower():
                        VIP_USERS.add(u.id)
                        await self.highrise.send_channel(f"⭐ {u.username} is now a VIP!")
                        return

            if cmd == "removevip":
                if not getattr(user, "is_owner", False):
                    return
                target_name = msg.split(" ", 1)[1]
                room_users = await self.highrise.get_room_users()
                for u in room_users.content:
                    if u.username.lower() == target_name.lower():
                        VIP_USERS.discard(u.id)
                        await self.highrise.send_channel(f"❌ {u.username} is no longer a VIP.")
                        return

# ------------------------
# START BOT
# ------------------------
import os
BOT_TOKEN = os.getenv("API_TOKEN")
ROOM_ID = os.getenv("ROOM_ID")

bot = HighriseRoomBot()
asyncio.run(bot.run(BOT_TOKEN, room=ROOM_ID))
