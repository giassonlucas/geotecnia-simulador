# Análise de engenharia — Simulador de tensões geotécnicas

**Status:** modelo reconstruído a partir do material do professor e das capturas de tela do usuário. Cota e N.A. confirmados pelo usuário. Nenhuma equação de dimensionamento ou critério de segurança será inferido.

## 1. Fontes analisadas

### Materiais do professor

- **Trabalho Final.pdf** (3 páginas): descrição do problema, parâmetros de carregamento, coordenadas e Figuras 1 e 2.
- **Roteiro Simplificado.pdf** (1 página): etapas de cálculo e instrução para normalizar o acréscimo pela tensão efetiva inicial.
- **Critérios de Avaliação.pdf** (2 páginas): itens e pesos de avaliação, apresentação, memória de cálculo e entrega.
- **Variação de A.jpg.jpeg** e **Variação de B.jpg.jpeg**: tabelas de coeficientes A′/B′ para tensões sob área circular uniforme. A legenda identifica Ahlvin & Ulery (1962), *National Cooperative Highway Research Program*, Bulletin 342.

### Planilhas de colegas (referência, não fonte normativa)

- **Mapeamento_Tensoes_Verticais.xlsx**: abas de resumo, perfil, cálculo ponto a ponto e memória de fórmulas. A memória declara Boussinesq para a torre, solução de faixa semi-infinita atribuída a Carothers/Terzaghi, tabelas A′/B′ para escavação e anel e superposição.
- **Planilha_Geotecnia_Trabalho_Final.xlsx**: abas de instruções, perfil, cargas, malha e mapa de calor. A malha usa passo 2,5 m e cobre aproximadamente x=0–45 m, y=0–28 m.
- O Google Doc **TRABALHO DE GEOTECNIA** é uma capa/estrutura com títulos, sem memória ou parâmetros preenchidos. A Google Sheet **GEOTECNIA** não apresenta conteúdo útil.

### Referência visual fornecida pelo usuário

O usuário enviou três capturas do vídeo:

1. **Perfil de tensões iniciais**: curvas de tensão total, poropressão e tensão efetiva em função da cota; eixo vertical invertido (0 a −14 m), eixo horizontal em kPa e linhas de referência no N.A. e interfaces.
2. **Superposição dos carregamentos**: campo XY colorido na cota −4 m, barra de cores para Δσv em kPa, torre marcada por triângulo, centro da escavação/anel e contornos circulares; linhas verticais indicam os limites do aterro em x=5 m e x=15 m.
3. **Isóbaras normalizadas**: mesmo domínio XY, agora com Δσv/σ′v, níveis de contorno rotulados e barra de cores percentual, mostrando contribuição positiva concentrada na torre e efeitos assinados das cargas/alívio.

O modelo da interface seguirá esse fluxo conceitual com dois mapas (acréscimo em kPa e razão normalizada em %) e o perfil em cota. As imagens são estáticas e não mostram diretamente uma alteração de parâmetro; portanto não se inferiu comportamento adicional de interação além de recalcular e atualizar as visualizações após executar a simulação.

## 2. O problema conforme o professor

O trabalho pede (a) o diagrama de tensão vertical total, poropressão e tensão efetiva, sem as cargas externas, até a cota −14 m; e (b) curvas isóbaras em um plano horizontal na cota atribuída ao grupo, exibindo o acréscimo total de tensão vertical dividido pela tensão efetiva inicial nessa cota.

Dados legíveis do enunciado e das figuras:

- Superfície natural: cota 0 m; coordenadas da planta em metros.
- Torre: carga concentrada Q = 5000 kN em (18, 22) m.
- Escavação circular: diâmetro 7 m e profundidade 1 m, centro (25, 17) m.
- O solo escavado é reutilizado em aterro anelar ao redor da escavação, com largura 1 m e mesma densidade.
- Aterro extenso: altura 3,8 m; γnat = 16,5 kN/m³, logo q = 62,7 kPa.
- Perfil: areia siltosa até −8 m (γnat = 18,5 kN/m³; γsat = 19,2 kN/m³), argila mole entre −8 e −12 m (γsat = 15,4 kN/m³) e argila média entre −12 e −14 m (γsat = 19,0 kN/m³).
- O usuário confirmou N.A. na cota −3 m.
- Figura 2 e as capturas mostram domínio aproximado x=0–45 m e y=0–28 m, e limites verticais de aterro em x=5 m e x=15 m. O protótipo representará o aterro como faixa uniforme finita em x∈[5,15] e extensa em y.
- O usuário confirmou a cota atribuída ao grupo em −4 m.
- O usuário indicou “limite do aterro −14 m”; conforme o enunciado, −14 m é tratado como limite inferior do perfil geotécnico, não como limite em planta do aterro.

## 3. Entradas propostas

O aplicativo deve distinguir **dados fixos do enunciado**, **cota/grupo** e **resolução da malha**. Os valores abaixo acompanham suas fontes; faixas indicadas como “validação física” não são critérios do professor.

| Entrada | Significado / unidade / tipo | Faixa ou padrão | Origem | Uso |
|---|---|---|---|---|
| Cota do plano do grupo | Cota z, m; número | −4 m confirmada; entre −14 m e abaixo da base da escavação (≤−1 m) para incluir todos os carregamentos | Confirmação do usuário | Perfil inicial no plano e normalização Δσv/σ′v |
| Cota do N.A. | Cota z, m; número | −3 m confirmada; editável entre −14 m e 0 m | Confirmação do usuário e Figura 1 | u(z), separação γnat/γsat |
| γw | Peso específico da água, kN/m³; número | 9,81 como valor de referência editável; professor não fornece valor numérico | Hipótese explícita do software; worksheets usam 9,81 e 10 | u = γw·h |
| γnat da areia siltosa | kN/m³; número | 18,5; >0 (checagem física) | Figura 1 | σv acima do N.A.; alívio de escavação/solo reutilizado |
| γsat da areia siltosa | kN/m³; número | 19,2; >0 | Figura 1 | σv abaixo do N.A. |
| γsat da argila mole | kN/m³; número | 15,4; >0 | Figura 1 | σv de −8 a −12 m |
| γsat da argila média | kN/m³; número | 19,0; >0 | Figura 1 | σv de −12 a −14 m |
| Profundidades das interfaces | −8, −12 e −14 m; números | Fixas pelo perfil mostrado, avançadas/editáveis se o perfil for generalizado | Figura 1 | Integração por trechos |
| Q da torre | kN; número | 5000 | Enunciado | Boussinesq |
| xT, yT | Coordenadas, m; números | (18,22) | Informações adicionais do enunciado | Distância r à torre |
| haterro e γaterro | m e kN/m³; números | 3,8 e 16,5 | Figura 1/enunciado | q = γh |
| Limites x do aterro extenso | m; números | 5 e 15; editável | Figura 2 e capturas fornecidas pelo usuário | Solução de faixa infinita em y e finita em x |
| Centro da escavação | x,y em m | (25,17) | Informações adicionais do enunciado | Distância radial |
| Diâmetro e profundidade da escavação | m; números | 7 e 1 | Enunciado | Raio, alívio q e cota da fonte |
| Largura do anel | m; número | 1 | Informação adicional do enunciado | Raio externo = raio interno + largura |
| Δx, Δy da malha | m; números | Editáveis; 2,5 m reproduz uma planilha; 1 m é escolha visual mais fina | Roteiro manda construir malha; espaçamento é decisão do grupo | Domínio e processamento numérico |
| Extensão da planta | xmin/xmax/ymin/ymax em m | 0–45 e 0–28 conforme eixos da Figura 2 | Figura 2 e capturas | Grade 2D |
| Número de níveis de contorno | inteiro | Escolha do usuário; professor manda arbitrar | Roteiro Simplificado | Isóbaras |

Checagens de entrada: valores numéricos finitos; γ>0; cota do plano dentro do perfil e abaixo da base da escavação para a análise completa; σ′v inicial >0 para normalização; limites e espaçamentos de malha coerentes; raio externo maior que interno. Sem aprovação/reprovação estrutural, pois o professor não forneceu fator de segurança ou critério de aceitação de estabilidade.

## 4. Modelo matemático proposto

Convenção: profundidade d = −cota, positiva para baixo; tensão em kPa, carga Q em kN, comprimentos em m. Assim, kN/m² = kPa.

### 4.1 Tensões iniciais

Para camadas horizontais e peso específico γᵢ constante em cada trecho:

\[
\sigma_v(d)=\sum_i \gamma_i\,\Delta d_i,\qquad
u(d)=\begin{cases}0,&d\le d_{NA}\\\gamma_w(d-d_{NA}),&d>d_{NA}\end{cases},\qquad
\sigma'_v(d)=\sigma_v(d)-u(d).
\]

Cada trecho usa a interseção entre [0,d] e os limites da camada. A curva é contínua; sua inclinação muda em N.A. e interfaces. É calculada antes dos carregamentos externos, como pede o item (a).

### 4.2 Torre — carga concentrada

\[
\Delta\sigma_{v,Q}=\frac{3Qz^3}{2\pi(r^2+z^2)^{5/2}},\qquad
r^2=(x-x_T)^2+(y-y_T)^2.
\]

z é a distância vertical entre o plano de aplicação (superfície) e o plano calculado. Formulação de Boussinesq, citada nos critérios do professor como método possível para a torre. Requer z>0.

### 4.3 Aterro extenso — faixa uniforme

q = γaterro haterro. Para faixa que se estende indefinidamente em y e ocupa x∈[a,b], integrar a solução de Boussinesq sobre a faixa resulta em:

\[
\Delta\sigma_{v,faixa}=\frac{q}{\pi}\left[F\!\left(\frac{b-x}{z}\right)-F\!\left(\frac{a-x}{z}\right)\right],\quad
F(t)=\arctan(t)+\frac{t}{1+t^2}.
\]

Para faixa semi-infinita x≤b, usar o limite a→−∞. A extensão lateral e a interpretação de x∈[5,15] precisam ser confirmadas pela Figura 2/professor antes de fixar a configuração padrão. A planilha A usa β=arctan((b−x)/z)+π/2 numa combinação que não é consistente com a integral de Boussinesq; a planilha B acerta o limite semi-infinito em alguns pontos, mas assume geometria diferente.

### 4.4 Escavação circular e anel de aterro

A referência do professor inclui tabelas A′/B′ de Ahlvin & Ulery para carga uniforme em disco. Para evitar leitura/interpolação de tabela no cálculo do mapa, o protótipo pode integrar numericamente a equação de Boussinesq em cada área carregada:

\[
\Delta\sigma_v(x,y)=\iint_A \frac{3q z^3}{2\pi\left[(x-X)^2+(y-Y)^2+z^2\right]^{5/2}}\,dA.
\]

Na escavação, qesc = −γnat hesc e o plano de aplicação é a base da escavação na cota −1 m; portanto z = dplano − 1 m. No anel, ri=3,5 m, re=4,5 m. Pela conservação de volume do solo escavado:

\[
h_{anel}=\frac{\pi r_i^2h_{esc}}{\pi(r_e^2-r_i^2)}=1{,}53125\,m,\qquad
q_{anel}=\gamma_{nat}h_{anel}\approx28{,}3281\,kPa.
\]

A tensão do anel é integrada diretamente sobre ri≤r≤re; a escavação leva sinal negativo. Essa integração é matematicamente equivalente à superposição do disco externo menos o disco interno.

### 4.5 Soma e normalização

\[
\Delta\sigma_{v,total}=\Delta\sigma_{v,Q}+\Delta\sigma_{v,faixa}+\Delta\sigma_{v,esc}+\Delta\sigma_{v,anel},\qquad
I(x,y)=\frac{\Delta\sigma_{v,total}(x,y)}{\sigma'_{v,inicial}(d_{plano})}.
\]

Exibir I como razão adimensional e 100I em %. Usar precisão integral sem arredondamento intermediário; arredondar apenas no painel/tabelas.

## 5. Divergências encontradas nas planilhas

| Tema | Planilha A | Planilha B | Leitura do material do professor / decisão |
|---|---|---|---|
| N.A. | −1 m | −1,5 m | Figura 1 parece −3 m; prevalece a figura do professor, sujeito a confirmação visual |
| γw | 9,81 | 10,0 | professor não fixa valor numérico; 9,81 será hipótese visível/editável |
| Tensão inicial | Aba de perfil internamente inconsistente: valores a −4 m não seguem uma única divisão N.A./camada; resumo associa 105,25/44,15/61,11 kPa a −4 m, mas esses valores correspondem a linha mais profunda | inclui carregamento/aterro no cálculo chamado “inicial”, usa γw=10 e adota −1,5 m; para −4 m mostra 122,10 kPa, mas resumo traz σ′v=4,00 kPa e mapa usa 50,75 kPa | item (a) é antes dos carregamentos externos e usa Figura 1. Recalcular do zero por integração, sem usar esses denominadores |
| Aterro extenso | Aba de memória indica x≤15 m, mas sua equação β e valores não conciliam com a integração do kernel de Boussinesq | usa x≤15 m e chega a 62,47 kPa em (0,0), compatível com faixa semi-infinita | Figura 2/capturas do usuário mostram limites x=5 e 15. Implementar faixa finita [5,15]; o cálculo semi-infinito permanece apenas como comparação |
| Escavação | −10,61 kPa no eixo para z informado de 3 m | −10,61 kPa no eixo | integração direta para q=−18,5 kPa, raio 3,5 m e plano 3 m abaixo da base dá −13,4009 kPa; diferença ~20,8%, provável erro na profundidade/coeficiente. Recalcular |
| Anel | 3,66 kPa no centro | 3,66 kPa no centro | integração direta para a geometria declarada dá ≈3,7677 kPa; diferença ≈2,9%, maior que simples arredondamento a centésimos |
| Torre | Boussinesq descrito | 149,21 kPa no eixo a 4 m | fórmula independente dá 149,2078 kPa; concorda com a planilha B após arredondamento |
| Mapa | malha detalhada ponto a ponto | heatmap em escala de cores, 2,5 m; eixos, cores e valores em % | interface pode adotar heatmap/contorno interativo, mas somente alimentado por cálculos corrigidos |

Os dados dos colegas não são usados para “votar” em um método. Boussinesq e a integração/superposição compatível com ele são mantidos; as tensões de referência são refeitas a partir do perfil do professor.

## 6. Casos independentes calculados

### Caso P1 — tensão inicial no plano de referência (cota −4 m)

Usando provisoriamente N.A. em −3 m, γw=9,81 kN/m³ e o perfil da Figura 1:

| Entrada | Resultado independente | Comparação com referência |
|---|---:|---|
| d=4 m; areia siltosa 0–3 m com γnat=18,5; 3–4 m com γsat=19,2; N.A.=3 m | σv=74,70 kPa; u=9,81 kPa; σ′v=64,89 kPa | diverge das duas planilhas; ambas usam N.A./segmentações diferentes e uma inclui o aterro na condição inicial |

### Caso P2 — torre sobre o próprio eixo

| Entrada | Resultado de Boussinesq | Planilha B | Diferença absoluta | Diferença percentual | Situação |
|---|---:|---:|---:|---:|---|
| Q=5000 kN; z=4 m; r=0 | 149,207759 kPa | 149,21 kPa | 0,002241 kPa | 0,00150% | APROVADO após arredondamento a 0,01 kPa |

### Caso P3 — carga de faixa

Para q=62,7 kPa, z=4 m, no ponto (x,y)=(0,0):

- faixa semi-infinita x≤15 m: 62,467694 kPa, concordando com a Planilha B (62,47 kPa);
- faixa finita x∈[5,15] m: 3,498569 kPa.

A diferença não é um erro de arredondamento: é consequência direta da geometria da carga. É necessário seguir os limites que o professor quis representar na Figura 2.

### Caso P4 — área circular sob o centro

Para carga uniforme circular, a integração radial sob o eixo reduz a q[1−(1+(R/z)²)^(−3/2)]. Com q=−18,5 kPa, R=3,5 m e z=3 m medidos da base até o plano −4 m, resulta −13,400858 kPa. As duas planilhas mostram −10,61 kPa: **DIVERGENTE** (diferença absoluta 2,790858 kPa; relativa 20,83% do módulo de referência independente).

### Caso P5 — anel sob o centro

Usando discos concêntricos (R=4,5 m menos R=3,5 m), z=4 m, q=28,328125 kPa, resulta +3,767671 kPa. As planilhas mostram +3,66 kPa: **DIVERGENTE** (diferença absoluta 0,107671 kPa; relativa 2,86%).

## 7. Fluxo lógico

```text
Entradas do problema e cota atribuída
  ↓ validar unidades, faixas físicas, interfaces e plano de observação
Perfil por camadas → σv(d), u(d), σ′v(d)
  ↓ confirmar σ′v(dplano) > 0
Malha x-y no domínio da Figura 2
  ↓
Calcular Δσ da torre, faixa, escavação e anel separadamente
  ↓ verificar sinais; somar os quatro efeitos sem arredondar
Normalizar pela σ′v inicial na cota do grupo
  ↓
Resultados numéricos, perfil, mapa de cores/isóbaras e rastreabilidade
  ↓
Exportar CSV e relatório PDF com entradas, equações, unidades, caso e limitações
```

## 8. Resultados e interface necessários

- **Numéricos:** σv, u e σ′v ao longo do perfil; tensão efetiva inicial do plano; Δσ separado por carregamento; Δσ total; razão adimensional e porcentagem; extremos (máximo/mínimo) e coordenadas.
- **Intermediários:** espessuras integradas por camada; pressão dos aterros; raios; altura por conservação de volume; distâncias/termos geométricos e contribuições assinadas por carga.
- **Gráficos:** perfil com σv/u/σ′v vs cota/profundidade; mapa XY interativo com pan/zoom, barra de cores e contornos rotulados de Δσ/σ′v (%); pontos das cargas e geometria do aterro/escavação/anel.
- **Alertas:** parâmetros ausentes ou inválidos; plano fora do perfil; plano acima da base de escavação; σ′v≤0; malha muito grosseira; premissas ainda não confirmadas. Nenhum alerta de “seguro/inseguro” sem critério fornecido.
- **Rastreabilidade:** cada resultado pode ser expandido em entrada → equação → termos → contribuição por carga → soma → normalização.

## 9. Arquitetura proposta

Python + NumPy para os cálculos vetorizados, Streamlit para painéis de entrada/resultados e Plotly para perfil e mapa interativos. NumPy/Gauss-Legendre realiza a integração de áreas; não é necessário embutir fórmulas na interface. Pandas cria tabelas/CSV; ReportLab gera relatório PDF. A escolha mantém o cálculo verificável e o aplicativo executável localmente via navegador, sem serviço externo.

```text
geotecnia-simulador/
├── app.py                    # interface Streamlit
├── calculation/
│   ├── model.py              # tensões iniciais e carregamentos
│   ├── validation.py         # checagens físicas e geométricas
│   └── units.py              # convenções e conversões
├── visualization/plots.py    # perfil, heatmap e contornos
├── reporting.py              # rastreabilidade, CSV e PDF
├── reference_cases.json      # casos e limites de comparação
├── tests/                    # validações autorizadas no pedido
├── requirements.txt
└── README.md
```

## 10. Premissas e limitações a exibir no software

1. γw=9,81 kN/m³ é uma hipótese operacional editável, não um valor numérico fornecido pelo professor.
2. O aterro é tratado como faixa infinita em y e finita entre x=5 e 15 m, conforme os desenhos; altura e γ vêm do enunciado/Figura 1.
3. As capturas fornecem a referência visual, mas não comprovam um comportamento dinâmico ao alterar parâmetros. A interface permitirá alterar entradas e executar novamente.
4. Não há critério de segurança/ruptura nem de aceitação de obra informado; o software calcula tensões, sem declarar a estrutura/solo seguro ou inseguro.
## Protótipo e validação independente

Foi criado um protótipo local executável em Python/HTML/JavaScript. Ele adota, por enquanto, −14 m como limite inferior do perfil de cálculo, conforme o eixo vertical da figura; a faixa do aterro no plano é interpretada pelas linhas x=5–15 m das imagens. Essa leitura deve ser confirmada se “limite do aterro −14 m” pretendia outra geometria.

Sete testes automatizados passaram. Casos conferidos: perfil inicial em −4 m (74,70 kPa total; 9,81 kPa poropressão; 64,89 kPa efetiva), carga pontual no eixo (149,207759 kPa), faixa finita (3,498569 kPa), disco de alívio e anel. Disco e anel têm solução axial fechada independente e os testes comparam a quadratura numérica com essas soluções. A API local e geração do PDF foram verificadas. Os casos da planilha permanecem divergentes pelas hipóteses distintas registradas acima e não servem, sem alinhamento, como gabarito único.

O protótipo não implementa verificação de estabilidade/segurança; o material não forneceu critério para isso. A integração numérica e a idealização elástica precisam ser apresentadas ao professor para confirmar que são adequadas ao escopo acadêmico.
## Auditoria da entrada numérica (correção)

Os `input[type=number]` usavam `step="0.1"` em conjunto com `min="0.01"`. O HTML alinha os valores válidos ao mínimo (0,01 + n·0,1), causando exatamente rejeições como 15,32 e mensagens de opções próximas 15,31/15,41. O incremento era apenas configuração incidental do formulário, não uma exigência do professor. O mínimo 0,01 também era incidental. As entradas passaram a texto decimal com teclado touch; o cliente e o servidor aceitam ponto e vírgula, sem lista/grade. Validação: reais finitos; valores >0 para cargas/pesos/dimensões positivas; faixas preservadas para cotas, passo e contornos; regras cruzadas de aterro e plano/escavação. Coordenadas são livres e não limitadas à janela de visualização.

Foram adicionados testes de precisão arbitrária para cada parâmetro numérico, decimais 15,31/15,32/15,35/15,40, parsing de vírgula em pesos, geometria e coordenadas, rejeição de texto e zero/negativos, preservação de limites técnicos e verificação de combinações geométricas. O conjunto final contém 15 testes aprovados. As fórmulas e casos de referência permaneceram iguais; valores padrão continuam retornando σv=74,70 kPa, u=9,81 kPa e σ′v=64,89 kPa na cota −4 m.

## Investigação do erro “Failed to fetch”

Na versão com erro, o submit em `static/app.js` enviava `POST /api/simulate` com `Content-Type: application/json` e todos os 21 parâmetros numéricos do formulário. A rota existe em `app.py`, porta padrão 8501 local e porta `PORT` em deploy. O backend respondeu HTTP 200 ao mesmo payload padrão durante a verificação. A API de health respondeu 200. O código não exigia CORS em serviço na mesma origem; um erro do modelo ou validação teria retornado HTTP 4xx/5xx e não a rejeição de rede “Failed to fetch”. Esta mensagem ocorre antes de uma resposta HTTP chegar ao frontend: origem inacessível, arquivo `file://`, backend não iniciado na mesma origem/porta, conexão recusada ou bloqueio de rede. A captura não exibia o endereço e a automação não conseguiu ler a URL da aba, então não atribuo conclusivamente um desses cenários específicos.

Para remover essa dependência do botão **Executar simulação**, o conjunto completo de cálculo foi portado para `static/calculation.js`; agora o formulário valida e calcula no navegador. Não existe requisição de simulação no caminho do botão, não há CORS/localhost e o uso PWA pode calcular no cliente. A API Python continua como referência e para relatório PDF opcional. Foi comparado o motor JavaScript com Python para seis casos (padrão, γ de argila 15,3/15,4/15,5, decimal com vírgula e Q=5500 kN): mais de 105 mil valores de perfil, malha, contornos-base, componentes, resumos e geometria coincidiram, com erro absoluto máximo de 1,78×10⁻¹⁴.

Páginas sem estilo eram compatíveis com abrir `index.html` diretamente via `file://`: referências absolutas `/styles.css` e `/app.js` apontavam para a raiz do sistema. Agora CSS, JavaScript e motor são relativos. O motor JS executa as simulações localmente sem API; o servidor Python/Render mantém rota opcional para o PDF. A PWA inclui manifest, service worker e ícones e conserva os cálculos no cliente. `render.yaml` configura bind público e porta de hospedagem para o Render. Nenhuma publicação externa foi feita porque não existe neste ambiente um repositório remoto autenticado/conta Render. A URL da captura não ficou visível e a automação bloqueou a leitura da aba, portanto não foi possível diferenciar conclusivamente se a origem que falhou era `file://`, localhost sem servidor ou hospedagem sem API; as três situações deixam de bloquear o cálculo com o motor local.

## Correção do gráfico do perfil na visão geral

A cadeia de dados estava íntegra: `GeotechCalculation.simulate()` gera 61 pontos do perfil com cotas entre 0 e −14 m, incluindo nível d’água e interfaces de −8, −12 e −14 m; `render()` recebia essas séries calculadas. A falha acontecia na etapa de renderização: `render()` era chamado com o contêiner `#results` ainda oculto. O canvas media largura zero, e `drawProfile()` retornava sem desenhar. Corrigi a ordem para revelar o painel e aguardar um quadro de layout antes de desenhar; dimensões nulas agora geram erro explícito em vez de um gráfico branco silencioso.

As curvas usam diretamente os campos `sigma_v_kPa`, `u_kPa` e `sigma_eff_kPa` do motor, em kPa, ao longo de `elevation_m` em m. O gráfico marca o N.A. e as interfaces −8 m e −12 m, mostra valores/cotas no cursor e redesenha quando a janela muda de tamanho. O resumo lateral agora gera elementos `.config-item` compatíveis com o CSS; os valores de σ′v inicial, q do aterro e altura do anel são preenchidos do mesmo resultado da simulação. Também completei o cartão de máximo Δσv e sua coordenada. O status de erro não é mais substituído por “Simulação concluída” no `finally`.

A troca do cache da PWA para `geotecnia-shell-v3` força clientes que atualizarem a aplicação a buscar o JavaScript corrigido. No caso padrão: σv(−4 m)=74,70 kPa, u(−4 m)=9,81 kPa, σ′v(−4 m)=64,89 kPa; a identidade σ′v=σv−u tem resíduo numérico zero. O γsat da argila mole afeta o perfil a partir da interface de −8 m; o N.A. altera u e σ′v; a carga da torre altera os mapas de carregamento, mas não σv inicial.

Verificação executada: 16 testes Python passaram; `node --check` passou nos dois arquivos JavaScript; o motor JS confirmou 61 linhas finitas e respostas paramétricas coerentes. A API local `/api/health` respondeu HTTP 200. A tentativa de abrir a página em navegador automatizado não completou porque o runtime Playwright não tem o browser headless instalado e a inicialização pelo Edge local excedeu o tempo limite; portanto, não afirmo validação visual efetiva do canvas nem teste em iPhone. A interface mantém redimensionamento responsivo baseado no evento `resize`.
## Preparação para iOS com Capacitor

Inventário atual: interface HTML em `static/index.html`, estilos em `static/styles.css`, controlador/visualização em `static/app.js`, motor JS independente em `static/calculation.js`, motor de referência Python em `calculation/model.py`, backend HTTP/PDF em `app.py`/`reporting.py`, ativos PWA e testes em `tests/`. Não há React/TypeScript nem biblioteca de gráficos externa; os mapas e perfil são canvas 2D. O formulário de simulação chama o motor local, sem `fetch`; somente o relatório PDF ainda usa `POST /api/report`.

Foi preparada a configuração Capacitor 8 com `webDir=static`, Bundle ID candidato `br.com.geotecnia.simuladortensoes`, nome iOS `Geotecnia`, metadados mobile com safe areas, ícone e splash nos tamanhos-fonte do gerador Capacitor. Removi a importação remota de fontes Google para reduzir dependências de rede. Adicionei salvamento local dos cinco casos mais recentes no armazenamento do aparelho e compartilhamento de CSV/JSON/PNG/PDF com `navigator.share` quando o Web Share aceitar arquivos; o PDF ainda depende do backend. As entradas de cota e coordenadas potencialmente negativas usam teclado textual no iOS para permitir o sinal `−`, mantendo o parser de decimal ponto/vírgula.

Foram adicionados sete testes do motor JavaScript cobrindo valor padrão/σ′=σ−u, pontos e interfaces do perfil, γsat de argila, NA, carga da torre, geometria, cotas negativas e decimal com vírgula. Os sete testes JavaScript e os 16 testes Python passam. Os recursos-fonte do ícone e splash respeitam o requisito mínimo de 1024×1024 e 2732×2732 do gerador oficial Capacitor Assets.

A instalação do Capacitor CLI e a materialização de `ios/App/App.xcodeproj` não foram possíveis neste ambiente: o `pnpm install` tentou acessar `registry.npmjs.org` e recebeu `EACCES`; não há npm/CLI Capacitor em cache. Também não há macOS/Xcode, conta Apple Developer, certificados ou perfil. O Bundle ID é sintaticamente válido, mas sua disponibilidade global não pode ser confirmada fora da conta Apple. Foi adicionado o workflow manual macOS `.github/workflows/ios-testflight.yml`; após criar repositório GitHub, configurar secrets de assinatura/API e executar a ação, ele instala dependencies, gera a pasta iOS, testa os motores, assina e envia uma build ao App Store Connect. Nenhum build/upload/TestFlight foi executado. A validação em iPhone 14 físico e no simulador iOS 18 ainda é obrigatória.
