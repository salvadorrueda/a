# ai.py — Eina d'IA per a la línia de comandes

Eina per preguntar a múltiples proveïdors d'intel·ligència artificial des del terminal de Linux. S'integra amb el gestor de tasques `a` i s'executa dins d'un contenidor Docker per no instal·lar res al sistema amfitrió.

---

## Fitxers

```
Scripts/
  ai.py          — lògica Python: parseja arguments, crida l'API del proveïdor
  ai.sh          — wrapper Bash: construeix/executa el contenidor Docker
  Dockerfile.ai  — imatge Docker amb les dependències dels SDKs cloud
```

---

## Arquitectura i disseny

### Per què Docker?

Les llibreries dels proveïdors cloud (`anthropic`, `openai`, `google-generativeai`) s'instal·len dins la imatge Docker, no al sistema. Això manté el sistema net i evita conflictes de versions.

```
[usuari]
   │
   ▼
a ai "pregunta"          ← gestor de tasques (a.py)
   │
   ▼
ai.sh                    ← wrapper Bash
   │  construeix la imatge si no existeix
   │  passa les claus API com a variables d'entorn
   │  --network host  (per accedir a Ollama al localhost)
   ▼
docker run ai-cli        ← contenidor Python 3.11-slim
   │
   ▼
ai.py                    ← lògica Python dins el contenidor
   │
   ▼
API del proveïdor        ← Claude / ChatGPT / Gemini / Ollama
```

### Flux d'execució

1. L'usuari invoca `a ai "pregunta"` o directament `./Scripts/ai.sh "pregunta"`.
2. `ai.sh` comprova si la imatge Docker `ai-cli` existeix. Si no, la construeix (únicament el primer cop).
3. `ai.sh` executa `docker run` passant les claus API com a `-e VAR=valor`.
4. Dins el contenidor, `ai.py` parseja els arguments, determina el proveïdor i el model, i crida l'API corresponent en mode **streaming** (els tokens apareixen progressivament al terminal).

### Imports lazy (carrega sota demanda)

Els SDKs cloud (`anthropic`, `openai`, `google.generativeai`) s'importen dins de cada funció de proveïdor, no a l'inici del script. Això permet:

- Usar Ollama sense cap SDK instal·lat (usa `urllib.request` de la biblioteca estàndard).
- Mostrar un missatge d'error clar si falta un paquet, indicant exactament com instal·lar-lo.

### Taula de despachament

```python
PROVEIDORS = {
    "claude":  preguntar_claude,
    "chatgpt": preguntar_chatgpt,
    "gemini":  preguntar_gemini,
    "ollama":  preguntar_ollama,
}
```

`main()` resol el proveïdor i crida la funció corresponent. Afegir un nou proveïdor és tan simple com afegir una funció i una entrada al diccionari.

---

## Proveïdors suportats

| Proveïdor | SDK Python | Variable d'entorn | Model per defecte |
|-----------|-----------|-------------------|-------------------|
| `claude`  | `anthropic` | `ANTHROPIC_API_KEY` | `claude-sonnet-4-6` |
| `chatgpt` | `openai` | `OPENAI_API_KEY` | `gpt-4o` |
| `gemini`  | `google-generativeai` | `GOOGLE_API_KEY` | `gemini-1.5-pro` |
| `ollama`  | _(cap, stdlib)_ | _(cap)_ | `llama3` |

Ollama es connecta al servei local a `http://localhost:11434`. El flag `--network host` de Docker permet al contenidor arribar al localhost de la màquina amfitriona.

---

## Instal·lació i posada en marxa

### Prerequisits

- Docker instal·lat i en execució.
- Per a Ollama: `ollama` instal·lat i `ollama serve` en execució.
- Claus API dels proveïdors cloud que es vulguin usar.

### Primer ús (construeix la imatge automàticament)

```bash
# Definir les claus API (p. ex. al ~/.bashrc o ~/.profile)
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="AIza..."

# Registrar la tasca al gestor (només cal fer-ho un cop)
python3 /home/user/a/a.py add Scripts/ai.sh ai "Pregunta a la IA des d'un contenidor Docker"

# Primera execució: construeix la imatge i fa la consulta
a ai "Hola, digues alguna cosa en català"
```

La imatge Docker `ai-cli` es construeix automàticament la primera vegada. Les execucions posteriors arrenquen directament.

### Reconstruir la imatge (si canvia ai.py o Dockerfile.ai)

```bash
docker build -t ai-cli -f Scripts/Dockerfile.ai Scripts/
```

---

## Ús

### Sintaxi

```
a ai [opcions] "pregunta"
```

o bé directament:

```
./Scripts/ai.sh [opcions] "pregunta"
```

### Opcions

| Opció | Descripció |
|-------|-----------|
| `-p PROVEIDOR` | Proveïdor: `claude`, `chatgpt`, `gemini`, `ollama` |
| `-m MODEL` | Model específic (sobreescriu el per defecte) |

### Exemples

```bash
# Proveïdor per defecte (Claude si no s'ha configurat AI_DEFAULT_PROVIDER)
a ai "Quina és la capital de Catalunya?"

# Escollir proveïdor explícitament
a ai -p chatgpt "Explica'm la fotosíntesi"
a ai -p gemini  "Quins planetes té el sistema solar?"
a ai -p ollama  "Resumeix aquest concepte: recursivitat"

# Escollir model específic
a ai -p claude  -m claude-opus-4-6 "Analitza aquest poema..."
a ai -p chatgpt -m gpt-4o-mini    "Tradueix: hello world"
a ai -p ollama  -m mistral        "Quina diferència hi ha entre TCP i UDP?"

# Llegir la pregunta des de stdin (pipe)
echo "Quantes lletres té 'Catalunya'?" | a ai
cat document.txt | a ai -p gemini "Resumeix aquest text:"

# Canviar el proveïdor per defecte
export AI_DEFAULT_PROVIDER="gemini"
a ai "Quin dia és avui?"   # usa Gemini
```

---

## Variables d'entorn

| Variable | Valor | Descripció |
|----------|-------|-----------|
| `ANTHROPIC_API_KEY` | `sk-ant-...` | Clau per a Claude |
| `OPENAI_API_KEY` | `sk-...` | Clau per a ChatGPT |
| `GOOGLE_API_KEY` | `AIza...` | Clau per a Gemini |
| `AI_DEFAULT_PROVIDER` | `claude` (per defecte) | Proveïdor si no s'especifica `-p` |

Les claus es defineixen al sistema amfitrió i `ai.sh` les passa al contenidor via `-e`. **No s'emmagatzemen dins la imatge Docker.**

---

## Gestió d'errors

| Situació | Missatge |
|----------|---------|
| Clau API absent | `Error: cal definir la variable d'entorn ANTHROPIC_API_KEY per usar Claude.` |
| Ollama no disponible | `Error: no s'ha pogut connectar amb Ollama a http://localhost:11434.` |
| Interrupció (Ctrl+C) | `Interromput.` (exit 130) |
