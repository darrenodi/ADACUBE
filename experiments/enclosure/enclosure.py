"""First ADACUBE experiment: a small electronics enclosure built with build123d.

The assembly has a base with a floor, PCB standoffs and corner screw bosses,
a lid with a display window and screw clearance holes, a PCB, a LiPo battery
under the PCB, a display module on a pin header, and four M3 screws.

Positions are derived from a few driving dimensions rather than typed in
separately, so changing e.g. the PCB size moves the standoffs with it. That is
a small, hand-written version of the "design intent" idea in docs/.

Run:
    python experiments/enclosure/enclosure.py            # build, check, export
    python experiments/enclosure/enclosure.py --out DIR  # choose output folder

Outputs (default: experiments/enclosure/out/):
    enclosure_assembly.step   named, coloured assembly for FreeCAD
    <part>.stl                one mesh per part
    report.json               dimensions, volumes and interference results
"""

from __future__ import annotations

import argparse
import itertools
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from build123d import (
    Align,
    Box,
    Color,
    Compound,
    Cylinder,
    Location,
    Part,
    Pos,
    export_step,
    export_stl,
)

MIN = (Align.CENTER, Align.CENTER, Align.MIN)  # centred in XY, sitting on Z=0


@dataclass(frozen=True)
class Params:
    # Enclosure (outer dimensions, mm)
    length: float = 100.0
    width: float = 60.0
    base_height: float = 26.0  # floor bottom to lid seat
    wall: float = 2.0
    lid_thickness: float = 2.0

    # PCB
    pcb_length: float = 80.0
    pcb_width: float = 50.0
    pcb_thickness: float = 1.6
    pcb_hole_inset: float = 3.5  # hole centre from PCB edge
    pcb_hole_dia: float = 3.2
    standoff_height: float = 8.0  # floor top to PCB underside
    standoff_dia: float = 6.0

    # Battery (flat LiPo pouch, sits on the floor under the PCB)
    battery_length: float = 50.0
    battery_width: float = 30.0
    battery_thickness: float = 5.0

    # Display module (board + glass), mounted on a pin header above the PCB
    display_board: tuple[float, float] = (36.0, 30.0)
    display_board_thickness: float = 1.6
    display_glass: tuple[float, float] = (34.0, 26.0)
    display_glass_thickness: float = 2.0
    display_offset_x: float = 12.0  # display centre relative to enclosure centre
    display_lid_gap: float = 0.5  # glass top to lid underside
    window_margin: float = 1.0  # lid window larger than glass on each side
    header_size: tuple[float, float] = (2.5, 20.0)  # pin header footprint

    # Corner screws (M3)
    screw_inset: float = 6.0  # boss centre from outer edge
    boss_dia: float = 7.0
    pilot_hole_dia: float = 2.5  # for thread-forming into plastic
    lid_clearance_dia: float = 3.4
    screw_dia: float = 3.0
    screw_length: float = 10.0
    screw_head_dia: float = 5.5
    screw_head_height: float = 2.5


# ---------------------------------------------------------------- derived values


def floor_top(p: Params) -> float:
    return p.wall


def pcb_bottom(p: Params) -> float:
    return floor_top(p) + p.standoff_height


def pcb_top(p: Params) -> float:
    return pcb_bottom(p) + p.pcb_thickness


def lid_bottom(p: Params) -> float:
    return p.base_height


def pcb_hole_xy(p: Params) -> list[tuple[float, float]]:
    dx = p.pcb_length / 2 - p.pcb_hole_inset
    dy = p.pcb_width / 2 - p.pcb_hole_inset
    return [(sx * dx, sy * dy) for sx in (-1, 1) for sy in (-1, 1)]


def screw_xy(p: Params) -> list[tuple[float, float]]:
    dx = p.length / 2 - p.screw_inset
    dy = p.width / 2 - p.screw_inset
    return [(sx * dx, sy * dy) for sx in (-1, 1) for sy in (-1, 1)]


def display_z(p: Params) -> dict[str, float]:
    glass_top = lid_bottom(p) - p.display_lid_gap
    glass_bottom = glass_top - p.display_glass_thickness
    board_bottom = glass_bottom - p.display_board_thickness
    return {"glass_top": glass_top, "glass_bottom": glass_bottom, "board_bottom": board_bottom}


# ---------------------------------------------------------------------- parts


def make_base(p: Params) -> Part:
    shell = Box(p.length, p.width, p.base_height, align=MIN)
    cavity = Pos(0, 0, p.wall) * Box(
        p.length - 2 * p.wall, p.width - 2 * p.wall, p.base_height, align=MIN
    )
    base = shell - cavity

    for x, y in pcb_hole_xy(p):
        standoff = Pos(x, y, floor_top(p)) * Cylinder(
            p.standoff_dia / 2, p.standoff_height, align=MIN
        )
        hole = Pos(x, y, floor_top(p)) * Cylinder(
            p.pilot_hole_dia / 2, p.standoff_height, align=MIN
        )
        base = base + standoff - hole

    boss_height = p.base_height - floor_top(p)
    for x, y in screw_xy(p):
        boss = Pos(x, y, floor_top(p)) * Cylinder(p.boss_dia / 2, boss_height, align=MIN)
        hole = Pos(x, y, floor_top(p)) * Cylinder(p.pilot_hole_dia / 2, boss_height, align=MIN)
        base = base + boss - hole
    return base


def make_lid(p: Params) -> Part:
    lid = Pos(0, 0, lid_bottom(p)) * Box(p.length, p.width, p.lid_thickness, align=MIN)
    gx, gy = p.display_glass
    window = Pos(p.display_offset_x, 0, lid_bottom(p)) * Box(
        gx + 2 * p.window_margin, gy + 2 * p.window_margin, p.lid_thickness, align=MIN
    )
    lid -= window
    for x, y in screw_xy(p):
        lid -= Pos(x, y, lid_bottom(p)) * Cylinder(
            p.lid_clearance_dia / 2, p.lid_thickness, align=MIN
        )
    return lid


def make_pcb(p: Params) -> Part:
    pcb = Pos(0, 0, pcb_bottom(p)) * Box(p.pcb_length, p.pcb_width, p.pcb_thickness, align=MIN)
    for x, y in pcb_hole_xy(p):
        pcb -= Pos(x, y, pcb_bottom(p)) * Cylinder(p.pcb_hole_dia / 2, p.pcb_thickness, align=MIN)
    return pcb


def make_battery(p: Params) -> Part:
    return Pos(0, 0, floor_top(p)) * Box(
        p.battery_length, p.battery_width, p.battery_thickness, align=MIN
    )


def make_display(p: Params) -> Part:
    z = display_z(p)
    bx, by = p.display_board
    gx, gy = p.display_glass
    board = Pos(p.display_offset_x, 0, z["board_bottom"]) * Box(
        bx, by, p.display_board_thickness, align=MIN
    )
    glass = Pos(p.display_offset_x, 0, z["glass_bottom"]) * Box(
        gx, gy, p.display_glass_thickness, align=MIN
    )
    return board + glass


def make_header(p: Params) -> Part:
    """Pin header joining the display board to the PCB, along the display's -X edge."""
    hx, hy = p.header_size
    bx, _ = p.display_board
    x = p.display_offset_x - bx / 2 + hx / 2
    height = display_z(p)["board_bottom"] - pcb_top(p)
    return Pos(x, 0, pcb_top(p)) * Box(hx, hy, height, align=MIN)


def make_screw(p: Params, x: float, y: float) -> Part:
    lid_top = lid_bottom(p) + p.lid_thickness
    head = Pos(x, y, lid_top) * Cylinder(p.screw_head_dia / 2, p.screw_head_height, align=MIN)
    shank = Pos(x, y, lid_top - p.screw_length) * Cylinder(
        p.screw_dia / 2, p.screw_length, align=MIN
    )
    return head + shank


# ------------------------------------------------------------------- assembly

COLOURS = {
    "base": Color(0.85, 0.85, 0.88),
    "lid": Color(0.30, 0.30, 0.34),
    "pcb": Color(0.05, 0.45, 0.20),
    "battery": Color(0.20, 0.35, 0.80),
    "display": Color(0.05, 0.05, 0.08),
    "header": Color(0.10, 0.10, 0.10),
    "screw": Color(0.75, 0.75, 0.70),
}


def build(p: Params) -> dict[str, Part]:
    parts = {
        "base": make_base(p),
        "lid": make_lid(p),
        "pcb": make_pcb(p),
        "battery": make_battery(p),
        "display": make_display(p),
        "header": make_header(p),
    }
    for i, (x, y) in enumerate(screw_xy(p), start=1):
        parts[f"screw_{i}"] = make_screw(p, x, y)
    return parts


# --------------------------------------------------------------------- checks

# Screws are meant to overlap the base: the 3.0 mm shank cuts its own thread in
# the 2.5 mm pilot hole. Every other overlap is a design error.
INTENDED_OVERLAPS = {("base", f"screw_{i}") for i in range(1, 5)}

# The PCB rests on the standoffs and the header touches PCB and display; shared
# faces have zero overlap volume, so a tiny tolerance absorbs kernel noise.
VOLUME_TOL = 1e-3  # mm^3


def interferences(parts: dict[str, Part]) -> list[dict]:
    found = []
    for (a, pa), (b, pb) in itertools.combinations(parts.items(), 2):
        pa_box, pb_box = pa.bounding_box(), pb.bounding_box()
        if not pa_box.overlaps(pb_box):
            continue
        common = pa & pb
        vol = common.volume if common is not None else 0.0
        if vol > VOLUME_TOL:
            pair = tuple(sorted((a, b)))
            found.append(
                {"parts": list(pair), "volume_mm3": round(vol, 3), "intended": pair in INTENDED_OVERLAPS}
            )
    return found


def clearances(p: Params) -> dict[str, float]:
    """Gaps that should stay positive whatever the parameters are."""
    inner_x = p.length / 2 - p.wall
    inner_y = p.width / 2 - p.wall
    d = display_z(p)
    boss_r = p.boss_dia / 2
    return {
        "pcb_to_wall_x": inner_x - p.pcb_length / 2,
        "pcb_to_wall_y": inner_y - p.pcb_width / 2,
        "battery_to_pcb": pcb_bottom(p) - (floor_top(p) + p.battery_thickness),
        "display_to_lid": lid_bottom(p) - d["glass_top"],
        "header_height": d["board_bottom"] - pcb_top(p),
        # nearest point of a corner boss to the PCB corner region
        "boss_to_pcb_x": (p.length / 2 - p.screw_inset - boss_r) - p.pcb_length / 2,
        "screw_tip_above_floor": (lid_bottom(p) + p.lid_thickness - p.screw_length) - floor_top(p),
    }


# --------------------------------------------------------------------- export


def export(parts: dict[str, Part], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    labelled = []
    for name, part in parts.items():
        part.label = name
        part.color = COLOURS["screw" if name.startswith("screw") else name]
        labelled.append(part)
        export_stl(part, str(out / f"{name}.stl"))
    assembly = Compound(label="adacube_enclosure", children=labelled)
    export_step(assembly, str(out / "enclosure_assembly.step"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=Path(__file__).parent / "out")
    args = ap.parse_args()

    p = Params()
    parts = build(p)

    gaps = clearances(p)
    clashes = interferences(parts)
    bad_gaps = {k: v for k, v in gaps.items() if v <= 0}
    bad_clashes = [c for c in clashes if not c["intended"]]

    for name, part in parts.items():
        if not part.is_valid:
            print(f"INVALID SOLID: {name}")
            return 1

    export(parts, args.out)

    report = {
        "params": asdict(p),
        "parts": {
            n: {"volume_mm3": round(s.volume, 2), "bbox_mm": [round(v, 2) for v in s.bounding_box().size]}
            for n, s in parts.items()
        },
        "clearances_mm": {k: round(v, 3) for k, v in gaps.items()},
        "interferences": clashes,
        "ok": not bad_gaps and not bad_clashes,
    }
    (args.out / "report.json").write_text(json.dumps(report, indent=2))

    print(f"Exported {len(parts)} parts to {args.out}")
    for k, v in gaps.items():
        print(f"  {k:24s} {v:7.2f} mm{'  <-- PROBLEM' if v <= 0 else ''}")
    for c in clashes:
        tag = "intended" if c["intended"] else "UNINTENDED"
        print(f"  overlap {c['parts'][0]} / {c['parts'][1]}: {c['volume_mm3']} mm^3 ({tag})")
    print("OK" if report["ok"] else "PROBLEMS FOUND")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
