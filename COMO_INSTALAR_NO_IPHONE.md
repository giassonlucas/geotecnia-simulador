# Instalar o Geotecnia no iPhone

Este projeto preserva a aplicação web atual e prepara um contêiner iOS com Capacitor, que incorpora os arquivos da pasta `static`. O motor `static/calculation.js` executa as simulações localmente; os gráficos, mapas e memória de cálculo reutilizam o mesmo objeto `result`. A rota Python `/api/simulate` permanece disponível como referência de backend, mas não é necessária ao botão **Executar simulação**.

## Situação e requisitos

O identificador configurado é `br.com.geotecnia.simuladortensoes`, o nome mostrado é **Geotecnia**, versão inicial **1.0.0**, build inicial **1**. O identificador é sintaticamente adequado, mas só pode ser confirmado como disponível ao registrá-lo na conta Apple Developer. Não há Mac/Xcode, assinatura ou conta Apple neste ambiente; portanto, ainda não há `.ipa`, upload, build de TestFlight nem publicação.

Capacitor 8 foi escolhido para reutilizar a aplicação existente sem reescrever seu motor. Para compilar iOS será necessário macOS e Xcode. iPhone 14 com iOS 18.3.2 é o alvo de validação deste projeto; a compatibilidade visual e de execução ainda precisa ser confirmada no simulador e em um aparelho depois do primeiro build assinado. A documentação atual do Capacitor lista Node.js 22+ e Xcode como requisitos para desenvolvimento iOS. [Requisitos oficiais do Capacitor](https://capacitorjs.com/docs/getting-started/environment-setup)

## 1. Gerar o projeto iOS

No Windows, os testes do motor web podem ser executados com Node 22+; o build e a geração/assinatura do contêiner iOS devem ser feitos em macOS com Xcode. O conteúdo web local é `static/`; a configuração não define uma URL de servidor. Assim, os cálculos continuam disponíveis sem internet depois de instalar o aplicativo. Os ícones e splash vêm dos arquivos em `assets/`; o script `ios:prepare` gera os recursos iOS e atualiza a cópia dos arquivos web.

No Mac com Xcode instalado:

```bash
npm install
npm run ios:add        # somente na primeira vez
npm run ios:prepare
npm run ios:open
```

Para validar os cálculos no Windows, use `npm run test:web` e `python -m unittest discover -s tests -v`; isso não substitui o build iOS.

No Xcode, selecione o target **App**, confirme o display name **Geotecnia**, o bundle ID `br.com.geotecnia.simuladortensoes`, o time de assinatura e uma versão/build. Escolha um simulador iPhone 14 com iOS 18.3.2, ou conecte o iPhone e selecione-o como destino. Faça primeiro um build Development e valide simulação, gráfico, mapa, memória, orientação retrato/paisagem e exportações.

## 2. Conta e assinatura Apple

1. Entre em [Apple Developer](https://developer.apple.com/programs/) e conclua a adesão ao Apple Developer Program.
2. Em **Certificates, Identifiers & Profiles**, registre o Bundle ID `br.com.geotecnia.simuladortensoes`. Se já estiver ocupado, escolha outro identificador único e altere `capacitor.config.json`, `COMO_INSTALAR_NO_IPHONE.md` e o workflow antes de gerar o build.
3. Crie um certificado **Apple Distribution** e um provisioning profile **App Store Connect** para esse App ID. Guarde o `.p12`, a senha e o `.mobileprovision` com segurança.
4. Crie o app record em [App Store Connect](https://appstoreconnect.apple.com/), com nome **Geotecnia**, plataforma iOS, Bundle ID registrado, SKU próprio (por exemplo `geotecnia-simulador-tensoes`) e versão `1.0.0`.
5. Configure a ficha: descrição, categoria adequada (sugestão: Educação ou Utilidades), classificação etária, política de privacidade conforme o comportamento final, ícone, capturas de tela de iPhone e informação de criptografia/export compliance. A disponibilidade do título e do bundle é decidida pela Apple.

Para TestFlight externo, preencha também os detalhes de teste e envie a build para revisão beta quando o App Store Connect solicitar. A Apple processa o binário enviado antes de exibi-lo na aba TestFlight. [Carregar builds](https://developer.apple.com/help/app-store-connect/manage-builds/upload-builds/) · [Visão geral do TestFlight](https://developer.apple.com/help/app-store-connect/test-a-beta-version/testflight-overview/)

## 3. Gerar e enviar um build

### Pelo Xcode no Mac

No Xcode: **Product → Archive**; na janela Organizer, valide o archive e escolha **Distribute App → App Store Connect → Upload**. A assinatura deve usar o certificado/profile criados acima. O build aparece em App Store Connect após o processamento da Apple.

### Pelo GitHub Actions, sem comprar um Mac

O workflow manual `.github/workflows/ios-testflight.yml` usa um runner macOS hospedado pelo GitHub. Ele roda os testes do motor Python, gera o projeto iOS Capacitor, assina, arquiva e envia a build para App Store Connect. O repositório precisa estar no GitHub e o workflow exige estes GitHub Actions Secrets:

- `APPLE_TEAM_ID`: Team ID da conta Apple Developer.
- `APPLE_CERTIFICATE_BASE64`: certificado `.p12` codificado em Base64.
- `APPLE_CERTIFICATE_PASSWORD`: senha do `.p12`.
- `APPLE_PROVISIONING_PROFILE_BASE64`: profile App Store Connect codificado em Base64.
- `APP_STORE_CONNECT_API_KEY_ID`, `APP_STORE_CONNECT_ISSUER_ID`, `APP_STORE_CONNECT_API_PRIVATE_KEY`: chave de API com permissão de upload ao App Store Connect.

Codifique o certificado/profile em Base64 na máquina local (sem enviá-los ao chat): no PowerShell use `[Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\caminho\arquivo.p12"))` e repita para o `.mobileprovision`; cole os conteúdos nos respectivos secrets. Crie a chave API em App Store Connect → Users and Access → Integrations, salve o `.p8` e o Issuer ID, e proteja a chave privada. Configure os secrets apenas no repositório privado/ambiente protegido. Depois de testar o build e confirmar bundle ID, execute **Actions → Build iOS and upload to TestFlight → Run workflow**. Esse workflow só envia após execução manual. Os runners macOS e Xcode variam; este workflow seleciona `macos-26`, atualmente publicado como runner hospedado padrão. Repositórios privados podem consumir minutos faturáveis; confira os limites da conta GitHub. [Runners hospedados pelo GitHub](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)

O Xcode Cloud é outra opção hospedada pela Apple e se integra ao App Store Connect, mas exige membership no Apple Developer Program e a conexão do repositório. [Configurar Xcode Cloud](https://developer.apple.com/documentation/xcode/setting-up-your-project-to-use-xcode-cloud)

## 4. Instalar pelo TestFlight

1. Depois do processamento, abra a aba **TestFlight** no App Store Connect e adicione testadores internos ou crie um grupo externo.
2. Para teste interno, convide o Apple Account do testador. Para distribuição externa, preencha os dados beta e submeta a build à revisão beta se solicitada.
3. No iPhone 14, instale **TestFlight** pela App Store, abra o convite recebido e toque **Instalar** em **Geotecnia**.
4. Abra o app em modo avião e execute uma simulação completa. PDF usa o endpoint Python `/api/report` e precisa de servidor/rede nesta versão; CSV, JSON, gráfico PNG e motor de cálculo permanecem locais. Se o menu de compartilhamento Web Share não estiver disponível no WKWebView, os botões usam download como fallback.

## 5. Salvar, exportar e atualizar

**Salvar no aparelho** grava os cinco casos mais recentes (entradas, resultado integral e data) no armazenamento local do navegador/WebView. O salvamento não sincroniza com o notebook nem é incluído automaticamente em backup. Exporte o JSON para manter cópia.

CSV, JSON e PNG compartilham pelo menu do sistema quando `navigator.share` aceita arquivos; caso contrário, oferecem download. O PDF continua usando a API Python e requer o servidor.

Para atualizar: incremente `version` no `package.json` e `MARKETING_VERSION` no Xcode/workflow; cada envio precisa de um `CURRENT_PROJECT_VERSION`/build number maior. Rode `npm run ios:prepare`, valide a nova versão e envie outro build pelo Xcode ou pelo workflow. A equipe/TestFlight pode então disponibilizar o update aos testadores.

## Limites da validação neste ambiente

A versão web existente continua na pasta `static/`, com backend Python e testes independentes em `tests/`. A simulação do formulário e gráficos usam o motor local `calculation.js`, então `Failed to fetch` não bloqueia o cálculo. Não foi possível produzir nem executar o binário iOS aqui: o ambiente atual não inclui macOS, Xcode, conta Apple, certificados, provisioning profile ou segredos do App Store Connect. O identificador ainda precisa ser registrado/confirmado. O build e a revisão final de layout/teclado devem ser feitos no simulador Xcode e no iPhone real antes do TestFlight.
