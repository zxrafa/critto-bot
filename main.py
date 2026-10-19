import os
import sys
import logging
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

# Configuração do Cargo Automático de Entrada (Guest)
GUEST_ROLE_CFG = {
    "name": "GS ៸៸ GUEST",
    "aliases": ["Guest", "GS", "Visitante", "Membro"],
    "color": discord.Color.from_rgb(63, 63, 70)
}

# Definição dos Cargos de Desenvolvimento para o Menu Interativo
ROLES_CONFIG = [
    {
        "name": "SC ៸៸ SCRIPTER",
        "aliases": ["Script", "Scripter", "SC", "Programador"],
        "label": "Script / Scripter",
        "description": "Programação Luau, backend, lógica, mecânicas e sistemas",
        "emoji": "💻",
        "color": discord.Color.from_rgb(255, 255, 255)
    },
    {
        "name": "BL ៸៸ BUILDER",
        "aliases": ["Builder", "BL", "Construção"],
        "label": "Builder (Mapas & Cenário)",
        "description": "Construção de mapas, level design e arquitetura no Studio",
        "emoji": "🔨",
        "color": discord.Color.from_rgb(228, 227, 231)
    },
    {
        "name": "3D ៸៸ 3D MODELER",
        "aliases": ["3D Modeler", "Modeler 3D", "Modeler", "3D", "Modelador"],
        "label": "3D Modeler (Blender)",
        "description": "Modelagem de criaturas, itens, armas e meshes 3D",
        "emoji": "🗿",
        "color": discord.Color.from_rgb(212, 211, 216)
    },
    {
        "name": "CA ៸៸ CONCEPT ARTIST",
        "aliases": ["Concept Artist", "Concept", "CA", "Arte Conceitual"],
        "label": "Concept Artist (Design Visual)",
        "description": "Design visual, sketches de criaturas, armas e biomas",
        "emoji": "💡",
        "color": discord.Color.from_rgb(161, 161, 170)
    },
    {
        "name": "UI ៸៸ UI DESIGNER",
        "aliases": ["UI Designer", "UI/UX Designer", "UI", "Interface"],
        "label": "UI Designer (Interfaces)",
        "description": "HUDs, menus, telas, botões, ícones e layout visual",
        "emoji": "🎨",
        "color": discord.Color.from_rgb(161, 161, 170)
    },
    {
        "name": "AN ៸៸ ANIMATOR",
        "aliases": ["Animator", "Animador", "AN"],
        "label": "Animator (Rigs & Movimentos)",
        "description": "Animações de combate, idle, caminhada, rigs e emotes",
        "emoji": "🦴",
        "color": discord.Color.from_rgb(161, 161, 170)
    },
    {
        "name": "VF ៸៸ VFX ARTIST",
        "aliases": ["VFX Artist", "VFX", "VF", "Efeitos"],
        "label": "VFX Artist (Efeitos Visuais)",
        "description": "Partículas, magias, luzes, feixes e shaders",
        "emoji": "✨",
        "color": discord.Color.from_rgb(161, 161, 170)
    },
    {
        "name": "SD ៸៸ SOUND DESIGNER",
        "aliases": ["Sound Designer", "SFX & Audio", "SD", "Audio", "Sonoplasta"],
        "label": "Sound Designer (SFX & Áudio)",
        "description": "Efeitos sonoros, trilhas sonoras e atmosfera acústica",
        "emoji": "🎵",
        "color": discord.Color.from_rgb(113, 113, 122)
    },
    {
        "name": "QA ៸៸ QA TESTER",
        "aliases": ["QA Tester", "Tester", "QA", "Playtester"],
        "label": "QA Tester (Playtest)",
        "description": "Testes de estresse, reporte de bugs e balanceamento",
        "emoji": "🧪",
        "color": discord.Color.from_rgb(113, 113, 122)
    },
    {
        "name": "CT ៸៸ CONTRACTOR",
        "aliases": ["Contractor", "CT", "Contratante", "Recrutador"],
        "label": "Contractor (Contratante / Recrutador)",
        "description": "Contratação, recrutamento e busca de desenvolvedores para o estúdio",
        "emoji": "💼",
        "color": discord.Color.from_rgb(82, 82, 91)
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

class StudioRoleSelect(discord.ui.Select):
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
            placeholder="Selecione sua função / especialidade no estúdio...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="critto_studio_role_select_menu"
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
                    reason="Criação automática pelo Painel de Cargos Critto Studios"
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
                    description=f"{role_cfg['emoji']} Você não possui mais a função **@{target_role.name}**.",
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
                    description=f"{role_cfg['emoji']} Você recebeu a função **@{target_role.name}** na equipe!\n\n> *Especialidade:* {role_cfg['description']}",
                    color=discord.Color.from_rgb(0, 229, 255)
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f"Erro ao adicionar cargo: `{e}`", ephemeral=True)

class StudioRolesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(StudioRoleSelect())

def create_panel_embed():
    embed = discord.Embed(
        title="🛠️ CRITTO STUDIOS // SELEÇÃO DE FUNÇÃO & CARGOS",
        description=(
            "Bem-vindo à equipe de desenvolvimento!\n"
            "Escolha no menu abaixo a sua especialidade de atuação no projeto.\n\n"
            "💡 *Dica: Se você já tiver o cargo e selecioná-lo novamente, ele será removido (toggle).*"
        ),
        color=discord.Color.from_rgb(0, 229, 255)
    )

    for cfg in ROLES_CONFIG:
        embed.add_field(
            name=f"{cfg['emoji']} {cfg['label']}",
            value=f"└ {cfg['description']}",
            inline=False
        )

    embed.set_footer(text="Critto Studios • Sistema Autônomo de Cargos • Discloud Free")
    return embed

# Intents necessários para atribuição de roles e evento on_member_join
intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    logger.info(f"Bot conectado como {bot.user} (ID: {bot.user.id})")
    bot.add_view(StudioRolesView())
    try:
        synced = await bot.tree.sync()
        logger.info(f"Comandos Slash sincronizados: {len(synced)}")
    except Exception as e:
        logger.error(f"Erro ao sincronizar comandos slash: {e}")

@bot.event
async def on_member_join(member: discord.Member):
    """Atribui automaticamente o cargo Guest a qualquer novo membro que entrar no servidor."""
    guild = member.guild
    bot_member = guild.me
    if not bot_member.guild_permissions.manage_roles:
        logger.warning(f"Sem permissão de gerenciar cargos para dar Guest em {guild.name}.")
        return

    guest_role = find_guild_role(guild, GUEST_ROLE_CFG)
    if not guest_role:
        try:
            guest_role = await guild.create_role(
                name=GUEST_ROLE_CFG["name"],
                color=GUEST_ROLE_CFG["color"],
                reason="Criação automática do cargo de entrada Guest"
            )
            logger.info(f"Cargo '{GUEST_ROLE_CFG['name']}' criado automaticamente em {guild.name}.")
        except Exception as e:
            logger.error(f"Erro ao criar cargo Guest: {e}")
            return

    if guest_role >= bot_member.top_role:
        logger.warning(f"Cargo Guest (@{guest_role.name}) está acima do bot em {guild.name}.")
        return

    try:
        await member.add_roles(guest_role, reason="Auto-cargo de boas-vindas (Guest)")
        logger.info(f"Cargo Guest atribuído com sucesso para {member} no servidor {guild.name}.")
    except Exception as e:
        logger.error(f"Erro ao atribuir cargo Guest para {member}: {e}")

@bot.command(name="cargos", aliases=["painel", "roles"])
@commands.has_permissions(manage_roles=True)
async def send_roles_panel(ctx: commands.Context):
    """Envia o painel de seleção de cargos no canal atual."""
    embed = create_panel_embed()
    view = StudioRolesView()
    await ctx.send(embed=embed, view=view)
    try:
        await ctx.message.delete()
    except Exception:
        pass

@bot.tree.command(name="cargos", description="Envia o painel interativo de seleção de cargos do estúdio.")
@discord.app_commands.default_permissions(manage_roles=True)
async def slash_send_roles_panel(interaction: discord.Interaction):
    """Envia o painel interativo de cargos via Slash Command."""
    embed = create_panel_embed()
    view = StudioRolesView()
    await interaction.response.send_message(embed=embed, view=view)

@send_roles_panel.error
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Você precisa da permissão de `Gerenciar Cargos` para usar este comando.", delete_after=5)
    else:
        logger.error(f"Erro no comando: {error}")

if __name__ == "__main__":
    try:
        bot.run(TOKEN)
    except discord.errors.PrivilegedIntentsRequired:
        print("\n" + "="*70)
        print("⚠️ [ATENÇÃO] PRIVILEGED INTENTS REQUIRED!")
        print("Para o cargo automático de Guest funcionar ao entrar:")
        print("1. Acesse: https://discord.com/developers/applications")
        print("2. Selecione seu Bot -> Aba 'Bot'")
        print("3. Em 'Privileged Gateway Intents', marque: 'SERVER MEMBERS INTENT'")
        print("4. Clique em 'Save Changes' e inicie o bot!")
        print("="*70 + "\n")
        sys.exit(1)
