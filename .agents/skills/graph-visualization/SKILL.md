---
name: graph-visualization
description: Use when developing, optimizing, or debugging interactive graph visualizations, D3.js force simulations, SVG rendering, zoom/pan/drag controls, and node/link click events in the Angular frontend.
---

# Graph Visualization Skill

## 1. Overview & Purpose
This skill covers the interactive graph rendering engine implemented in [`frontend/src/app/components/graph-viewer.component.ts`](file:///Users/kamalesh/Downloads/neo4j-visualizer/visualizer/frontend/src/app/components/graph-viewer.component.ts) using D3.js (v7).

It provides detailed instructions for constructing force-directed layouts, rendering nodes and directed relationships, handling viewport interactions, and managing component lifecycle without memory leaks.

---

## 2. Visual Elements & Specifications

As specified in Section 3.3 of [BRD.md](file:///Users/kamalesh/Downloads/neo4j-visualizer/visualizer/BRD.md):

### 2.1 Nodes
- **Representation:** Circles with radial gradient or solid fill.
- **Labels:** Node `name` displayed centered or directly below the circle.
- **Identifier:** Retains original UUID from `nodes.csv`.
- **Interactions:**
  - Hover: Highlights node circle and incident edges.
  - Click: Selects node and opens Detail Panel via `GraphService.selectNode(node)`.
  - Drag: Pins node temporarily during simulation dragging.

### 2.2 Relationships (Edges)
- **Representation:** Directional lines connecting `source` to `target` nodes.
- **Arrowhead:** SVG `<defs><marker id="arrow">` positioned at the target node boundary.
- **Labels:** Text element along or centered on the link showing `relationship_name`.
- **Interactions:**
  - Click: Selects relationship and opens Detail Panel via `GraphService.selectRelation(relation)`.
  - Hover: Increases stroke width and highlights edge label.

---

## 3. D3 Force Simulation Setup

```typescript
import * as d3 from 'd3';

// 1. Initialize SVG container with zoom behavior
const svg = d3.select(this.svgElement.nativeElement)
  .attr('width', width)
  .attr('height', height);

const g = svg.append('g').attr('class', 'graph-container');

const zoom = d3.zoom<SVGSVGElement, unknown>()
  .scaleExtent([0.1, 4])
  .on('zoom', (event) => {
    g.attr('transform', event.transform);
  });

svg.call(zoom);

// 2. Configure Force Simulation
const simulation = d3.forceSimulation<D3Node>(nodes)
  .force('link', d3.forceLink<D3Node, D3Link>(links).id(d => d.id).distance(120))
  .force('charge', d3.forceManyBody().strength(-400))
  .force('center', d3.forceCenter(width / 2, height / 2))
  .force('collision', d3.forceCollide().radius(40));

// 3. Tick handler updating positions
simulation.on('tick', () => {
  linkElements
    .attr('x1', d => (d.source as D3Node).x!)
    .attr('y1', d => (d.source as D3Node).y!)
    .attr('x2', d => (d.target as D3Node).x!)
    .attr('y2', d => (d.target as D3Node).y!);

  nodeElements
    .attr('transform', d => `translate(${d.x},${d.y})`);
});
```

---

## 4. Lifecycle & Performance Management

To guarantee high performance (rendering 1,000 nodes in under 3 seconds without memory leaks):

1. **Clean Re-rendering:**
   ```typescript
   private clearGraph(): void {
     if (this.simulation) {
       this.simulation.stop();
     }
     d3.select(this.svgElement.nativeElement).selectAll('*').remove();
   }
   ```
2. **Teardown on Destroy:**
   Always stop simulations and complete RxJS subjects in `ngOnDestroy()`:
   ```typescript
   ngOnDestroy(): void {
     this.clearGraph();
     this.destroy$.next();
     this.destroy$.complete();
   }
   ```
3. **Simulation Cooldown:**
   Allow the simulation alpha to decay naturally. Avoid resetting alpha to 1 on minor UI updates.

---

## 5. Controls & User Actions
- **Zoom In / Out:** Buttons invoking `d3.zoom().scaleBy(svg, factor)`.
- **Fit to Viewport / Reset Zoom:** Transition `svg.transition().call(zoom.transform, d3.zoomIdentity)`.
- **Node Dragging:**
  ```typescript
  function drag(simulation: d3.Simulation<D3Node, undefined>) {
    return d3.drag<SVGGElement, D3Node>()
      .on('start', (event, d) => {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      })
      .on('drag', (event, d) => {
        d.fx = event.x;
        d.fy = event.y;
      })
      .on('end', (event, d) => {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      });
  }
  ```

---

## 6. Testing Instructions
Run graph viewer component unit tests:
```bash
cd frontend
npm test -- --watch=false --browsers=ChromeHeadless --include=**/graph-viewer.component.spec.ts
```
Verify:
- SVG nodes render matching input node counts.
- Links render matching relationship counts.
- Click triggers service selection.
- Simulation stops cleanly upon component destruction.
