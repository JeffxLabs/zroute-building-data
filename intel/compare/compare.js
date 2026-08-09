"use strict";
(function () {

const $ = id => document.getElementById(id);
const home = Intel.alliances.p1mp;
const opponent = Intel.alliances.biw;
const homeStats = Intel.stats(home.players);
const opponentStats = Intel.stats(opponent.players);
const ranks = ["R5","R4","R3","R2","R1"];
const formatDelta = value => `${value >= 0 ? "+" : "−"}${Intel.formatPower(Math.abs(value))}`;
const countAt = (alliance, threshold) => alliance.players.filter(player => player.power >= threshold).length;
const powerAt = (alliance, threshold) => Intel.sum(alliance.players.filter(player => player.power >= threshold).map(player => player.power));
const top = (alliance, depth) => Intel.sortedPlayers(alliance.players).slice(0, depth);

function summary(alliance) {
  const metric = Intel.stats(alliance.players);
  return `<div><div class="label">Listed</div><div class="value">${metric.count}</div></div><div><div class="label">Total</div><div class="value">${Intel.formatPower(metric.total)}</div></div><div><div class="label">Median</div><div class="value">${Intel.formatPower(metric.median)}</div></div>`;
}
$("home-summary").innerHTML = summary(home);
$("opponent-summary").innerHTML = summary(opponent);

function metricCard(label, homeValue, opponentValue, formatter = value => value) {
  const homeWins = homeValue > opponentValue, opponentWins = opponentValue > homeValue;
  return `<article><div class="label">${label}</div><div class="values"><span class="${homeWins ? "winner" : ""}">${formatter(homeValue)}</span><span class="${opponentWins ? "winner" : ""}">${formatter(opponentValue)}</span></div><div class="note">P1MP <span style="float:right">BIW</span></div></article>`;
}

function render() {
  const depth = Number($("lineup-depth").value);
  const threshold = Number($("power-threshold").value);
  const homeTop = top(home, depth), opponentTop = top(opponent, depth);
  const homeTopPower = Intel.sum(homeTop.map(player => player.power));
  const opponentTopPower = Intel.sum(opponentTop.map(player => player.power));
  const homeThresholdPower = powerAt(home, threshold), opponentThresholdPower = powerAt(opponent, threshold);
  const thresholdText = threshold ? `${threshold}M+` : "All listed";
  const thresholdIntro = threshold ? `At ${threshold}M+` : "Across all listed players";
  $("threshold-label").textContent = threshold ? `${threshold}M+` : "All power";
  $("lineup-title").textContent = `Top ${depth} lineup`;
  $("assessment-title").textContent = homeStats.total > opponentStats.total ? "P1MP holds a narrow roster-power edge" : "BIW holds the roster-power edge";
  $("assessment-note").textContent = `P1MP ${formatDelta(homeStats.total - opponentStats.total)} overall`;
  $("comparison-metrics").innerHTML = [
    metricCard("Total power", homeStats.total, opponentStats.total, Intel.formatPower),
    metricCard("Average power", homeStats.average, opponentStats.average, Intel.formatPower),
    metricCard("Median power", homeStats.median, opponentStats.median, Intel.formatPower),
    metricCard("Strongest member", homeStats.strongest.power, opponentStats.strongest.power, Intel.formatPower),
    metricCard(`${thresholdText} members`, countAt(home, threshold), countAt(opponent, threshold)),
    metricCard(`${thresholdText} power`, homeThresholdPower, opponentThresholdPower, Intel.formatPower),
    metricCard(`Top ${depth} power`, homeTopPower, opponentTopPower, Intel.formatPower),
    metricCard("Highest level", homeStats.maxLevel, opponentStats.maxLevel, value => `Lv. ${value}`),
    metricCard("Average level", homeStats.averageLevel, opponentStats.averageLevel, value => value.toFixed(1))
  ].join("");

  const thresholdCountDelta = countAt(home, threshold) - countAt(opponent, threshold);
  const lineupDelta = homeTopPower - opponentTopPower;
  $("insights").innerHTML = `
    <article class="insight"><strong>Overall: slight P1MP edge</strong>P1MP lists ${opponentStats.count - homeStats.count} fewer players but about ${Intel.formatPower(homeStats.total - opponentStats.total)} more power (+${((homeStats.total / opponentStats.total - 1) * 100).toFixed(1)}%). Its median is ${Intel.formatPower(homeStats.median - opponentStats.median)} higher.</article>
    <article class="insight"><strong>Lineup depth: ${lineupDelta >= 0 ? "P1MP" : "BIW"} at top ${depth}</strong>The selected lineup totals differ by ${Intel.formatPower(Math.abs(lineupDelta))}. P1MP wins ${homeTop.filter((player,index) => player.power > (opponentTop[index]?.power ?? 0)).length} of ${Math.min(homeTop.length,opponentTop.length)} same-position matchups.</article>
    <article class="insight"><strong>Threshold: ${thresholdCountDelta >= 0 ? "P1MP" : "BIW"} has ${Math.abs(thresholdCountDelta)} more</strong>${thresholdIntro}, P1MP has ${countAt(home,threshold)} listed members and BIW has ${countAt(opponent,threshold)}. Change the threshold to test the middle or elite band.</article>
    <article class="insight"><strong>Different strengths at the ceiling</strong>P1MP's strongest member is ${homeStats.strongest.name} at ${Intel.formatPower(homeStats.strongest.power)}; BIW reaches the higher Base level ceiling at Lv. ${opponentStats.maxLevel} versus Lv. ${homeStats.maxLevel}.</article>`;

  const rankTotals = Object.fromEntries(ranks.map(rank => [rank, {
    home: Intel.sum(home.players.filter(player => player.rank === rank).map(player => player.power)),
    opponent: Intel.sum(opponent.players.filter(player => player.rank === rank).map(player => player.power))
  }]));
  const maxRank = Math.max(...Object.values(rankTotals).flatMap(value => [value.home,value.opponent]));
  $("rank-bars").innerHTML = ranks.map(rank => `<div><div class="bar-row"><strong class="rank-${rank.toLowerCase()}">${rank} P1MP</strong><div class="bar-track"><div class="bar" style="width:${rankTotals[rank].home / maxRank * 100}%"></div></div><div class="bar-value">${Intel.formatPower(rankTotals[rank].home,1)}</div></div><div class="bar-row"><span class="note">${rank} BIW</span><div class="bar-track"><div class="bar opponent" style="width:${rankTotals[rank].opponent / maxRank * 100}%"></div></div><div class="bar-value">${Intel.formatPower(rankTotals[rank].opponent,1)}</div></div></div>`).join("");

  $("matchups").innerHTML = homeTop.map((player,index) => {
    const enemy = opponentTop[index];
    const difference = player.power - (enemy?.power || 0);
    return `<tr><td data-label="Match">${index + 1}</td><td data-label="P1MP"></td><td data-label="P1MP power" class="power">${Intel.formatPower(player.power)}</td><td data-label="BIW"></td><td data-label="BIW power" class="power">${enemy ? Intel.formatPower(enemy.power) : "—"}</td><td data-label="Edge" class="${difference >= 0 ? "advantage-home" : "advantage-opponent"}">${difference >= 0 ? "P1MP" : "BIW"} ${Intel.formatPower(Math.abs(difference))}</td></tr>`;
  }).join("");
  homeTop.forEach((player,index) => {
    $("matchups").rows[index].cells[1].textContent = player.name;
    $("matchups").rows[index].cells[3].textContent = opponentTop[index]?.name || "—";
  });
}

$("lineup-depth").addEventListener("change", render);
$("power-threshold").addEventListener("input", render);
render();
})();
