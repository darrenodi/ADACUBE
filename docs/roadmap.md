# Roadmap

Build one complete workflow end to end before widening scope. Use an existing CAD kernel; put development effort into drawing interpretation, internal reconstruction and automatic revision.

## First experiment

Using Python and Open CASCADE (via build123d), generate a small enclosure containing a PCB, battery, display and screws. Export to STEP and inspect it in FreeCAD.

## Phases

1. **CAD foundation**: primitives, holes, enclosures, assemblies; STEP and STL export.
2. **Interactive 3D app**: Three.js viewport with rotate, zoom, select, hide; component tree.
3. **Drawing interpretation**: detect dimensions, shapes and annotations; convert them into structured CAD instructions.
4. **Automatic revision**: diff original and revised drawings, update affected geometry, preserve the rest, check collisions.
5. **Simulation**: mechanical motion, electrical simulation, sync with animation; Play, Pause, Reset, speed control.
6. **Manufacturing**: printable parts; STEP, STL, 3MF export; clearance and fit checks.

## Learning order

C++ fundamentals, Python, Open CASCADE, TypeScript, Three.js, physics simulation.
