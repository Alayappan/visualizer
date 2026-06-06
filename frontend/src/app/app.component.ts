/**
 * Main app component
 */
import { Component, OnInit } from '@angular/core';
import { trigger, state, style, transition, animate } from '@angular/animations';
import { GraphService } from './services/graph.service';

@Component({
    selector: 'app-root',
    template: `
    <div class="app-container">
      <header class="app-header">
        <h1>Graph Visualizer</h1>
        <p class="subtitle">Interactive Node and Relationship Visualization</p>
      </header>

      <div class="app-content">
        <app-file-upload #uploadComponent></app-file-upload>

        <div class="graph-section" *ngIf="isGraphLoaded">
          <app-graph-viewer></app-graph-viewer>
          <app-detail-panel></app-detail-panel>
        </div>
      </div>
    </div>
  `,
    styles: [`
    .app-container {
      display: flex;
      flex-direction: column;
      height: 100vh;
      background-color: #fff;
    }

    .app-header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 20px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .app-header h1 {
      margin: 0;
      font-size: 28px;
      font-weight: 600;
    }

    .subtitle {
      margin: 5px 0 0 0;
      font-size: 14px;
      opacity: 0.9;
    }

    .app-content {
      display: flex;
      flex-direction: column;
      flex: 1;
      overflow: hidden;
      padding: 20px;
    }

    .graph-section {
      display: flex;
      flex: 1;
      gap: 20px;
      overflow: hidden;
    }

    app-graph-viewer {
      flex: 1;
      border: 1px solid #ddd;
      border-radius: 8px;
      overflow: hidden;
    }
  `]
})
export class AppComponent implements OnInit {
    isGraphLoaded = false;

    constructor(private graphService: GraphService) { }

    ngOnInit(): void {
        this.graphService.graphData$.subscribe(graph => {
            this.isGraphLoaded = !!graph;
        });
    }
}
