/**
 * Graph data models for frontend
 */

export interface INode {
    name: string;
    uuid: string;
    properties?: { [key: string]: any };
}

export interface IRelation {
    source_uuid: string;
    target_uuid: string;
    relationship_name: string;
    relationship_uuid: string;
    properties?: { [key: string]: any };
}

export interface IGraph {
    nodes: INode[];
    relations: IRelation[];
    node_count: number;
    relation_count: number;
}

export interface IValidationResponse {
    valid: boolean;
    errors: string[];
    node_count: number;
    relation_count: number;
}
