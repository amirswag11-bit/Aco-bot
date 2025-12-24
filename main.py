import os
import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

TICKET_CATEGORY_NAME = "Order Tickets"

# ---------- MODAL ----------
class OrderModal(discord.ui.Modal, title="Food Order Information"):

    name = discord.ui.TextInput(label="Your name (Driver contact)")
    phone = discord.ui.TextInput(label="Phone number (Driver contact)")
    restaurant = discord.ui.TextInput(label="Restaurant name (Grubhub only)")
    address = discord.ui.TextInput(
        label="Full delivery address",
        style=discord.TextStyle.paragraph
    )
    subtotal = discord.ui.TextInput(
        label="Order subtotal",
        placeholder="Example: 23 or 23.00"
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild

        category = discord.utils.get(guild.categories, name=TICKET_CATEGORY_NAME)
        if not category:
            category = await guild.create_category(TICKET_CATEGORY_NAME)

        channel = await guild.create_text_channel(
            name=f"order-{interaction.user.name}".lower(),
            category=category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True),
                guild.me: discord.PermissionOverwrite(view_channel=True)
            }
        )

        embed = discord.Embed(title="📦 New Order Ticket", color=discord.Color.green())
        embed.add_field(name="Name", value=self.name.value, inline=False)
        embed.add_field(name="Phone Number", value=self.phone.value, inline=False)
        embed.add_field(name="Restaurant", value=self.restaurant.value, inline=False)
        embed.add_field(name="Delivery Address", value=self.address.value, inline=False)
        embed.add_field(name="Order Subtotal", value=f"${self.subtotal.value}", inline=False)
        embed.set_footer(text=f"User ID: {interaction.user.id}")

        await channel.send(
            content=f"{interaction.user.mention}\nPlease upload **image(s) of your cart)** ⬇️",
            embed=embed
        )

        await interaction.response.send_message(
            f"✅ Ticket created: {channel.mention}",
            ephemeral=True
        )

# ---------- BUTTON ----------
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Create Order Ticket",
        style=discord.ButtonStyle.green,
        custom_id="create_order_ticket"
    )
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(OrderModal())

# ---------- /ADD ----------
@bot.tree.command(name="add", description="Send the order ticket button")
@app_commands.checks.has_permissions(administrator=True)
async def add(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🍔 Create an Order Ticket",
        description="Click the button below to start your order.",
        color=discord.Color.blue()
    )
    await interaction.channel.send(embed=embed, view=TicketView())
    await interaction.response.send_message("✅ Ticket panel sent.", ephemeral=True)

# ---------- /CLOSE ----------
@bot.tree.command(name="close", description="Close this ticket and save transcript")
@app_commands.checks.has_permissions(administrator=True)
async def close(interaction: discord.Interaction):

    channel = interaction.channel

    if not channel.category or channel.category.name != TICKET_CATEGORY_NAME:
        await interaction.response.send_message(
            "❌ This command can only be used in ticket channels.",
            ephemeral=True
        )
        return

    await interaction.response.send_message("📄 Saving transcript and closing ticket...")

    messages = []
    async for msg in channel.history(limit=None, oldest_first=True):
        timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M")
        content = msg.content if msg.content else ""
        attachments = " ".join(a.url for a in msg.attachments)

        messages.append(
            f"[{timestamp}] {msg.author}: {content} {attachments}"
        )

    transcript_text = "\n".join(messages)
    filename = f"transcript-{channel.name}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(transcript_text)

    await channel.send(
        content="✅ Ticket closed. Transcript saved below.",
        file=discord.File(filename)
    )

    os.remove(filename)
    await channel.delete()

# ---------- READY ----------
@bot.event
async def on_ready():
    bot.add_view(TicketView())
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")

# ---------- RUN ----------
bot.run(os.getenv("DISCORD_TOKEN"))
