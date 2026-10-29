# Task 1 – diskusia o architektúre RecipeCove

Dátum začiatku: 2026-10-29. Stav pri začiatku: analýza požiadaviek; architektúra nebola vybraná. Aktuálny výsledok a kontrola sú v E006.

## Zdroje a hranice

- [Oficiálne zadanie Task 1](../../Tasks/Task_1.md)
- [Pôvodné požiadavky RecipeCove](../../Tasks/data/RecipeCove.txt)
- Načítaný workflow: `.agents/skills/architecture-adr-workflow/SKILL.md` v koreni repozitára.
- Nový nezávislý priebeh: bez čítania pôvodných riešení, starších ADR alebo predchádzajúcich diskusií. Výstupy len v tomto adresári. ADR, Task 2 a porovnávacia správa zatiaľ nie sú povolené. Bez zmeny zadaní alebo skillu a bez commit/push.
- Záznam je priebežné zhrnutie skutočných výmen; nepredstavuje doslovný prepis. Opravy a zmeny rozhodnutí budú dopĺňané novými položkami.

## E001 – požiadavka používateľa a začiatok analýzy

**Používateľ:** Žiada načítať a overiť skill, analyzovať Task 1 a RecipeCove, priebežne zapisovať autentickú diskusiu a postupne preskúmať tri odlišné architektúry bez predurčenia voľby. Najprv stručná analýza, architektonické nejasnosti a jedna otázka; potom počkať na odpoveď.

**Asistent – overenie:** Súbor skillu bol skutočne načítaný z disku spolu s oboma pôvodnými podkladmi. Workflow vyžaduje oddeľovať požiadavky, predpoklady, návrhy a otvorené otázky; skúmať alternatívy po jednej vrátane implementačných kompromisov a zlyhaní; ponechať rozhodnutie používateľovi; viesť chronologický záznam a zastaviť po otázke vyžadujúcej odpoveď. Neznáma záťaž alebo tím sa nebudú interpretovať ako malý systém.

**Potvrdené požiadavky:** Webová aplikácia umožňuje vyhľadávanie receptov podľa názvu, zobrazenie receptov a ingrediencií (príbehy 2–4), odporúčania podľa diéty cez chatbot podľa opisu systému a príbehu 5, registráciu cez Google a prihlásenie/odhlásenie s profilom (1, 6–8), osobné kalendáre s udalosťami viazanými na recepty (9–11) a obľúbené recepty (12–14). Zadanie Task 1 vyžaduje diskusiu troch architektúr a záznam rozhovoru vrátane náročných implementačných detailov.

**Otvorené otázky a ich dopad:**

- Pôvod a aktualizácia receptov/ingrediencií: vlastný katalóg alebo externý zdroj ovplyvňuje vlastníctvo dát, vyhľadávanie a fungovanie pri výpadku.
- Správanie chatbota: pravidlové alebo generatívne odporúčania, práca s existujúcimi receptmi a význam dodržania diéty ovplyvňujú overovanie odpovedí, odozvu a závislosti. Zadanie nepredpisuje LLM.
- Rozsah pripomienok: udalosť v internom kalendári alebo aj aktívne upozornenie ovplyvňuje potrebu plánovania úloh a doručovania. Google prihlásenie samo osebe neznamená integráciu s Google Calendar.
- Neznáma záťaž, dostupnosť, rozpočet a kapacity tímu neumožňujú zatiaľ zdôvodniť prevádzkovú zložitosť alebo oddelené škálovanie.

**Pracovné predpoklady a návrhy:** Žiadne technologické riešenie, poskytovateľ, databáza ani veľkosť prevádzky neboli prijaté. Ide o analýzu, nie výber architektúry.

**Otázka asistenta:** Odkiaľ majú pochádzať recepty a údaje o ingredienciách: z vlastného katalógu RecipeCove, z externého API, alebo je to zatiaľ otvorené?

**Rozhodnutie:** Žiadne. Čaká sa na odpoveď používateľa; rozbor prvej alternatívy ešte nezačal.

## E002 – otvorený pôvod dát; prvá alternatíva

**Používateľ:** Pôvod receptov a ingrediencií ponecháva otvorený, pretože ho zadanie neurčuje. Žiada pri skúmaní architektúr zohľadniť vlastný katalóg aj externé API, ich výhody, nevýhody a dopad na návrh. Nechce zatiaľ prijímať rozhodnutia, ktoré nie sú nevyhnutné na porovnanie architektúr.

**Dohodnutý postup:** Obe možnosti ostávajú otvorené naprieč alternatívami. Nejde o rozhodnutie implementovať oba zdroje súčasne. Nasledujúce detaily sú návrh prvej alternatívy, nie prijaté rozhodnutia.

**Asistent – alternatíva A, modulárny monolit:** Jeden nasadzovaný backend s modulmi pre identitu/profil, katalóg, odporúčania, obľúbené a kalendár. Webové rozhranie volá backend cez HTTP; moduly sa volajú v procese. Trvalý stav je v spoločnej databáze s tabuľkami spravovanými príslušným modulom; medzi modulmi sú definované rozhrania. Viac replík celého backendu je možné, ale moduly sa v tomto návrhu samostatne nenasadzujú. Konkrétna databázová technológia ani hosting nie sú určené.

**Prechod požiadavkami:** Vyhľadávanie smeruje do katalógu; chatbot používa katalóg a mechanizmus výberu podľa diéty bez predpísania LLM. Pri pridaní obľúbeného receptu backend overí reláciu používateľa a uloží väzbu používateľ–recept. Jedinečnosť tejto dvojice v databáze zabráni duplicitám pri súbežných požiadavkách. Kalendár overuje vlastníctvo; súbežné zmazanie kalendára a pridanie udalosti treba ošetriť transakciou a referenčnou integritou. Aktívne doručovanie pripomienok zostáva otvorené.

**Variant vlastného katalógu:** Umožňuje lokálne vyhľadávanie, kontrolu štruktúry a transakčné väzby na recepty. Vyžaduje získavanie, aktualizáciu a normalizáciu údajov vrátane ingrediencií a diétnych značiek; správa katalógu nie je sama osebe potvrdenou používateľskou funkciou.

**Variant externého API:** Katalógový modul môže prekladať odpovede poskytovateľa do interného formátu. Znižuje potrebu vlastného zberu obsahu, ale prináša závislosť od dostupnosti, limitov, kvality a podmienok poskytovateľa. Obľúbené a udalosti zostávajú lokálne; externý recept potrebuje identitu zahŕňajúcu zdroj. Cudzí kľúč nemôže zaručiť existenciu záznamu u poskytovateľa. Pri zmiznutí receptu treba rozhodnúť o správaní rozhrania a prípadnej lokálnej kópii, ktorej prípustnosť zatiaľ nepoznáme.

**Zlyhanie a implementačný kompromis:** Pomalé externé API môže obsadiť kapacitu obsluhy požiadaviek spoločného backendu a spomaliť profil aj kalendár. Timeout, obmedzený počet súbežných volaní a oddelený fond spojení zmierňujú dopad, ale neobnovia chýbajúce dáta ani neodstránia spoločný proces a databázu ako miesta zlyhania. Opakovanie iba vybraných dočasných chýb musí byť obmedzené, inak môže preťaženie zhoršiť. Externé volanie sa nemá držať vo vnútri otvorenej databázovej transakcie.

**Prínosy a náklady:** Lokálne volania, jednoduchšie spoločné transakcie a jedno nasadenie oproti previazaným vydaniam, spoločnej kapacite a menšej izolácii porúch. Hranice modulov treba presadzovať v kóde, aby ich neobišli priame zásahy do cudzích tabuliek. Zatiaľ nejde o hodnotenie voči dvom ešte nepreskúmaným alternatívam.

**Otázka asistenta:** Ako hodnotíš pri RecipeCove kompromis medzi spoločným nasadením s jednoduchšími transakciami a rizikom, že pomalý chatbot alebo externé API ovplyvní aj profil a kalendár?

**Rozhodnutie a otvorené body:** Pôvod dát ostáva výslovne otvorený. Architektúra A ani jej detaily nie sú schválené. Čaká sa na reakciu k prvému návrhu; ďalšie dve alternatívy ešte neboli rozobraté.

## E003 – hodnotenie monolitu a druhá alternatíva

**Používateľ:** Spoločné nasadenie a jednoduchšie transakcie považuje za významné výhody vzhľadom na súvisiace údaje RecipeCove. Uznáva riziko spotreby spoločných zdrojov chatbotom alebo externým API, ale upozorňuje, že pomalé volanie automaticky nezablokuje celý backend: záleží na súbežnom spracovaní, timeoutoch a správe zdrojov. Monolit ostáva vhodným kandidátom bez konečného výberu. Žiada ďalšiu architektúru a vysvetlenie, či výhody vyvážia dodatočnú zložitosť.

**Spresnenie asistenta:** Pomalé I/O pri asynchrónnom spracovaní nemusí blokovať obslužné vlákno, stále však spotrebúva napríklad otvorené spojenia a pamäť. Výpočtová práca má iný dopad než čakanie na sieť. Predchádzajúci scenár je podmienené riziko vyčerpania kapacity, nie nevyhnutné zablokovanie backendu. Toto spresnenie nemení používateľovo hodnotenie na schválenie architektúry.

**Asistent – alternatíva B, samostatne nasadzované služby:** Konkrétny návrh má služby pre účet/profil, katalóg, odporúčania a osobné zbierky (obľúbené aj kalendáre). Web komunikuje cez vstupné API, ktoré smeruje požiadavky do služieb. Každá služba sa nasadzuje samostatne a vlastní svoje trvalé údaje; ostatné služby nečítajú priamo jej tabuľky. Vlastníctvo nepredpisuje samostatný fyzický databázový server. Odporúčania môžu byť bez vlastného trvalého úložiska. Medzi službami sa v tomto návrhu používajú sieťové API; broker ani udalosti zatiaľ nie sú potrebnou súčasťou. Ide o príklad rozdelenia, nie schválené hranice.

**Vlastný katalóg aj externé API:** Vlastný katalóg dáva katalógovej službe kontrolu nad receptami a ich aktualizáciou; jej výpadok však stále znemožní živé vyhľadávanie. Pri externom API ho sprostredkuje katalógová služba, ktorá rieši preklad údajov, timeouty a limity. Obe možnosti ponechávajú otvorenú dostupnosť receptov odkazovaných osobnými zbierkami. Zmena pôvodu dát nevyžaduje sama osebe distribuovanú architektúru: podobnú abstrakciu možno vytvoriť aj v monolite.

**Priebeh funkcií:** Vyhľadávanie ide do katalógu. Odporúčania volajú katalóg a prípadný ďalší mechanizmus odporúčania. Uloženie obľúbeného receptu ide do osobných zbierok, ktoré overia identitu a vlastníctvo; na každej požiadavke nemusia sieťovo volať profil, ak používajú lokálne overiteľný podpísaný doklad identity. Spôsob relácií a odhlásenia ostáva otvorený: okamžité zneplatnenie má ďalšie nároky. Obľúbené a kalendáre sú spolu, aby operácie nad nimi mohli zostať v lokálnej transakcii.

**Konzistencia a súbeh:** Pri overení existencie receptu v katalógu a následnom uložení obľúbeného receptu v inej službe neexistuje spoločná bežná databázová transakcia. Recept môže medzi krokmi zmiznúť; platí to aj pre vlastný katalóg, ak je oddelený. Návrh môže povoľovať dočasne neplatný odkaz s jasným zobrazením a následnou kontrolou, ale ide o kompromis vyžadujúci rozhodnutie. Samotná kontrola cez API nezaručí trvalú platnosť odkazu. Externé API má tento problém už v monolite. Súbeh zmazania kalendára a pridania udalosti ostáva lokálny v službe osobných zbierok.

**Poruchy, opakovanie a náklady:** Samostatná služba odporúčaní umožňuje oddelene obmedziť kapacitu, škálovať a nasadzovať jej zmeny. Jej výpadok nemusí zhodiť službu osobných zbierok; izolácia však závisí aj od infraštruktúry, vstupného API a spoločných závislostí. Stratená odpoveď po úspešnom zápise môže vyvolať opakovanú požiadavku: obľúbené chráni jedinečnosť dvojice používateľ–recept, vytváranie udalostí môže potrebovať identifikátor operácie s atómovým uložením výsledku. Zlyhanie jednej služby nemá viesť k nekontrolovaným opakovaniam v ostatných. Pribúdajú verzie API, autentifikácia medzi službami, koordinácia zmien, sieťová latencia a sledovanie požiadaviek naprieč procesmi.

**Porovnanie s A:** B ponúka samostatné nasadenie, riadenie kapacity a lepšiu izoláciu porúch za cenu sieťovej komunikácie, prevádzky viacerých služieb a konzistencie medzi vlastníkmi dát. A má tieto hranice v kóde a jednoduchšie lokálne transakcie, pričom vie tiež používať asynchrónne I/O a limity zdrojov. Bez údajov o záťaži, požadovanej izolácii, dostupnosti a tíme nemožno tvrdiť, že prínosy B vyvážia náklady. Relevantným hypotetickým dôvodom pre B je potreba samostatne prevádzkovať a meniť odporúčania pri zachovaní funkčnosti osobných zbierok; nie je to potvrdená požiadavka.

**Otázka asistenta:** Bolo by pre RecipeCove prijateľné uložiť odkaz na recept, ktorý môže byť neskôr nedostupný, a tento stav používateľovi vysvetliť, alebo očakávaš, že uložený recept zostane vždy zobraziteľný?

**Rozhodnutie a otvorené body:** Monolit zostáva kandidátom, výber nepadol. Druhá architektúra ani jej navrhnuté hranice neboli schválené. Otázka dostupnosti uloženého receptu je otvorená pre obe alternatívy, osobitne pri externom zdroji. Tretia alternatíva ešte nebola rozobratá.

## E004 – nedostupné recepty a tretia alternatíva

**Používateľ:** Považuje za prijateľné, že uložený recept môže byť neskôr nedostupný, najmä pri externom poskytovateľovi. Aplikácia má nedostupnosť jasne vysvetliť. Ak to podmienky zdroja umožnia, možno zachovať základné informácie ako názov. Uvádza prínos jednoduchšej implementácie bez úplných kópií aj nevýhodu straty prístupu k obsahu. Presnú podobu ponecháva otvorenú podľa pôvodu dát. Žiada tretiu architektúru bez finálneho výberu.

**Zachytené hodnotenie:** Ide o všeobecnú preferenciu správania RecipeCove, nie o výber architektúry B. Trvalá dostupnosť obsahu sa nevyžaduje; spôsob uchovania metadát nie je rozhodnutý. Dočasný výpadok alebo timeout sa nesmie automaticky vykladať ako definitívne odstránenie receptu.

**Asistent – alternatíva C, serverless funkcie s udalosťami a oddelenými čítacími pohľadmi:** Web volá vstupné HTTP API a krátko žijúce funkcie pre vyhľadávanie, profil, obľúbené a kalendár. Spravované úložisko drží autoritatívny používateľský stav; zápisové funkcie kontrolujú identitu a vlastníctvo a používajú transakčné možnosti úložiska. Zmeny sa cez spoľahlivý prúd zmien alebo transakčný outbox dostanú do frontu. Spracovateľ udalostí aktualizuje odvodený pohľad pre zoznam obľúbených a kalendár, napríklad s povolenými základnými metadátami receptu. Odporúčania a vyhľadávanie môžu byť synchrónne funkcie; generatívny model ani asynchrónny chatbot nie sú predpísané. Funkcie sa spúšťajú na požiadavky alebo udalosti, nemajú spoľahlivý trvalý stav v pamäti a nasadzujú sa ako samostatné jednotky alebo skupiny. Konkrétny poskytovateľ nie je vybraný.

**Odlišnosť a prekryv:** C je tiež distribuované riešenie a môže sa kombinovať so službami. Tu sa od B líši konkrétnym modelom krátko žijúcich funkcií, spravovaného spúšťania a asynchrónnej tvorby čítacích pohľadov namiesto priamo čítaných údajov jednotlivých služieb. Samotný prepis služieb do funkcií by tento rozdiel nevytvoril. Front má v návrhu účel oddeliť aktualizáciu pohľadov od potvrdenia zápisu, nie automaticky zabezpečovať zatiaľ neurčené pripomienky.

**Priebeh uloženia obľúbeného receptu:** Funkcia uloží väzbu a záznam udalosti atómovo, až potom potvrdí uloženie. Spracovateľ neskôr doplní čítací pohľad. Bez spoľahlivého zachytenia zmeny by pád medzi zápisom a odoslaním udalosti mohol nechať pohľad trvalo neaktuálny. Ihneď otvorený zoznam môže dočasne chýbajúcu položku zobraziť až po dobehnutí spracovania; rozhranie môže podržať potvrdenú položku alebo dočasne čítať autoritatívny stav. To je ďalšia implementačná vetva, nie odstránenie problému.

**Súbeh a poruchy:** Udalosti môžu prísť opakovane alebo mimo poradia. Ak používateľ recept pridá a hneď odstráni, oneskorené pridanie nesmie obnoviť zmazanú položku. Spracovateľ potrebuje napríklad verziu väzby a záznam zmazania; samotné filtrovanie duplicitných identifikátorov nestačí na poradie. Počas výpadku spracovateľa zápisy môžu pokračovať, ale pohľady zostávajú zastarané a treba sledovať aj opätovne spracovať neúspešné udalosti. Front nie je záloha autoritatívnych dát; pohľady majú byť obnoviteľné. Súbeh zmazania kalendára a pridania udalosti treba stále riešiť v autoritatívnom zápise, nie až v projekcii.

**Dva zdroje receptov:** Pri vlastnom katalógu možno zmenami aktualizovať aj odvodený vyhľadávací index, ak by bol potrebný; pridáva to oneskorenie indexácie a obnovu indexu. Pri externom API ostáva živé vyhľadávanie závislé od poskytovateľa a jeho limitov. Udalosti o jeho zmenách nemožno predpokladať; zistenie odstránenia môže vyžadovať načítanie alebo povolené pravidelné kontroly. Čítací pohľad nie je automatická záruka aktuálnosti ani oprávnenia kopírovať obsah. Nie je nevyhnutné vytvárať samostatný vyhľadávací index v oboch variantoch.

**Prínosy a náklady oproti A a B:** C presúva spúšťanie a časť škálovania na platformu a umožňuje samostatne spracovať nápor udalostí; spravované služby stále vyžadujú konfiguráciu, dohľad a limity. Automatické pribúdanie funkcií môže vyčerpať databázové spojenia alebo kvótu externého API, preto treba obmedziť súbežnosť. Pribúdajú studené štarty, limity trvania, oneskorenie pohľadov, opakovanie udalostí, závislosť od platformy a diagnostika naprieč krokmi. Náklady závisia od počtu spustení, čítaní, správ a záťaže; nemožno tvrdiť, že C je lacnejšia. A a B môžu po úspešnom zápise čítať priamo jeho stav bez dodatočnej asynchrónnej projekcie. C dáva zmysel skúmať, ak sú hodnotné oddelené spracovanie a spravovaná prevádzka a prijateľné oneskorenie pohľadov; také priority zatiaľ neboli potvrdené.

**Otázka asistenta:** Bolo by pre teba prijateľné, aby po potvrdenom pridaní obľúbeného receptu alebo udalosti zoznam krátko zobrazoval starší stav, alebo očakávaš, že nasledujúce načítanie už potvrdenú zmenu vždy ukáže?

**Rozhodnutie a otvorené body:** Finálny výber nepadol; C ani jej podrobnosti nie sú schválené. Všetky tri alternatívy už majú úvodný rozbor, diskusia a overovanie kompromisov pokračujú. Otvorená je tolerancia oneskorených čítacích pohľadov; nebola odvodená z prijateľnosti nedostupného receptu. ADR, Task 2 a porovnávacia správa sa nezačali.

## E005 – viditeľnosť vlastných zmien a podpora výberu

**Používateľ:** Pre obľúbené a kalendárové udalosti preferuje viditeľnosť potvrdenej zmeny pri nasledujúcom načítaní, pretože inak používateľ môže pochybovať o úspechu operácie. Rozumie prínosu aj zložitosti asynchrónnych pohľadov; krátke oneskorenie vyhľadávacieho indexu považuje za prijateľnejšie. Žiada stručne vysvetliť úpravu C, potom porovnať všetky tri návrhy rovnakými kritériami a pripraviť ho na vlastný výber. Finálne rozhodnutie nemá urobiť asistent.

**Zachytená preferencia a jej rozsah:** Viditeľnosť vlastného potvrdeného zápisu je kritérium naprieč alternatívami. Nie je požiadavkou na nulovú latenciu ani zárukou, že stav už nezmení iná súbežná operácia. Ide o spresnenie od používateľa, nie o doslovnú požiadavku pôvodného zadania. Pri indexe je tolerancia oneskorenia kvalitatívna; konkrétny čas nebol určený.

**Asistent – navrhnutá úprava C:** Zápisové funkcie potvrdia operáciu až po úspešnom commite. Čítacie funkcie pre obľúbené a kalendár čítajú priamo autoritatívne údaje režimom garantujúcim viditeľnosť potvrdených zápisov v potrebnom rozsahu. Obchádzajú zastarané cache a oneskorené repliky; konkrétne úložisko a jeho garancie treba ešte vybrať a overiť. Prúdy zmien alebo outbox môžu ďalej zásobovať asynchrónne odvodené údaje, napríklad index vlastného katalógu, ak bude potrebný. Optimizmus rozhrania sám osebe nezaručuje správnosť po obnovení stránky. Pri súbežnej neskoršej zmene môže byť správny výsledok odlišný od pôvodného zápisu.

**Kompromis:** Osobné zoznamy už nezávisia od dobehnutia projekcie a nepotrebujú jej synchronizáciu, ale ich čítanie zaťažuje autoritatívne úložisko a je závislé od jeho dostupnosti. Ak ho nemožno bezpečne čítať, rozhranie musí oznámiť problém, nie potichu prezentovať starý stav ako aktuálny. Silnejšie čítanie môže obmedziť výber úložiska a lacných replík či cache. Funkcie, front a spracovanie opakovaných udalostí zostávajú tam, kde sa udalosti naďalej používajú. C sa tým mení na hybrid; pôvodné oneskorené osobné pohľady z E004 nie sú súčasťou tejto upravenej verzie. Ide o návrh úpravy, nie schválenie architektúry používateľom.

**Spoločné porovnanie – A, B a upravená C:**

| Kritérium | A: modulárny monolit | B: samostatné služby | C: serverless s priamym čítaním osobných dát a asynchrónnymi odvodenými údajmi |
| --- | --- | --- | --- |
| Viditeľnosť vlastných zmien | Commit a čítanie autoritatívnych dát; pozor na cache/repliky | Rovnaká garancia v službe osobných zbierok; nie automaticky medzi službami | Commit a konzistentné čítanie priamo z úložiska; osobné projekcie nie sú potrebné |
| Transakcie a vlastníctvo | Spoločná databáza umožňuje transakcie naprieč modulmi; treba chrániť hranice modulov | Lokálne transakcie u vlastníka; väzby medzi službami bez spoločného cudzieho kľúča | Závisí od transakčných možností úložiska; funkcie samy garancie nevytvoria |
| Poruchy a kapacita | Asynchrónne I/O a limity pomáhajú, proces a nasadenie zostávajú spoločné | Samostatná kapacita a nasadenia; izoláciu môžu narušiť spoločné závislosti | Platforma spúšťa funkcie; treba limity súbežnosti a ochranu úložiska/API; front izoluje iba asynchrónnu časť |
| Prevádzka a implementácia | Menej sieťových hraníc, spoločné vydanie a potreba modulárnej disciplíny | Verzie API, sieťové chyby, zabezpečenie a diagnostika naprieč službami | Menej správy bežiacich procesov, ale limity platformy, opakovanie udalostí, dohľad a závislosť od poskytovateľa |
| Vlastný katalóg / externé API | Oba cez modul katalógu | Oba cez službu katalógu | Oba cez funkcie; index môže byť asynchrónny, externé zmeny nemožno automaticky odoberať |
| Náklady a vhodnosť | Neznáme bez záťaže a hostingu; spoločné škálovanie | Neznáme; viac prevádzkovaných jednotiek, možnosť cielenej kapacity | Neznáme; počet volaní, správ a operácií úložiska aj prípadná trvalá kapacita ovplyvnia cenu |

**Podpora rozhodnutia:** Používateľ už oceňuje jednoduché transakcie a nasadenie, požaduje viditeľnosť vlastných zmien a pripúšťa stratu dostupnosti pôvodného receptu. Oddelená prevádzka odporúčaní je možný prínos B, nie potvrdená priorita. Spravované spúšťanie je možný prínos C, ale prijatie platformových obmedzení a udalostí zatiaľ nie je potvrdené. Všetky tri návrhy môžu splniť preferenciu viditeľnosti osobných zmien pri správnom úložisku a čítaní. Neznáma záťaž, tím, dostupnosť a rozpočet neumožňujú vymyslieť váhy, benchmarky ani cenové poradie. Nie je určený víťaz.

**Otázka asistenta:** Ktorá priorita má pri tvojom výbere najväčšiu váhu: jednoduché spoločné nasadenie a transakcie, nezávislá prevádzka jednotlivých častí, alebo spravované spúšťanie funkcií za cenu obmedzení platformy?

**Stav:** Čaká sa na používateľove priority alebo doplňujúce otázky. Finálna architektúra nebola vybraná. Porovnanie je súčasťou vyžiadanej diskusie Task 1; samostatná porovnávacia správa, ADR ani Task 2 neboli vytvorené. Záznam bol doplnený priebežne, bez spätnej zmeny predchádzajúcich stanovísk.

## E006 – používateľovo rozhodnutie a kontrola Task 1

**Používateľovo rozhodnutie:** Vyberá **modulárny monolit**. Najväčšiu váhu dáva jednoduchosti implementácie, spoločného nasadzovania a práce so súvisiacimi údajmi; tieto prínosy považuje za relevantné už pre súčasné požiadavky. Potreba nezávislého škálovania a nasadzovania služieb zatiaľ nie je podložená údajmi. Dodatočnú zložitosť serverless návrhu vrátane udalostí, čítacích pohľadov a limitov platformy zatiaľ nepovažuje za odôvodnenú.

**Prijaté nevýhody a postup:** Akceptuje spoločné nasadzovanie a zdieľané zdroje. Ich vplyv sa má monitorovať a prednostne riešiť v rámci monolitu. Meraniami preukázaná potreba nezávislého škálovania alebo lepšej izolácie niektorej funkčnej oblasti je podnetom na prehodnotenie; nejde o prísľub migrácie. Konkrétne metriky, prahy a technické riešenia zatiaľ neboli dohodnuté ani merané.

**Rozsah rozhodnutia:** Schválená je voľba architektúry, nie ADR ani každý ilustračný implementačný detail. Naďalej platia používateľove preferencie z E004–E005: prijateľná nedostupnosť pôvodného receptu s vysvetlením a viditeľnosť vlastných potvrdených zmien v obľúbených a kalendári. Pôvod dát, prípadné uchovanie metadát, mechanizmus chatbota, doručovanie pripomienok, databáza a hosting zostávajú otvorené.

**Požiadavka na kontrolu:** Používateľ žiada overiť úplnosť voči oficiálnemu Task 1, bez vymýšľania interakcií a bez čítania pôvodného riešenia. ADR ani Task 2 sa nemajú začať.

### Kontrola vykonaná asistentom

Opätovne boli prečítané oficiálne zadanie Task 1, pôvodný RecipeCove.txt a celý tento nový záznam. Kontrola je manuálne posúdenie obsahu a nadväznosti; nejde o test implementácie ani o hodnotenie pridelené vyučujúcim.

| Požiadavka alebo kontrolovaný prvok | Dôkaz v zázname | Výsledok |
| --- | --- | --- |
| Načítanie požiadaviek prideleného projektu | E001, odkazy na pôvodné podklady | Splnené; RecipeCove určil používateľ, overenie e-mailového pridelenia nebolo súčasťou práce |
| Priebežné poznámky vyžiadané pred diskusiou | E001 a postupne vytvorené E002–E006 | Splnené |
| Tri konkrétne architektonické návrhy | A v E002, B v E003, C v E004 a jeho úprava v E005 | Splnené; popísané komponenty, vykonávanie, komunikácia, stav a nasadenie |
| Odlišnosť alternatív | Proces a spoločná databáza A; samostatní vlastníci dát a sieťové API B; funkcie a udalosti C | Splnené; prekryv B/C priznaný v E004, úprava C transparentne zachovaná v E005 |
| Kompromisy a náročné implementačné problémy | A: súbeh, obmedzenia databázy, spoločné zdroje; B: neplatné odkazy a opakované zápisy; C: spoľahlivý prenos, poradie a duplicity udalostí, konzistentné čítanie | Splnené vrátane scenárov zlyhania a limitov mitigácií |
| Väzba na RecipeCove a oba možné zdroje dát | E001–E005; vyhľadávanie, odporúčania, osobné údaje, kalendár | Splnené na úrovni architektonickej diskusie |
| Skutočné používateľove reakcie a rozhodnutia | E002: zdroj otvorený; E003: korekcia dopadu pomalého I/O; E004: nedostupný recept; E005: viditeľnosť zápisu; E006: výber monolitu | Zaznamenané; reakcie preukazujú prácu s kompromismi, nie formálny dôkaz úplného porozumenia |
| Porovnanie rovnakými kritériami | Tabuľka v E005 | Splnené bez vymyslených váh, meraní alebo cien |
| Požadovaný výstup – záznam rozhovoru | Tento súbor | Vytvorený; zadanie nevyžaduje doslovný prepis |

**Výsledok:** Task 1 považuje asistent podľa uvedených požiadaviek za obsahovo splnený. Nebol zistený chýbajúci povinný výstup. Autentické reakcie boli zaznamenané bez dopĺňania fiktívnych výmen. Úvodný údaj o stave bol označený ako historický a doplnený odkazom na túto položku; predchádzajúce stanoviská sa nemenili.

**Zostávajúce obmedzenia:** Nie všetky používateľské príbehy boli rozobraté krok po kroku; detailné Google prihlásenie/odhlásenie, spôsob odporúčaní a doručovanie pripomienok zostávajú na ďalšie spresnenie. Zadanie Task 1 nevyžaduje úplný implementačný návrh každého príbehu. Neznáma záťaž, tím, rozpočet a ciele dostupnosti obmedzujú prevádzkové a cenové závery. V upravenej C odpadli osobné čítacie projekcie; ich správa teda nie je nevyhnutným nákladom tejto upravenej verzie, hoci môže zostať pri iných odvodených údajoch. Táto poznámka spresňuje porovnanie a nemení používateľovo rozhodnutie.

**Hranice kontroly:** Predchádzajúce riešenia, ADR ani diskusie sa nečítali. Zmenený bol len tento súbor vo `with_skill/`. Neboli vykonané implementačné testy, merania ani validácia diagramov; záznam diagram neobsahuje. ADR, Task 2, samostatná porovnávacia správa, git commit ani push sa nevykonali. Schválenie architektúry používateľom sa nezamieňa so schválením konečného znenia tohto záznamu.

**Technická kontrola po zápise:** Opätovné načítanie UTF-8 potvrdilo položky E001–E006 bez duplicitných identifikátorov, prítomnosť rozhodovacej položky a existenciu oboch relatívne odkazovaných zdrojových súborov. Nebol nájdený náhradný znak Unicode U+FFFD. Nešlo o úplnú validáciu Markdownu ani jeho vykreslenia.
