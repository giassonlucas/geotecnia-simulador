# Simulador de tensões geotécnicas

Protótipo local para reproduzir o perfil de tensões iniciais e a superposição de acréscimos verticais no plano do grupo. Interface em português, mapas interativos, memória de cálculo e exportação CSV, JSON, PNG e PDF.

## Instalação e execução

Para executar a simulação no navegador, a versão corrigida também pode abrir diretamente `static/index.html`; o motor JavaScript calcula localmente, sem chamadas de rede. Para usar o relatório PDF e/ou o servidor local completo, requer Python 3.10 ou superior. No Windows, instale a dependência PDF e inicie:

```powershell
cd caminho\para\geotecnia-simulador
py -3 -m pip install -r requirements.txt
py -3 app.py
```

Ou execute `run.bat`; o navegador é aberto automaticamente em `http://127.0.0.1:8501`. Esse modo fornece também a rota de relatório PDF. O servidor escuta apenas no computador local. Para encerrar, pressione Ctrl+C na janela do terminal.

## Uso

Os campos começam com os parâmetros lidos das referências e confirmados pelo usuário: plano do grupo −4 m, N.A. −3 m e perfil até −14 m. Revise as entradas, clique **Executar simulação**, e navegue entre Visão geral, Memória de cálculo e Validação. Campos aceitam ponto ou vírgula decimal e precisão arbitrária; mensagens explicam valores fora dos limites do modelo. No mapa, escolha o componente, passe o cursor para consultar valores e use arraste/roda para mover e ampliar. CSV exporta pontos da malha; JSON guarda entradas e resultados; PNG salva os gráficos; PDF requer o servidor local/Render.

## Auditoria das entradas

O navegador antes interpretava `min="0.01" step="0.1"` como grade discreta começando em 0,01. Assim, aceitava 15,31, 15,41 etc. e rejeitava 15,32 ou 15,40. A grade era um acidente do formulário, sem base documental. Agora as entradas são texto numérico com teclado decimal (touch), parser para vírgula/ponto e validação própria; Python também converte vírgula decimal. O passo decimal foi removido. O mínimo 0,01 foi substituído por condição física estrita `> 0` para pesos específicos, cargas, alturas, diâmetro, profundidade e largura do anel.

| Campos | Tipo/limites validados |
|---|---|
| Cota do grupo | real em −14 a −1 m; precisa estar abaixo da base da escavação |
| N.A. | real em −14 a 0 m |
| γ da água, γnat/γsat dos solos | real finito maior que zero; sem máximo arbitrário/documentado |
| Carga Q | real finito maior que zero; sem máximo arbitrário |
| Coordenadas da torre, aterro, escavação | real finito; sem intervalo numérico no material. Podem ficar fora da janela XY, caso em que o ponto/carga pode não aparecer no domínio mostrado |
| Altura e γ do aterro | real maior que zero |
| x inicial/final do aterro | reais; x final > x inicial |
| Diâmetro, profundidade, largura do anel | reais > 0; profundidade ≤ profundidade do plano |
| Passo da malha | real entre 0,25 e 2,5 m |
| Número de isóbaras | inteiro entre 4 e 30 |
| Interfaces do perfil | fixas em −8, −12 e −14 m, conforme o material; não são parâmetros editáveis |

O professor não estabeleceu faixa máxima para γ ou cargas. O simulador não inventa um limite superior; protege contra valores não finitos, sinais fisicamente inválidos e combinações geométricas incompatíveis.

## Modelo matemático implementado

Convenção: cota negativa abaixo do terreno; profundidade `d` positiva para baixo. Unidades coerentes: kN, m, kN/m³ e kPa.

- Tensão vertical inicial por camadas: `σv = Σ(γi Δzi)`.
- Poropressão hidrostática: `u = γw max(0, d − dNA)`; `σ′v = σv − u`.
- Torre como carga pontual (Boussinesq): `Δσv = 3Qz³/[2π(r²+z²)^(5/2)]`.
- Aterro: integração analítica do mesmo núcleo sobre faixa finita em x e infinita em y.
- Escavação e anel: integração numérica polar do núcleo de Boussinesq sobre disco/anel; alívio negativo e aterro anelar positivo.
- Razão de isóbaras: `Δσv,total / σ′v inicial` na cota do plano, apresentada em porcentagem.

Estratos considerados: areia natural 0–3 m, areia saturada 3–8 m, argila mole 8–12 m, argila média 12–14 m. Interfaces e cotas seguem a figura do professor e a confirmação do usuário. O anel usa conservação de volume do solo escavado.

## Validação e divergências

Execute `py -3 -m unittest discover -s tests -v`. Os casos cobrem perfil em −4 m, solução analítica da carga pontual, faixa uniforme e integração do disco/anel. Testes de formulário/modelo aceitam 15,31; 15,32; 15,35; 15,40; vírgula decimal; precisão fracionária em todos os campos numéricos; e rejeitam texto não numérico e valores não positivos. Valores independentes: em −4 m, σv=74,70 kPa, u=9,81 kPa e σ′v=64,89 kPa; sob Q=5000 kN a 4 m, 149,207759 kPa; faixa finita indicada nas figuras em x=5–15 m, observada em x=0 e z=4 m, 3,498569 kPa. A quadratura do disco e do anel é comparada com solução axial independente.

As planilhas dos colegas adotam N.A. −1 m e −1,5 m, respectivamente, e diferem entre si e do N.A. −3 m da referência confirmada. Uma planilha usa aterro semi-infinito, enquanto as figuras mostram faixa limitada em x=5–15 m. Por isso, seus valores não foram assumidos como gabarito. O mapa ainda depende das hipóteses declaradas abaixo, pois não há caso de referência numérica completo e inequívoco fornecido pelo professor.

## Arquitetura

- `app.py`: servidor HTTP local, API opcional de referência e geração de relatório PDF.
- `calculation/model.py`: motor de referência em Python, validação, perfil e malha.
- `static/calculation.js`: motor completo executado no navegador, incluindo superposição e quadratura numérica.
- `static/index.html`, `styles.css`, `app.js`: interface, mapas, gráficos, validação de formulário e exportações.
- `reporting.py`: relatório PDF.
- `tests/test_model.py`: casos de validação independentes.
- `ANALISE_PRELIMINAR.md`: levantamento das fontes, requisitos, divergências e decisões de modelagem.
- `render.yaml`: configuração de implantação Render. O cálculo é executado no navegador; o backend Python fica disponível para geração de PDF e endpoint de referência.
- `static/manifest.webmanifest`, `static/sw.js`, ícones: shell instalável/PWA; o motor local funciona sem rede após os arquivos estarem disponíveis.

## iPhone e publicação

O layout é responsivo para tela estreita/vertical e horizontal e usa campos com `inputmode=decimal` e alvos de toque maiores. A simulação executa localmente no navegador, inclusive no iPhone, sem endpoint ou CORS. O modo PWA precisa ser servido via HTTPS. Para publicar:

1. Crie um repositório GitHub vazio chamado `geotecnia-simulador`.
2. Envie o **conteúdo desta pasta como raiz** do repositório (não coloque um nível adicional de pasta em volta).
3. Abra [Render Blueprints](https://dashboard.render.com/blueprints), escolha **New Blueprint Instance**, conecte o repositório e confirme a criação do serviço `geotecnia-simulador` definido em `render.yaml`.
4. Aguarde o build e o deploy. Render mostrará o endereço HTTPS `*.onrender.com` na página do serviço.
5. No iPhone, abra esse endereço no Safari, toque em Compartilhar e selecione **Adicionar à Tela de Início**.

O Blueprint configura `HOST=0.0.0.0`, comando `python app.py`, dependências e health check. Render exige que web services escutem em `0.0.0.0` e recomenda a porta da variável `PORT`; o app usa esses valores em implantação. A definição `render.yaml` fica no repositório para criar/atualizar o serviço como infraestrutura versionada ([referência Render](https://render.com/docs/blueprint-spec), [portas de Web Services](https://render.com/docs/web-services#port-binding)).

No iPhone 14 com iOS 18.3.2, abra esse endereço HTTPS no Safari, toque em Compartilhar e selecione **Adicionar à Tela de Início**. O manifest e os ícones são incluídos. O service worker mantém a interface e o motor em cache; os cálculos podem ocorrer sem backend. O PDF usa a rota opcional e precisa de conexão ao serviço Render. A hospedagem pública não foi criada nesta entrega: ela exige que o proprietário conecte uma conta GitHub/Render e autorize o repositório; este ambiente não tem uma conta de hospedagem autenticada nem um repositório remoto para publicar. O modo responsivo e os arquivos PWA foram preparados, mas a verificação visual final no iPhone depende de deploy em HTTPS e teste no dispositivo.

## Hipóteses e limites

O cálculo incremental usa Boussinesq e superposição em meio homogêneo, isotrópico, elástico e semi-infinito. O perfil inicial é estratificado. A faixa de aterro foi interpretada como infinita em y e finita em x. A remoção do solo atua como alívio uniforme na base da escavação; o solo é redistribuído em anel por conservação de volume. `γw=9,81 kN/m³` é editável e foi adotado por padrão, pois o material não especifica seu valor. O domínio XY reproduz o enquadramento das figuras (0–45 × 0–28 m), não necessariamente os limites físicos completos.

Os materiais não definem critério de ruptura, estabilidade, recalque ou fator de segurança. Portanto, o protótipo não declara segurança/aceitação e não substitui projeto ou revisão profissional. Para uso acadêmico, valide as hipóteses de idealização com o professor antes de tratar os mapas como resposta definitiva.

## Aplicativo iOS (Capacitor)

Configuração de Capacitor para encapsular os mesmos arquivos `static/`, com cálculo local/offline, armazenamento local e exportações. Consulte [COMO_INSTALAR_NO_IPHONE.md](COMO_INSTALAR_NO_IPHONE.md) para gerar o projeto iOS, configurar assinatura e usar o workflow GitHub Actions/TestFlight. O build iOS não foi executado neste ambiente Windows sem Xcode e credenciais Apple.

Testes JS do motor: `npm run test:web`. Testes Python: `python -m unittest discover -s tests -v`.

## Implantação no Vercel

O projeto exporta a aplicação ASGI `app` de `app.py`, que o runtime Python do Vercel usa como entrypoint. Importe este repositório no Vercel, mantenha a pasta raiz como diretório do projeto e deixe a detecção do Python automática; as dependências são instaladas a partir de `requirements.txt`. A aplicação FastAPI serve a interface em `/`, disponibiliza `/api/health` e `/api/simulate`, e gera o PDF em `/api/report`. O servidor `python app.py` continua sendo o modo local e o `render.yaml` continua configurando o Render.
