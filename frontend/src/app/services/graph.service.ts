/**
 * Service for graph API communication
 */
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { IGraph, IValidationResponse, INode, IRelation } from '../models/graph.model';

@Injectable({
    providedIn: 'root'
})
export class GraphService {
    private apiUrl = 'http://localhost:8000/api';

    private graphDataSubject = new BehaviorSubject<IGraph | null>(null);
    public graphData$ = this.graphDataSubject.asObservable();

    private selectedNodeSubject = new BehaviorSubject<INode | null>(null);
    public selectedNode$ = this.selectedNodeSubject.asObservable();

    private selectedRelationSubject = new BehaviorSubject<IRelation | null>(null);
    public selectedRelation$ = this.selectedRelationSubject.asObservable();

    constructor(private http: HttpClient) { }

    /**
     * Validate CSV files
     */
    validateFiles(nodesFile: File, relationsFile: File): Observable<IValidationResponse> {
        const formData = new FormData();
        formData.append('nodes_file', nodesFile);
        formData.append('relations_file', relationsFile);

        return this.http.post<IValidationResponse>(
            `${this.apiUrl}/validate`,
            formData
        );
    }

    /**
     * Load graph from CSV files
     */
    loadGraph(nodesFile: File, relationsFile: File): Observable<IGraph> {
        const formData = new FormData();
        formData.append('nodes_file', nodesFile);
        formData.append('relations_file', relationsFile);

        return this.http.post<IGraph>(
            `${this.apiUrl}/load-graph`,
            formData
        );
    }

    /**
     * Store graph data in service
     */
    setGraphData(graph: IGraph): void {
        this.graphDataSubject.next(graph);
    }

    /**
     * Get current graph data
     */
    getGraphData(): IGraph | null {
        return this.graphDataSubject.value;
    }

    /**
     * Select a node
     */
    selectNode(node: INode): void {
        this.selectedNodeSubject.next(node);
    }

    /**
     * Deselect node
     */
    deselectNode(): void {
        this.selectedNodeSubject.next(null);
    }

    /**
     * Select a relation
     */
    selectRelation(relation: IRelation): void {
        this.selectedRelationSubject.next(relation);
    }

    /**
     * Deselect relation
     */
    deselectRelation(): void {
        this.selectedRelationSubject.next(null);
    }

    /**
     * Clear all data
     */
    clearGraph(): void {
        this.graphDataSubject.next(null);
        this.deselectNode();
        this.deselectRelation();
    }

    /**
     * Find node by UUID
     */
    findNodeByUUID(uuid: string): INode | undefined {
        const graph = this.getGraphData();
        return graph?.nodes.find(n => n.uuid === uuid);
    }

    /**
     * Find relation by UUID
     */
    findRelationByUUID(uuid: string): IRelation | undefined {
        const graph = this.getGraphData();
        return graph?.relations.find(r => r.relationship_uuid === uuid);
    }
}
