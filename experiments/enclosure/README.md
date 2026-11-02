# Experiment 1: enclosure assembly

A parametric electronics enclosure built with [build123d](https://github.com/gumyr/build123d) (a Python CAD library on top of the Open CASCADE kernel). It is the first experiment in [the roadmap](../../docs/roadmap.md).

## What it builds

| Part      | Description                                                            |
| --------- | ---------------------------------------------------------------------- |
| base      | 100 x 60 x 26 mm shell, 2 mm walls, 4 PCB standoffs, 4 corner bosses    |
| lid       | 2 mm plate with a display window and 4 screw clearance holes            |
| pcb       | 80 x 50 x 1.6 mm board with 4 mounting holes, 8 mm above the floor      |
| battery   | 50 x 30 x 5 mm LiPo pouch on the floor under the PCB                    |
| display   | 36 x 30 mm module board with 34 x 26 mm glass, 0.5 mm below the lid     |
| header    | pin header joining the display board to the PCB                        |
| screw_1-4 | M3 x 10 pan-head screws through the lid into the corner bosses          |

All sizes are in the `Params` dataclass at the top of `enclosure.py`. Positions are derived from them: standoffs follow the PCB holes, the display height follows the lid, the header fills the gap between PCB and display. Changing one dimension updates the dependent parts.

## Checks

After building, the script:

- verifies every solid is valid
- computes the overlap volume of every pair of parts and flags any that are not intended (the screws overlapping the base is intended: the 3.0 mm shank cuts its thread into a 2.5 mm pilot hole)
- reports clearances that must stay positive (PCB to wall, battery to PCB, display to lid, etc.)

It exits with status 1 if anything fails. For example, setting `battery_thickness=9.0` reports a 1500 mm^3 battery/PCB clash.

## Run it

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python experiments/enclosure/enclosure.py
```

Output goes to `experiments/enclosure/out/` (not committed):

- `enclosure_assembly.step`: the assembly with named, coloured parts
- one `.stl` per part
- `report.json`: parameters, part volumes and bounding boxes, clearances, overlaps

## View in FreeCAD

File > Open `enclosure_assembly.step`. The parts appear by name in the model tree. Hide `lid` and `base` to see the inside.

## Known simplifications

- Boxes stand in for real component shapes; there are no connectors, cable routing or USB opening yet.
- The corner bosses clear the PCB by only 0.5 mm in X, which is tight for a printed part.
- The lid has no lip or alignment features, and the screw threads are not modelled.
