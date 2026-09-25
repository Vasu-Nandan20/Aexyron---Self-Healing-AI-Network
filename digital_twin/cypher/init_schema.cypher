// Neo4j Schema Constraints and Indexes for Aexyron Network Digital Twin

// Uniqueness Constraints
CREATE CONSTRAINT device_id_unique IF NOT EXISTS
FOR (d:Device) REQUIRE d.id IS UNIQUE;

CREATE CONSTRAINT interface_id_unique IF NOT EXISTS
FOR (i:Interface) REQUIRE i.id IS UNIQUE;

CREATE CONSTRAINT link_id_unique IF NOT EXISTS
FOR (l:NetworkLink) REQUIRE l.id IS UNIQUE;

// Indexes for High-Throughput Lookup
CREATE INDEX device_role_idx IF NOT EXISTS
FOR (d:Device) ON (d.role);

CREATE INDEX interface_status_idx IF NOT EXISTS
FOR (i:Interface) ON (i.status);

CREATE INDEX link_status_idx IF NOT EXISTS
FOR (l:NetworkLink) ON (l.status);
