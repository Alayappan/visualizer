/**
 * Unit tests for GraphService
 */
import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { GraphService } from '../services/graph.service';
import { IGraph, IValidationResponse, INode } from '../models/graph.model';

describe('GraphService', () => {
    let service: GraphService;
    let httpMock: HttpTestingController;

    beforeEach(() => {
        TestBed.configureTestingModule({
            imports: [HttpClientTestingModule],
            providers: [GraphService]
        });
        service = TestBed.inject(GraphService);
        httpMock = TestBed.inject(HttpTestingController);
    });

    afterEach(() => {
        httpMock.verify();
    });

    it('should be created', () => {
        expect(service).toBeTruthy();
    });

    describe('validateFiles', () => {
        it('should call POST /api/validate with form data', () => {
            const mockFile1 = new File(['content1'], 'nodes.csv');
            const mockFile2 = new File(['content2'], 'relations.csv');

            const mockResponse: IValidationResponse = {
                valid: true,
                errors: [],
                node_count: 3,
                relation_count: 2
            };

            service.validateFiles(mockFile1, mockFile2).subscribe(result => {
                expect(result.valid).toBe(true);
                expect(result.node_count).toBe(3);
            });

            const req = httpMock.expectOne('http://localhost:8000/api/validate');
            expect(req.request.method).toBe('POST');
            req.flush(mockResponse);
        });

        it('should handle validation errors', () => {
            const mockFile1 = new File(['content1'], 'nodes.csv');
            const mockFile2 = new File(['content2'], 'relations.csv');

            const mockResponse: IValidationResponse = {
                valid: false,
                errors: ['Invalid UUID format'],
                node_count: 0,
                relation_count: 0
            };

            service.validateFiles(mockFile1, mockFile2).subscribe(result => {
                expect(result.valid).toBe(false);
                expect(result.errors.length).toBe(1);
            });

            const req = httpMock.expectOne('http://localhost:8000/api/validate');
            req.flush(mockResponse);
        });
    });

    describe('loadGraph', () => {
        it('should call POST /api/load-graph', () => {
            const mockFile1 = new File(['content1'], 'nodes.csv');
            const mockFile2 = new File(['content2'], 'relations.csv');

            const mockGraph: IGraph = {
                nodes: [
                    { name: 'Node1', uuid: '550e8400-e29b-41d4-a716-446655440000' }
                ],
                relations: [],
                node_count: 1,
                relation_count: 0
            };

            service.loadGraph(mockFile1, mockFile2).subscribe(graph => {
                expect(graph.node_count).toBe(1);
            });

            const req = httpMock.expectOne('http://localhost:8000/api/load-graph');
            expect(req.request.method).toBe('POST');
            req.flush(mockGraph);
        });
    });

    describe('graph data management', () => {
        it('should set and get graph data', () => {
            const mockGraph: IGraph = {
                nodes: [],
                relations: [],
                node_count: 0,
                relation_count: 0
            };

            service.setGraphData(mockGraph);
            const result = service.getGraphData();

            expect(result).toEqual(mockGraph);
        });

        it('should emit graph data updates', (done) => {
            const mockGraph: IGraph = {
                nodes: [],
                relations: [],
                node_count: 0,
                relation_count: 0
            };

            service.graphData$.subscribe(graph => {
                if (graph) {
                    expect(graph).toEqual(mockGraph);
                    done();
                }
            });

            service.setGraphData(mockGraph);
        });

        it('should clear graph data', () => {
            const mockGraph: IGraph = {
                nodes: [],
                relations: [],
                node_count: 0,
                relation_count: 0
            };

            service.setGraphData(mockGraph);
            service.clearGraph();

            expect(service.getGraphData()).toBeNull();
        });
    });

    describe('node selection', () => {
        it('should select and deselect nodes', (done) => {
            const mockNode: INode = {
                name: 'Test Node',
                uuid: '550e8400-e29b-41d4-a716-446655440000'
            };

            service.selectNode(mockNode);

            service.selectedNode$.subscribe(node => {
                if (node) {
                    expect(node.name).toBe('Test Node');
                    service.deselectNode();
                    done();
                }
            });
        });
    });

    describe('find methods', () => {
        it('should find node by UUID', () => {
            const mockGraph: IGraph = {
                nodes: [
                    { name: 'Node1', uuid: '550e8400-e29b-41d4-a716-446655440000' },
                    { name: 'Node2', uuid: '550e8400-e29b-41d4-a716-446655440001' }
                ],
                relations: [],
                node_count: 2,
                relation_count: 0
            };

            service.setGraphData(mockGraph);
            const found = service.findNodeByUUID('550e8400-e29b-41d4-a716-446655440000');

            expect(found?.name).toBe('Node1');
        });

        it('should return undefined for non-existent node', () => {
            const mockGraph: IGraph = {
                nodes: [],
                relations: [],
                node_count: 0,
                relation_count: 0
            };

            service.setGraphData(mockGraph);
            const found = service.findNodeByUUID('non-existent-uuid');

            expect(found).toBeUndefined();
        });
    });
});
