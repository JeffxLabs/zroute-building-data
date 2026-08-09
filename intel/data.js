"use strict";
(function () {

const makePlayers = rows => rows.map(([rank, name, level, power, role]) => ({rank, name, level, power, role}));

const alliances = {
  biw: {
    id: "biw", tag: "BIW", name: "BloodWing", server: 116, relation: "Opponent alliance",
    leader: "МатьСерверов~", language: "Russian", scouted: "Aug 9, 2026 · 2:05 p.m. ET", serverTime: "Aug 9, 2026 · 4:05 p.m.",
    precision: "Powers were supplied rounded to 0.1M.",
    players: makePlayers([
      ["R5","МатьСерверов~",20,12.4],
      ["R4","-Ragnar-",23,26.7],["R4","Egoistelux",21,17.8],["R4","Lordsnoy6",20,15.8],["R4","-Sunshine-",17,9.1],["R4","Депутат",22,26.6],
      ["R3","qviler13",26,22.9],["R3","Колчакъ",20,13.9],["R3","Виталик124",20,12.6],["R3","EHOT22",20,12.0],["R3","2Rist96",20,10.2],["R3","1Dark~King1",19,10.3],["R3","Yana163",19,8.0],["R3","AlexKiller",18,10.3],["R3","Легендарный",18,11.2],["R3","☯Harmony☯",21,16.2],["R3","Влад26",20,14.7],["R3","ViKki",20,9.5],["R3","Hooch",21,14.8],["R3","🤌Белочка🤌",19,11.8],["R3","САХАРОК161",20,13.2],["R3","денчик26",18,7.5],["R3","КрасныйТелепузик",21,20.7],["R3","Crazy-KrakeN",21,22.4],["R3","DenSibir",20,15.1],["R3","Lady~Vengeance",20,15.8],["R3","Egoistkalux",18,10.0],["R3","Мэмфис",18,12.6],["R3","MooN",20,17.1],["R3","V0van",24,22.6],["R3","TopOneSNG",18,6.1],["R3","харашо",17,9.2],["R3","Семь",20,14.9],["R3","Пилигрим",20,11.0],["R3","GROZZ",20,11.5],["R3","Kellt",21,17.9],["R3","Кот-Капоне🤝",18,6.8],["R3","JIaMnoBa-H9IIIKa",21,22.8],["R3","MONTER",19,11.9],["R3","Пулька-Шпулька",19,8.6],["R3","opexu",18,6.6],["R3","-PRETORIAN-",20,13.1],["R3","Artesska",18,8.4],["R3","Ruslan4ik228",18,12.8],["R3","alex6419",17,9.6],
      ["R2","♔ØŁ乇G♔",18,8.1],["R2","Bastian",18,5.3],["R2","Tirr",16,7.5],["R2","Шиш1986",15,8.3],["R2","MYROMEC",17,5.5],["R2","Egoist61",19,5.2],["R2","MonsterEnergy031",18,8.7],["R2","путятя",18,6.3],["R2","blikmax",19,9.2],["R2","АНАТОЛИЙ44",17,7.8],["R2","PIWTIPIWPIW",17,8.4],["R2","МакаЧленс",17,7.7],["R2","Kristinkka",15,4.9],["R2","кофеιη",16,4.3],["R2","Ömer16",18,8.1],["R2","NSA26",17,5.6],["R2","VezdexoD",17,10.4],["R2","Ромарио1987",18,7.3],["R2","•SunRay•",18,8.4],["R2","Alexbro",18,6.2],["R2","DIZELL",18,8.0],["R2","Umbrella",17,5.4],["R2","9миля",16,6.7],["R2","incitanem",20,12.1],["R2","тремар",18,10.4],["R2","Dobruy",20,10.8],["R2","Дминко",15,7.7],["R2","22ОТБМП55Бр",15,5.1],["R2","♔ARHØNT♔",17,5.8],["R2","Кэкусик",17,10.4],["R2","Колумб-Псков",19,6.2],["R2","says",18,6.5],
      ["R1","drKsen",21,15.2],["R1","VIsion",18,11.0],["R1","гнутый",18,6.3],["R1","MaríaAmarilla",17,8.6],["R1","горемуж",16,7.1],["R1","Tre3d3",15,7.4],["R1","dyhbvdfg",15,7.4],["R1","Noname669",17,7.3],["R1","meoook",15,4.6],["R1","татарин23408",19,10.0],["R1","ToKio",18,6.1],["R1","DrKiss",16,6.5],["R1","Karatel777",10,2.6],["R1","V1rtyoZ",20,15.1],["R1","Fenrir1488",17,9.9],["R1","SoriuGared",15,7.3],["R1","kbpf77",16,4.4],["R1","черныйкот",16,7.7],["R1","Ruha°",16,5.4],["R1","Evgenk0",15,6.0],["R1","Bizon33",17,5.9],["R1","Шершавый",17,9.0],["R1","Kulik72",17,8.0]
    ])
  },
  p1mp: {
    id: "p1mp", tag: "P1MP", name: "JU1CE", server: 117, relation: "Home alliance",
    leader: "TheRequiem", language: "Not supplied", scouted: "Aug 9, 2026 · 6:24 p.m. ET", serverTime: "Aug 9, 2026 · 8:24 p.m.",
    precision: "TheRequiem and CallMeP1MPKamil are exact; other powers were supplied rounded to 0.1M.",
    players: makePlayers([
      ["R5","TheRequiem",24,24.746607],
      ["R4","Jeff",19,11.5,"Butler"],["R4","T83",18,8.4],["R4","Disorder762",23,26.0,"Warlord"],["R4","PettyPimp",20,16.9,"Goddess"],["R4","MacadamiaNut",19,10.2],["R4","CallMeP1MPKamil",21,22.086973],["R4","luckyy",20,17.3],
      ["R3","chauncey",22,25.3],["R3","AyeGee",21,12.4],["R3","SerenaMoon",20,11.5],["R3","LegendTR",19,12.9],["R3","Boomboomberry",19,12.8],["R3","skinnybigpoppa",18,11.9],["R3","GoodBabyGirl",18,11.9],["R3","JoanCornielle",18,11.5],["R3","Chickendog",19,10.8],["R3","vforvendetta",18,11.5],["R3","Librarian",21,20.0],["R3","B3N",19,12.1],["R3","GeekHunter",16,8.0],["R3","Wacker",17,12.1],["R3","Owen6767",20,12.8],["R3","PimpinDudes",20,17.6],["R3","Isab3ll",16,9.6],["R3","JimmyJam",21,26.2],["R3","MrWhiskey",21,19.4],["R3","Mohammad2824",18,10.6],["R3","Luke65",20,20.0],["R3","laggingPotato",16,9.1],["R3","HandStrong",15,8.1],["R3","Eldagrim",23,32.3],["R3","Locianos",17,8.5],["R3","Limps",18,7.7],["R3","DemonKiller",18,8.4],["R3","DLiner75",18,10.8],["R3","Staemmo",17,10.7],["R3","Blockboy5",19,9.3],["R3","Analbrutal",18,9.5],["R3","PreacheR",16,11.0],["R3","DeathReapers",18,10.2],["R3","babeblade",19,5.9],["R3","Sinister-Soul",19,11.4],["R3","Shunter",20,11.6],["R3","dbjack23",17,6.8],["R3","Kpeast",17,5.8],["R3","PimpReaper",18,13.0],["R3","Rhyzup",19,9.4],["R3","Rhyss",18,12.3],["R3","Freaxx99",20,12.7],["R3","Toblinice",18,13.2],["R3","Momof7",18,10.5],["R3","Nando6331",19,9.0],["R3","STEALTH",21,13.7],["R3","Spicy1",19,10.4],["R3","archer339",18,6.6],["R3","알까기",19,15.2],["R3","SupremeDuke",21,13.2],["R3","becerrito123",17,11.2],["R3","HAMMERS",16,8.6],["R3","Id3mo",19,12.7],["R3","TheGreaterGood",18,13.2],["R3","DewaLipan",20,13.8],["R3","Pipocashisha",17,10.5],["R3","Bode",19,11.6],["R3","BOUGE",18,7.0],["R3","lupa1987",15,8.1],["R3","Azumiii",17,5.3],["R3","LumaPR",19,12.3],["R3","Agam0017",20,16.7],
      ["R2","Brody138",19,12.6],["R2","周星星",18,11.8],["R2","FFChucky",18,11.1],["R2","SadSquatch",17,9.2],["R2","KaryLive",17,8.5],["R2","BoredAtWork",20,9.0],["R2","KILLABWOY2002",13,2.7],["R2","DrUpInSmoke",18,7.4],["R2","Nevers54",18,9.2],["R2","Slickback",17,7.6],["R2","Vieques",20,15.2],["R2","Rakna",15,6.7],["R2","-NERO-",18,10.1],["R2","ComandanteMike",15,6.8],["R2","PimpIsDaddy",17,4.2],["R2","XYZ-A",18,10.8],["R2","Redwind",20,6.2],["R2","asiruh09",17,10.2],["R2","Dracolish",17,6.0],["R2","Grandpaowl",18,8.5],["R2","HCultLeader",17,6.3],["R2","dujones",18,10.7],["R2","Skitz0",18,5.1],["R2","CuteCat",18,9.0],["R2","tdoggg",18,7.0],["R2","winterwulf",17,6.5],["R2","ImaV",19,5.0],
      ["R1","ChucklesTheHutt",18,5.5]
    ])
  }
};

const rankOrder = {R1: 1, R2: 2, R3: 3, R4: 4, R5: 5};
const sum = values => values.reduce((total, value) => total + value, 0);
const average = values => sum(values) / values.length;
const median = values => {
  const sorted = [...values].sort((a, b) => a - b);
  return (sorted[(sorted.length - 1) >> 1] + sorted[sorted.length >> 1]) / 2;
};
const stats = players => ({
  count: players.length,
  total: sum(players.map(player => player.power)),
  average: average(players.map(player => player.power)),
  median: median(players.map(player => player.power)),
  averageLevel: average(players.map(player => player.level)),
  maxLevel: Math.max(...players.map(player => player.level)),
  strongest: [...players].sort((a, b) => b.power - a.power)[0]
});
const formatPower = (value, digits = 2) => `${value.toLocaleString(undefined, {maximumFractionDigits: digits})}M`;
const sortedPlayers = (players, key = "power", descending = true) => [...players].sort((a, b) => {
  const direction = descending ? -1 : 1;
  const difference = key === "name" ? a.name.localeCompare(b.name) : key === "rank" ? rankOrder[a.rank] - rankOrder[b.rank] : a[key] - b[key];
  return direction * difference || a.name.localeCompare(b.name);
});

if (alliances.biw.players.length !== 100 || alliances.p1mp.players.length !== 98 || Math.abs(stats(alliances.biw.players).average - 10.321) > 1e-9) {
  throw new Error("Alliance intel data self-check failed");
}

window.Intel = {alliances, rankOrder, stats, formatPower, sortedPlayers, sum};
})();
