# ADACUBE

A design environment where a drawing is the starting point and the main editing interface for an engineering model. A user uploads a sketch, gets an editable 3D assembly including the internal components, presses Play to watch the device operate based on simulation results, and revises the design by uploading a new drawing, typing a change, or editing directly in 3D.

Guiding principle: one design, one editable engineering model, multiple ways to create, modify, simulate and manufacture it.

## Core capabilities

1. **Sketch-to-CAD**: convert drawings into editable 3D assemblies.
2. **Internal reconstruction**: infer hidden components (PCB, battery, fasteners, mechanisms) and their relationships.
3. **Play simulation**: animate the device from engineering simulation results, not generated video.
4. **Drawing-based revision**: upload a revised drawing; the system detects the differences and updates the existing model instead of starting over.
5. **Manufacturing**: export individual parts, assemblies and printable models (STEP, STL, 3MF).
6. **Version control**: compare revisions, restore earlier designs, track what changed.

Designs can be changed three ways, all updating the same model: **Draw** (new sketch), **Describe** (e.g. "make the enclosure 15 mm wider and move the battery to the bottom"), and **Direct edit** (select a component and change it).

## Target users

Clients commissioning products, modelling companies, toy companies, hobbyists and electrical/electronics engineers.

## Documentation

- [Architecture](docs/architecture.md)
- [Roadmap](docs/roadmap.md)
- [Open decisions](docs/decisions.md)

## Status

Planning. No code yet. The first experiment is described in the roadmap.
