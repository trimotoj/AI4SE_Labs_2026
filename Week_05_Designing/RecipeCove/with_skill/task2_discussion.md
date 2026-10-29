# Task 2 – príprava a hodnotenie ADR RecipeCove

Dátum začiatku: 2026-10-29. Fáza pri začiatku: prvý pracovný návrh. Aktuálny priebeh je v chronologických položkách nižšie.

## Zdroje a pravidlá záznamu

- [Zadanie Task 2](../../Tasks/Task_2.md)
- [Pôvodné požiadavky RecipeCove](../../Tasks/data/RecipeCove.txt)
- [Naša diskusia Task 1](task1_discussion.md), položky E001–E006.
- Workflow: `.agents/skills/architecture-adr-workflow/SKILL.md` v koreni repozitára, načítaný v tejto relácii.

Ide o chronologické zhrnutie skutočnej práce, nie doslovný prepis. Nové pripomienky a revízie budú dopĺňané až po ich vzniku. Čítanie iných experimentov a pôvodných riešení je vylúčené. Povolené nové výstupy sú tento záznam a [ADR.md](ADR.md) v aktuálnom adresári. Task 1 sa nemení. Bez implementácie, Task 3, samostatnej porovnávacej správy, commit alebo push.

## T2-E001 – zadanie prvej pracovnej verzie

**Používateľ:** Považuje Task 1 za dokončený a povoľuje Task 2. Žiada načítať oficiálne zadanie a aktuálnu diskusiu, samostatne navrhnúť štruktúru a rozsah ADR, vytvoriť `ADR.md` aj priebežný záznam `task2_discussion.md`. Vyžaduje nezávislosť experimentu, autentické poznámky a návrh určený na kritické hodnotenie, nie finálne schválenie. Po predstavení prvej verzie má asistent počkať na spätnú väzbu.

**Asistent – načítané podklady:** Zadanie Task 2, pôvodný RecipeCove.txt a aktuálny záznam Task 1. Zadanie vyžaduje vytvorenie ADR, jeho kritické posúdenie používateľom a úpravy podľa skutočnej spätnej väzby; konečné výstupy sú záznam rozhovoru a finálne ADR. Táto výmena pokrýva iba prvý návrh. Nevytvára sa fiktívna séria úprav.

**Navrhnutá štruktúra:** Identifikácia a oddelené stavy rozhodnutia a dokumentu; kontext s vysledovateľnosťou požiadaviek; kritériá; prijatá voľba a navrhované detaily s malým diagramom; porovnanie troch alternatív; dôsledky a mitigácie; budúce overenie a prehodnotenie; otvorené otázky a zdroje. Rozsah má zachytiť dôvody rozhodnutia bez úplného návrhu API, databázovej schémy alebo technologického stacku.

**Stav rozhodnutia:** Modulárny monolit bol zvolený používateľom v Task 1/E006. Znenie ADR zatiaľ schválené nebolo. Pôvod receptov, konkrétne technológie a ďalšie otvorené voľby sa nesmú uzavrieť bez podkladu. Detaily serverless alternatívy sa posudzujú aj v jej upravenej podobe z E005, ktorá už nevyžaduje osobné čítacie projekcie.

**Čakajúci bod:** Po vytvorení a kontrole návrhu bude používateľ vyzvaný posúdiť vecnú správnosť, chýbajúce alebo nadbytočné informácie a štruktúru. Žiadna spätná väzba k ADR zatiaľ neprišla.

## T2-E002 – vytvorenie návrhu 0.1 a vykonané kontroly

**Vykonaná práca asistenta:** Vytvoril `ADR.md`, ADR-001, verziu 0.1 s dátumom rozhodnutia 2026-10-29. Dokument odlišuje voľbu monolitu prijatú v Task 1 od zatiaľ neschváleného znenia ADR. Obsahuje osem vecných častí podľa štruktúry v T2-E001, porovnávaciu tabuľku a Mermaid diagram navrhovaného rozdelenia monolitu. Neurčuje poskytovateľa, databázu ani pôvod receptov. Budúce overovacie scenáre a konkrétnejšie mitigácie označuje ako návrhy asistenta, nie ako vykonané testy alebo používateľom schválené podrobnosti.

**Manuálna obsahová kontrola:** Požiadavky boli previazané so skupinami príbehov 1–14, rozhodnutie s E006, preferencie s E002/E004/E005 a riziko spoločných zdrojov so spresnením E003. Porovnanie zahŕňa upravené C bez povinných osobných projekcií. Diagram bol manuálne skontrolovaný proti textu: jeden backend, päť navrhnutých modulov, spoločná databáza, Google a podmienené zdroje receptov. Nebol validovaný parserom, vykreslený ani vizuálne posúdený po vykreslení. Obsah bol posúdený aj z hľadiska opakovania: požiadavky sú zhrnuté v jednej tabuľke, história rozhovoru sa do ADR neprepisuje.

**Technické kontroly:** Opätovné načítanie oboch nových súborov v UTF-8, kontrola existencie všetkých relatívnych odkazov a prítomnosti ôsmich hlavných častí ADR. Odkazy smerujú na existujúce súbory; znak U+FFFD sa nenašiel. SHA-256 záznamu Task 1 pred tvorbou a po vytvorení dokumentov je rovnaký, teda Task 1 nebol zmenený. Nevykonali sa implementačné testy ani merania; nejde o úplnú validáciu Markdownu.

**Výsledok a hranica:** Prvý návrh je pripravený na kritické hodnotenie, Task 2 ešte nie je dokončený. Oficiálne zadanie predpokladá používateľské posúdenie a skutočné úpravy; k ADR zatiaľ neexistuje spätná väzba ani schválenie. Nebola vytvorená ďalšia verzia, fiktívna iterácia ani experimentálna porovnávacia správa. Pôvodné riešenia a staršie ADR sa nečítali. Výstupy tejto fázy sú iba `ADR.md` a tento záznam.

**Výzva na hodnotenie:** Používateľ má posúdiť presnosť zachytenia rozhodnutia, chýbajúce alebo nadbytočné informácie a vhodnosť rozsahu, štruktúry, tabuľky a diagramu. Asistent po odovzdaní čaká na skutočnú spätnú väzbu.

## T2-E003 – skutočná pripomienka k vstupu HTTP a revízia 0.2

**Používateľova spätná väzba:** Je veľmi spokojný s obsahom prvej verzie: správne zachytáva rozhodnutie, alternatívy, kompromisy, otvorené otázky a budúce overovanie. Pred schválením žiada jasnejší vstup webu do monolitu: explicitné HTTP API vnútri rámca so smerovaním k modulom namiesto HTTP šípky na celý rámec. Iné obsahové zmeny nepovažuje za potrebné. Požaduje zachovať 0.1, vytvoriť 0.2, overiť konzistentnosť a odkazy aj syntax a podľa dostupných možností vykreslenie Mermaid. Zatiaľ nedáva finálne schválenie.

**Vykonaná revízia:** Pôvodné `ADR.md` bolo pred úpravou skopírované do [ADR_v0.1.md](ADR_v0.1.md). Pracovné [ADR.md](ADR.md) má verziu 0.2. Webová HTTP šípka teraz vedie do uzla `H[HTTP API]` vnútri monolitu; päť vnútorných šípok smeruje do existujúcich modulov. Sprievodný text vysvetľuje, že ide o vnútorný komponent a volania v procese, nie samostatnú službu. Aktualizovaná je história dokumentu. Dátum rozhodnutia, architektúra, technológie, prijaté rozhodnutia, navrhovaný charakter detailov aj ostatný vecný obsah zostali zachované. Úvodný stav tohto záznamu bol označený ako historický, aby nepopieral skutočnú prijatú spätnú väzbu.

**Kontrola konzistentnosti:** Zmenené riadky boli porovnané s archivovanou 0.1; zmeny sú obmedzené na verziu, diagram, jeho vysvetlenie a históriu. Rozhodnutie a otvorené otázky boli porovnané s Task 1/E006. HTTP API konkretizuje pôvodné HTTP volania backendu z E002, nemení hranicu nasadenia ani vlastníctvo dát. Archív má rovnaký SHA-256 ako pôvodný súbor pred úpravou. Hash Task 1 zostal nezmenený. Relatívne odkazy v oboch verziách ADR a v zázname boli skontrolované voči existencii cieľových súborov; všetky kontrolované odkazy sú platné.

**Mermaid – skutočne vykonané:** Diagram bol extrahovaný z aktualizovaného ADR a manuálne skontrolovaný vrátane `flowchart LR`, páru `subgraph`/`end`, definícií uzlov, hranatých a databázových zátvoriek, šípok a ich popisov. Identifikátor H je definovaný v monolite a všetkých päť cieľových modulov existuje. Manuálna kontrola nezistila syntaktický ani významový problém. Nejde o potvrdenie parserom.

**Mermaid – dostupnosť a neoverené:** V PATH neboli nájdené `node`, `npm`, `mmdc` ani `mermaid`; Node nebol ani v kontrolovanom štandardnom umiestnení. Vyhľadanie názvov súborov Mermaid a projektových balíkov mimo vylúčených výstupov nevrátilo lokálny nástroj. Edge je nainštalovaný, ale samotný prehliadač neposkytuje Mermaid parser; pripojený prehliadačový nástroj nebol dostupný. Parserová validácia, skutočné vykreslenie ani vizuálna kontrola vykresleného diagramu preto neboli vykonané. Nové závislosti sa neinštalovali a obsah sa neposielal externému rendereru. Úprava nie je označená za graficky overenú.

**Stav:** Jedna skutočná obsahová pripomienka viedla k jednej revízii, z 0.1 na 0.2. Dokument zostáva pracovným návrhom, nie Accepted. Asistent odovzdáva verziu 0.2 a čaká na finálne hodnotenie. Ďalšie iterácie, commit ani push sa nevykonali.

## T2-E004 – výslovné schválenie a dokončenie

**Používateľovo finálne hodnotenie:** Skontroloval ADR 0.2, je spokojný s obsahom aj zapracovaním HTTP API ako súčasti monolitu a potvrdzuje zachovanie ostatných rozhodnutí. Výslovne uviedol: „Schvaľujem ADR v0.2 ako obsahovo finálny.“ Žiada archivovať pracovné verzie, vydať 1.0 Accepted bez zmeny schváleného obsahu a pôvodného dátumu rozhodnutia, overiť odkazy a dostupné kontroly diagramu a uzavrieť Task 2 checklistom. Porovnávacia správa, commit a push zostávajú vylúčené.

**Vykonané dokončenie:** Pracovná 0.2 bola pred zmenami zachovaná v [ADR_v0.2.md](ADR_v0.2.md); [ADR_v0.1.md](ADR_v0.1.md) zostala nezmenená. [ADR.md](ADR.md) je verzia 1.0 so stavom Accepted a dátumom schválenia dokumentu 2026-10-29. Pôvodný dátum architektonického rozhodnutia zostal 2026-10-29. Zmeny sú iba metadáta a história; prijatie dokumentu neuzatvára otvorené technické otázky a nemení navrhovaný charakter detailov.

**Skutočný priebeh:** Jeden prvý návrh (0.1), jedna vecná revízia podľa jednej skutočnej pripomienky k diagramu (0.2), potom výslovné schválenie a administratívne vydanie 1.0. Vydanie 1.0 nie je ďalšia obsahová iterácia. Žiadne ďalšie pripomienky, úpravy ani testy sa nevymýšľali.

**Overenie zachovania:** SHA-256 archívu 0.2 sa zhoduje s pracovným súborom pred finalizáciou; kontrola tiež potvrdila pôvodný hash 0.1 a nezmenený Task 1. Text častí 1–7 aj Mermaid blok sú medzi 0.2 a 1.0 presne zhodné. Aktualizovaná história uvádza skutočné schválenie a odkazy na oba archívy.

**Diagram – hranice kontroly:** Mermaid blok bol znovu extrahovaný a ručne skontrolovaný: `flowchart LR`, rámec `subgraph`/`end`, uzly a ich identifikátory, zátvorky, popisy hrán a vstup Web → HTTP API → päť modulov. Ručná kontrola nezistila problém a diagram je nezmenený oproti používateľom schválenej 0.2. Opätovné zisťovanie dostupnosti v PATH nenašlo `node`, `npm`, `mmdc` ani `mermaid`; v predchádzajúcej kontrole sa nenašiel ani lokálny Mermaid balík. **Validácia Mermaid parserom neprebehla. Skutočné vykreslenie ani vizuálna kontrola vykresleného diagramu neprebehli.** Samotná dostupnosť Edge nenahrádza renderer. Neboli inštalované nástroje ani použité externé renderovacie služby.

### Záverečný checklist podľa Task_2.md

- [x] ADR vychádza z našej diskusie o troch architektúrach z Task 1; rozhodnutie a jeho dôvody sú vysledovateľné.
- [x] Používateľ požiadal o poznámky vopred; tento priebežný záznam obsahuje zadanie, reálnu spätnú väzbu, úpravu a finálne schválenie.
- [x] Používateľ posúdil obsah aj diagram, vyžiadal konkrétnu zmenu a následne výsledok schválil.
- [x] Finálny ADR je vydaný ako 1.0 Accepted, pracovné 0.1 a 0.2 sú zachované.
- [x] Diagram a schválený vecný obsah sa pri finalizácii nezmenili; otvorené otázky a návrhy zostávajú označené.
- [x] Vykonané a nevykonané kontroly sú výslovne oddelené; neuvádzajú sa vymyslené merania alebo úspešné testy.

**Výklad rozsahu iterácií:** Oficiálne zadanie povzbudzuje upravovať ADR „a few times until you like the result“. V tomto priebehu používateľ vyžiadal jednu vecnú revíziu a potom dokument výslovne schválil. Záznam preto nepreukazuje viacnásobné vecné revízie; táto odlišnosť od doslovného množného vyjadrenia je uvedená transparentne. Ďalšie revízie sa podľa používateľových pokynov nevyrábajú. Požadované dva typy výstupov — záznam rozhovoru a finálny ADR — sú pripravené; konečné akademické hodnotenie prislúcha vyučujúcemu.

**Výstupy Task 2:** [ADR.md](ADR.md), [ADR_v0.1.md](ADR_v0.1.md), [ADR_v0.2.md](ADR_v0.2.md) a [task2_discussion.md](task2_discussion.md). Existujúci [task1_discussion.md](task1_discussion.md) zostáva nezmenený. Task 2 je v schválenom rozsahu uzavretý. Bez čítania `without_skill/`, zmeny skillu alebo zadaní, porovnávacej správy, commit či push.

**Výsledok záverečnej kontroly súborov:** Po zápise schválenia sa overila existencia všetkých piatich uvedených súborov a všetkých 37 výskytov relatívnych Markdown odkazov v nich. Ciele existujú a význam odkazov zodpovedá zdrojom alebo archivovaným verziám. Opätovné načítanie UTF-8 nenašlo znak U+FFFD. Strojovo sa potvrdila verzia 1.0, stav Accepted a zachovaný dátum rozhodnutia. Táto kontrola nie je úplnou validáciou Markdownu ani Mermaid parserom.
