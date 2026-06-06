/**
 * Unit tests for FileUploadComponent
 */
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { FileUploadComponent } from '../components/file-upload.component';
import { GraphService } from '../services/graph.service';
import { of, throwError } from 'rxjs';

describe('FileUploadComponent', () => {
    let component: FileUploadComponent;
    let fixture: ComponentFixture<FileUploadComponent>;
    let graphServiceMock: jasmine.SpyObj<GraphService>;

    beforeEach(async () => {
        const spy = jasmine.createSpyObj('GraphService', [
            'validateFiles',
            'loadGraph',
            'setGraphData',
            'clearGraph'
        ]);

        await TestBed.configureTestingModule({
            declarations: [FileUploadComponent],
            imports: [FormsModule, CommonModule],
            providers: [{ provide: GraphService, useValue: spy }]
        }).compileComponents();

        graphServiceMock = TestBed.inject(GraphService) as jasmine.SpyObj<GraphService>;
    });

    beforeEach(() => {
        fixture = TestBed.createComponent(FileUploadComponent);
        component = fixture.componentInstance;
        fixture.detectChanges();
    });

    it('should create', () => {
        expect(component).toBeTruthy();
    });

    describe('file selection', () => {
        it('should handle nodes file selection', () => {
            const mockFile = new File(['content'], 'nodes.csv');
            const event = {
                target: {
                    files: [mockFile]
                }
            };

            component.onNodesFileSelected(event);

            expect(component.nodesFile).toBe(mockFile);
            expect(component.nodesFileName).toBe('nodes.csv');
        });

        it('should handle relations file selection', () => {
            const mockFile = new File(['content'], 'relations.csv');
            const event = {
                target: {
                    files: [mockFile]
                }
            };

            component.onRelationsFileSelected(event);

            expect(component.relationsFile).toBe(mockFile);
            expect(component.relationsFileName).toBe('relations.csv');
        });
    });

    describe('validation', () => {
        it('should enable validate button when both files selected', () => {
            component.nodesFile = new File(['content'], 'nodes.csv');
            component.relationsFile = new File(['content'], 'relations.csv');

            expect(component.canValidate).toBe(true);
        });

        it('should disable validate button when files missing', () => {
            component.nodesFile = null;
            component.relationsFile = new File(['content'], 'relations.csv');

            expect(component.canValidate).toBe(false);
        });

        it('should call validation service on validate', () => {
            component.nodesFile = new File(['content'], 'nodes.csv');
            component.relationsFile = new File(['content'], 'relations.csv');

            graphServiceMock.validateFiles.and.returnValue(
                of({
                    valid: true,
                    errors: [],
                    node_count: 3,
                    relation_count: 2
                })
            );

            component.onValidate();

            expect(graphServiceMock.validateFiles).toHaveBeenCalledWith(
                component.nodesFile,
                component.relationsFile
            );
        });

        it('should display validation errors', () => {
            component.nodesFile = new File(['content'], 'nodes.csv');
            component.relationsFile = new File(['content'], 'relations.csv');

            graphServiceMock.validateFiles.and.returnValue(
                of({
                    valid: false,
                    errors: ['Invalid UUID format'],
                    node_count: 0,
                    relation_count: 0
                })
            );

            component.onValidate();

            expect(component.validationResult?.valid).toBe(false);
            expect(component.validationResult?.errors.length).toBe(1);
        });
    });

    describe('load graph', () => {
        it('should load graph on success', () => {
            component.nodesFile = new File(['content'], 'nodes.csv');
            component.relationsFile = new File(['content'], 'relations.csv');

            const mockGraph = {
                nodes: [{ name: 'Node1', uuid: 'uuid1' }],
                relations: [],
                node_count: 1,
                relation_count: 0
            };

            graphServiceMock.loadGraph.and.returnValue(of(mockGraph));

            component.onLoadGraph();

            expect(graphServiceMock.setGraphData).toHaveBeenCalledWith(mockGraph);
            expect(component.isLoaded).toBe(true);
        });

        it('should handle load error', () => {
            component.nodesFile = new File(['content'], 'nodes.csv');
            component.relationsFile = new File(['content'], 'relations.csv');

            graphServiceMock.loadGraph.and.returnValue(
                throwError({ error: { detail: 'Error loading graph' } })
            );

            component.onLoadGraph();

            expect(component.validationResult?.valid).toBe(false);
        });
    });

    describe('reset', () => {
        it('should reset component state', () => {
            component.isLoaded = true;
            component.nodesFile = new File(['content'], 'nodes.csv');
            component.relationsFile = new File(['content'], 'relations.csv');

            component.onReset();

            expect(component.isLoaded).toBe(false);
            expect(component.nodesFile).toBeNull();
            expect(component.relationsFile).toBeNull();
            expect(graphServiceMock.clearGraph).toHaveBeenCalled();
        });
    });
});
