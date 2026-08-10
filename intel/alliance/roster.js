"use strict";
(function () {

const $ = id => document.getElementById(id);
const id = new URLSearchParams(location.search).get("id") || "biw";
const alliance = Intel.alliances[id] || Intel.alliances.biw;

const metric = Intel.stats(alliance.players);
document.title = `[${alliance.tag}] ${alliance.name} Alliance Intel`;
$("insignia").textContent = alliance.tag;
if (id === "p1mp") $("insignia").classList.add("home");
$("alliance-name").innerHTML = `<span>[${alliance.tag}]</span> ${alliance.name}`;
$("precision").textContent = alliance.precision;
$("precision").hidden = !alliance.precision;
$("server").textContent = `#${alliance.server}`;
$("leader").textContent = alliance.leader;
$("language").textContent = alliance.language;
$("members").textContent = metric.count;
$("scouted").textContent = alliance.scouted;
$("server-time").textContent = alliance.serverTime;
$("total-power").textContent = Intel.formatPower(metric.total);
$("average-power").textContent = Intel.formatPower(metric.average);
$("median-power").textContent = Intel.formatPower(metric.median);
$("average-level").textContent = metric.averageLevel.toFixed(1);

let sort = "power", descending = true;
function render() {
  const query = $("search").value.trim().toLocaleLowerCase();
  const rank = $("rank-filter").value;
  const visible = Intel.sortedPlayers(alliance.players.filter(player => (!rank || player.rank === rank) && (!query || player.name.toLocaleLowerCase().includes(query))), sort, descending);
  const ranked = sort === "power" || sort === "level";
  const standings = new Map();
  if (ranked) {
    let previous, standing;
    Intel.sortedPlayers(alliance.players, sort, true).forEach((player, index) => {
      if (player[sort] !== previous) previous = player[sort], standing = index + 1;
      standings.set(player, standing);
    });
  } else visible.forEach((player, index) => standings.set(player, index + 1));
  $("standing-title").textContent = ranked ? `${sort[0].toUpperCase() + sort.slice(1)} #` : "View #";
  $("players").innerHTML = visible.length ? visible.map(player => `<tr class="rank-${player.rank.toLowerCase()}"><td class="standing" title="${ranked ? `${sort} rank` : "view position"} ${standings.get(player)}">#${standings.get(player)}</td><td class="rank rank-${player.rank.toLowerCase()}"><span>${player.rank}</span></td><td></td><td>Lv. ${player.level}</td><td class="power">${Intel.formatPower(player.power)}</td></tr>`).join("") : `<tr><td class="empty" colspan="5">No players match.</td></tr>`;
  visible.forEach((player, index) => {
    const cell = $("players").rows[index].cells[2];
    cell.textContent = player.name;
    if (player.role) cell.insertAdjacentHTML("beforeend", ` <span class="role"></span>`), cell.lastElementChild.textContent = `· ${player.role}`;
  });
  $("status").textContent = `Showing ${visible.length} of ${alliance.players.length} players · ${sort[0].toUpperCase() + sort.slice(1)} ${descending ? "high to low" : "low to high"}`;
  document.querySelectorAll("th").forEach(th => th.removeAttribute("aria-sort"));
  document.querySelector(`[data-sort="${sort}"]`).parentElement.setAttribute("aria-sort", descending ? "descending" : "ascending");
  $("sort-by").value = sort;
  $("direction").textContent = descending ? "Descending ↓" : "Ascending ↑";
}

document.querySelectorAll("[data-sort]").forEach(button => button.addEventListener("click", () => {
  if (sort === button.dataset.sort) descending = !descending;
  else sort = button.dataset.sort, descending = sort !== "name";
  render();
}));
$("sort-by").addEventListener("change", event => { sort = event.target.value; descending = sort !== "name"; render(); });
$("direction").addEventListener("click", () => { descending = !descending; render(); });
$("search").addEventListener("input", render);
$("rank-filter").addEventListener("change", render);
render();
})();
