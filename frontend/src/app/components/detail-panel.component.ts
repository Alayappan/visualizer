/**
 * Detail panel component for displaying node/relation information
 */
import { Component, OnInit, OnDestroy } from '@angular/core';
import { trigger, state, style, transition, animate } from '@angular/animations';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { GraphService } from '../../services/graph.service';
import { INode, IRelation } from '../../models/graph.model';

@Component({
  selector: 'app-detail-panel',
  template: `
    <div class="detail-panel" *ngIf="selectedNode || selectedRelation" [@slideIn]>
      <div class="panel-header">
        <h3>{{ selectedNode ? 'Node Details' : 'Relationship Details' }}</h3>
        <button class="close-btn" (click)="onClose()" title="Close">&times;</button>
      </div>

      <div class="panel-content">
        <!-- Node Details -->
        <div *ngIf="selectedNode" class="details">
          <div class="detail-row">
            <span class="label">Name:</span>
            <span class="value">{{ selectedNode.name }}</span>
          </div>
          <div class="detail-row">
            <span class="label">UUID:</span>
            <span class="value uuid">{{ selectedNode.uuid }}</span>
          </div>
          <div *ngIf="selectedNode.properties" class="properties-section">
            <h4>Properties:</h4>
            <div class="property-item" *ngFor="let key of objectKeys(selectedNode.properties)">
              <span class="property-key">{{ key }}:</span>
              <span class="property-value">{{ formatPropertyValue(selectedNode.properties[key]) }}</span>
            </div>
          </div>
          <div *ngIf="!selectedNode.properties || objectKeys(selectedNode.properties).length === 0" class="no-properties">
            No properties
          </div>
        </div>

        <!-- Relation Details -->
        <div *ngIf="selectedRelation" class="details">
          <div class="detail-row">
            <span class="label">Type:</span>
            <span class="value">{{ selectedRelation.relationship_name }}</span>
          </div>
          <div class="detail-row">
            <span class="label">From:</span>
            <span class="value">{{ getNodeName(selectedRelation.source_uuid) }}</span>
          </div>
          <div class="detail-row">
            <span class="label">To:</span>
            <span class="value">{{ getNodeName(selectedRelation.target_uuid) }}</span>
          </div>
          <div class="detail-row">
            <span class="label">UUID:</span>
            <span class="value uuid">{{ selectedRelation.relationship_uuid }}</span>
          </div>
          <div *ngIf="selectedRelation.properties" class="properties-section">
            <h4>Properties:</h4>
            <div class="property-item" *ngFor="let key of objectKeys(selectedRelation.properties)">
              <span class="property-key">{{ key }}:</span>
              <span class="property-value">{{ formatPropertyValue(selectedRelation.properties[key]) }}</span>
            </div>
          </div>
          <div *ngIf="!selectedRelation.properties || objectKeys(selectedRelation.properties).length === 0" class="no-properties">
            No properties
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .detail-panel {
      position: fixed;
      right: 0;
      top: 0;
      height: 100vh;
      width: 350px;
      background-color: white;
      border-left: 1px solid #ddd;
      box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
      display: flex;
      flex-direction: column;
      z-index: 1000;
      overflow-y: auto;
    }

    .panel-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 15px;
      border-bottom: 1px solid #ddd;
      background-color: #f8f9fa;
    }

    .panel-header h3 {
      margin: 0;
      font-size: 16px;
      color: #333;
    }

    .close-btn {
      background: none;
      border: none;
      font-size: 24px;
      cursor: pointer;
      color: #666;
      padding: 0;
      width: 30px;
      height: 30px;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    .close-btn:hover {
      color: #000;
    }

    .panel-content {
      padding: 15px;
      flex: 1;
      overflow-y: auto;
    }

    .details {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .detail-row {
      display: flex;
      gap: 10px;
      word-break: break-word;
    }

    .label {
      font-weight: 600;
      color: #555;
      min-width: 80px;
      flex-shrink: 0;
    }

    .value {
      color: #333;
      word-break: break-word;
      flex: 1;
    }

    .value.uuid {
      font-family: monospace;
      font-size: 12px;
      background-color: #f5f5f5;
      padding: 4px 8px;
      border-radius: 3px;
      color: #666;
    }

    .properties-section {
      margin-top: 10px;
      padding-top: 10px;
      border-top: 1px solid #eee;
    }

    .properties-section h4 {
      margin: 0 0 10px 0;
      font-size: 14px;
      color: #555;
      font-weight: 600;
    }

    .property-item {
      display: flex;
      gap: 8px;
      padding: 8px;
      background-color: #f9f9f9;
      border-radius: 3px;
      margin-bottom: 6px;
      word-break: break-word;
    }

    .property-key {
      font-weight: 500;
      color: #666;
      min-width: 100px;
      flex-shrink: 0;
    }

    .property-value {
      color: #333;
      flex: 1;
    }

    .no-properties {
      font-style: italic;
      color: #999;
      padding: 8px;
    }

    @media (max-width: 600px) {
      .detail-panel {
        width: 100%;
      }
    }
  `],
  animations: [
    trigger('slideIn', [
      state('void', style({
        transform: 'translateX(100%)',
        opacity: 0
      })),
      state('*', style({
        transform: 'translateX(0)',
        opacity: 1
      })),
      transition('void => *', [
        animate('300ms ease-in-out')
      ]),
      transition('* => void', [
        animate('300ms ease-in-out')
      ])
    ])
  ]
})
export class DetailPanelComponent implements OnInit, OnDestroy {
  selectedNode: INode | null = null;
  selectedRelation: IRelation | null = null;
  private destroy$ = new Subject<void>();

  constructor(private graphService: GraphService) { }

  ngOnInit(): void {
    this.graphService.selectedNode$
      .pipe(takeUntil(this.destroy$))
      .subscribe((node: any) => {
        this.selectedNode = node;
        this.selectedRelation = null;
      });

    this.graphService.selectedRelation$
      .pipe(takeUntil(this.destroy$))
      .subscribe((relation: any) => {
        this.selectedRelation = relation;
        this.selectedNode = null;
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  onClose(): void {
    this.graphService.deselectNode();
    this.graphService.deselectRelation();
  }

  objectKeys(obj: any): string[] {
    return obj ? Object.keys(obj) : [];
  }

  formatPropertyValue(value: any): string {
    if (value === null || value === undefined) {
      return 'N/A';
    }
    if (typeof value === 'object') {
      return JSON.stringify(value);
    }
    return String(value);
  }

  getNodeName(uuid: string): string {
    const node = this.graphService.findNodeByUUID(uuid);
    return node ? node.name : 'Unknown Node';
  }
}
