/**
 * File upload component
 */
import { Component } from '@angular/core';
import { GraphService } from '../../services/graph.service';
import { IValidationResponse } from '../../models/graph.model';

@Component({
    selector: 'app-file-upload',
    template: `
    <div class="upload-container">
      <h2>Load Graph Data</h2>
      
      <div class="upload-section" *ngIf="!isLoaded">
        <div class="file-input-group">
          <label for="nodes-file">Select Nodes CSV:</label>
          <input 
            type="file" 
            id="nodes-file" 
            accept=".csv"
            (change)="onNodesFileSelected($event)"
            [disabled]="isLoading"
          />
          <span class="file-name" *ngIf="nodesFileName">{{ nodesFileName }}</span>
        </div>

        <div class="file-input-group">
          <label for="relations-file">Select Relations CSV:</label>
          <input 
            type="file" 
            id="relations-file" 
            accept=".csv"
            (change)="onRelationsFileSelected($event)"
            [disabled]="isLoading"
          />
          <span class="file-name" *ngIf="relationsFileName">{{ relationsFileName }}</span>
        </div>

        <button 
          (click)="onValidate()" 
          [disabled]="!canValidate || isLoading"
          class="btn btn-validate"
        >
          {{ isLoading ? 'Validating...' : 'Validate' }}
        </button>
      </div>

      <!-- Validation Results -->
      <div class="validation-result" *ngIf="validationResult">
        <div *ngIf="validationResult.valid" class="success">
          <h3>✓ Validation Successful</h3>
          <p>Nodes loaded: {{ validationResult.node_count }}</p>
          <p>Relations loaded: {{ validationResult.relation_count }}</p>
          <button (click)="onLoadGraph()" class="btn btn-primary">Load Graph</button>
        </div>

        <div *ngIf="!validationResult.valid" class="error">
          <h3>✗ Validation Failed</h3>
          <ul>
            <li *ngFor="let error of validationResult.errors">{{ error }}</li>
          </ul>
          <button (click)="onRetry()" class="btn btn-retry">Retry</button>
        </div>
      </div>

      <!-- Loading/Success State -->
      <div class="success-message" *ngIf="isLoaded">
        <h3>Graph Loaded Successfully!</h3>
        <p>Nodes: {{ loadedNodeCount }} | Relations: {{ loadedRelationCount }}</p>
        <button (click)="onReset()" class="btn btn-reset">Load Different Files</button>
      </div>
    </div>
  `,
    styles: [`
    .upload-container {
      padding: 20px;
      border: 1px solid #ddd;
      border-radius: 8px;
      background-color: #f9f9f9;
      margin-bottom: 20px;
    }

    h2 {
      margin-top: 0;
      color: #333;
    }

    .upload-section {
      display: flex;
      flex-direction: column;
      gap: 15px;
    }

    .file-input-group {
      display: flex;
      flex-direction: column;
      gap: 5px;
    }

    label {
      font-weight: 500;
      color: #555;
    }

    input[type="file"] {
      padding: 8px;
      border: 1px solid #ccc;
      border-radius: 4px;
      cursor: pointer;
    }

    input[type="file"]:disabled {
      background-color: #f0f0f0;
      cursor: not-allowed;
    }

    .file-name {
      font-size: 12px;
      color: #666;
      margin-top: 3px;
    }

    .btn {
      padding: 10px 20px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 14px;
      font-weight: 500;
      transition: all 0.3s ease;
    }

    .btn:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .btn-validate, .btn-retry {
      background-color: #007bff;
      color: white;
    }

    .btn-validate:hover:not(:disabled), .btn-retry:hover:not(:disabled) {
      background-color: #0056b3;
    }

    .btn-primary {
      background-color: #28a745;
      color: white;
    }

    .btn-primary:hover {
      background-color: #218838;
    }

    .btn-reset {
      background-color: #6c757d;
      color: white;
    }

    .btn-reset:hover {
      background-color: #5a6268;
    }

    .validation-result {
      margin-top: 20px;
      padding: 15px;
      border-radius: 4px;
    }

    .success {
      background-color: #d4edda;
      border: 1px solid #c3e6cb;
      color: #155724;
      padding: 15px;
      border-radius: 4px;
    }

    .error {
      background-color: #f8d7da;
      border: 1px solid #f5c6cb;
      color: #721c24;
      padding: 15px;
      border-radius: 4px;
    }

    .error ul {
      margin: 10px 0;
      padding-left: 20px;
    }

    .error li {
      margin: 5px 0;
    }

    .success-message {
      background-color: #d4edda;
      border: 1px solid #c3e6cb;
      color: #155724;
      padding: 15px;
      border-radius: 4px;
      text-align: center;
    }
  `]
})
export class FileUploadComponent {
    nodesFile: File | null = null;
    relationsFile: File | null = null;
    nodesFileName = '';
    relationsFileName = '';
    isLoading = false;
    isLoaded = false;
    validationResult: IValidationResponse | null = null;
    loadedNodeCount = 0;
    loadedRelationCount = 0;

    get canValidate(): boolean {
        return !!this.nodesFile && !!this.relationsFile;
    }

    constructor(private graphService: GraphService) { }

    onNodesFileSelected(event: Event): void {
        const target = event.target as HTMLInputElement;
        const files = target.files;
        if (files && files.length > 0) {
            this.nodesFile = files[0];
            this.nodesFileName = this.nodesFile!.name;
        }
    }

    onRelationsFileSelected(event: Event): void {
        const target = event.target as HTMLInputElement;
        const files = target.files;
        if (files && files.length > 0) {
            this.relationsFile = files[0];
            this.relationsFileName = this.relationsFile!.name;
        }
    }

    onValidate(): void {
        if (!this.canValidate) return;

        this.isLoading = true;
        this.graphService.validateFiles(this.nodesFile!, this.relationsFile!).subscribe({
            next: (result: IValidationResponse) => {
                this.validationResult = result;
                this.isLoading = false;
            },
            error: (error: any) => {
                this.validationResult = {
                    valid: false,
                    errors: ['Failed to validate files: ' + (error.error?.detail || error.message)],
                    node_count: 0,
                    relation_count: 0
                };
                this.isLoading = false;
            }
        });
    }

    onLoadGraph(): void {
        if (!this.canValidate) return;

        this.isLoading = true;
        this.graphService.loadGraph(this.nodesFile!, this.relationsFile!).subscribe({
            next: (graph: any) => {
                this.graphService.setGraphData(graph);
                this.isLoaded = true;
                this.loadedNodeCount = graph.node_count;
                this.loadedRelationCount = graph.relation_count;
                this.isLoading = false;
            },
            error: (error: any) => {
                this.validationResult = {
                    valid: false,
                    errors: ['Failed to load graph: ' + (error.error?.detail || error.message)],
                    node_count: 0,
                    relation_count: 0
                };
                this.isLoading = false;
            }
        });
    }

    onRetry(): void {
        this.validationResult = null;
    }

    onReset(): void {
        this.isLoaded = false;
        this.validationResult = null;
        this.nodesFile = null;
        this.relationsFile = null;
        this.nodesFileName = '';
        this.relationsFileName = '';
        this.graphService.clearGraph();
    }
}
