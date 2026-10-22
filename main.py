import os
import sys
import logging
import datetime
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = os.getenv("PREFIX", "!")

if not TOKEN:
    print("[ERRO] DISCORD_TOKEN não encontrado no arquivo .env!")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("CrittoRolesBot")

# Configuração do Cargo Automático de Entrada (Membro - Servidor Aberto a Todos)
MEMBER_ROLE_CFG = {
    "name": "👤・Membro",
    "aliases": ["Membro", "Member", "👤・Membro"],
    "color": discord.Color.from_rgb(113, 113, 122)
}

# IDs dos canais oficiais da Fábrica de Criaturas
CHANNELS = {
    "welcome": 1561693233988370493,      # 👋・boas-vindas
    "rules": 1556292191750586461,        # 📜・regras
    "announcements": 1560610569625534576,# 📢・avisos
    "faq": 1560622890984939611,          # ❓・faq-lancamento
    "notifications": 1560619508920746097,# 🔔・notificacoes
    "spoilers": 1560620877945643040,     # 👀・spoilers
    "suggestions": 1560620708676108318,  # 💡・sugestoes
    "chat": 1560620520293138533,         # 💬・chat-geral
    "media": 1560620550663970958         # 📸・midia
}

# Definição dos Cargos de Notificação para o Menu Interativo
ROLES_CONFIG = [
    {
        "name": "🔔・Avisos de Lançamento",
        "aliases": ["Avisos de Lançamento", "Lancamento", "Avisos"],
        "label": "Avisos de Lançamento",
        "description": "Receba ping no minuto exato em que o jogo abrir no Roblox",
        "emoji": "🔔",
        "color": discord.Color.from_rgb(46, 204, 113)
    },
    {
        "name": "👀・Spoilers & Teasers",
        "aliases": ["Spoilers & Teasers", "Spoilers", "Teasers"],
        "label": "Spoilers & Teasers",
        "description": "Notificações em primeira mão de novas criaturas, fotos e vídeos",
        "emoji": "👀",
        "color": discord.Color.from_rgb(52, 152, 219)
    },
    {
        "name": "🎁・Códigos & Eventos",
        "aliases": ["Códigos & Eventos", "Codigos", "Eventos"],
        "label": "Códigos & Eventos",
        "description": "Avisos de novos códigos promocionais de lançamento e eventos",
        "emoji": "🎁",
        "color": discord.Color.from_rgb(233, 30, 99)
    },
    {
        "name": "📱・Mobile",
        "aliases": ["Mobile", "Celular"],
        "label": "Jogador Mobile / Celular",
        "description": "Dispositivo principal: Celular / Tablet",
        "emoji": "📱",
        "color": discord.Color.from_rgb(149, 165, 166)
    },
    {
        "name": "💻・PC",
        "aliases": ["PC", "Computador"],
        "label": "Jogador PC",
        "description": "Dispositivo principal: Computador / Teclado e Mouse",
        "emoji": "💻",
        "color": discord.Color.from_rgb(149, 165, 166)
    }
]

def find_guild_role(guild: discord.Guild, role_cfg: dict) -> discord.Role | None:
    """Busca o cargo no servidor pelo nome exato, aliases ou substring inteligente."""
    role = discord.utils.get(guild.roles, name=role_cfg["name"])
    if role:
        return role

    for alias in role_cfg.get("aliases", []):
        role = discord.utils.get(guild.roles, name=alias)
        if role:
            return role

    for r in guild.roles:
        r_name_clean = r.name.lower()
        if role_cfg["name"].lower() in r_name_clean:
            return r
        for alias in role_cfg.get("aliases", []):
            if alias.lower() in r_name_clean:
                return r

    return None

class PlayerRoleSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label=cfg["label"][:100],
                value=cfg["name"][:100],
                description=cfg["description"][:100],
                emoji=cfg["emoji"]
            )
            for cfg in ROLES_CONFIG
        ]
        super().__init__(
            placeholder="Escolha suas notificações e plataforma...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="critto_player_role_select_menu"
        )

    async def callback(self, interaction: discord.Interaction):
        if not interaction.guild or not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message("Este comando só pode ser utilizado em um servidor.", ephemeral=True)
            return

        chosen_role_name = self.values[0]
        role_cfg = next((r for r in ROLES_CONFIG if r["name"] == chosen_role_name), None)

        if not role_cfg:
            await interaction.response.send_message("Cargo não encontrado na configuração.", ephemeral=True)
            return

        guild = interaction.guild
        bot_member = guild.me
        if not bot_member.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "⚠️ **Erro de Permissão:** O bot precisa da permissão `Gerenciar Cargos` no servidor para poder atribuir cargos.",
                ephemeral=True
            )
            return

        await interaction.response.defer(ephemeral=True)

        target_role = find_guild_role(guild, role_cfg)
        if not target_role:
            try:
                target_role = await guild.create_role(
                    name=role_cfg["name"],
                    color=role_cfg["color"],
                    reason="Criação automática pelo Painel de Cargos Fábrica de Criaturas"
                )
                logger.info(f"Cargo '{role_cfg['name']}' criado automaticamente no servidor {guild.name}.")
            except discord.Forbidden:
                await interaction.followup.send(
                    "❌ Falha ao criar o cargo automaticamente. Meu cargo deve ter permissões de gerenciar cargos.",
                    ephemeral=True
                )
                return

        if target_role >= bot_member.top_role:
            await interaction.followup.send(
                f"⚠️ O cargo **@{target_role.name}** está acima ou no mesmo nível que o meu cargo mais alto. Mova o meu cargo para o topo na lista de cargos do servidor!",
                ephemeral=True
            )
            return

        member = interaction.user
        if target_role in member.roles:
            try:
                await member.remove_roles(target_role, reason="Remoção via Painel de Cargos")
                embed = discord.Embed(
                    title="Cargo Removido",
                    description=f"{role_cfg['emoji']} Você não receberá mais a notificação de **@{target_role.name}**.",
                    color=discord.Color.from_rgb(239, 68, 68)
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"Erro ao remover cargo: `{e}`", ephemeral=True)
        else:
            try:
                await member.add_roles(target_role, reason="Atribuição via Painel de Cargos")
                embed = discord.Embed(
                    title="Cargo Atribuído com Sucesso!",
                    description=f"{role_cfg['emoji']} Você agora possui **@{target_role.name}**!\n\n> *Benefício:* {role_cfg['description']}",
                    color=discord.Color.from_rgb(46, 204, 113)
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"Erro ao adicionar cargo: `{e}`", ephemeral=True)

class PlayerRolesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PlayerRoleSelect())

def create_panel_embed():
    embed = discord.Embed(
        title="🧪 FÁBRICA DE CRIATURAS // NOTIFICAÇÕES & PREFERÊNCIAS",
        description=(
            "Personalize seus alertas e preferências para o grande lançamento!\n"
            "Selecione as opções desejadas no menu suspenso abaixo.\n\n"
            "💡 *Dica: Se já tiver o cargo e selecioná-lo novamente, ele será removido (toggle).* "
        ),
        color=discord.Color.from_rgb(46, 204, 113)
    )

    for cfg in ROLES_CONFIG:
        embed.add_field(
            name=f"{cfg['emoji']} {cfg['label']}",
            value=f"└ {cfg['description']}",
            inline=False
        )

    embed.set_footer(text="Fábrica de Criaturas • Roblox Experience • Sistema de Notificações")
    return embed

def create_welcome_embed(member: discord.Member, member_count: int, guild_icon_url: str | None = None) -> discord.Embed:
    """Gera o embed estilizado de boas-vindas com múltiplos fields e design moderno."""
    embed = discord.Embed(
        title="🎉 Seja bem-vindo(a) à Fábrica de Criaturas!",
        description=(
            f"Olá {member.mention}, prepare-se para explorar biomas insulares, colher elementos puros e chocar criaturas lendárias no Roblox!\n\n"
            f"Você recebeu automaticamente o cargo **`👤・Membro`**."
        ),
        color=discord.Color.from_rgb(46, 204, 113),
        timestamp=datetime.datetime.now(datetime.timezone.utc)
    )

    embed.set_author(
        name=f"{member.display_name} entrou na ilha!",
        icon_url=member.display_avatar.url
    )
    embed.set_thumbnail(url=member.display_avatar.url)

    embed.add_field(
        name="🧭 Primeiros Passos",
        value=(
            f"> • Fique por dentro em <#{CHANNELS['announcements']}>\n"
            f"> • Leia as diretrizes em <#{CHANNELS['rules']}>\n"
            f"> • Tire suas dúvidas em <#{CHANNELS['faq']}>"
        ),
        inline=False
    )

    embed.add_field(
        name="🔥 Pré-Lançamento",
        value=(
            f"> • Veja novidades em <#{CHANNELS['spoilers']}>\n"
            f"> • Escolha seus alertas em <#{CHANNELS['notifications']}>\n"
            f"> • Envie sugestões em <#{CHANNELS['suggestions']}>"
        ),
        inline=True
    )

    embed.add_field(
        name="💬 Comunidade",
        value=(
            f"> • Converse em <#{CHANNELS['chat']}>\n"
            f"> • Mande prints e memes em <#{CHANNELS['media']}>\n"
            f"> • Entre em call na categoria de voz!"
        ),
        inline=True
    )

    embed.add_field(
        name="👥 Membro Oficial",
        value=f"Você é o treinador **#{member_count}** a desembarcar na ilha!",
        inline=False
    )

    footer_text = "Fábrica de Criaturas • Experiência Roblox Oficial"
    if guild_icon_url:
        embed.set_footer(text=footer_text, icon_url=guild_icon_url)
    else:
        embed.set_footer(text=footer_text)

    return embed

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    logger.info(f"Bot conectado como {bot.user} (ID: {bot.user.id})")
    bot.add_view(PlayerRolesView())
    try:
        synced = await bot.tree.sync()
        logger.info(f"Comandos Slash sincronizados: {len(synced)}")
    except Exception as e:
        logger.error(f"Erro ao sincronizar comandos slash: {e}")

@bot.event
async def on_member_join(member: discord.Member):
    """Atribui automaticamente o cargo Membro e envia embed individual de boas-vindas."""
    guild = member.guild
    bot_member = guild.me

    # 1. Atribuir cargo Membro automaticamente (Servidor liberado para todos)
    if bot_member.guild_permissions.manage_roles:
        member_role = find_guild_role(guild, MEMBER_ROLE_CFG)
        if not member_role:
            try:
                member_role = await guild.create_role(
                    name=MEMBER_ROLE_CFG["name"],
                    color=MEMBER_ROLE_CFG["color"],
                    reason="Criação automática do cargo Membro"
                )
            except Exception as e:
                logger.error(f"Erro ao criar cargo Membro: {e}")

        if member_role and member_role < bot_member.top_role:
            try:
                await member.add_roles(member_role, reason="Auto-cargo de entrada (Membro)")
                logger.info(f"Cargo Membro atribuído para {member}.")
            except Exception as e:
                logger.error(f"Erro ao atribuir cargo Membro para {member}: {e}")

    # 2. Enviar mensagem de boas-vindas individual com fields
    welcome_ch = guild.get_channel(CHANNELS["welcome"])
    if not welcome_ch:
        welcome_ch = discord.utils.get(guild.text_channels, name="👋・boas-vindas") or discord.utils.get(guild.text_channels, name="boas-vindas")

    if welcome_ch and welcome_ch.permissions_for(bot_member).send_messages:
        icon_url = guild.icon.url if guild.icon else None
        embed = create_welcome_embed(member, guild.member_count, icon_url)
        try:
            await welcome_ch.send(content=f"👋 {member.mention}", embed=embed)
        except Exception as e:
            logger.error(f"Erro ao enviar embed de boas-vindas: {e}")

@bot.command(name="cargos", aliases=["painel", "roles", "notificacoes"])
@commands.has_permissions(manage_roles=True)
async def send_roles_panel(ctx: commands.Context):
    """Envia o painel de seleção de cargos no canal atual."""
    embed = create_panel_embed()
    view = PlayerRolesView()
    await ctx.send(embed=embed, view=view)
    try:
        await ctx.message.delete()
    except Exception:
        pass

@bot.tree.command(name="cargos", description="Envia o painel interativo de notificações e preferências da Fábrica.")
@discord.app_commands.default_permissions(manage_roles=True)
async def slash_send_roles_panel(interaction: discord.Interaction):
    """Envia o painel interativo de cargos via Slash Command."""
    embed = create_panel_embed()
    view = PlayerRolesView()
    await interaction.response.send_message(embed=embed, view=view)

@bot.command(name="testar-boas-vindas")
@commands.has_permissions(manage_guild=True)
async def test_welcome_cmd(ctx: commands.Context):
    """Testa o envio da mensagem de boas-vindas com o usuário atual."""
    icon_url = ctx.guild.icon.url if ctx.guild.icon else None
    embed = create_welcome_embed(ctx.author, ctx.guild.member_count, icon_url)
    await ctx.send(content=f"👋 {ctx.author.mention}", embed=embed)

@send_roles_panel.error
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Você precisa da permissão de `Gerenciar Cargos` para usar este comando.", delete_after=5)
    else:
        logger.error(f"Erro no comando: {error}")

if __name__ == "__main__":
    bot.run(TOKEN)
