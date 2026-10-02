---
name: neo4j-modeling
description: Use when working with property graph data modeling, node and relationship schema design, Neo4j compatibility, Cypher queries, graph traversal, and referential integrity.
---

# Neo4j Modeling Skill

## 1. Overview & Purpose
This skill defines the graph modeling guidelines, node and relationship schema semantics, and Neo4j compatibility standards for the Visualizer application.

The project models data according to the **Labeled Property Graph (LPG)** model utilized by Neo4j, enabling graph visual representation and future database synchronization (BRD Section 10).

---

## 2. Labeled Property Graph (LPG) Semantics

### 2.1 Nodes (Entities)
In Neo4j property graph terminology, each node is an independent entity:
- **Identifier:** `uuid` (UUID v4 string conforming to RFC 4122).
- **Label / Display Name:** `name` (string, e.g. "Server-001", "Database").
- **Properties:** Arbitrary key-value map serialized as JSON in CSV (e.g. `{"cpu": "80%", "memory": "16GB"}`).

**Cypher Representation:**
```cypher
CREATE (n:Node {
  uuid: $uuid,
  name: $name,
  cpu: "80%",
  memory: "16GB"
})
```

### 2.2 Relationships (Edges)
Relationships represent directed connections between two nodes:
- **Identifier:** `relationship_uuid` (unique UUID v4).
- **Type / Label:** `relationship_name` (e.g. `depends_on`, `queries`, `connected_to`).
- **Endpoints:** `source_uuid` (start node) and `target_uuid` (end node).
- **Properties:** Arbitrary key-value map serialized as JSON in CSV (e.g. `{"strength": "high", "latency": "50ms"}`).

**Cypher Representation:**
```cypher
MATCH (source:Node {uuid: $source_uuid})
MATCH (target:Node {uuid: $target_uuid})
CREATE (source)-[r:DEPENDS_ON {
  relationship_uuid: $relationship_uuid,
  strength: "high",
  latency: "50ms"
}]->(target)
```

---

## 3. Referential Integrity Rules

1. **Existence Requirement:** A relationship cannot exist without both its source and target nodes existing in the node dataset.
2. **Directed Edges:** All relationships have an explicit direction (`source` -> `target`). In the visualization, arrows indicate directionality.
3. **Multi-edges Support:** Multiple relationships between the exact same pair of nodes are permitted, provided each relationship has a unique `relationship_uuid` (and optionally differing `relationship_name` or properties).
4. **Self-referencing Loops:** A node may connect to itself (`source_uuid == target_uuid`). The graph renderer must handle self-referencing curves gracefully without collapsing.
5. **Disconnected Subgraphs:** The graph model supports multiple disconnected components and isolated nodes (degree = 0).

---

## 4. Neo4j Cypher Data Import Script

To export or load these CSV datasets directly into a Neo4j instance:

```cypher
// 1. Create Unique Constraints
CREATE CONSTRAINT node_uuid_unique FOR (n:Node) REQUIRE n.uuid IS UNIQUE;
CREATE CONSTRAINT rel_uuid_unique FOR ()-[r:RELATION]-() REQUIRE r.relationship_uuid IS UNIQUE;

// 2. Load Nodes
LOAD CSV WITH HEADERS FROM 'file:///nodes.csv' AS row
MERGE (n:Node {uuid: row.uuid})
SET n.name = row.name,
    n.properties = apoc.convert.fromJsonMap(row.properties);

// 3. Load Relationships
LOAD CSV WITH HEADERS FROM 'file:///relations.csv' AS row
MATCH (s:Node {uuid: row.source_uuid})
MATCH (t:Node {uuid: row.target_uuid})
MERGE (s)-[r:RELATION {relationship_uuid: row.relationship_uuid}]->(t)
SET r.type = row.relationship_name,
    r.properties = apoc.convert.fromJsonMap(row.properties);
```

---

## 5. Performance Guidelines for Large Graphs
- For datasets approaching 1,000+ nodes and 5,000+ relationships:
  - Cache node lookup dictionaries by UUID (O(1) lookup during edge creation).
  - Pre-calculate degree distribution for node sizing if dynamic sizing is enabled.
  - Tune D3 force collision radius and charge strength to prevent edge crossing clutter.
