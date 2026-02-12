from highrise import BaseBot, User, ResponseError
from highrise.models import Emote
import os

VIP_USERS = set()
MUSIC_QUEUE = []

# FREE emotes = safe to use on others
FREE_EMOTES = {
    "!wave": Emote.emote_wave,
    "!punch": Emote.emote_punch,
    "!laidback": Emote.emote_laidback,
    "!smooch": Emote.emote_kiss,
}

# PAID emotes = self only
PAID_EMOTES = {
    "!dance": Emote.emote_dance,
    "!worm": Emote.emote_worm,
}

class HighriseRoomBot(BaseBot):

    async def on_start(self, session):
        print("✅ BOT CONNECTED SUCCESSFULLY")

    async def safe_emote(self, emote, target_id=None):
        try:
            if target_id:
                await self.highrise.send_emote(emote, target_id)
            else:
                await self.highrise.send_emote(emote)
        except ResponseError:
            await self.highrise.send_channel(
                "❌ That emote can’t be used on that user."
            )

    async def on_chat(self, user: User, message: str):
        msg = message.lower().strip()
        parts = message.split()

        # ---------------- HELP ----------------
        if msg == "!help":
            await self.highrise.send_channel(
                "🆘 Commands:\n"
                "Free: !wave !punch !laidback !smooch\n"
                "VIP: !play <song> | !queue\n"
                "Mods: !addvip @user | !removevip @user"
            )
            return

        # ----------- FREE EMOTES (ALL USERS) -----------
        if parts[0] in FREE_EMOTES:
            emote = FREE_EMOTES[parts[0]]

            # Target another user
            if len(parts) > 1 and parts[1].startswith("@"):
                if user.id not in VIP_USERS:
                    await self.highrise.send_channel(
                        "❌ Only VIPs / mods can target others."
                    )
                    return

                target_name = parts[1][1:].lower()
                users = await self.highrise.get_room_users()

                for u in users.content:
                    if u.username.lower() == target_name:
                        await self.safe_emote(emote, u.id)
                        return

                await self.highrise.send_channel("❌ User not found.")
                return

            # Self emote
            await self.safe_emote(emote, user.id)
            return

        # ----------- PAID EMOTES (SELF ONLY) -----------
        if parts[0] in PAID_EMOTES:
            await self.safe_emote(PAID_EMOTES[parts[0]], user.id)
            return

        # ---------------- MUSIC ----------------
        if msg.startswith("!play "):
            if user.id not in VIP_USERS:
                await self.highrise.send_channel(
                    "🎵 Music requests are VIP-only."
                )
                return

            song = message[6:].strip()
            MUSIC_QUEUE.append((user.username, song))
            await self.highrise.send_channel(
                f"🎶 Added to queue: {song}"
            )
            return

        if msg == "!queue":
            if not MUSIC_QUEUE:
                await self.highrise.send_channel("📭 Queue empty.")
                return

            text = "🎵 Music Queue:\n"
            for i, (name, song) in enumerate(MUSIC_QUEUE, 1):
                text += f"{i}. {song} — {name}\n"

            await self.highrise.send_channel(text)
            return

        # ----------- VIP MANAGEMENT (MOD / OWNER) -----------
        if msg.startswith("!addvip ") or msg.startswith("!removevip "):
            users = await self.highrise.get_room_users()

            # Only mods / owner
            room_user = next((u for u in users.content if u.id == user.id), None)
            if not room_user or not room_user.is_moderator:
                return

            target_name = parts[1][1:].lower()

            for u in users.content:
                if u.username.lower() == target_name:
                    if msg.startswith("!addvip"):
                        VIP_USERS.add(u.id)
                        await self.highrise.send_channel(
                            f"⭐ {u.username} is now VIP!"
                        )
                    else:
                        VIP_USERS.discard(u.id)
                        await self.highrise.send_channel(
                            f"❌ {u.username} removed from VIP."
                        )
                    return
