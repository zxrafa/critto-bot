# 🛠️ Critto Studios - Bot de Cargos (Discloud Free)

Bot de Discord com painel interativo de seleção de cargos para estúdio de desenvolvimento Roblox / Game Dev.

---

## 🚀 Como Fazer Deploy na Discloud (Passo a Passo)

1. Baixe o arquivo **`critto-roles-bot.zip`** gerado na raiz do projeto.
2. Acesse o painel da Discloud: [https://discloud.app](https://discloud.app)
3. Vá na aba **Add App / Adicionar Aplicativo**.
4. Arraste e solte o arquivo **`critto-roles-bot.zip`** diretamente no painel.
5. Clique em **Commit / Upload**.
6. A Discloud instalará automaticamente o Python e as dependências (`requirements.txt`).
7. Pronto! O bot ficará **Online** em alguns segundos.

---

## 🎮 Como Usar no Servidor Discord

1. Certifique-se de que o bot foi convidado com as permissões:
   - `Gerenciar Cargos` (Manage Roles)
   - `Enviar Mensagens` (Send Messages)
   - `Ver Canais` (View Channels)
   - `Usar Comandos de Barra` (Use Application Commands)
2. **IMPORTANTE (Hierarquia de Cargos):**
   - No Discord, vá em: `Configurações do Servidor` ➔ `Cargos`.
   - Arraste o cargo do **Bot** para **CIMA** de todos os cargos de desenvolvimento (`Script`, `Builder`, `Concept Artist`, etc.). O Discord não permite que um bot dê cargos que estejam acima dele.
3. No canal desejado (ex: `#cargos` ou `#boas-vindas`), digite:
   - `/cargos` ou `!cargos`
4. O bot enviará o painel com o menu suspenso.
5. Quando um membro escolher sua função, o bot atribuirá o cargo instantaneamente (e criará o cargo com a cor configurada caso ele ainda não exista no servidor!).
