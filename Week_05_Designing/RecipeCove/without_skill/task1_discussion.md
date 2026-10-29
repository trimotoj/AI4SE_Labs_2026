# RecipeCove — záznam diskusie k Task 1

## 2026-10-29 — prvý krok: porozumenie zadaniu

### Dohodnutý spôsob spolupráce

- Študent požaduje postupnú, interaktívnu diskusiu s technicky presnými a zrozumiteľnými vysvetleniami. Chce priestor na otázky, pripomienky a vlastné závery.
- Počas Task 1 máme dôkladne preskúmať aspoň tri odlišné softvérové architektúry vrátane výhod, nevýhod, kompromisov a problémov implementácie v kontexte RecipeCove.
- Zaznamenávame iba skutočný priebeh diskusie. Predpoklady budeme výslovne označovať.
- Zatiaľ nevytvárame ADR ani AI skill, nepoužívame vlastný skill pre túto úlohu, neimplementujeme aplikáciu, nemeníme pôvodné zadania ani ostatné týždne a nerobíme git commit ani push.
- Aktuálny rozsah je iba úvodný krok; po prvej otázke čakáme na odpoveď študenta.

### Prečítané zdroje

- `Week_05_Designing/Tasks/Task_1.md`
- `Week_05_Designing/Tasks/data/RecipeCove.txt`

Task 1 vyžaduje diskusiu o troch architektúrach, porozumenie ich kompromisom a implementačným ťažkostiam. Výstupom je záznam rozhovoru.

### Úvodné vysvetlenie asistenta

RecipeCove je webová aplikácia na objavovanie receptov, získavanie informácií o receptoch a ingredienciách a organizáciu osobných kuchárskych plánov.

Funkčné požiadavky podľa zadania:

- Návštevník môže vyhľadávať recept podľa názvu, prezerať detaily receptov a ingrediencií a získať odporúčania receptov pre konkrétnu diétu. Opis systému uvádza chatbota na odporúčanie receptov.
- Registrácia cez existujúci Google účet; prihlásenie a odhlásenie registrovaného používateľa.
- Zobrazenie osobného profilu so základnými údajmi.
- Pridávanie receptov medzi obľúbené, ich odoberanie a zobrazenie zoznamu obľúbených.
- Vytvorenie a vymazanie kalendára a pridávanie udalostí pripomínajúcich prípravu konkrétneho receptu v určitý deň.

### Identifikované nejasnosti

- Nie je určený zdroj receptov a ingrediencií ani spôsob ich získavania a aktualizácie. Zadanie nepožaduje používateľské vytváranie či úpravu receptov.
- Nie je jasné, či chatbot používa pravidlá, filtrovanie, alebo jazykový model; chýba definícia podporovaných diét a spôsobu výberu odporúčaní.
- Nie je určený spôsob doručenia pripomienok ani počet kalendárov na používateľa. Prepojenie s Google Calendar nie je uvedené.
- Nie sú uvedené očakávané počty používateľov, objem dát, výkon, dostupnosť, rozpočet ani veľkosť vývojového tímu. Nemožno ich považovať za dané požiadavky.
- Pri odhlásení je formulácia dôvodu nejednoznačná („leave my information within the website“); nevyplýva z nej požiadavka na vymazanie údajov.

### Prvá otázka asistenta — čaká na odpoveď

Ako rozumieš chatbotovi v tomto zadaní: stačí podľa teba vybrať diétu a dostať vhodné recepty, alebo očakávaš rozhovor vo voľnom texte, v ktorom chatbot postupne zisťuje preferencie? Ak to zo zadania nevieme určiť, môžeme obe možnosti zatiaľ ponechať otvorené.

Dôvod otázky: jednoduché filtrovanie a konverzačný chatbot môžu vyžadovať odlišné komponenty a integrácie. Samotné slovo chatbot neznamená požiadavku na jazykový model.

### Stav rozhodnutí

Zatiaľ sme nevybrali architektúru ani technológie a neprijali dodatočné funkčné či nefunkčné predpoklady. Konkrétne architektonické alternatívy ešte neboli prediskutované. Študent zatiaľ nepoložil doplňujúce otázky ani neodpovedal na prvú otázku.

## Pokračovanie — filtrovanie a konverzačné rozhranie

### Odpoveď a otázka študenta

Študent si pod chatbotom predstavuje konverzačné rozhranie, kde používateľ prirodzeným jazykom opíše stravovacie preferencie a dostane vhodné recepty. Výslovne navrhol viesť túto predstavu ako pracovný predpoklad, nie potvrdenú požiadavku. Chce preskúmať aj jednoduchšie filtrovanie podľa diéty. Požiadal o vysvetlenie rozdielov v architektúre, implementačnej zložitosti, komponentoch a využití LLM.

### Vysvetlenie asistenta

- Obe možnosti môžu využívať rovnaký katalóg receptov a rovnakú logiku výberu. Rozdiel je najmä v prevode používateľského vstupu na kritériá výberu. Ani jedna možnosť sama osebe neurčuje architektúru celej aplikácie a konverzačné rozhranie automaticky nevyžaduje mikroslužby.
- Filtrovanie: formulár s výberom diéty → backend overí podporovanú hodnotu → výber receptov z katalógu → zobrazenie výsledkov. Logickými komponentmi sú formulár, obsluha požiadavky, logika filtrovania a prístup ku katalógu (databáza alebo adaptér externého zdroja podľa budúceho rozhodnutia). LLM nie je potrebný.
- Aj jednoduché filtrovanie potrebuje spoľahlivé údaje o receptoch a definíciu diét. Ak recepty majú vhodné označenia, dotaz môže byť jednoduchý; pri odvodzovaní z ingrediencií treba riešiť ich normalizáciu a pravidlá príslušnosti k diéte. Chýbajúce údaje nemožno automaticky považovať za potvrdenie vhodnosti. Prázdny výsledok je legitímny výsledok.
- Konverzácia: chat → interpretácia správy so zohľadnením kontextu → štruktúrované kritériá → kontrola kritérií backendom → rovnaká logika výberu → odpoveď s existujúcimi receptmi. Pre viackrokový rozhovor treba riešiť stav konverzácie; nemusí byť trvalo uložený ani viazaný na prihlásenie, keďže odporúčania sú dostupné aj návštevníkovi.
- Ilustračný vstup „Chcem vegánsku večeru“ sa môže previesť na podporované kritérium `diet = vegan`. Otázka používateľa „A niečo iné?“ ukazuje potrebu kontextu. Príklady nie sú dodatočné požiadavky na rozsah podporovaných preferencií.
- LLM môže interpretovať prirodzený jazyk, pomôcť položiť doplňujúcu otázku a formulovať odpoveď. Navrhnutou hranicou zodpovednosti je ponechať výber a overovanie existujúcich receptov aplikačnej logike. Štruktúrovaný výstup LLM treba kontrolovať: formát, podporované hodnoty, identifikátory receptov a súlad s kritériami. Správny formát nezaručuje správny význam. Nejasné alebo nepodporované preferencie sa majú objasniť, nie potichu ignorovať.
- Pri použití externého LLM pribúda integračný adaptér, ochrana prístupových údajov na serveri, časové limity, spracovanie výpadkov a nákladov na požiadavky. Treba rozhodnúť, aká časť konverzácie sa posiela poskytovateľovi. Pri lokálnom modeli sa namiesto závislosti od externého API rieši jeho prevádzka a výpočtové zdroje. Nie je potrebné automaticky pridávať vektorovú databázu, samostatnú službu ani trénovať vlastný model.
- Konverzácia je možná aj bez LLM pomocou pravidiel a rozpoznávania známych výrazov, ale širší voľný jazyk prináša viac ručne riešených formulácií a nejednoznačností. Také rozhranie musí jasne obmedziť svoje schopnosti.
- Overovanie filtra je prevažne deterministické: známe dáta a kritériá majú očakávané výsledky. Pri konverzácii treba navyše skúšať rôzne formulácie, nadväzujúce správy, nejednoznačný vstup a chybné výstupy či výpadky modelu.

### Kompromisy a stav rozhodnutí

- Filtrovanie prináša menšiu implementačnú a prevádzkovú zložitosť a predvídateľné správanie, ale používateľ je obmedzený ponúkanými voľbami.
- Konverzácia ponúka prirodzenejšie vyjadrenie preferencií za cenu zložitejšej interpretácie, správy kontextu, overovania a prípadnej prevádzky LLM.
- Pracovný predpoklad konverzačného rozhrania pochádza od študenta. Jednoduchší filter zostáva otvorenou alternatívou. Použitie LLM ani konkrétna architektúra neboli schválené.
- Asistent navrhol ako možnosť oddeliť výber receptov od interpretácie vstupu, aby ho vedel použiť filter aj chat. Ide zatiaľ o návrh na diskusiu, nie spoločné rozhodnutie.
- Toto je porovnanie dvoch variantov funkcie odporúčania; ešte nejde o splnenie požiadavky dôkladne preskúmať tri architektúry celej aplikácie.

### Otázka na pokračovanie — čaká na odpoveď

Dáva ti zmysel, aby chatbot iba prekladal želanie používateľa na kritériá a konečný výber receptov robila bežná aplikačná logika, alebo by si časť samotného výberu zveril aj LLM? Prečo?

## Pokračovanie — dohodnuté zodpovednosti a prvá architektúra

### Závery študenta

- Študent uprednostnil oddelenie interpretácie požiadavky od výberu receptov. LLM má prevádzať prirodzený jazyk na štruktúrované kritériá a prípadne formulovať odpovede. Backend má kritériá overovať a vyhľadávať recepty.
- Dôvody: predvídateľnosť, jednoduchšie testovanie a spoľahlivejšie dodržiavanie diétnych obmedzení.
- LLM by prípadne mohlo zoradiť recepty, ktoré už prešli filtrovaním. Ide o možnosť, nie povinnú funkciu; poradie nesmie obísť filter ani pridať neoverené recepty.
- Študent rozlišuje toto rozhodnutie od výberu architektúry celej aplikácie. Požiadal začať prvou z troch architektúr a zatiaľ neprechádzať na ďalšie dve.
- Dohoda o zodpovednostiach platí pre konverzačný variant. Samotný rozsah chatbota zostáva pracovným predpokladom a filter otvorenou alternatívou.

### Prvá predstavená architektúra: modulárny monolit

Asistent predstavil jeden backend nasadzovaný ako celok, vnútorne rozdelený na moduly s jasnými rozhraniami. Webový frontend komunikuje s backendom cez HTTP; moduly medzi sebou volajú funkcie/metódy v rovnakom procese. Google identita a prípadný externý LLM sú sieťové integrácie. Monolit neznamená jednu triedu ani nutne iba jednu bežiacu inštanciu.

Pre konkrétny náčrt asistent navrhol spoločnú relačnú databázu a katalóg dostupný cez modul Katalóg. Je to návrhový variant, nie požiadavka zadania; zdroj a aktualizácia receptov ostávajú otvorené. Adaptér externého katalógu môže byť skrytý za rovnakým rozhraním, ale mení dostupnosť a konzistenciu dát.

Navrhnuté moduly a ich zodpovednosti:

- Identita a profil: Google prihlásenie/registrácia, lokálna identita, relácia, odhlásenie, profil.
- Katalóg: recepty, ingrediencie, detaily a vyhľadávanie podľa názvu; vlastní prístup k týmto dátam.
- Odporúčania: overovanie podporovaných kritérií a výber vhodných receptov cez rozhranie katalógu.
- Konverzácia: kontext rozhovoru a adaptér LLM; interpretácia vstupu, volanie odporúčaní a príprava odpovede.
- Obľúbené: používateľské zoznamy a pridávanie/odoberanie receptov.
- Kalendár: vytváranie/mazanie kalendára a pridávanie udalostí s odkazom na recept a deň.

### Komunikácia na konkrétnych funkciách

1. Vyhľadávanie podľa názvu: frontend → HTTP backendu → Katalóg → databáza → výsledky. Nie je potrebné volanie LLM. Filter podľa diéty používa Odporúčania → Katalóg.
2. Chat: frontend → Konverzácia → LLM → štruktúrované kritériá → Odporúčania (kontrola a filtrovanie) → Katalóg → výsledky → odpoveď. Prípadné zoradenie modelom sa obmedzí na identifikátory v už vyfiltrovanej množine; backend tento výstup overí. Pri nejasnej interpretácii sa požiadavka objasňuje. Výpadok LLM nemusí zablokovať samostatný filter ani vyhľadávanie.
3. Obľúbené: backend zistí používateľa z overenej relácie, Obľúbené overia recept cez Katalóg a uložia väzbu používateľ–recept. Jedinečné obmedzenie dvojice v databáze zabráni duplicitám aj pri súbehu. Samotné overenie „ešte neexistuje“ pred zápisom na súbeh nestačí.
4. Kalendár: Kalendár overí vlastníctvo kalendára a referenciu na recept a uloží udalosť. Podmienka vlastníctva musí byť v serverovej operácii; identifikátor poslaný klientom nepreukazuje oprávnenie. V tejto databázovej variante možno vymazanie kalendára a jeho udalostí urobiť atómovo v transakcii alebo pomocou vhodnej kaskády.
5. Google prihlásenie: Identita overí výsledok prihlásenia od Google, nájde alebo vytvorí lokálneho používateľa a vytvorí reláciu. Ostatné moduly pracujú s lokálnou identitou. Google prihlásenie neznamená integráciu s Google Calendar.

Spôsob doručovania pripomienok nie je rozhodnutý. Pri udalosti pre konkrétny deň treba odlíšiť kalendárny dátum od časového okamihu. Ak by sa dohodli aktívne notifikácie, bolo by potrebné plánovanie úloh a riešenie opakovaného doručenia; v aktuálnom návrhu to nie je potvrdená funkcia.

### Výhody, nevýhody a konkrétne implementačné problémy

- Jeden backend zjednodušuje nasadenie, sledovanie toku požiadavky a lokálne testovanie. Vnútorné volania nepotrebujú sieťový protokol. Spoločná databáza umožňuje transakcie cez súvisiace zápisy.
- Hranice modulov treba vynucovať: napríklad Konverzácia nemá čítať tabuľky receptov priamo a obísť pravidlá Odporúčaní. Spoločná databáza sama osebe modularitu nezaručuje. Pomáha vlastníctvo tabuliek, verejné rozhrania a kontrola závislostí pri zostavení alebo revízii kódu.
- Moduly sa nasadzujú spoločne. Aj zmena kalendára znamená nové nasadenie backendu. Replikovať možno celý backend; jednotlivé moduly sa samostatne neškálujú. Viac inštancií vyžaduje vyriešiť zdieľanie relácií a prípadného kontextu rozhovoru.
- Zdieľaný proces a prostriedky znižujú izoláciu porúch. Pomalé LLM volania môžu vyčerpať kapacitu aj pre iné funkcie. Potrebné sú časové limity, obmedzenie súbežných volaní a nedržanie databázovej transakcie počas čakania na LLM. Samotná prítomnosť timeoutu nezaručuje úplnú izoláciu.
- Dostupnosť a význam diétnych údajov zostávajú problémom aj pri jednoduchej architektúre. Treba určiť správanie pri neúplných dátach a odstránení alebo nedostupnosti receptu odkazovaného z obľúbených či kalendára. Ak je katalóg externý, lokálna transakcia nezaručí jeho nemennosť alebo dostupnosť.
- Primeraná stratégia overovania zahŕňa testy filtrov, oprávnení a databázovej integrity a integračné testy tokov. LLM adaptér sa dá v bežných testoch nahradiť kontrolovanými odpoveďami; kvalita interpretácie sa hodnotí osobitne na príkladoch. Žiadna aplikácia ani testy sa teraz neimplementovali.

### Aktuálny stav a otvorená otázka

Modulárny monolit je prvý kandidát na diskusiu, nie zvolená výsledná architektúra. Zatiaľ bol predstavený; otázky a hodnotenie študenta k nemu ešte nepoznáme. Ďalšie dve architektúry zatiaľ neboli predstavené.

Otázka asistenta: Predstav si, že LLM odpovedá veľmi pomaly, ale používateľ si chce pridať recept medzi obľúbené. Čo podľa teba musí backend zabezpečiť, aby ho chat neblokoval? Stačí na to rozdelenie kódu na moduly?

## Pokračovanie — súbežné požiadavky v modulárnom monolite

### Odpoveď a otázka študenta

Študent správne odlíšil modularitu od súbežnosti. Navrhol asynchrónne I/O alebo viacerých pracovníkov servera, časové limity a obmedzenie spotreby spoločných zdrojov. Požiadal o jednoduchý konkrétny príklad implementácie v modulárnom monolite.

### Vysvetlenie a ilustračný príklad asistenta

Asistent ukázal Pythonový náčrt dvoch asynchrónnych obslúh v jednom backendovom procese. Nejde o implementáciu aplikácie, výber technológií ani spustiteľný kompletný server; HTTP smerovanie, klient LLM, databázové adaptéry a prevod výnimiek na HTTP odpovede sú abstrakcie.

```python
import asyncio

class ChatBusy(Exception):
    pass

class ChatUnavailable(Exception):
    pass

# Jedna zdieľaná inštancia na proces, nie nová pre každú požiadavku.
llm_slots = asyncio.Semaphore(4)

async def chat(message, context):
    try:
        await asyncio.wait_for(llm_slots.acquire(), timeout=0.05)
    except TimeoutError:
        raise ChatBusy()

    try:
        raw = await asyncio.wait_for(
            llm.interpret_async(message, context), timeout=8.0
        )
    except TimeoutError:
        raise ChatUnavailable()
    finally:
        llm_slots.release()

    criteria = recommendations.validate(raw)
    recipes = await recommendations.find_async(criteria)
    return {"recipes": recipes}

async def add_favorite(current_user, recipe_id):
    await catalog.require_exists_async(recipe_id)
    await favorites.insert_if_absent_async(current_user.id, recipe_id)
    return {"saved": True}
```

Čísla 4, 0.05 sekundy a 8 sekúnd sú výlučne ilustračné, nie požiadavky ani zmerané vhodné nastavenie. `current_user` pochádza z overenej relácie. `insert_if_absent_async` predpokladá databázové jedinečné obmedzenie dvojice používateľ–recept a vhodné spracovanie konfliktu. `ChatBusy` sa mapuje napríklad na HTTP 503, `ChatUnavailable` pri prekročení času externého volania napríklad na HTTP 504; mapovanie musí zabezpečiť HTTP vrstva, inak by išlo o neobslúžené výnimky.

Počas skutočne asynchrónneho sieťového čakania na LLM môže slučka udalostí spracovať požiadavku na obľúbené. Semafor obmedzuje rozpracované LLM volania a krátky limit čakania na jeho získanie bráni dlhému čakaniu v tejto bráne. Nejde o úplné obmedzenie všetkých prichádzajúcich požiadaviek; pri preťažení treba aj serverové limity prijímania požiadaviek. Vyčerpanie kapacity chatu sa v príklade oznámi klientovi, nepresunie sa do neobmedzenej fronty.

Samotné `async def` ani `await` neurobia blokujúcu knižnicu neblokujúcou. LLM aj databázové adaptéry musia používať skutočne asynchrónne I/O alebo vhodne obmedzený pool pracovníkov. Dlhý výpočet môže slučku udalostí blokovať a potrebuje osobitné riešenie. Počas LLM volania sa nemá držať databázové spojenie, transakcia ani globálny zámok. HTTP klient potrebuje vlastné sieťové timeouty a podporu zrušenia; zrušenie lokálneho čakania nezaručuje zastavenie práce u poskytovateľa LLM.

Semafor platí iba pre jeden proces: tri procesy s limitom štyri môžu spolu vykonať dvanásť volaní. Globálny limit by potreboval koordináciu alebo iné rozdelenie kapacity. Moduly naďalej zdieľajú CPU, pamäť a databázový pool, takže nejde o úplnú izoláciu porúch. Dva scenáre vhodné na overenie návrhu sú pomalé LLM pri súbežnom pridaní obľúbeného receptu a obsadenie všetkých LLM slotov pri ďalšej chatovej požiadavke. Žiadne testy ani aplikácia sa v tomto kroku nespúšťali ani neimplementovali.

### Stav diskusie

Naďalej skúmame prvú architektúru, modulárny monolit. Nebol zvolený konkrétny jazyk, framework ani konečná architektúra. Otázka asistenta na pokračovanie: Čo by sa podľa teba stalo, keby chat pred čakaním na LLM získal databázové spojenie a držal ho až do príchodu odpovede — aj keby samotné volanie LLM bolo asynchrónne?

## Pokračovanie — uzavretie základov monolitu a druhá architektúra

### Odpoveď a záver študenta

Študent vysvetlil, že držanie databázového spojenia počas čakania na LLM zbytočne obsadzuje connection pool. Viac chatových požiadaviek by mohlo pool vyčerpať a tým zdržať alebo znemožniť aj pridávanie obľúbených receptov. Navrhol používať spojenia iba počas potrebných databázových operácií a uvoľniť ich pred čakaním na LLM. Asistent potvrdil vysvetlenie; rovnaké pravidlo platí aj pri ďalšej architektúre.

Študent uviedol, že rozumie základom modulárneho monolitu, jeho výhodám a implementačným kompromisom. Požiadal prejsť na druhú odlišnú architektúru, priebežne ju porovnávať s monolitom, pokračovať interaktívne a zatiaľ neprechádzať na tretiu.

### Druhá architektúra: mikroslužby

Asistent predstavil samostatne bežiace a nasadzované služby s komunikáciou cez sieťové API. Na rozdiel od interného volania funkcie v monolite sieťové volanie prináša oneskorenie a možnosť čiastočného výpadku. Služby vlastnia svoje dáta a ostatné služby ich používajú cez rozhrania, nie priamym čítaním cudzích tabuliek. Samostatné vlastníctvo dát nevyžaduje samostatný fyzický databázový server pre každú službu; zdieľaná infraštruktúra však znižuje izoláciu.

Ilustračné rozdelenie, nie konečné rozhodnutie:

- Identita a profil: Google prihlásenie, lokálna identita a profil.
- Recepty a odporúčania: katalóg, ingrediencie, validácia kritérií a filtrovanie; tieto súvisiace časti zatiaľ zostávajú spolu.
- Konverzácia: kontext a LLM adaptér; volá službu Recepty a odporúčania.
- Obľúbené: väzby používateľov na recepty.
- Kalendár: kalendáre a ich udalosti.

Frontend komunikuje cez vstupnú bránu (API gateway), ktorá smeruje požiadavky. Brána je návrhová voľba, nie definícia mikroslužieb; potrebuje vlastné limity a prevádzku. Citlivé operácie musia mať overenú identitu a kontrolu oprávnení; nestačí dôverovať ľubovoľnému používateľskému identifikátoru od klienta. Identitu možno bezpečne overovať lokálne na základe podpísaných údajov, takže každá operácia nemusí povinne volať službu identity.

### Konkrétne toky a porovnanie

- Vyhľadávanie podľa názvu: frontend → brána → Recepty a odporúčania → jej úložisko. V monolite ide po príchode požiadavky o interné volanie Katalógu; tu smerujeme do samostatného procesu.
- Chat: frontend → brána → Konverzácia → LLM → Konverzácia → Recepty a odporúčania → výsledky. Dohodnutá zodpovednosť LLM a backendu sa nemení. Overovanie a filtrovanie zostáva v službe Recepty a odporúčania. Jednoduchý filter ju volá priamo cez bránu a nezávisí od Konverzácie.
- Pomalý alebo nefunkčný chat nemusí spotrebovať procesové pracovníky a databázové spojenia služby Obľúbené. To predpokladá správne oddelené limity a zdroje. Spoločná brána, databázový server alebo hostiteľ zostávajú spoločnými rizikami; závislosť na nedostupnom katalógu môže ovplyvniť aj obľúbené.
- Pridanie obľúbeného receptu: Obľúbené overia používateľa, cez API overia recept a lokálne uložia väzbu s jedinečným obmedzením. Monolit so spoločnou databázou môže použiť cudzí kľúč a lokálnu transakciu. Pri samostatných dátach nemáme bežný lokálny cudzí kľúč na katalóg ani spoločnú atómovú transakciu. Kontrola receptu pred zápisom nezaručí, že sa medzičasom nezmení jeho dostupnosť.
- Pri výpadku služby Recepty vzniká produktové rozhodnutie: zápis obľúbeného receptu odmietnuť, alebo ho prijať s odloženým overením. Druhá možnosť vyžaduje stav čakajúceho overenia, opakované spracovanie a riešenie neplatnej referencie. Zatiaľ nebola zvolená.
- Vymazanie kalendára a jeho udalostí môže zostať jednou lokálnou transakciou, pretože ich vlastní tá istá služba. Mikroslužby teda neznamenajú zrušenie všetkých databázových transakcií; problémom sú operácie cez hranice služieb.

### Implementačné kompromisy

- Samostatné nasadzovanie a škálovanie umožňuje pridať kapacitu Konverzácii bez replikovania Kalendára. Máme však viac procesov, konfigurácií, úložísk a nasadzovaní.
- Každé sieťové volanie potrebuje timeout a rozpočet času pre celý reťazec. Opakovať zápis naslepo je nebezpečné: timeout nepreukazuje, že sa zápis nevykonal. Jedinečné obmedzenia alebo identifikátory operácií pomáhajú dosiahnuť bezpečné opakovanie. Pri problémoch môže byť vhodné dočasne prerušiť volania nefunkčnej služby (circuit breaker).
- Chybu treba sledovať naprieč službami pomocou spoločného identifikátora požiadavky a prepojených logov. Rozhrania a dátové formáty musia umožňovať kompatibilné zmeny počas postupného nasadzovania. Potrebné sú aj testy kompatibility API a scenárov s výpadkami.
- Oddelené procesy prinášajú lepšiu možnosť izolácie porúch, ale závislosti ju môžu znovu oslabiť. Samotné rozdelenie na služby nezaručuje spoľahlivosť.
- Broker správ ani Kubernetes nie sú automaticky potrebné. Pre tento úvodný variant používame synchrónne HTTP API. Menšie služby nie sú cieľom samy osebe; preto sa katalóg a filtrovanie nerozdeľujú bez preukázanej potreby.
- Nie sú známe rozsah prevádzky ani tímy, ktoré by nezávislé nasadzovanie vyžadovali. Asistent zatiaľ nevidí v zadaní dostatočný dôvod uprednostniť vyššiu zložitosť mikroslužieb pred monolitom; nejde o konečný výber architektúry.

### Stav a otázka na pokračovanie

Druhá architektúra bola predstavená, jej dôkladné interaktívne preskúmanie pokračuje. Tretia ešte nebola predstavená. Nebol prijatý nový funkčný predpoklad ani konečné rozhodnutie o architektúre.

Otázka asistenta: Ak používateľ pridáva recept medzi obľúbené a služba Recepty práve neodpovedá, uprednostnil by si zápis odmietnuť s možnosťou skúsiť to znovu, alebo ho prijať a recept overiť neskôr? Aký kompromis by si tým prijal?

## Pokračovanie — rozhodnutie pri výpadku katalógu a scenár rastu

### Rozhodnutie študenta a jeho zdôvodnenie

Pre skúmaný variant mikroslužieb študent zvolil odmietnutie pridania receptu medzi obľúbené, ak služba Recepty nie je dostupná a nemožno overiť jeho existenciu. Zápis sa neuloží ako čakajúci; používateľ dostane informáciu o dočasnom probléme a môže operáciu skúsiť neskôr.

Študent túto operáciu považuje pre RecipeCove za nekritickú a dočasné odmietnutie za primerané. Výhodou je jednoduchšia implementácia bez čakajúcich zápisov, dodatočného overovania a riešenia neplatných záznamov z tohto postupu. Výslovne prijíma menšiu dostupnosť v prospech jednoduchosti a predvídateľnosti. Rozumie, že úspešná kontrola existencie nezaručuje budúcu dostupnosť receptu; tento problém rozhodnutie neodstraňuje. Nejde o výber mikroslužieb za výslednú architektúru ani o všeobecné pravidlo pre všetky zápisy.

### Otázka študenta

Pred uzavretím druhej architektúry chce pochopiť konkrétny scenár rastu, v ktorom by prínosy mikroslužieb prevážili ich zložitosť, a stručne porovnať mikroslužby s modulárnym monolitom. Tretiu architektúru zatiaľ nežiada predstaviť.

### Vysvetlenie asistenta: hypotetický rast, nie požiadavka zadania

Asistent opísal postupný scenár: RecipeCove spočiatku vyvíja jeden tím a modulárny monolit postačuje. Neskôr výrazne narastie používanie chatu, zatiaľ čo používanie kalendára sa mení málo. Vzniknú samostatné tímy pre konverzáciu, katalóg a osobné funkcie, ktoré potrebujú rozdielne tempo nasadzovania. Ide výlučne o hypotetické predpoklady na porovnanie, nie fakty o projekte.

- Samotný nárast počtu používateľov nie je dôvod na mikroslužby. Najskôr treba merať, optimalizovať dotazy a indexy, podľa potreby používať cache a replikovať monolit. Nárast sa môže týkať databázy, ktorú samotné rozdelenie backendu neodľahčí.
- Oddelenie Konverzácie môže mať zmysel, keď merania ukážu, že jej špičky opakovane vyčerpávajú kapacitu spoločného procesu alebo že replikovanie celého backendu kvôli chatu je nákladné. Samostatná služba môže mať vlastnú kapacitu, limity a nasadzovanie. Nezvyšuje však automaticky kvótu poskytovateľa LLM ani nezrýchli jeho odpovede. Neobmedzené pridávanie inštancií môže zvýšiť náklady a počet požiadaviek na závislé služby.
- Viac samostatných tímov môže nezávisle meniť vnútornú implementáciu svojich služieb, pokiaľ zachovajú kompatibilné API. Pri monolite je možné súbežne vyvíjať moduly, ale vydáva sa spoločný artefakt. Ak každá zmena vyžaduje koordinované vydanie viacerých služieb, očakávaná nezávislosť sa nenaplnila.
- Oddelenie pomáha obmedziť dosah zlyhania Konverzácie na procesové zdroje Obľúbených a Kalendára, ak majú skutočne oddelené zdroje a limity. Služba Obľúbené však podľa prijatého rozhodnutia stále odmietne zápis, keď nevie overiť recept cez nedostupnú službu Recepty.
- Podmienkou prínosu je schopnosť prevádzkovať viac služieb: automatizované nasadzovanie, monitoring, prepojené logy, správa konfigurácií, bezpečná komunikácia a kompatibilita API. Výhodu treba porovnať s konkrétnymi prevádzkovými a vývojovými nákladmi; neexistuje univerzálny počet používateľov ako hranica.
- Rozumná cesta môže byť najskôr vyčleniť iba Konverzáciu za stabilným rozhraním a zvyšok ponechať v modulárnom monolite. Je to možnosť postupného prechodu k mikroslužbám, nie tretia architektúra ani prijaté rozhodnutie. Rozhranie modulu pomáha, ale extrakcia stále vyžaduje riešiť sieťové chyby, identitu, kontext konverzácie, dáta a nasadenie.

### Stručné porovnanie

| Oblasť | Modulárny monolit | Mikroslužby |
|---|---|---|
| Nasadenie | Jeden artefakt, jednoduchšia koordinácia prevádzky | Nezávislé vydania, viac nasadzovaní a konfigurácií |
| Komunikácia | Interné volania s menšou réžiou | Sieťové API, timeouty, čiastočné výpadky |
| Dáta | Jednoduchšie lokálne transakcie a referenčná integrita | Lokálne transakcie v službe; vzťahy cez služby vyžadujú ďalšie pravidlá |
| Škálovanie | Typicky replikovanie celého backendu | Cielené pridávanie kapacity jednotlivým službám, závislosti zostávajú limitom |
| Poruchy | Spoločný proces a zdroje, menšia izolácia | Lepšia možnosť izolácie, oslabená spoločnými zdrojmi a závislosťami |
| Vývoj a overovanie | Jednoduchšie sledovanie toku a integračné testy; potreba strážiť modularitu | Samostatnosť tímov za cenu kompatibility API a testovania výpadkov |

### Stav diskusie

Prínosy mikroslužieb sú podmienené preukázanou potrebou nezávislého škálovania, nasadzovania alebo izolácie a schopnosťou niesť prevádzkové náklady. Známe zadanie takú potrebu zatiaľ nepreukazuje. Konečná architektúra nebola vybraná. Tretia architektúra nebola predstavená.

Otázka asistenta na reflexiu: Ktorý z uvedených signálov by bol pre teba najsilnejším dôvodom oddeliť Konverzáciu od monolitu: namerané problémy so zdrojmi, potreba nezávislých vydaní tímov, alebo izolácia porúch?

## Pokračovanie — meranie pred extrakciou a tretia architektúra

### Názor a zdôvodnenie študenta

Študent považuje za najsilnejší dôvod oddelenia Konverzácie namerané problémy so zdrojmi. Najskôr chce monitoringom identifikovať konkrétne úzke miesto a overiť jednoduchšie riešenia v modulárnom monolite. Samotná možnosť nezávislého škálovania nie je dostatočný dôvod zaviesť mikroslužby. Ak by chat preťažoval backend a poškodzoval ostatné funkcie, oddelenie by mohlo priniesť izoláciu zdrojov a nezávislé škálovanie. Rozumie, že extrakcia nevyrieši limit externého LLM poskytovateľa.

Študent považuje modulárny monolit a mikroslužby za dostatočne preskúmané. Požiadal predstaviť tretiu odlišnú architektúru, pokračovať interaktívne a zatiaľ nevyberať konečnú architektúru ani nevytvárať ADR.

### Tretí kandidát: serverless funkcie a spravované služby

Asistent predstavil konkrétny serverless variant: staticky hostovaný webový frontend, HTTP/API brána, funkcie spúšťané požiadavkami, spravovaná relačná databáza, overovanie Google identity a externý LLM adaptér. Spravovaná relačná databáza je návrhová voľba, nie požiadavka zadania. Zdroj a aktualizácia receptov zostávajú otvorené; prístup ku katalógu možno zapuzdriť adaptérom. Nie je vybraný cloud, produkt, cenový plán ani databázová technológia.

Serverless znamená, že platforma spravuje vykonávanie a prideľovanie inštancií funkcií; servery naďalej existujú. Vývojár stále zodpovedá za kód, oprávnenia, limity, dátový model a prevádzkové správanie. Predchádzajúce návrhy boli jeden trvalo bežiaci backend a samostatne prevádzkované služby; tu nasadzujeme obsluhy udalostí/požiadaviek do spravovaného prostredia. Ide o odlišný prevádzkový model. Modulárnosť a mikroslužby opisujú aj iné aspekty návrhu a môžu sa so serverless kombinovať; názvy nie sú vzájomne výlučné kategórie.

Logické skupiny funkcií:

- Vyhľadávanie, detaily receptov a ingrediencií a odporúčania: používajú modul Katalóg a deterministické pravidlá filtrovania.
- Chat: prevod vstupu cez LLM, kontrola kritérií a filtrovanie; v tomto variante môže použiť rovnakú verzovanú knižnicu odporúčaní priamo bez volania ďalšej funkcie.
- Obľúbené: overená identita, kontrola receptu a zápisy do databázy.
- Kalendár: kontrola vlastníctva, vytváranie/mazanie kalendára a pridávanie udalostí.
- Identita a profil: overenie výsledku Google prihlásenia, lokálny používateľ a profil. Google prihlásenie neznamená Google Calendar.

Konkrétna granularita balíkov funkcií ostáva otvorená; nie je potrebné mať jednu funkciu pre každý pomocný krok. V tomto variante používajú funkcie spoločnú databázu s určeným vlastníctvom tabuliek. Nepredpokladáme databázu na funkciu ani oddelené dátové vlastníctvo ako v predchádzajúcom mikroslužbovom variante.

### Komunikácia a konkrétne implementačné problémy

- Vyhľadávanie: prehliadač → API brána → funkcia vyhľadávania → databáza → odpoveď. Platforma prideľuje inštancie podľa prevádzky v rámci nastavených a dostupných limitov.
- Chat: brána → funkcia chatu → LLM → overenie kritérií → databázové vyhľadávanie → odpoveď. Databázové spojenie sa nedrží počas čakania na LLM. Pravidlá filtrovania zostávajú rovnaké ako pri predchádzajúcich návrhoch. LLM prístupové údaje zostávajú na serverovej strane.
- Kontext konverzácie nesmie závisieť od pamäte jednej inštancie, pretože ďalšia správa môže prísť do inej. Možno ho držať v úložisku podľa identifikátora konverzácie alebo odovzdávať z klienta s primeranou kontrolou. Návrhovou možnosťou je krátkodobé úložisko s expiráciou; nie je rozhodnuté trvalé archivovanie rozhovorov. Prístup musí chrániť aj konverzácie návštevníkov bez účtu.
- Obľúbené a kalendár môžu používať lokálne databázové transakcie a cudzie kľúče, lebo tento variant má spoločnú relačnú databázu. Serverless samo osebe neznamená eventual consistency. Ak nemožno overiť recept pre nedostupnosť dátového zdroja, možno zachovať dohodnuté odmietnutie zápisu bez čakania na dodatočné overenie; konkrétna závislosť už nemusí byť služba Recepty.
- Odhlásenie a overovanie relácií musia fungovať naprieč inštanciami; stav len v pamäti jednej funkcie nie je spoľahlivým základom.

### Výhody a kompromisy

- Platforma preberá správu vykonávacích inštancií. Pri nepravidelnej prevádzke môže byť výhodné prideľovanie kapacity a účtovanie podľa použitia; nejde o záruku nižších nákladov. Náklady zahŕňajú aj databázu, bránu, úložisko kontextu, logy a LLM. Čakanie na LLM môže podľa modelu účtovania stáť peniaze.
- Studený štart môže pridať oneskorenie pri inicializácii. Funkcia aj API brána majú časové limity, ktoré treba zistiť pre zvolenú platformu a zosúladiť s LLM timeoutom. Nie je univerzálny číselný limit pre serverless všeobecne. Ak sa synchrónny chat do limitu nezmestí, možno zvážiť úlohu spracovanú na pozadí a neskoršie vyzdvihnutie výsledku, ale pribudne fronta, stav úlohy a zložitejšie používateľské rozhranie. Nie je to zatiaľ súčasť zvoleného návrhu.
- Automatické škálovanie funkcií môže vyčerpať spojenia relačnej databázy alebo LLM kvótu. Malý pool v každej inštancii sa násobí počtom inštancií. Potrebné sú limity súbežnosti, vhodná správa/prípadné sprostredkovanie databázových spojení a ochrana závislostí.
- Semafor v pamäti jednej inštancie neobmedzí všetky inštancie. Pri limitoch chatu treba podľa schopností platformy vyhradiť kapacitu pre ostatné funkcie a koordinovať celkový rozpočet LLM volaní. Zdieľané limity účtu môžu oslabiť izoláciu.
- Timeout alebo opakovanie požiadavky môže viesť k opakovanému vykonaniu. Pri obľúbených pomáha jedinečná dvojica používateľ–recept; pri vytvorení udalosti môže pomôcť identifikátor operácie. Dve úmyselné udalosti s rovnakými údajmi nemožno automaticky považovať za jednu len podľa obsahu.
- Viac konfigurácie, oprávnení a logov, závislosť od poskytovateľských rozhraní a potreba overiť správanie v reálnom spravovanom prostredí. Jednotkové testovanie pravidiel zostáva jednoduché, lokálne testy však nenahradia overenie cloudových limitov a oprávnení.
- Aktívne notifikácie ani integrácia Google Calendar sa nepridali ako požiadavky. Ak sa neskôr dohodnú aktívne pripomienky, plánovaná udalosť môže spúšťať funkciu; jej doručovanie by vyžadovalo osobitný návrh.

### Stav a otázka na pokračovanie

Serverless variant bol predstavený ako tretí kandidát. Zatiaľ nepoznáme otázky a hodnotenie študenta k nemu; jeho interaktívne skúmanie pokračuje. Nevybrali sme finálnu architektúru, nevytvorili ADR ani aplikáciu.

Otázka asistenta: Predstav si, že pri špičke platforma spustí 100 inštancií funkcie chatu a každá má semafor povoľujúci štyri LLM volania. Chránilo by to spoločnú kvótu poskytovateľa LLM? Kde by si chcel uplatniť limit? Čísla sú iba ilustračné.

## Pokračovanie — odlišnosť serverless návrhu a porovnanie troch kandidátov

### Odpoveď a pripomienka študenta

Študent vysvetlil, že 100 inštancií s lokálnym limitom štyroch môže umožniť až 400 súbežných LLM volaní. Navrhol centrálne koordinované obmedzovanie naprieč inštanciami vrátane súbežnosti, počtu požiadaviek a tokenov za časové obdobie. Rozumie riziku preťaženia databázy a LLM pri automatickom škálovaní. Asistent spresnil, že celkový koordinovaný limit nemusí znamenať jediný fyzický proces; pri tokenoch treba rátať aj s neznámou dĺžkou budúcej odpovede, napríklad konzervatívnou rezerváciou a následným vyúčtovaním. Limiter sám potrebuje definované správanie pri výpadku.

Študent upozornil na kombinovateľnosť serverless s inými architektúrami. Požiadal objasniť konkrétnu odlišnosť od nášho mikroslužbového návrhu a primeranosť tretej alternatívy pre zadanie. Ďalej požiadal stručné porovnanie troch návrhov podľa implementácie, prevádzkových nákladov, škálovateľnosti, spoľahlivosti a izolácie, konzistencie a vhodnosti pre RecipeCove. Výslovne naďalej nechce ADR ani finálny výber.

### Spresnenie asistenta: porovnávame konkrétne návrhy

Serverless nie je logický protiklad mikroslužieb. Samotné presunutie rovnakých mikroslužieb do serverless prostredia by nebolo presvedčivým vysvetlením tretej architektúry. Rozdiely v našich konkrétnych návrhoch sú:

- Mikroslužby: samostatne bežiace služby s vlastníctvom dát; Konverzácia volá sieťové API služby Recepty a odporúčania; Obľúbené nemajú bežný lokálny databázový cudzí kľúč do katalógu. Lokálne transakcie končia na hranici služby. Kapacitu dlhšie žijúcich procesov riadime prevádzkovou konfiguráciou; aj tieto služby možno automaticky škálovať.
- Serverless variant: krátkodobé vykonania funkcií vyvolané požiadavkami, spravovaný životný cyklus inštancií a spoločná relačná databáza. Konverzácia a filter môžu používať spoločnú knižnicu pravidiel priamo a pristupovať ku katalógu cez dátový adaptér, bez samostatnej služby Recepty. Databázové cudzie kľúče a transakcie cez súvisiace tabuľky sú možné. Funkcie nemajú byť závislé od lokálnej pamäte na správnosť ďalšej požiadavky; kontext a relácie sú dostupné mimo konkrétnej inštancie. Toto pravidlo platí aj pre replikované mikroslužby či monolit, ale pri funkciách je základným predpokladom návrhu.
- Serverless variant presúva väčšiu časť plánovania vykonávania na platformu a prináša explicitné časové limity vykonania, studené štarty a násobenie poolov pri vzniku inštancií. Aj mikroslužby majú časové limity a prevádzkové kvóty; nejde o absolútnu vlastnosť iba jednej kategórie.
- Spoločná databáza a spoločná knižnica vytvárajú väzby: funkcie musia koordinovať kompatibilitu schémy a verzie pravidiel. Viac funkcií neznamená automaticky nezávislosť mikroslužieb. Hranice vlastníctva tabuliek treba stále rešpektovať.

Asistent hodnotí tento konkrétny návrh ako obhájiteľnú tretiu alternatívu pre text Task 1: líši sa nasadením, dátovými hranicami aj komunikáciou, nie iba názvom hostingu. Zadanie vyžaduje tri architektúry, ale neustanovuje taxonómiu ani zakázané kombinácie. Hodnotenie vyučujúceho nemožno zaručiť. V zázname treba otvorene uviesť, že ide o tri konkrétne návrhy s čiastočne sa prekrývajúcimi architektonickými princípmi. Samostatné kategórie s úplne nezávislými vlastnosťami by boli nepresným zjednodušením.

### Porovnanie konkrétnych variantov

| Kritérium | Modulárny monolit | Mikroslužby | Serverless funkcie a spoločná DB |
|---|---|---|---|
| Implementačná zložitosť | Relatívne nižšia; vnútorné rozhrania, lokálne transakcie | Vyššia; sieťové API, čiastočné výpadky, dátové hranice a kompatibilita | Menej správy procesov; zložitejšia cloudová konfigurácia, externý stav, limity a opakovanie |
| Prevádzkové náklady | Menšia prevádzková réžia; náklady kapacity celého backendu | Viac služieb, monitoringu a práce; možná úspora cieleným škálovaním | Závisia od platformy a priebehu záťaže; potenciál pri nepravidelnej prevádzke, náklady volaní, trvania a spravovaných služieb |
| Škálovateľnosť | Replikovanie backendu; treba chrániť DB a LLM | Cielená kapacita služieb; závislosti a kvóty zostávajú | Platforma škáluje vykonania v rámci limitov; nutná kontrola súbežnosti, spojení a LLM kvót |
| Spoľahlivosť a izolácia | Jednoduchší tok, menej sieťových hraníc; spoločný proces a zdroje | Lepšia možnosť izolácie; viac čiastočných zlyhaní a závislostí | Spravované vykonávanie, oddelené funkcie; spoločná DB, brána, kvóty a regionálne/platformové výpadky |
| Konzistencia dát | Spoločná DB umožňuje transakcie a cudzie kľúče | Lokálne transakcie; cez služby dodatočné pravidlá, bez automatickej celkovej konzistencie | V našom variante spoločná relačná DB umožňuje transakcie a cudzie kľúče; nezaručuje atómovosť s LLM |
| Aktuálne RecipeCove | Priama cesta na splnenie funkcií s malým počtom prevádzkových častí | Funkčne možné, ale potreba vyššej zložitosti nie je v zadaní preukázaná | Funkčne možné pri vhodných limitoch a dostupnej platforme; výhodnosť nemožno určiť bez údajov o záťaži a nákladoch |

Náklady nie sú iba faktúra za infraštruktúru, ale aj čas správy a riešenia incidentov. Pre žiadny variant neboli známe ceny, nameraná záťaž ani SLA; porovnanie je kvalitatívne. Žiadny variant automaticky nevyrieši kvótu LLM alebo kvalitu diétnych dát. Presadzovanie transakcií v DB sa nevzťahuje na atómové vykonanie databázovej operácie spolu s externým LLM volaním.

### Stav diskusie

Predstavili a porovnali sme tri konkrétne návrhy. Študent už uviedol porozumenie prvým dvom; serverless návrh ďalej spresňujeme na jeho otázku. Nevybrali sme finálnu architektúru a nevytvorili ADR, skill ani implementáciu. Asistent sa na záver pýta, či je rozdiel medzi variantmi teraz dostatočne jasný, najmä rozlíšenie vlastnených dát služieb od spoločnej databázy funkcií. Odpoveď študenta zatiaľ nie je zaznamenaná.

## Uzavretie Task 1 — finálne rozhodnutie študenta a kontrola záznamu

### Finálne rozhodnutie

Študent po porovnaní všetkých troch návrhov zvolil **modulárny monolit** ako najvhodnejšiu architektúru RecipeCove pre aktuálne požiadavky a dostupné informácie.

Zdôvodnenie študenta:

- Funkčné oblasti možno oddeliť do modulov bez potreby prevádzkovať ich ako samostatné služby.
- Monolit poskytuje jednoduchšiu implementáciu, internú komunikáciu, jednoduchšie databázové transakcie a nižšiu prevádzkovú zložitosť.
- Mikroslužby ponúkajú nezávislé nasadzovanie a škálovanie, ale zavádzajú sieťové závislosti, komplikovanejšiu konzistenciu a vyššie nároky na prevádzku. Známe zadanie tieto náklady zatiaľ neodôvodňuje.
- Serverless môže byť vhodný pri nepravidelnej záťaži, ale prináša závislosť od platformy, stav mimo inštancií, prevádzkové limity a koordináciu prístupu k DB a LLM. Potreba koordinovať spoločné zdroje pritom platí aj pre ostatné varianty pri ich replikovaní, ako sme už vysvetlili.

Akceptované kompromisy a opatrenia:

- Moduly sa nasadzujú spoločne a zdieľajú zdroje; nepredpokladáme úplnú izoláciu porúch ani samostatné škálovanie každého modulu.
- Riziká možno čiastočne obmedziť jasnými hranicami modulov, súbežným spracovaním, limitmi LLM volaní, timeoutmi, krátkym používaním databázových spojení a monitoringom. Tieto opatrenia neodstraňujú všetky nevýhody spoločného procesu.
- Ak merania preukážu potrebu nezávislej kapacity alebo izolácie Konverzácie, možno zvážiť jej vyčlenenie. Nie je to plánovaná nevyhnutnosť ani automatické riešenie kvót poskytovateľa LLM.

Platnosť rozhodnutia: nemáme potvrdené požiadavky na mimoriadne vysokú záťaž, nezávislé vývojové tímy ani špecifické prevádzkové obmedzenia. Ich neprítomnosť v zadaní nie je dôkaz, že nikdy nevzniknú; pri nových informáciách možno rozhodnutie prehodnotiť.

Naďalej platí dohodnuté oddelenie interpretácie vstupu od overovania a výberu receptov. Konverzačné rozhranie zostáva pracovným predpokladom nad rámec presne definovaných schopností chatbota v zadaní. Finálna voľba monolitu sama neurčuje jazyk, framework, cloud, konkrétny LLM ani zdroj receptov.

### Kontrola vernosti záznamu

Kontrola porovnala chronologické poznámky so skutočnými správami v rozhovore. Zaznamenané otázky a názory študenta, jeho čiastkové rozhodnutia aj finálna voľba zodpovedajú rozhovoru. Neboli doplnené vymyslené odpovede. Na poslednú otázku asistenta o jasnosti rozdielov študent neodpovedal samostatným potvrdením; namiesto toho predložil vyššie uvedené finálne rozhodnutie. Nepripisujeme mu dodatočné potvrdenie.

Pri kontrole sa ukázalo, že niektoré priebežné technické poznámky boli širšie než vysvetlenia v správach asistenta. Pre presnosť ich týmto označujeme ako **doplnkové poznámky asistenta zapísané v súbore, nie samostatne prediskutované témy ani študentom prijaté rozhodnutia**. Ide najmä o:

- detailnejšiu stratégiu testov a ich nahrádzanie kontrolovanými odpoveďami LLM, dátum verzus časový okamih a niektoré detaily relácií a Google identity;
- circuit breaker a lokálne overovanie podpísaných údajov identity v mikroslužbách;
- konkrétny zoznam optimalizácií pred extrakciou (indexy, cache), statické hostovanie frontendu a detailnejšie poznámky o testovaní cloudových oprávnení;
- potrebu správania koordinovaného limitera pri jeho výpadku a niektoré rozšírenia o atómovosti DB operácií s externým LLM.

Tieto poznámky neslúžia ako dôkaz uskutočnených interakcií. Pôvodný priebeh a historické stavy „zatiaľ nevybrané“ ponechávame na mieste; opisujú danú fázu rozhovoru, nie stav po tomto uzavretí. Táto kontrolná poznámka spresňuje pôvod obsahu bez predstierania dokonalejšej diskusie.

### Kontrola voči `Week_05_Designing/Tasks/Task_1.md`

| Požiadavka zadania | Výsledok a podklad |
|---|---|
| Prečítať požiadavky prideleného projektu z priečinka data | Splnené: na začiatku bol prečítaný `Tasks/data/RecipeCove.txt` spolu s Task 1. Pridelenie projektu e-mailom nebolo nezávisle overované; používateľ určil RecipeCove. |
| Viesť rozhovor o troch architektúrach pre tento systém | Splnené: modulárny monolit, mikroslužby a konkrétny serverless variant s funkciami a spoločnou DB. |
| Dôkladne prebrať princípy, kompromisy a implementačné ťažkosti | Splnené: tok vyhľadávania a chatu, obľúbené a kalendár, transakcie, sieťové výpadky, pooly, súbežnosť, limity LLM, stav konverzácie a škálovanie. |
| Podporiť skutočné porozumenie študenta | Doložené jeho vlastnými odpoveďami o súbežnosti, vyčerpaní DB poolu, voľbe odmietnuť zápis pri výpadku, meraní pred extrakciou a globálnych LLM kvótach. Študent sám požiadal o vysvetlenie hraníc serverless návrhu a zdôvodnil finálnu voľbu. Nejde o formálne preskúšanie. |
| Požiadať o priebežné poznámky pred začiatkom | Splnené: požiadavka bola v úvodnej správe a súbor vznikol pred prvým vecným vysvetlením. |
| Odovzdať záznam rozhovoru; doslovný prepis nie je nutný | Splnené týmto súborom vrátane spresnenia pôvodu doplnkových poznámok. |

**Výsledok:** oproti textu Task 1 nebola zistená nesplnená obsahová požiadavka. Task 1 považujeme za kompletný. Serverless nie je vzájomne výlučná kategória voči mikroslužbám; odlišnosť konkrétnych návrhov bola otvorene prediskutovaná a zaznamenaná. Ak by vyučujúci používal užšiu taxonómiu, jeho posúdenie nemožno z textu zadania zaručiť; nejde o zistenú chýbajúcu požiadavku.

Nejasnosti zdrojového zadania (napríklad pôvod receptov, presné schopnosti chatbota a doručovanie pripomienok) zostávajú otvorené a označené; Task 1 nevyžaduje ich vymyslené uzavretie. Nebolo vytvorené ADR, AI skill ani aplikácia. Pôvodné zadania a ostatné týždne neboli pri tejto práci menené; nebol vykonaný commit ani push. Po oznámení výsledku sa práca na Task 1 zastavuje do ďalších pokynov študenta.
