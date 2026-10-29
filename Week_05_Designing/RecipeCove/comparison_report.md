# Porovnanie architektonických experimentov RecipeCove

**Verzia 1.0 – finálna správa. Schválená používateľom 2026-10-29.** Dátum: 2026-10-29. Pracovné verzie [0.1](comparison_report_v0.1.md) a [0.2](comparison_report_v0.2.md) sú zachované. Vecný obsah schválenej verzie 0.2 zostáva nezmenený.

## 1. Cieľ a podklady

Správa plní záverečnú porovnávaciu časť [Task 3](../Tasks/Task_3.md): porovnáva zaznamenané riešenie Task 1 a Task 2 bez skillu a po jeho zavedení. Posudzuje priebeh, kvalitu ADR a pozorovateľný prínos [architecture-adr-workflow](../../.agents/skills/architecture-adr-workflow/SKILL.md). Oba priebehy vychádzajú z rovnakých [požiadaviek RecipeCove](../Tasks/data/RecipeCove.txt); oba skončili výberom modulárneho monolitu.

Preskúmané boli všetky zachované podklady:

| Experiment | Diskusie | Pracovné ADR | Finálne ADR |
| --- | --- | --- | --- |
| Bez skillu | [Task 1](without_skill/task1_discussion.md), [Task 2](without_skill/task2_discussion.md) | [0.1](without_skill/ADR_v0.1.md), [0.2](without_skill/ADR_v0.2.md), [0.3](without_skill/ADR_v0.3.md) | [1.0 Accepted](without_skill/ADR.md) |
| So skillom | [Task 1](with_skill/task1_discussion.md), [Task 2](with_skill/task2_discussion.md) | [0.1](with_skill/ADR_v0.1.md), [0.2](with_skill/ADR_v0.2.md) | [1.0 Accepted](with_skill/ADR.md) |

Čítanie oboch adresárov bolo povolené až na porovnanie po dokončení experimentov. Správa nemení ich obsah ani spätne nedopĺňa interakcie.

## 2. Metodika a jednotky počítania

Ide o opisnú prípadovú štúdiu dvoch priebehov, nie kontrolovaný experiment. Rovnaké jednotky sa používajú v oboch prípadoch:

- **Substantívna výmena:** zaznamenaná požiadavka, otázka, hodnotenie alebo rozhodnutie používateľa a príslušná odpoveď či výsledok práce asistenta. Počítame aj úvodné zadanie a záverečné schválenie. Viac požiadaviek v jednej výmene nezvyšuje počet. Priebežné správy, nástroje, kontrolné podsekcie a samotná čakajúca otázka asistenta sa samostatne nepočítajú.
- **Pripomienkový balík k ADR:** jedna používateľská spätná väzba po prečítaní návrhu, ktorá žiada jeho zmenu. Schválenie bez obsahových zmien sa nepočíta. Doplnkovo počítame jednotlivé vecné požiadavky v balíkoch; archivácia, číslovanie a samotné kontroly bez žiadanej zmeny obsahu sú procesné pokyny.
- **Obsahová iterácia ADR:** prechod medzi návrhmi, ktorý mení argumentáciu, usporiadanie, overovacie scenáre alebo diagram podľa spätnej väzby. Prvé vytvorenie ADR ani administratívne vydanie 1.0 sa nepočítajú.
- **Usmerňovanie:** uvádzame konkrétne úvodné pokyny a následné zásahy oddelene. Nevytvárame celkové skóre „potrebnej pomoci“: záznam neukazuje, čo by asistent urobil bez pokynu, a jedna správa môže zároveň odpovedať, rozhodovať aj usmerňovať.

Počty sú rekonštrukciou **doložených výmen s Codexom zo súhrnných záznamov**. Bez skillu sú záznamy členené tematickými nadpismi, so skillom stabilnými identifikátormi; rozdielna štruktúra a podrobnosť môžu ovplyvniť zoskupenie a rekonštruovaný počet výmen. Nejde o presný počet všetkých správ, objektívne meranie rýchlosti ani súčet práce vrátane ďalšieho asistenta (pozri §6). Kvalita sa posudzuje rovnakými kritériami v oddiele 4, bez bodového skóre.

## 3. Priebeh a miera usmerňovania

### 3.1 Doložené počty

| Ukazovateľ | Bez skillu | So skillom |
| --- | --- | --- |
| Substantívne výmeny Task 1 | 9 | 6 |
| Substantívne výmeny Task 2 | 4 | 3 |
| Spolu za Task 1 a Task 2 | 13 | 9 |
| Pripomienkové balíky k ADR | 2 | 1 |
| Vecné požiadavky na zmenu ADR v týchto balíkoch | 5 | 1 |
| Obsahové iterácie ADR po prvom návrhu | 2: 0.1 → 0.2 → 0.3 | 1: 0.1 → 0.2 |

Súčty **13 a 9** zachovávame podľa nižšie uvedeného auditu; ich porovnateľnosť obmedzuje rozdielne členenie a podrobnosť záznamov. Nezahŕňajú samostatnú konverzáciu s ChatGPT mentorom ani všetku prácu používateľa.

**Audit výmen:** Deväť výmen bez skillu zodpovedá deviatim chronologickým oddielom [Task 1](without_skill/task1_discussion.md): úvod; filtrovanie/konverzácia; zodpovednosti a monolit; súbežnosť; uzavretie monolitu a služby; výpadok a rast; meranie a serverless; odlišnosť serverless a porovnanie; finálny výber. So skillom ide o E001–E006 v [Task 1](with_skill/task1_discussion.md). V [Task 2 bez skillu](without_skill/task2_discussion.md) sa „začatie“ a „vytvorenie prvej pracovnej verzie“ počítajú spolu: ide o odpoveď na jedno zadanie; nasledujú prvá spätná väzba, druhá spätná väzba a schválenie. Rovnakým spôsobom sa v [Task 2 so skillom](with_skill/task2_discussion.md) zlučujú T2-E001 a T2-E002; nasledujú T2-E003 a T2-E004.

**Audit pripomienok:** Bez skillu prvý balík žiadal štyri vecné zmeny: diagram, väzbu kritérií na porovnanie, prehľad stavov rozhodnutí a odstránenie opakovania. Druhý pridal návrh budúceho overovania: spolu päť. Ďalšie body druhého balíka žiadali kontroly diagramu, odkazov a textu; nepočítajú sa ako nové vecné zmeny. So skillom išlo o jednu zmenu: explicitné HTTP API v diagrame a zodpovedajúce vysvetlenie. Dôkazom sú príslušné spätné väzby v oboch záznamoch Task 2 a zachované ADR.

### 3.2 Čo sa skúmalo a čo používateľ požadoval

Bez skillu sa diskusia sústredila na interpretáciu prirodzeného jazyka, oddelenie LLM od výberu receptov, asynchrónny Pythonový príklad, DB pool a globálne kvóty. Používateľ výslovne žiadal vysvetliť filter verzus konverzáciu, implementačný príklad, scenár rastu a odlišnosť serverless od služieb. Asistent už pri službách uviedol, že zatiaľ nevidí dostatočný dôvod uprednostniť ich zložitosť; finálny výber však zostal používateľovi ([Task 1 bez skillu](without_skill/task1_discussion.md), príslušné oddiely „Pokračovanie“).

So skillom sa podrobnejšie rozoberali vlastný katalóg verzus API, nedostupný uložený recept, poradie a duplicity udalostí a viditeľnosť vlastných zápisov. Používateľ vyžiadal zachovať oba možné zdroje dát (E002), spresnil, že pomalé I/O neblokuje automaticky celý backend (E003), a vyžiadal hybrid serverless s priamym čítaním osobných dát (E005). Ani so skillom teda neodpadlo technické usmerňovanie ([Task 1 so skillom](with_skill/task1_discussion.md)).

Najjasnejší rozdiel v samostatnej práci asistenta nastal pri ADR: bez skillu si používateľ dodatočne vypýtal diagram, porovnanie podľa spoločných kritérií a konkrétny plán overovania; so skillom boli už v prvom návrhu bez osobitnej požiadavky na tieto tri prvky ([prvé ADR bez skillu](without_skill/ADR_v0.1.md), §3–6; [prvé ADR so skillom](with_skill/ADR_v0.1.md), §3–6; oba záznamy Task 2). Samostatnosť sa týka týchto prvkov, nie celého experimentu: používateľ aj v druhom priebehu určoval fázy, výstupy, nezávislosť a kontrolné kroky.

## 4. Kvalita prvých návrhov a finálnych výstupov

| Spoločné kritérium | Bez skillu | So skillom |
| --- | --- | --- |
| Úplnosť prvého ADR | Už 0.1 má kontext, príbehy, kritériá, rozhodnutie, alternatívy, riziká a otvorené otázky. Chýba diagram a konkrétna tabuľka scenárov overovania. | Už 0.1 pridáva diagram, spoločnú maticu alternatív a konkrétne scenáre; diagram ešte nemá explicitný vstup HTTP API. |
| Architektonická argumentácia | 0.1 zdôvodňuje primeranosť monolitu a nevydáva ho za univerzálne najlacnejší. Vo 0.2 sú priority priamo prepojené s maticou alternatív. | 0.1 priamo viaže výber na priority z E006 a vysvetľuje, prečo zatiaľ nie je podložená potreba nezávislých služieb. |
| Požiadavky, predpoklady a otvorené voľby | Už 0.1 ich rozlišuje; 0.2 pridáva súhrnnú tabuľku stavov. Konverzácia je pracovný predpoklad, DB návrhový variant. | Už 0.1 oddeľuje pôvodné príbehy, doplnené preferencie, prijatú voľbu a navrhované detaily; nevyberá konkrétnu DB ani LLM. |
| Spoločné kritériá alternatív | 0.1 má tabuľku prínosov a kompromisov podľa návrhov; maticu rovnakých kritérií získava vo 0.2. | Matica implementácie, transakcií, viditeľnosti zápisu, kapacity, zdroja dát a nákladov existuje už v 0.1. |
| Diagram | Doplnený vo 0.2; HTTP API už má, vo 0.3 sa upraví poradie zápisu jeho hrany. Finálny diagram explicitne označuje prijatý rámec a návrhové uzly. | Existuje v 0.1, HTTP API sa doplní vo 0.2. Návrhový charakter vysvetľuje nadpis a text, varianty zdroja dát prerušované hrany. |
| Technické riziká | Silná konkretizácia DB poolu, lokálnych verzus globálnych LLM limitov, relácií a integrity. | Silná konkretizácia viditeľnosti zápisov, súbehu kalendára, opakovaného zápisu a nedostupných externých receptov. |
| Budúce overovanie | 0.1 má podmienky prehodnotenia a potrebu merania; konkrétne scenáre s ukazovateľmi pribudnú vo 0.3. | Scenáre a sledované zdroje sú už v 0.1, bez vymyslených prahov alebo výsledkov. |
| Finálne ADR | 1.0 Accepted obsahuje diagram, maticu, riziká, otvorené otázky a plán merania so zvýraznením LLM. | 1.0 Accepted obsahuje rovnaké typy častí, dôraz na osobné zápisy a pôvod dát; história odkazuje na archívy. |

Podklady tabuľky: [bez skillu 0.1](without_skill/ADR_v0.1.md), [0.2](without_skill/ADR_v0.2.md), [0.3](without_skill/ADR_v0.3.md) a [finálne ADR](without_skill/ADR.md), najmä §1–7; [so skillom 0.1](with_skill/ADR_v0.1.md), [0.2](with_skill/ADR_v0.2.md) a [finálne ADR](with_skill/ADR.md), najmä §1–8. Rozdiely verzií boli porovnané aj priamo, nielen podľa názvov súborov.

Finálne dokumenty sa kvalitou zbližujú. Rozdielne LLM a dátové detaily zodpovedajú odlišnému rozsahu diskusie, nie samy osebe chybám dokumentov.

V oboch záznamoch Task 2 je overenie Mermaid obmedzené na ručnú kontrolu; parserová validácia, vykreslenie a vizuálna kontrola vykresleného výsledku neprebehli. Nemožno preto tvrdiť, že skill priniesol graficky overený diagram ([bez skillu](without_skill/task2_discussion.md), „Výsledky kontroly“; [so skillom](with_skill/task2_discussion.md), T2-E003–E004).

## 5. Pozorovateľný prínos skillu a alternatívne vysvetlenia

Pozorovania zodpovedajú viacerým pravidlám [SKILL.md](../../.agents/skills/architecture-adr-workflow/SKILL.md):

| Pravidlo skillu | Pozorovaný prejav a hranica záveru |
| --- | --- |
| §4: kompaktná štruktúra, spoločné kritériá, diagram a scenáre overenia | Tieto prvky sú už v ADR 0.1 so skillom; bez skillu sa diagram, matica a scenáre dopĺňali v dvoch spätných väzbách. Ide o súlad s pravidlom, nie izolovaný dôkaz jeho kauzálneho účinku. |
| „Authentic records“: stabilné identifikátory a oddelenie doplnkov | E001–E006 a T2-E001–E004 uľahčujú dohľadanie rozhodnutí. Záznam bez skillu má namiesto identifikátorov tematické nadpisy a v závere Task 1 transparentne označuje technické doplnky, ktoré neboli samostatne prediskutované. Ani identifikátor sám nezaručí úplnú vernosť prepisu. |
| §1 a §3: neznáme údaje nevydávať za fakty; rozhoduje používateľ | Druhý priebeh tieto pravidlá dodržiava, ale rovnaké vlastnosti obsahuje už prvé ADR bez skillu. Nemožno ich vydávať za novinku spôsobenú skillom. |
| §2: alternatívy konkretizovať a priznať prekryv štýlov | So skillom je prekryv B/C vysvetlený pri prvom uvedení C (E004); bez skillu sa podrobnejšie objasnil na používateľovu otázku. Konkrétne C však bolo v druhom priebehu aj technicky iné. |
| „Verification“: nepredstierať kontroly a rýchlosť | Druhý záznam jasne oddeľuje ručnú kontrolu od renderovania, ale rovnako transparentný je aj prvý. Správa preto nevyvodzuje časovú úsporu. |

Pozorovateľným rozdielom je najmä skoršia pripravenosť dokumentačnej štruktúry a menší počet dodatočných balíkov úprav ADR. Súvis s pravidlami skillu je doložený obsahom, jeho výlučný účinok však nie je oddelený od usmerňovania a učenia používateľa.

## 6. Obmedzenia porovnania

1. **Učenie a poradie:** používateľ v druhom experimente už poznal projekt a skúsenosti z prvého. Nezávislé čítanie podkladov neodstráni jeho znalosť projektu ani vplyv formulácie ďalších otázok.
2. **Rozdielne usmerňovanie:** bez skillu používateľ už v úvodnom zadaní Task 2 explicitne uviedol žiadané časti a oddelenie predpokladov; so skillom poveril asistenta návrhom štruktúry, ale podrobne riadil hranice a kontroly. „Bez skillu“ neznamená bez kvalitného promptu ([oba záznamy Task 2](without_skill/task2_discussion.md), [T2-E001 so skillom](with_skill/task2_discussion.md)).
3. **Rozdielne technické varianty:** bez skillu serverless používalo spoločnú relačnú DB a knižnicu pravidiel; so skillom začalo s udalosťami a projekciami, potom prešlo na priame osobné čítanie. Zložitosť udalostí preto nie je všeobecnou nevýhodou každého serverless návrhu. Druhý priebeh zároveň prijal iné čiastkové preferencie: nedostupné uložené recepty a viditeľnosť zápisov. Nemožno porovnávať iba názvy architektúr.
4. **Externá pomoc ChatGPT mentora:** používateľ pri hodnotení správy uviedol, že počas oboch experimentov využíval aj samostatnú konverzáciu s ChatGPT ako študijným mentorom. Pomáhala mu porozumieť architektonickým otázkam, formulovať niektoré odpovede a pokyny pre Codex a hodnotiť ADR. Zdrojom tejto informácie je používateľova metodická pripomienka k verzii 0.1; záznam mentorskej konverzácie nebol poskytnutý ani preskúmaný. Jej rozsah, počet interakcií a rozdielnu intenzitu medzi experimentmi nevieme vyčísliť. Výmeny s Codexom preto nezachytávajú celkové množstvo práce ani všetky interakcie s asistentmi. Pozorované zlepšenia nemožno pripísať výhradne skillu.
5. **Záznamy a podmienky:** tematické súhrny bez skillu a identifikované položky so skillom nie sú úplnými prepismi; ich rozdielna podrobnosť môže meniť rekonštruovaný počet výmen aj pri jednotnej definícii. Chýbajú reprodukovateľné konfigurácie modelov a audit nových relácií. Nezávislosť práce s pôvodnými podkladmi je deklarovaná používateľom a záznamami; správa ju spätne nedokazuje a neznamená absenciu externej pomoci. Doplnkové poznámky z prvého Task 1 sa nepočítajú ako samostatné výmeny.
6. **Rýchlosť a výsledná kvalita:** chýbajú porovnateľné údaje o aktívnom čase, latencii nástrojov a nákladoch. Odpoveď na „rýchlejšie?“ v Task 3 je preto: **časovo neoveriteľné; zo záznamov rekonštruujeme menej výmen s Codexom a obsahových revízií ADR**. Tieto počty nepreukazujú rovnakú hĺbku, porozumenie ani celkovú náročnosť. Dva priebehy neumožňujú všeobecný kauzálny záver.
7. **Rozsah iterácií:** prvý Task 2 má dve vecné revízie, druhý jednu a výslovné schválenie. Druhý záznam sám priznáva odlišnosť od množného odporúčania úprav v Task 2; umelé iterácie nevznikli ([T2-E004](with_skill/task2_discussion.md)).

## 7. Záver

Oba experimenty vytvorili zdôvodnené a používateľom schválené ADR pre modulárny monolit. So skillom bol prvý návrh dokumentačne kompletnejší a prešiel jednou obsahovou revíziou oproti dvom bez skillu. Prvý priebeh podrobnejšie skúmal konverzačný variant a súbežnosť; finálne dokumenty pokrývajú podobné základné náležitosti. Skill sa javí ako užitočná opora postupu a včasnej dokumentácie. Vplyv učenia, rozdielnych diskusií a ChatGPT mentora však nemožno oddeliť; časové zrýchlenie ani výlučný účinok skillu nie sú preukázané.

## 8. Kontrola voči Task 3

- Správa porovnáva diskusie, prvé návrhy, všetky zachované iterácie a finálne ADR; uvádza jednotnú metodiku aj zdroje zistení.
- Existujúci skill je uvedený ako samostatný požadovaný výstup Task 3. Jeho historické vytvorenie a použitie novej relácie sa tu nereprodukujú; predmetom je posledná porovnávacia fáza.
- Otázka rýchlosti je vyhodnotená s obmedzeniami, bez vymyslených časov, benchmarkov či skóre.
- Kontroly súborov a relatívnych odkazov sú zaznamenané nižšie. Správa bola používateľom finálne schválená; nevznikla ďalšia iterácia experimentov ani commit/push.

### História úpravy správy

Verzia 0.1 bola pred úpravou zachovaná. Verzia 0.2 reaguje na dve skutočné metodické pripomienky používateľa: priznáva pomoc samostatného ChatGPT mentora a spresňuje porovnateľnosť súhrnných záznamov. Počty, audit výmen, porovnávacie výsledky a zdrojové odkazy zostali zachované; skrátili sa opakujúce sa hodnotiace formulácie. Nepribudli odhady mentorských interakcií ani nové experimentálne údaje.

Kontrola verzie 0.2 potvrdila existenciu cieľov všetkých 36 relatívnych odkazov; archív 0.1 má 35 platných odkazov. Pôvodné ciele odkazov aj tabuľky počtov a kvality zostali zachované. Manuálne bol overený súlad metodiky, výsledkov a záveru vrátane oboch nových obmedzení. Hash archívu zodpovedá pôvodnej 0.1 a hashe 16 chránených podkladov sa nezmenili. Pri načítaní UTF-8 sa nenašiel náhradný znak U+FFFD. Vykreslenie Markdownu ani Mermaid sa neoverovalo; táto revízia žiadny diagram nemení.

Používateľ verziu 0.2 výslovne schválil ako obsahovo úplnú a finálnu. Pred administratívnym vydaním 1.0 bola zachovaná ako `comparison_report_v0.2.md`. Finalizácia aktualizuje iba metadáta, stav schválenia a túto históriu; nemení metodiku, výsledky ani závery.
