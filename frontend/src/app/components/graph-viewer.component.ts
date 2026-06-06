/**
 * Graph viewer component for rendering interactive graph visualization
 */
import { Component, OnInit, OnDestroy, ViewChild, ElementRef } from '@angular/core';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { GraphService } from '../../services/graph.service';
import { IGraph, INode, IRelation } from '../../models/graph.model';

declare var d3: any;

@Component({
    selector: 'app-graph-viewer',
    template: `
    <div class="graph-viewer-container" *ngIf="graph">
      <div class="graph-controls">
        <button (click)="resetView()" class="btn btn-small" title="Reset view">Reset View</button>
        <button (click)="zoomIn()" class="btn btn-small" title="Zoom in">+ Zoom</button>
        <button (click)="zoomOut()" class="btn btn-small" title="Zoom out">- Zoom</button>
        <span class="zoom-level">{{ currentZoom.toFixed(1) }}x</span>
      </div>
      <svg #graphSvg class="graph-svg"></svg>
    </div>
  `,
    styles: [`
    .graph-viewer-container {
      position: relative;
      width: 100%;
      height: 100%;
      background-color: #fafafa;
      border: 1px solid #ddd;
    }

    .graph-controls {
      position: absolute;
      top: 10px;
      left: 10px;
      display: flex;
      gap: 8px;
      z-index: 100;
      background-color: white;
      padding: 10px;
      border-radius: 4px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .btn {
      padding: 8px 12px;
      border: 1px solid #ddd;
      background-color: white;
      border-radius: 4px;
      cursor: pointer;
      font-size: 12px;
      transition: all 0.3s ease;
    }

    .btn:hover {
      background-color: #f0f0f0;
      border-color: #999;
    }

    .btn-small {
      padding: 6px 10px;
      font-size: 11px;
    }

    .zoom-level {
      padding: 8px 12px;
      font-size: 12px;
      color: #666;
    }

    .graph-svg {
      width: 100%;
      height: 100%;
    }

    :host ::ng-deep .node {
      cursor: pointer;
      stroke: #fff;
      stroke-width: 2px;
    }

    :host ::ng-deep .node:hover {
      stroke: #000;
      stroke-width: 3px;
    }

    :host ::ng-deep .node.selected {
      stroke: #ff0000;
      stroke-width: 3px;
    }

    :host ::ng-deep .link {
      stroke: #999;
      stroke-opacity: 0.6;
      cursor: pointer;
    }

    :host ::ng-deep .link:hover {
      stroke: #000;
      stroke-width: 2px;
    }

    :host ::ng-deep .link.selected {
      stroke: #ff0000;
      stroke-width: 2px;
    }

    :host ::ng-deep .link-label {
      font-size: 11px;
      pointer-events: none;
      fill: #666;
    }

    :host ::ng-deep .node-label {
      font-size: 12px;
      pointer-events: none;
      text-anchor: middle;
      dominant-baseline: middle;
      font-weight: 500;
    }
  `]
})
export class GraphViewerComponent implements OnInit, OnDestroy {
    @ViewChild('graphSvg') graphSvg!: ElementRef;

    graph: IGraph | null = null;
    currentZoom = 1;
    private destroy$ = new Subject<void>();
    private svg: any;
    private g: any;
    private simulation: any;
    private selectedNodeId: string | null = null;
    private selectedRelationId: string | null = null;

    constructor(private graphService: GraphService) { }

    ngOnInit(): void {
        this.graphService.graphData$
            .pipe(takeUntil(this.destroy$))
            .subscribe((graph: any) => {
                this.graph = graph;
                if (graph) {
                    setTimeout(() => this.renderGraph(), 100);
                }
            });
    }

    ngOnDestroy(): void {
        this.destroy$.next();
        this.destroy$.complete();
        if (this.simulation) {
            this.simulation.stop();
        }
    }

    private renderGraph(): void {
        if (!this.graph || !this.graphSvg) return;

        const container = this.graphSvg.nativeElement;
        const width = container.clientWidth || 800;
        const height = container.clientHeight || 600;

        // Clear previous content
        d3.select(container).selectAll('*').remove();

        // Create SVG
        this.svg = d3.select(container)
            .attr('width', width)
            .attr('height', height);

        // Create group for zoom/pan
        this.g = this.svg.append('g');

        // Add zoom behavior
        const zoom = d3.zoom()
            .on('zoom', (event: any) => {
                this.currentZoom = event.transform.k;
                this.g.attr('transform', event.transform);
            });

        this.svg.call(zoom);

        // Prepare data
        const nodes = this.graph.nodes.map((node: INode) => ({
            id: node.uuid,
            name: node.name,
            ...node
        }));

        const links = this.graph.relations.map((rel: IRelation) => ({
            id: rel.relationship_uuid,
            source: rel.source_uuid,
            target: rel.target_uuid,
            name: rel.relationship_name,
            ...rel
        }));

        // Create force simulation
        this.simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(links)
                .id((d: any) => d.id)
                .distance(100))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2))
            .force('collide', d3.forceCollide(30));

        // Draw links
        const link = this.g.selectAll('.link')
            .data(links)
            .enter()
            .append('line')
            .attr('class', 'link')
            .attr('stroke-width', 2)
            .on('click', (event: any, d: any) => this.onLinkClick(event, d));

        // Add link labels
        const linkLabels = this.g.selectAll('.link-label')
            .data(links)
            .enter()
            .append('text')
            .attr('class', 'link-label')
            .text((d: any) => d.name)
            .attr('dy', -5);

        // Draw nodes
        const node = this.g.selectAll('.node')
            .data(nodes)
            .enter()
            .append('circle')
            .attr('class', 'node')
            .attr('r', 20)
            .attr('fill', (d: any) => this.getNodeColor(d))
            .on('click', (event: any, d: any) => this.onNodeClick(event, d))
            .call(d3.drag()
                .on('start', (event: any, d: any) => this.dragStarted(event, d))
                .on('drag', (event: any, d: any) => this.dragged(event, d))
                .on('end', (event: any, d: any) => this.dragEnded(event, d)));

        // Add node labels
        const labels = this.g.selectAll('.node-label')
            .data(nodes)
            .enter()
            .append('text')
            .attr('class', 'node-label')
            .text((d: any) => this.truncateText(d.name, 15))
            .attr('fill', '#fff');

        // Update positions on tick
        this.simulation.on('tick', () => {
            link
                .attr('x1', (d: any) => d.source.x)
                .attr('y1', (d: any) => d.source.y)
                .attr('x2', (d: any) => d.target.x)
                .attr('y2', (d: any) => d.target.y);

            linkLabels
                .attr('x', (d: any) => (d.source.x + d.target.x) / 2)
                .attr('y', (d: any) => (d.source.y + d.target.y) / 2);

            node
                .attr('cx', (d: any) => d.x)
                .attr('cy', (d: any) => d.y);

            labels
                .attr('x', (d: any) => d.x)
                .attr('y', (d: any) => d.y);
        });
    }

    private onNodeClick(event: any, d: any): void {
        event.stopPropagation();
        this.selectedNodeId = d.id;
        this.selectedRelationId = null;
        this.graphService.selectNode(d);
        this.updateNodeSelection();
    }

    private onLinkClick(event: any, d: any): void {
        event.stopPropagation();
        this.selectedRelationId = d.id;
        this.selectedNodeId = null;
        this.graphService.selectRelation(d);
        this.updateLinkSelection();
    }

    private updateNodeSelection(): void {
        if (!this.svg) return;
        this.svg.selectAll('.node')
            .classed('selected', (d: any) => d.id === this.selectedNodeId);
        this.svg.selectAll('.link').classed('selected', false);
    }

    private updateLinkSelection(): void {
        if (!this.svg) return;
        this.svg.selectAll('.link')
            .classed('selected', (d: any) => d.id === this.selectedRelationId);
        this.svg.selectAll('.node').classed('selected', false);
    }

    private getNodeColor(d: any): string {
        return '#1f77b4';
    }

    private truncateText(text: string, maxLength: number): string {
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }

    private dragStarted(event: any, d: any): void {
        if (!event.active) this.simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    private dragged(event: any, d: any): void {
        d.fx = event.x;
        d.fy = event.y;
    }

    private dragEnded(event: any, d: any): void {
        if (!event.active) this.simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    resetView(): void {
        if (!this.svg) return;
        this.svg.transition().duration(750).call(
            d3.zoom().transform,
            d3.zoomIdentity.translate(this.graphSvg.nativeElement.clientWidth / 2,
                this.graphSvg.nativeElement.clientHeight / 2)
        );
        this.currentZoom = 1;
    }

    zoomIn(): void {
        if (!this.svg) return;
        this.svg.transition().duration(300).call(
            d3.zoom().scaleBy,
            1.3
        );
    }

    zoomOut(): void {
        if (!this.svg) return;
        this.svg.transition().duration(300).call(
            d3.zoom().scaleBy,
            0.7
        );
    }
}
