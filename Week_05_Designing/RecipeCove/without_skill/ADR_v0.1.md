# ADR-001: Modulárny monolit pre RecipeCove

| Údaj | Hodnota |
|---|---|
| Verzia dokumentu | 0.1 — prvá pracovná verzia na pripomienkovanie |
| Stav dokumentu | Rozpracovaný; ešte nebol zhodnotený študentom v Task 2 |
| Stav architektonického rozhodnutia | Modulárny monolit zvolený študentom na konci Task 1 |
| Dátum | 2026-10-29 |
| Rozsah | Architektúra backendu RecipeCove; bez výberu konkrétnych technológií |

## 1. Kontext

RecipeCove je webová aplikácia na objavovanie receptov, prezeranie informácií o receptoch a ingredienciách a organizáciu osobných kuchárskych plánov. Potrebujeme zvoliť architektúru, ktorá podporí tieto funkcie a pritom nezavedie zložitosť bez opory v známych požiadavkách.

### Potvrdené funkčné požiadavky

Podľa [opisu RecipeCove](../../Tasks/data/RecipeCove.txt):

| Oblasť | Požadované správanie | User stories |
|---|---|---|
| Objavovanie receptov | Návštevník vyhľadáva podľa názvu a prezerá detaily receptov a ingrediencií | 2–4 |
| Odporúčania | Návštevník dostane odporúčania podľa konkrétnej diéty; opis systému uvádza chatbota | 5 a opis systému |
| Identita a profil | Registrácia cez Google účet, prihlásenie, odhlásenie a zobrazenie osobného profilu | 1, 6–8 |
| Kalendár | Registrovaný používateľ vytvorí alebo vymaže kalendár a pridá udalosť pripomínajúcu prípravu receptu v určitý deň | 9–11 |
| Obľúbené | Registrovaný používateľ pridáva a odoberá recepty a prezerá svoj zoznam | 12–14 |

Spôsob doručovania pripomienok nie je určený. Google prihlásenie neznamená požiadavku na Google Calendar. Používateľské vytváranie receptov sa v zadaní neuvádza.

### Pracovné predpoklady a chýbajúce informácie

- **Pracovný predpoklad z diskusie:** chatbot umožní vyjadriť stravovacie preferencie prirodzeným jazykom. Presné konverzačné schopnosti nie sú potvrdenou požiadavkou. Jednoduchší filter podľa diéty zostáva preskúmanou alternatívou rozhrania.
- **Podmienka rozhodnutia:** nemáme potvrdené mimoriadne vysoké zaťaženie, nezávislé vývojové tímy ani osobitné prevádzkové obmedzenia. Neznamená to, že sme potvrdili malý počet používateľov alebo konkrétnu veľkosť tímu.
- Nevieme počet používateľov, objem dát, požadovanú odozvu, dostupnosť, rozpočet ani priebeh záťaže. Porovnanie výkonu a nákladov je kvalitatívne; nemáme benchmarky ani cenový výpočet.
- Zdroj a aktualizácia receptov a ingrediencií zostávajú otvorené. Výber monolitu sám neurčuje, či bude katalóg lokálny alebo externý.

## 2. Rozhodovacie kritériá

Z diskusie vyplynuli tieto kritériá, bez číselných váh:

- Primeraná implementačná a prevádzková zložitosť vzhľadom na známe funkcie.
- Predvídateľné a testovateľné pravidlá výberu receptov a overovania diétnych kritérií.
- Jednoduchá práca so súvisiacimi údajmi, transakciami a referenčnou integritou.
- Ochrana ostatných funkcií pred pomalými LLM volaniami a vyčerpaním spoločných zdrojov.
- Možnosť reagovať na neskôr preukázané nároky na škálovanie a izoláciu.

Nezávislé nasadzovanie a škálovanie sme posudzovali ako možné prínosy, nie ako potvrdené požiadavky.

## 3. Rozhodnutie

**Pre aktuálne RecipeCove volíme modulárny monolit.** Backend bude nasadzovaný ako jeden celok, vnútorne rozdelený podľa funkčných zodpovedností. Moduly budú spolupracovať cez definované interné rozhrania, bez potreby samostatnej sieťovej služby pre každú oblasť. Frontend bude komunikovať s backendom cez HTTP.

Rozhodnutie neobmedzuje systém na jednu bežiacu inštanciu. Pri replikovaní však treba riešiť relácie, kontext rozhovoru a koordináciu spoločných limitov.

### Náčrt modulov na ďalšie spresnenie

Nasledujúce hranice boli navrhnuté v Task 1; nie sú samostatne schváleným detailným návrhom:

| Modul | Zodpovednosť |
|---|---|
| Identita a profil | Google prihlásenie/registrácia, relácia, odhlásenie, profil |
| Katalóg | Prístup k receptom a ingredienciám, detaily a vyhľadávanie podľa názvu |
| Odporúčania | Overenie podporovaných kritérií a deterministický výber vhodných receptov |
| Konverzácia | Kontext rozhovoru, interpretácia cez LLM a príprava odpovede pri konverzačnom variante |
| Obľúbené | Používateľské zoznamy a pridávanie/odoberanie receptov |
| Kalendár | Kalendáre a udalosti odkazujúce na recept a deň |

Diskutovaný dátový variant používa spoločnú relačnú databázu. Tá umožňuje lokálne transakcie a cudzie kľúče medzi lokálne uloženými dátami; výber databázy ani finálna dátová schéma zatiaľ neboli prijaté. Ak bude katalóg externý, lokálna transakcia nezaručí jeho dostupnosť ani nemennosť. Spoločné úložisko nesmie viesť k obchádzaniu rozhraní a pravidiel modulov.

### Dohodnutá zodpovednosť pri konverzačnom variante

LLM prevádza prirodzený jazyk na štruktúrované kritériá a môže pomôcť formulovať odpoveď. Backend kritériá overuje a vyberá recepty z katalógu. Prípadné zoradenie pomocou LLM smie pracovať iba s už vyfiltrovanými receptmi a musí byť overené; nie je povinnou funkciou.

Tok: `Konverzácia → LLM → overenie v Odporúčaniach → Katalóg → výsledky`.

Jednoduchý filter môže využívať rovnaké Odporúčania bez LLM. Oddelenie interpretácie od filtrovania je prijatý princíp pre konverzačný variant, nie záväzok použiť konkrétny model či poskytovateľa.

## 4. Zvažované alternatívy a zdôvodnenie voľby

| Návrh z Task 1 | Prínos | Kompromis a dôvod, prečo ho teraz nevolíme |
|---|---|---|
| **Modulárny monolit — zvolený** | Interné volania, jednoduchšie transakcie a menší počet prevádzkových častí | Spoločné nasadzovanie a zdroje; akceptujeme ich pri aktuálne známych požiadavkách |
| **Mikroslužby s vlastnými dátami** | Nezávislé nasadzovanie, cielené škálovanie a lepšia možnosť izolácie | Sieťové závislosti, čiastočné výpadky, zložitejšie vzťahy medzi dátami a viac prevádzkovej práce; zadanie nepreukazuje potrebu týchto nákladov |
| **Serverless funkcie so spoločnou relačnou DB** | Spravované vykonávanie a možná výhodnosť pri nepravidelnej záťaži | Konfigurácia platformy, stav mimo inštancií, studené štarty, časové limity a ochrana závislostí pred násobením vykonaní; výhodnosť bez údajov o prevádzke nevieme doložiť |

Porovnávame konkrétne návrhy, nie vzájomne výlučné kategórie: serverless možno kombinovať aj s mikroslužbami. V našom serverless variante funkcie používali spoločnú DB a mohli zdieľať knižnicu pravidiel; mikroslužbový variant mal dátové vlastníctvo služieb a sieťové volanie Receptov z Konverzácie.

Monolit bol zvolený pre primeranosť, nie pre tvrdenie, že alternatívy nedokážu splniť funkčné požiadavky. Nemáme podklad na univerzálne tvrdenie, že je najlacnejší alebo najrýchlejší.

## 5. Dôsledky a akceptované kompromisy

### Prínosy

- Jeden nasadzovaný backend zjednodušuje prevádzku a sledovanie toku požiadavky.
- Moduly môžu oddeliť zodpovednosti bez zavedenia sieťových protokolov medzi nimi.
- Spoločná relačná DB, ak sa tento variant potvrdí, zjednoduší integritu obľúbených a transakčné operácie s kalendárom.
- Oddelené pravidlá odporúčania možno overovať nezávisle od interpretácie LLM.

### Nevýhody a opatrenia z diskusie

| Akceptované riziko | Opatrenie a jeho hranica |
|---|---|
| Spoločné vydanie backendu a replikovanie celku | Jasné hranice modulov; samostatné vydávanie modulov tým nezískame |
| Chat môže spotrebovať zdroje ostatných funkcií | Súbežné spracovanie pomocou neblokujúceho I/O alebo pracovníkov, timeouty a obmedzenie LLM volaní; nejde o úplnú izoláciu |
| Vyčerpanie DB poolu | Spojenia a transakcie používať iba počas potrebných DB operácií, nie počas čakania na LLM |
| Prekročenie LLM kvót pri viacerých procesoch | Koordinovať súbežnosť, počet požiadaviek a tokeny; lokálny semafor nechráni celú aplikáciu |
| Rozpad modularity pri spoločnom kóde a DB | Používať rozhrania modulov a neobchádzať pravidlá výberu receptov |

Presné limity ani implementácia týchto opatrení nie sú vybrané. Čísla z Pythonového príkladu v Task 1 nepredstavujú prevádzkové požiadavky. Opatrenia treba overiť meraniami; výsledky implementácie ani testovania zatiaľ neexistujú.

Pri skúmaní mikroslužieb študent výslovne zvolil odmietnutie pridania obľúbeného receptu, ak nemožno overiť jeho existenciu cez nedostupnú službu Recepty. Akceptoval nižšiu dostupnosť výmenou za absenciu čakajúcich zápisov. Toto čiastkové rozhodnutie nevytvára v monolite službu Recepty; konkrétne správanie pri nedostupnom lokálnom alebo externom katalógu treba spresniť. Ani úspešné overenie nezaručí budúcu dostupnosť receptu.

## 6. Podmienky prehodnotenia

Rozhodnutie prehodnotíme, ak nové požiadavky alebo merania preukážu potrebu nezávislého škálovania, izolácie či nasadzovania, ktorú nemožno primerane riešiť v monolite.

Najsilnejším signálom podľa študenta sú namerané problémy so zdrojmi. Najprv identifikujeme úzke miesto a overíme jednoduchšie riešenia. Ak Konverzácia naďalej poškodzuje ostatné funkcie, možno zvážiť jej vyčlenenie do služby. Nejde o záväzný migračný plán; extrakcia sama neodstráni kvóty externého LLM.

## 7. Otvorené otázky a rozsah ďalších rozhodnutí

- Odkiaľ získame recepty a ingrediencie, ako ich aktualizujeme a čo zobrazíme pri nedostupnom alebo odstránenom recepte?
- Ktoré diéty a kritériá podporujeme a ako vyhodnotíme neúplné údaje?
- Aký rozsah konverzácie je potrebný? Ako budeme spravovať kontext návštevníka a aké údaje prípadne pošleme LLM poskytovateľovi?
- Ako sa doručujú pripomienky a koľko kalendárov môže používateľ mať?
- Aká záťaž, odozva, dostupnosť, rozpočet a prevádzkové prostredie sa očakávajú?
- Potvrdíme spoločnú relačnú DB a navrhnuté moduly? Aký jazyk, framework a prípadný LLM použijeme?
- Aké konkrétne timeouty, limity a merania použijeme na overenie ochrany spoločných zdrojov?

Toto ADR neurčuje konkrétny cloud, produkt, počet inštancií ani číselné SLA a nepridáva funkcionality, ktoré zadanie alebo diskusia nepotvrdili.

## 8. Podklady

- [Požiadavky RecipeCove](../../Tasks/data/RecipeCove.txt) — funkčný rozsah.
- [Diskusia Task 1](task1_discussion.md) — tri návrhy, odpovede študenta a oddiel „Uzavretie Task 1 — finálne rozhodnutie študenta a kontrola záznamu“. Doplnkové poznámky asistenta označené v kontrole nepovažujeme za prijaté rozhodnutia.
- [Zadanie Task 2](../../Tasks/Task_2.md) a [záznam jeho diskusie](task2_discussion.md) — príprava a budúce pripomienkovanie dokumentu.
