#!/usr/bin/env python3
"""Génère les 12 niveaux de Super Maël Bros sous forme de tableaux de tuiles.

Chaque niveau est assemblé à partir de tronçons dessinés à la main
(alignés sur le bas, 15 lignes de haut), puis injecté dans index.html
entre les marqueurs LEVELS-BEGIN / LEVELS-END.

Légende des tuiles :
  .  vide          #  sol           B  brique         ?  bloc pièce
  P  bloc graine   M  brique à pièces multiples        S  pierre
  =  plateforme traversable          ^  piques         ~  lave
  o  pièce         C  lanterne (point de contrôle)     X  portail
  @  départ        A  entrée de l'arène                Z  boss
  w  peluchon (marcheur)   e  peluchon roux (fait demi-tour au bord)
  k  pikou (piquant)       f  frelune (volant)
  j  bondille (sauteur)    t  crachepierre (tireur)
"""
import json
import random
import re
import sys
from pathlib import Path

H = 15


def chunk(d, worlds, rows):
    return {"d": d, "w": worlds, "rows": rows}


CH = {
    "flat_coins": chunk(1, "1234", [
        "..............",
        "....oooooo....",
        "..............",
        "..............",
        "..............",
        "##############",
        "##############"]),
    "blocks": chunk(1, "1234", [
        "......?.......",
        "..............",
        "..............",
        "..............",
        "..B?BPB.......",
        "..............",
        "..............",
        "..........w...",
        "##############",
        "##############"]),
    "gap": chunk(1, "1234", [
        ".....ooo.....",
        ".............",
        ".............",
        ".............",
        "#####...#####",
        "#####...#####"]),
    "walkers": chunk(1, "1234", [
        "....?...?.....",
        "..............",
        "..............",
        "...w......w...",
        "##############",
        "##############"]),
    "stairs": chunk(1, "1234", [
        "........o.......",
        "........S.......",
        ".......SS.......",
        "......SSS.......",
        ".....SSSS.......",
        "....SSSSS....w..",
        "################",
        "################"]),
    "valley": chunk(1, "1234", [
        "...S........S...",
        "..SS...oo...SS..",
        ".SSS........SSS.",
        "SSSS...w....SSSS",
        "################",
        "################"]),
    "bricks": chunk(1, "1234", [
        "...oooooo.....",
        "..............",
        "..............",
        "..............",
        "..BBBMBB?B....",
        "..............",
        "..............",
        "..............",
        "##############",
        "##############"]),
    "oneway": chunk(2, "1234", [
        "........ooo.........",
        "....................",
        "....................",
        ".......=====........",
        "....................",
        "....................",
        "..====.......====...",
        "....................",
        "##..............####",
        "##..............####"]),
    "flyers": chunk(2, "1234", [
        "..........f.......",
        "..................",
        "....oooo..........",
        "..................",
        "..................",
        "..................",
        "######...#########",
        "######...#########"]),
    "jumpers": chunk(2, "1234", [
        "......B?B.......",
        "................",
        "................",
        "..j.........j...",
        "################",
        "################"]),
    "shooter": chunk(2, "1234", [
        "......B?B.........",
        "..................",
        "..................",
        "..o.o.o.....S..t..",
        "##################",
        "##################"]),
    "spikes": chunk(2, "1234", [
        "..............",
        "....oooooo....",
        "..............",
        "....======....",
        "..............",
        "....^^^^^^....",
        "##############",
        "##############"]),
    "pits": chunk(2, "1234", [
        "....o.....o....o...",
        "...................",
        "...................",
        "...................",
        "###...###...##...##",
        "###...###...##...##"]),
    "lowceiling": chunk(2, "2", [
        "..BBBBMBBBBBB...",
        "................",
        "...o.o.o.o.o....",
        "......w.........",
        "################",
        "################"]),
    "shooter_high": chunk(3, "34", [
        "..........t.....",
        ".........SS.....",
        "........SSS.....",
        ".......SSSS.....",
        "...w..SSSSS.....",
        "################",
        "################"]),
    "bigjump": chunk(3, "1234", [
        "..........ooo.......",
        "....................",
        "..S.................",
        ".SS.................",
        "SSS.............w...",
        "###.....############",
        "###.....############"]),
    "stepping": chunk(3, "1234", [
        "........f...........",
        "....................",
        "....................",
        "....ooo...ooo.......",
        "....................",
        "....SS...SS...SS....",
        "....................",
        "....................",
        "##................##",
        "##................##"]),
    "spikies": chunk(3, "34", [
        "......B?BB......",
        "................",
        "................",
        "..k.......k.....",
        "################",
        "################"]),
    "pillars": chunk(3, "1234", [
        "...............f.....",
        ".....................",
        "...........SS........",
        ".......SS..SS........",
        "...SS..SS..SS..SS....",
        "...SS..SS..SS..SS....",
        "...SS..SS..SS..SS....",
        "##.SS..SS..SS..SS..##",
        "##.SS..SS..SS..SS..##"]),
    "lavabridge": chunk(3, "4", [
        ".....o...o...o.......",
        ".....................",
        "....S...S...S...S....",
        "....S...S...S...S....",
        "##..S...S...S...S..##",
        "##..S...S...S...S..##"]),
    "castle_spikes": chunk(3, "4", [
        "..ooo...ooo.......",
        "..................",
        "..===...===.......",
        "..................",
        "..^^^^^^^^^^^^..t.",
        "##################",
        "##################"]),
    "gauntlet": chunk(4, "1234", [
        "......f.........f.....",
        "......................",
        "......................",
        ".........?............",
        "......................",
        "......................",
        "...j.........j........",
        "#######...#####...####",
        "#######...#####...####"]),
    "fortress_run": chunk(4, "34", [
        "............t.......",
        "...........SSS......",
        "....................",
        "......===...........",
        "....................",
        "...k.........k......",
        "#####..#############",
        "#####..#############"]),
}

START = [
    "............",
    ".@..........",
    "############",
    "############"]
CHECK = [
    "....C.....",
    "##########",
    "##########"]
END = [
    "...........SS...............",
    "..........SSS...............",
    ".........SSSS...............",
    "........SSSSS...............",
    ".......SSSSSS...............",
    "......SSSSSSS......X........",
    "############################",
    "############################"]
CORRIDOR = [
    "........",
    "########",
    "########"]
ARENA = [
    "SSSSSSSSSSSSSSSSSSSSSSSSSS",
    "SSSSSSSSSSSSSSSSSSSSSSSSSS",
    ".........................S",
    ".........................S",
    ".........................S",
    ".........................S",
    ".........................S",
    ".........................S",
    "....===..........===.....S",
    ".........................S",
    ".........................S",
    ".........................S",
    "A....................Z...S",
    "SSSSSSSSSSSSSSSSSSSSSSSSSS",
    "SSSSSSSSSSSSSSSSSSSSSSSSSS"]


def pad(rows, name):
    w = len(rows[0])
    for r in rows:
        if len(r) != w:
            sys.exit(f"tronçon {name}: largeur incohérente ({len(r)} au lieu de {w}) : {r}")
    if len(rows) > H:
        sys.exit(f"tronçon {name}: trop haut")
    return ["." * w] * (H - len(rows)) + list(rows)


for name, c in CH.items():
    rows = pad(c["rows"], name)
    for col in (0, len(rows[0]) - 1):
        if rows[13][col] != "#" or rows[14][col] != "#":
            sys.exit(f"tronçon {name}: la colonne {col} doit reposer sur le sol")
    c["rows"] = rows

MAXD = [1, 1, 2, 2, 2, 3, 2, 3, 3, 3, 4, 4]
NCH = [6, 7, 8, 8, 9, 10, 9, 10, 11, 10, 11, 8]
SUBST = {
    0: [("w", 1.0)],
    1: [("w", 0.6), ("e", 0.4)],
    2: [("w", 0.3), ("e", 0.4), ("k", 0.3)],
    3: [("e", 0.5), ("k", 0.5)],
}


def pick(rnd, table):
    x = rnd.random()
    for ch, p in table:
        x -= p
        if x <= 0:
            return ch
    return table[-1][0]


def build(idx):
    world = idx // 3
    rnd = random.Random(4242 + idx * 101)
    maxd = MAXD[idx]
    n = NCH[idx]
    pool = [k for k, c in CH.items() if c["d"] <= maxd and str(world + 1) in c["w"]]
    seq, last = [], None
    if idx == 0:
        seq, last = ["blocks"], "blocks"
    guard = 0
    while len(seq) < n:
        guard += 1
        weights = [1 + 2 * (CH[k]["d"] == maxd) + (CH[k]["d"] >= maxd - 1) for k in pool]
        k = rnd.choices(pool, weights)[0]
        if guard < 500 and (k == last or seq.count(k) >= 2):
            continue
        seq.append(k)
        last = k
    boss = idx == 11
    seq.insert(n // 2 if not boss else n, "__check")
    parts = [pad(START, "start")]
    spans = []
    x = len(START[0])
    for k in seq:
        rows = pad(CHECK, "check") if k == "__check" else CH[k]["rows"]
        spans.append((x, x + len(rows[0]), k))
        x += len(rows[0])
        parts.append(rows)
    if boss:
        parts.append(pad(CORRIDOR, "corridor"))
        parts.append(ARENA)
    else:
        parts.append(pad(END, "end"))
    grid = [list("".join(p[y] for p in parts)) for y in range(H)]
    width = len(grid[0])

    # Ennemis supplémentaires selon la difficulté
    extra = int(idx * 1.3)
    tries = 0
    while extra > 0 and tries < 400:
        tries += 1
        a, b, k = spans[rnd.randrange(len(spans))]
        if k == "__check":
            continue
        cx = rnd.randrange(a + 1, b - 1)
        if cx < 20:
            continue
        if grid[13][cx] == "#" and all(grid[y][cx] == "." for y in (10, 11, 12)) \
                and grid[12][cx - 1] == "." and grid[12][cx + 1] == ".":
            grid[12][cx] = "w"
            extra -= 1

    # Substitution des marcheurs selon le monde
    for y in range(H):
        for cx in range(width):
            if grid[y][cx] == "w":
                grid[y][cx] = pick(rnd, SUBST[world])

    # Bonus : au plus 2 (3 pour les longs niveaux), au moins un en première moitié
    ps = [(y, cx) for y in range(H) for cx in range(width) if grid[y][cx] == "P"]
    limit = 3 if n >= 10 else 2
    for y, cx in ps[limit:]:
        grid[y][cx] = "?"
    if not any(grid[y][cx] == "P" for y in range(H) for cx in range(width // 2)):
        for cx in range(width // 2):
            col = [y for y in range(H) if grid[y][cx] == "?"]
            if col:
                grid[col[0]][cx] = "P"
                break

    if world in (1, 3):  # plafond souterrain / forteresse
        for y in (0, 1):
            for cx in range(width):
                grid[y][cx] = "#" if grid[y][cx] == "." else grid[y][cx]
    if world == 3:  # fosses de lave
        for cx in range(width):
            if grid[13][cx] == "." and grid[14][cx] == ".":
                grid[14][cx] = "~"

    time = 200 + n * 12 + (100 if boss else 0)
    return {"w": world, "time": time, "map": ["".join(r) for r in grid]}


def main():
    levels = [build(i) for i in range(12)]
    out = ["const LEVELS=["]
    for lv in levels:
        out.append("{w:%d,time:%d,map:[" % (lv["w"], lv["time"]))
        out.extend(json.dumps(r) + "," for r in lv["map"])
        out.append("]},")
    out.append("];")
    js = "\n".join(out)
    target = Path(__file__).resolve().parent.parent / "index.html"
    html = target.read_text(encoding="utf-8")
    new = re.sub(r"(// LEVELS-BEGIN\n).*?(\n// LEVELS-END)",
                 lambda m: m.group(1) + js + m.group(2), html, flags=re.S)
    target.write_text(new, encoding="utf-8")
    for i, lv in enumerate(levels):
        print(f"{i // 3 + 1}-{i % 3 + 1}: {len(lv['map'][0])} tuiles, temps {lv['time']}")


if __name__ == "__main__":
    main()
