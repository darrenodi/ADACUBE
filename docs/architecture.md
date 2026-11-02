# Architecture

Hybrid stack: C++ for geometry and simulation, Python for AI and orchestration, TypeScript for the interface. Each language is used where its ecosystem is strongest rather than forcing one language across very different jobs.

## Layers

```
Frontend (TypeScript, React, Three.js)
  drawing upload, 3D viewport, editing, Play controls
        |  HTTP API / WebSocket
Backend (Python, FastAPI)
  coordinates AI, CAD, simulation and version management
        |
  +-------------+---------------+------------------+----------------+
  | AI engine   | CAD engine    | Mechanical sim   | Electrical sim |
  | Python:     | C++:          | C++:             | ngspice        |
  | PyTorch,    | Open CASCADE  | Project Chrono   |                |
  | OpenCV      | (build123d    |                  |                |
  |             |  for scripting)|                 |                |
  +-------------+---------------+------------------+----------------+
        |
Shared project data (PostgreSQL + file storage)
  parametric assembly, design intent graph, revisions
```

## Components

| System                | Technology                    | Responsibility                                  |
| --------------------- | ----------------------------- | ----------------------------------------------- |
| CAD kernel            | Open CASCADE Technology (C++) | Precise, editable solid geometry                |
| CAD scripting         | build123d (Python)            | Programmatic construction during prototyping    |
| Drawing interpretation| PyTorch, OpenCV (Python)      | Shapes, dimensions, annotations, revision diffs |
| 3D rendering          | Three.js (TypeScript)         | Display and manipulate assemblies               |
| Mechanical simulation | Project Chrono (C++)          | Rigid-body dynamics and motion                  |
| Electrical simulation | ngspice                       | Circuit behaviour                               |
| Backend               | FastAPI (Python)              | API and coordination between engines            |
| Database              | PostgreSQL                    | Projects, components, revisions                 |

Geometry, simulation and rendering are separate systems: geometry defines what the object is, simulation defines how it behaves, rendering defines how it is shown.

## Design intent graph

The central data structure. It records relationships between components, for example:

- enclosure contains PCB
- PCB supports microcontroller; display, buttons and battery connect to PCB
- screws attach enclosure halves
- mounting holes align with PCB holes

When one part changes, the graph identifies what else may be affected (PCB position, mounting supports, screw positions, cable lengths, display opening). Without it, revisions would produce disconnected 3D objects.

## Revision pipeline

1. Compare the new input against the current design.
2. Identify the requested modifications.
3. Find affected components through the design intent graph.
4. Modify the existing geometry.
5. Reposition or resize affected internal components.
6. Check collisions and structural conflicts.
7. Preserve everything not meant to change.
8. Save a new version.

## Data flow rule

The CAD engine holds the authoritative model. The frontend receives lightweight tessellated geometry plus structured metadata, not raw B-rep data on every change.

## Simulation

Play is driven by simulation output, synchronized with the 3D animation. Domains, roughly in order of priority: mechanical, electrical/electronic, control logic (sensors and controllers triggering actions), later thermal and fluid.

What-if runs (change motor RPM, battery capacity, gear ratio and replay) are a target feature.
