// app/static/js/app.js

/**
 * SmartCards — Frontend Logic
 * 
 * Arquitetura do JS:
 * - Funções de UI: mostrarLoading, esconderLoading, mostrarErro...
 * - Funções de API: gerarFlashcards (async/await)
 * - Funções de render: criarElementoFlashcard
 * - Event listeners: inicializados no DOMContentLoaded
 * 
 * PADRÃO ASYNC/AWAIT:
 * Em vez de callbacks aninhados (callback hell), usamos
 * async/await que torna o código assíncrono legível como síncrono.
 */

// ===========================
// ESTADO DA APLICAÇÃO
// Uma variável simples rastreia os flashcards gerados.
// Em apps maiores, isso seria um estado gerenciado (Redux, Zustand, etc.)
// ===========================
let flashcardsGerados = [];


// ===========================
// INICIALIZAÇÃO
// Executado quando o DOM estiver totalmente carregado.
// ===========================
document.addEventListener("DOMContentLoaded", () => {
  const textarea = document.getElementById("texto");
  const charCount = document.getElementById("char-count");

  // Atualiza contador de caracteres em tempo real
  textarea.addEventListener("input", () => {
    const count = textarea.value.length;
    charCount.textContent = count;
    // Muda cor quando está chegando no limite
    charCount.style.color = count > 4500 ? "#EF4444" : "";
  });
});


// ===========================
// FUNÇÕES DE UI
// Responsáveis apenas por manipular o DOM.
// Separadas da lógica de negócio (princípio SRP).
// ===========================

function mostrarLoading(mostrar) {
  const loading = document.getElementById("loading");
  const btn = document.getElementById("btn-gerar");

  if (mostrar) {
    loading.classList.remove("hidden");
    btn.disabled = true;
    btn.textContent = "⏳ Gerando...";
  } else {
    loading.classList.add("hidden");
    btn.disabled = false;
    btn.textContent = "✨ Gerar Flashcards";
  }
}

function mostrarErro(mensagem) {
  const erroEl = document.getElementById("erro");
  erroEl.textContent = `⚠️ ${mensagem}`;
  erroEl.classList.remove("hidden");

  // Auto-remove após 6 segundos
  setTimeout(() => erroEl.classList.add("hidden"), 6000);
}

function esconderErro() {
  document.getElementById("erro").classList.add("hidden");
}

function mostrarResultados(flashcards, total, modo) {
  // Atualiza badges de meta-informação
  document.getElementById("total-cards").textContent = `${total} flashcard${total !== 1 ? 's' : ''}`;
  document.getElementById("modo-badge").textContent = modo === "ia" ? "🤖 Inteligência Artificial" : "⚙️ Processamento por Regras";

  // Renderiza os cards no grid
  const grid = document.getElementById("flashcards-grid");
  grid.innerHTML = ""; // Limpa cards anteriores

  flashcards.forEach((fc, index) => {
    const elemento = criarElementoFlashcard(fc, index);
    grid.appendChild(elemento);
  });

  // Exibe a seção de resultados
  const secao = document.getElementById("resultados");
  secao.classList.remove("hidden");

  // Scroll suave até os resultados
  secao.scrollIntoView({ behavior: "smooth", block: "start" });
}


// ===========================
// CRIAÇÃO DO FLASHCARD (DOM)
// ===========================

/**
 * Cria o elemento HTML de um flashcard com efeito flip.
 * 
 * Estrutura gerada:
 * <div class="flashcard-wrapper">              ← perspectiva 3D
 *   <div class="flashcard" onclick="flipCard(this)">   ← cartão que vira
 *     <div class="flashcard__face flashcard__front">   ← frente
 *       ...
 *     </div>
 *     <div class="flashcard__face flashcard__back">    ← verso
 *       ...
 *     </div>
 *   </div>
 * </div>
 * 
 * @param {Object} fc    - Objeto flashcard da API
 * @param {number} index - Índice para animação sequencial
 * @returns {HTMLElement}
 */
function criarElementoFlashcard(fc, index) {
  const wrapper = document.createElement("div");
  wrapper.className = "flashcard-wrapper";

  // Animação de entrada escalonada (cada card aparece com delay)
  wrapper.style.animationDelay = `${index * 0.1}s`;

  const nomesTipo = {
    "verdadeiro_falso":   "Verdadeiro ou Falso",
    "preencha_lacuna":    "Preencha a Lacuna",
    "pergunta_resposta":  "Pergunta e Resposta",
  };

  wrapper.innerHTML = `
    <div class="flashcard" onclick="flipCard(this)" role="button" 
         aria-label="Flashcard: ${nomesTipo[fc.tipo] || fc.tipo}. Clique para ver a resposta."
         tabindex="0"
         onkeypress="if(event.key==='Enter'||event.key===' ') flipCard(this)">
      
      <!-- FRENTE DO CARTÃO -->
      <div class="flashcard__face flashcard__front">
        <div>
          <span class="flashcard__tipo tipo--${fc.tipo}">
            ${nomesTipo[fc.tipo] || fc.tipo}
          </span>
          <p class="flashcard__pergunta">${escapeHTML(fc.frente)}</p>
        </div>
        <p class="flashcard__hint">👆 Clique para ver a resposta</p>
      </div>

      <!-- VERSO DO CARTÃO -->
      <div class="flashcard__face flashcard__back">
        <div>
          <p class="flashcard__resposta-label">✅ Resposta</p>
          <p class="flashcard__resposta">${escapeHTML(fc.verso)}</p>
        </div>
        ${fc.dica ? `<p class="flashcard__dica-verso">💡 ${escapeHTML(fc.dica)}</p>` : ''}
      </div>

    </div>
  `;

  return wrapper;
}

/**
 * Vira o cartão adicionando/removendo a classe .is-flipped.
 * O CSS cuida da animação 3D.
 * 
 * @param {HTMLElement} element - O elemento .flashcard clicado
 */
function flipCard(element) {
  element.classList.toggle("is-flipped");
}

/**
 * Escapa caracteres HTML para prevenir XSS.
 * NUNCA insira texto de usuário no DOM sem sanitizar.
 * 
 * XSS (Cross-Site Scripting): ataque onde código malicioso
 * é injetado via input do usuário e executado no browser.
 * 
 * @param {string} str - String a ser escapada
 * @returns {string} String segura para innerHTML
 */
function escapeHTML(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}



// FUNÇÃO PRINCIPAL: ASYNC/AWAIT

// * Orquestra todo o fluxo de geração de flashcards.
 
async function gerarFlashcards() {
  const texto = document.getElementById("texto").value.trim();
  const usarIA = document.getElementById("usar-ia").checked;

  // Validação no frontend (defesa dupla — backend também valida)
  if (!texto) {
    mostrarErro("Por favor, insira um texto antes de gerar os flashcards.");
    return;
  }

  if (texto.length < 50) {
    mostrarErro("O texto é muito curto. Insira pelo menos 50 caracteres.");
    return;
  }

  // Limpa estado anterior
  esconderErro();
  document.getElementById("resultados").classList.add("hidden");

  // Inicia feedback visual de carregamento
  mostrarLoading(true);

  try {
    /**
     * fetch() retorna uma Promise.
     * `await` aguarda a resposta HTTP sem bloquear a thread.
     * 
     * Enquanto aguarda, o browser continua:
     * - Processando outros eventos
     * - Mantendo animações rodando
     * - Permitindo scroll da página
     */
    const resposta = await fetch("/api/gerar", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",  // Informa que o body é JSON
      },
      body: JSON.stringify({
        texto:    texto,
        usar_ia:  usarIA,
      }),
    });

    /**
     * .json() também retorna uma Promise.
     * Aguardamos o parse do corpo da resposta.
     */
    const dados = await resposta.json();

    // Verificamos o status HTTP explicitamente
    if (!resposta.ok) {
      // 4xx ou 5xx — dados.erro contém a mensagem do backend
      throw new Error(dados.erro || "Erro desconhecido no servidor.");
    }

    // Tudo certo! Guarda no estado e renderiza
    flashcardsGerados = dados.flashcards;
    mostrarResultados(dados.flashcards, dados.total, dados.modo);

  } catch (erro) {
    /**
     * O bloco catch captura:
     * 1. Erros de rede (sem conexão, timeout)
     * 2. Erros do servidor (lançados acima com throw)
     * 3. Erros de parse do JSON (corrompido)
     */
    console.error("Erro ao gerar flashcards:", erro);
    mostrarErro(erro.message || "Falha na comunicação com o servidor. Verifique sua conexão.");

  } finally {
    /**
     * finally sempre executa, independente de sucesso ou erro.
     * Garante que o loading sempre seja escondido.
     */
    mostrarLoading(false);
  }
}


// ===========================
// FUNÇÃO DE RESET
// ===========================

function resetar() {
  // Limpa o textarea
  document.getElementById("texto").value = "";
  document.getElementById("char-count").textContent = "0";

  // Esconde resultados
  document.getElementById("resultados").classList.add("hidden");

  // Scroll para o topo
  window.scrollTo({ top: 0, behavior: "smooth" });

  // Foca no textarea para UX fluida
  document.getElementById("texto").focus();
}
