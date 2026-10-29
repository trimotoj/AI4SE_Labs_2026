# RecipeCove — záznam diskusie k Task 2

## 2026-10-29 — začatie a zadanie prvej verzie

Študent požiadal prečítať `Week_05_Designing/Tasks/Task_2.md` a `task1_discussion.md` a vytvoriť prvú pracovnú verziu `ADR.md` na základe skutočnej diskusie v Task 1.

Požaduje zachytiť voľbu modulárneho monolitu, kontext, alternatívy, kritériá, kompromisy, dôsledky a otvorené otázky. Potvrdené požiadavky sa majú odlíšiť od pracovných predpokladov. Dokument sa bude iteratívne hodnotiť; po vytvorení prvej verzie má asistent vysvetliť štruktúru, požiadať o spätnú väzbu a bez nej nepokračovať v ďalších úpravách.

Obmedzenia: nevytvárať AI skill, nemeniť pôvodné zadania ani súbory Task 1, nevykonávať commit ani push. Tento záznam vznikol pred prípravou ADR.

### Prečítané podklady

- `Week_05_Designing/Tasks/Task_2.md`: vyžaduje vytvorenie ADR, jeho hodnotenie študentom a niekoľko úprav podľa spätnej väzby; výstupom má byť finálne ADR a záznam rozhovoru.
- `Week_05_Designing/RecipeCove/without_skill/task1_discussion.md`: vrátane finálneho rozhodnutia a kontroly vernosti záznamu. Technické doplnky označené v závere Task 1 nemožno vydávať za prijaté rozhodnutia.
- `Week_05_Designing/Tasks/data/RecipeCove.txt`: opätovne prečítané na overenie funkčných požiadaviek.

### Úvodná odpoveď asistenta

Asistent oznámil prečítanie podkladov, vytvorenie samostatného záznamu a prípravu prvej verzie s oddelením potvrdených požiadaviek, prijatých rozhodnutí a predpokladov. Prisľúbil po prvej verzii čakať na spätnú väzbu.

### Aktuálny stav

Príprava ADR sa ešte len začína. Študent zatiaľ nehodnotil žiadnu verziu ADR. Voľba modulárneho monolitu už pochádza z Task 1; predmetom následného hodnotenia bude jej dokumentácia, nie predstierané nové schválenie architektúry.

## Vytvorenie prvej pracovnej verzie ADR

Asistent v priebežnej správe upozornil, že voľba monolitu bola v Task 1 výslovne prijatá, zatiaľ čo presné hranice modulov a spoločná relačná DB boli návrhové detaily. Oznámil štruktúru kontext → rozhodnutie → alternatívy → dôsledky, doplnenú o prehodnotenie a otvorené otázky.

### Vykonaná práca

- Vytvorený `ADR.md`, označený ako ADR-001, verzia 0.1 na pripomienkovanie. Stav dokumentu je oddelený od stavu rozhodnutia už prijatého v Task 1.
- Použitá štruktúra: kontext a požiadavky, pracovné predpoklady, kritériá, rozhodnutie a náčrt modulov, alternatívy, dôsledky a opatrenia, podmienky prehodnotenia, otvorené otázky a zdrojové odkazy.
- Potvrdené funkcie boli previazané na čísla user stories. Neprítomnosť údajov o záťaži či tíme nebola premenená na tvrdenie o malej prevádzke.
- LLM interpretácia a deterministický výber boli zachytené ako dohodnuté zodpovednosti pre konverzačný variant; schopnosti chatbota zostávajú pracovným predpokladom.
- Zachované rozlíšenie konkrétneho serverless návrhu od mikroslužieb aj ich kombinovateľnosť. Rozhodnutie odmietnuť zápis pri výpadku služby Recepty je označené ako čiastkový záver z mikroslužbového variantu, nie dôkaz existencie samostatnej služby v monolite.
- Do ADR neboli prevzaté technické doplnky z poznámok Task 1 ako nové schválené rozhodnutia. Nebol vybraný framework, cloud, LLM, číselné SLA ani finálna databázová schéma.

### Kontrola prvej verzie

Overené uloženie ADR, jeho oddiely a relatívne cesty k zadaniu a požiadavkám. Hash kontrola potvrdila, že Task 2 zadanie, RecipeCove.txt a task1_discussion.md zostali pri príprave ADR nezmenené. Nešlo o test implementácie aplikácie a neexistujú namerané prevádzkové výsledky. Nebol vytvorený AI skill ani vykonaný commit alebo push.

### Odovzdanie na spätnú väzbu

Asistent predkladá prvú verziu a vysvetľuje jej štruktúru. Žiada študenta posúdiť, či dokument verne zachytáva rozhodnutie, či niečo chýba alebo je nadbytočné a či vyhovuje jeho rozsah a usporiadanie.

**Stav:** čakáme na prvú spätnú väzbu študenta. Zatiaľ sa neuskutočnila žiadna iterácia podľa pripomienok a dokument nie je finálny. Task 2 nie je ukončený: zadanie ešte vyžaduje hodnotenie a viacero úprav podľa skutočnej spätnej väzby. Bez nej asistent ďalšie úpravy ADR nevykoná.

## Prvá spätná väzba študenta — požiadavky na verziu 0.2

Študent prečítal verziu 0.1 a hodnotí ju ako obsahovo kvalitnú. Ocenil jasné rozhodnutie, oddelenie potvrdených požiadaviek od predpokladov, porovnanie troch alternatív a identifikáciu rizík. Pred finálnym schválením požaduje:

1. Stručný Mermaid diagram s frontendom, jedným backendom a jeho modulmi, externými integráciami a diskutovaným dátovým variantom; rozlíšenie prijatých rozhodnutí od návrhov.
2. Priame prepojenie rozhodovacích kritérií s hodnotením alternatív a vysvetlenie priority jednoduchosti a konzistencie pred nezávislým nasadzovaním a škálovaním. Bez vymyslených skóre alebo benchmarkov.
3. Krátky prehľad prijatých rozhodnutí, návrhových variantov a otvorených otázok bez predstierania výberu DB, frameworku alebo LLM poskytovateľa.
4. Zlepšiť čitateľnosť a odstrániť opakovanie pri zachovaní argumentov, kompromisov a rizík.

Pred úpravami má zostať zachovaná verzia `ADR_v0.1.md`; pracovné `ADR.md` má niesť verziu 0.2. Študent nepovoľuje finálne uzavretie, vytvorenie skillu ani commit/push a žiada po úprave čakať na ďalšie hodnotenie.

### Začatie úprav

Asistent oznámil plán zachovať prvú verziu a doplniť diagram, hodnotenie podľa kritérií a prehľad stavu rozhodnutí. Pred editovaním ADR vytvoril `ADR_v0.1.md` ako kópiu pôvodného súboru; zhodu obsahu overil pomocou SHA-256. Zatiaľ nejde o finálne schválenie ani novú voľbu architektúry.

### Vykonané úpravy — ADR 0.2

- Aktualizovaná verzia na 0.2 a stav na pracovnú verziu čakajúcu na ďalšie hodnotenie. Prijatá voľba z Task 1 sa nezmenila.
- Doplnený stručný prehľad „prijaté / návrhový variant / otvorené“. Výslovne nebol vybraný databázový produkt, schéma, framework, hosting ani konkrétny LLM poskytovateľ.
- Pridaný Mermaid diagram s frontendovým HTTP vstupom, jednou prijatou hranicou backendu, šiestimi navrhnutými modulmi, Google identitou, podmienenou LLM integráciou a navrhovanou spoločnou relačnou DB. Návrhy majú slovné označenie aj prerušované okraje. Diagram zobrazuje variant lokálneho katalógu, nie schválenie jeho zdroja; umiestnenie kontextu rozhovoru neurčuje.
- Pôvodné porovnanie „prínos / kompromis“ nahradené tabuľkou, ktorá hodnotí všetky tri návrhy podľa rovnakých rozhodovacích kritérií. Doplnené zdôvodnenie priority jednoduchosti a lokálnej integrity pred zatiaľ nepotvrdenou potrebou nezávislých služieb.
- Výslovne uvedené, že serverless so spoločnou DB môže mať rovnaké transakčné záruky ako monolit. Konzistencia ho preto sama nevylučuje. Oddelenie LLM interpretácie je možné vo všetkých troch návrhoch a samo o sebe nie je dôvodom vybrať monolit.
- Skrátené opakované zoznamy prínosov a formulácie o nevybraných technológiách. Zachované riziká poolu, zdieľaných zdrojov, LLM kvót, modularity, neznámych údajov a podmienky prehodnotenia. Pribudol odkaz na zachovanú verziu 0.1.

### Overenie a stav

Po úpravách bol celý text verzie 0.2 prečítaný a porovnaný s pripomienkami. Overený hash zálohy zodpovedá pôvodnej verzii 0.1. Diagram bol skontrolovaný na úrovni zápisu a súladu s textom; Mermaid CLI (`mmdc`) nie je dostupné, preto neprebehlo automatické vykreslenie diagramu. Nepripisujeme mu overenie renderovaním.

Študent zatiaľ verziu 0.2 nehodnotil ani neschválil. Asistent odovzdáva pracovnú verziu so stručným vysvetlením zmien a čaká na ďalšiu spätnú väzbu. Nejde o finálny dokument ani ukončenie Task 2. Nebol vytvorený AI skill ani vykonaný commit či push.

## Druhá spätná väzba študenta — požiadavky na verziu 0.3

Študent skontroloval verziu 0.2 a je spokojný so zapracovaním pripomienok. Diagram, porovnanie alternatív a odlíšenie prijatých a otvorených rozhodnutí podľa neho výrazne zlepšili dokument. Pred finálnym schválením požaduje ešte menšiu iteráciu:

1. Stručne navrhnúť budúce overovanie vhodnosti monolitu cez merateľné ukazovatele a konkrétne scenáre, najmä vplyv pomalého LLM na ostatné funkcie. Nevymýšľať výsledky, číselné hranice ani potvrdené prevádzkové požiadavky.
2. Skontrolovať syntax a význam Mermaid diagramu a podľa možností jeho vykreslenie a vizuálnu čitateľnosť. Ak vykreslenie nie je možné, otvorene to uviesť.
3. Overiť všetky relatívne odkazy v ADR.
4. Skontrolovať stručnosť, konzistentnosť a opakovanie.

Žiada zachovať 0.2 ako `ADR_v0.2.md`, ponechať všetky staršie verzie a označiť aktuálny dokument ako 0.3. Nejde o finálne schválenie. Bez vytvárania AI skillu, commitu či pushu má asistent po úpravách čakať.

### Začatie druhej iterácie

Asistent oznámil plán doplnenia návrhu merania a kontroly dokumentu. Pred úpravami vytvoril kópiu `ADR_v0.2.md` a overil zhodu SHA-256 s vtedajším `ADR.md`. Pôvodnú verziu 0.1 nemenil. Overenie dostupných nástrojov nenašlo Node.js, npm, Mermaid CLI ani pripojený prehliadačový nástroj; vykreslenie diagramu zatiaľ nie je k dispozícii.

### Vykonané úpravy — ADR 0.3

- Verzia dokumentu je 0.3, stále rozpracovaná a čakajúca na finálne schválenie študenta. Architektonické rozhodnutie ani jeho rozsah sa nezmenili.
- Oddiel 6 doplnený o stručný návrh budúceho overovania: pomalé LLM počas ostatných funkcií, výpadok a naplnenie kapacity chatu, rast záťaže/replikovanie a súbežné či prerušené dátové operácie. Ukazovatele zahŕňajú rozdelenie odoziev, chybovosť, timeouty, odmietnutia, čakanie na DB spojenia, pracovníkov, CPU/pamäť, priepustnosť, celkové LLM volania/tokeny a porušenia integrity.
- Výslovne nejde o uskutočnené testy. Nepribudli namerané výsledky, číselné prahy ani SLA. Návrh počíta s porovnaním rovnakého prostredia a záťaže a s budúcou dohodou o prijateľnom správaní.
- V Mermaid zápise bol HTTP vstup zapísaný až po definovaní backendového podgrafu a jeho uzlov, aby bolo umiestnenie HTTP rozhrania v backende jednoznačné aj pri čítaní zdroja. Architektonické väzby zostali zachované.
- Pridaný odkaz na zachovanú verziu 0.2. Skrátené opakovanie postupu „meranie → jednoduchšie opatrenia → prípadná extrakcia“ v oddiele o prehodnotení.

### Výsledky kontroly

- **Odkazy:** automaticky vyhľadaných všetkých sedem výskytov relatívnych Markdown odkazov a vyriešených voči adresáru ADR; všetky smerujú na existujúce súbory. Ide o šesť rôznych cieľov, lebo RecipeCove.txt je odkazovaný dvakrát. Kontrola zahŕňa zadanie Task 2, opis projektu, oba záznamy diskusií a obe staršie verzie. Odkazy nemajú fragmenty, ktoré by vyžadovali kontrolu kotiev.
- **Diagram:** ručne preverený zápis `flowchart`, podgraf a `end`, definície uzlov, hrany, databázový tvar, trieda návrhov a štýl backendu. V zápise nebola zistená syntaktická chyba. Všetkých šesť modulov a ich vzťahy zodpovedajú textu; Google a LLM sú mimo backendu a spoločná DB zostáva návrhovým variantom. Bez dostupného Mermaid parsera/renderera nejde o automaticky potvrdenú syntaktickú validáciu ani o vizuálne overenie vykresleného výsledku. Čitateľnosť po vykreslení zostáva neoverená.
- **Verzie a chránené podklady:** hash verzie 0.1 aj zálohy 0.2 zostal zhodný s obsahom pred úpravami. Hash kontrola potvrdila nezmenené zadanie Task 2, RecipeCove.txt a task1_discussion.md.
- **Text:** skontrolovaná konzistentnosť prijatých a otvorených rozhodnutí, podmienenosť LLM a DB variantu a oddelenie návrhu overovania od výsledkov. Nová časť je obmedzená na jednu tabuľku scenárov a stručné vysvetlenie; existujúce technické riziká zostali zachované. Iné obsahové problémy neboli pri kontrole zistené.

### Stav po druhej iterácii

Asistent odovzdáva verziu 0.3 s výsledkami kontrol. Študent ju zatiaľ nehodnotil ani finálne neschválil; žiadna taká interakcia sa nepredpokladá. Čakáme na jeho finálne schválenie alebo ďalšie pripomienky. AI skill nebol vytvorený a commit ani push nebol vykonaný.

## Finálne schválenie a dokončenie Task 2

### Schválenie študenta

Študent po kontrole verzie 0.3 uviedol, že je spokojný s obsahom, štruktúrou a argumentáciou, a výslovne ju schválil ako obsahovo finálnu. Požiadal zmeniť verziu na 1.0 a stav na `Accepted`, zachovať dátum a obsah, ponechať staršie verzie, overiť odkazy a diagram a porovnať výstupy s Task 2. Povolenú archiváciu verzie 0.3 asistent vykonal. Študent naďalej zakazuje meniť pôvodné zadania a Task 1, vytvárať skill a vykonať commit či push.

### Priebeh iterácií

| Verzia | Skutočná udalosť |
|---|---|
| 0.1 | Prvý návrh podľa Task 1; študent ocenil obsah a požiadal o diagram, prepojenie kritérií s alternatívami, prehľad stavu rozhodnutí a skrátenie opakovania. |
| 0.2 | Zapracovaná prvá spätná väzba; študent bol spokojný a požiadal o návrh overovania, kontrolu diagramu, odkazov a konzistentnosti. |
| 0.3 | Zapracovaná druhá spätná väzba; študent verziu výslovne obsahovo schválil. |
| 1.0 | Administratívne uzavretie schválenej verzie: zmenená iba verzia a stav dokumentu na `Accepted`. |

### Vykonané záverečné kontroly

- Pred zmenou metadát vznikol `ADR_v0.3.md`; jeho SHA-256 sa zhodoval s vtedajším pracovným ADR. Verzie 0.1 a 0.2 zostali nezmenené, čo potvrdili ich hashe zhodné s predchádzajúcimi kontrolami.
- Automatické porovnanie celého textu finálneho ADR s verziou 0.3 po nahradení iba dvoch riadkov metadát potvrdilo, že obsah zostal zachovaný. Osobitne overený dátum `2026-10-29` zostal nezmenený.
- Znovu automaticky vyhľadaných a voči adresáru ADR vyriešených všetkých sedem výskytov relatívnych odkazov (šesť rôznych cieľov). Všetky ciele existujú ako súbory: opis RecipeCove, Task 2 zadanie, oba záznamy diskusií a verzie 0.1 a 0.2. Odkazy nemajú fragmenty. Verzia 0.3 je archivovaná a uvedená v tomto zázname; do schváleného obsahu ADR nebol pridaný nový odkaz.
- Mermaid diagram bol znovu ručne skontrolovaný pri čítaní ADR: podgraf a jeho ukončenie, uzly, hrany, popisky, databázový tvar, trieda a štýl. V zápise nebola zistená syntaktická chyba ani rozpor s opisom. Jeden backend obsahuje HTTP rozhranie a šesť navrhovaných modulov; Google a podmienený LLM sú externé, DB je výslovne návrhový variant.
- Dostupnosť `node`, `npm` a `mmdc` bola znovu overená; tieto príkazy nie sú dostupné. **Skutočné vykreslenie, overenie Mermaid parserom ani vizuálna kontrola vykresleného diagramu neprebehli.** Ručnú kontrolu nevydávame za automatickú validáciu. Toto je zostávajúce obmedzenie overenia.
- Hash kontrola potvrdila, že Task 2 zadanie, opis RecipeCove a task1_discussion.md zostali oproti začiatku Task 2 nezmenené. Asistent nevytváral implementáciu ani výsledky prevádzkových testov, AI skill, commit či push.

### Záverečný checklist voči `Week_05_Designing/Tasks/Task_2.md`

- [x] ADR vytvorený na základe skutočnej diskusie o architektúrach z Task 1.
- [x] Študent prvý návrh prečítal a posúdil obsah, štruktúru, chýbajúce a nadbytočné časti.
- [x] Prebehli dve obsahové iterácie podľa skutočných pripomienok: 0.1 → 0.2 → 0.3.
- [x] Zapracované vizuálne znázornenie a tabuľka hodnotenia alternatív.
- [x] Priebežný záznam vyžiadaný na začiatku a vedený počas práce.
- [x] Finálny Architecture Decision Record existuje ako `ADR.md`, verzia 1.0, stav `Accepted`, po výslovnom obsahovom schválení študentom.
- [x] Výstupmi sú finálne ADR a tento záznam rozhovoru. Archívne verzie navyše dokladajú iterácie.

**Výsledok:** Task 2 je dokončený; nezistili sme nesplnenú požiadavku jeho zadania. Zadanie nevyžaduje vykreslený export Mermaid diagramu; nemožnosť vykreslenia je otvorene zaznamenaná, nie prezentovaná ako vykonaná kontrola.

### Súbory odovzdávané za Task 2

V adresári `Week_05_Designing/RecipeCove/without_skill/`:

- `ADR.md` — finálny dokument, verzia 1.0, `Accepted`.
- `task2_discussion.md` — záznam práce, hodnotení, iterácií, schválenia a kontrol.
- `ADR_v0.1.md` — nezmenená prvá pracovná verzia.
- `ADR_v0.2.md` — nezmenená druhá pracovná verzia.
- `ADR_v0.3.md` — obsahovo schválená tretia pracovná verzia pred administratívnym uzavretím.

`task1_discussion.md` zostáva existujúcim, nezmeneným podkladom Task 1, nie novým výstupom Task 2. Historické stavy čakania vyššie opisujú príslušné fázy a neboli spätne prepísané. Po oznámení výsledkov sa práca zastavuje do ďalších pokynov študenta.
