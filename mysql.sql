CREATE TABLE source_document (
  id char(36) NOT NULL PRIMARY KEY,
  source_name varchar(255) NOT NULL,
  source_type varchar(50) NOT NULL,
  content_hash varchar(128) NOT NULL,
  storage_uri text NULL,
  created_by varchar(255) NOT NULL,
  created_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_source_document_content_hash ON source_document (content_hash);
CREATE INDEX idx_source_document_created_at ON source_document (created_at);

CREATE TABLE generated_solution (
  id char(36) NOT NULL PRIMARY KEY,
  source_document_id char(36) NOT NULL,
  executive_summary text NOT NULL,
  status varchar(50) NOT NULL DEFAULT 'draft',
  artifact_json json NOT NULL,
  created_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_generated_solution_source_document FOREIGN KEY (source_document_id) REFERENCES source_document(id)
);

CREATE INDEX idx_generated_solution_source_document_id ON generated_solution (source_document_id);
CREATE INDEX idx_generated_solution_status ON generated_solution (status);

CREATE TABLE requirement (
  id char(36) NOT NULL PRIMARY KEY,
  generated_solution_id char(36) NOT NULL,
  requirement_code varchar(50) NOT NULL,
  requirement_type varchar(50) NOT NULL,
  description text NOT NULL,
  priority varchar(20) NOT NULL,
  business_rule text NULL,
  source_reference json NOT NULL,
  created_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_requirement_generated_solution FOREIGN KEY (generated_solution_id) REFERENCES generated_solution(id)
);

CREATE UNIQUE INDEX idx_requirement_solution_code ON requirement (generated_solution_id, requirement_code);

CREATE TABLE material (
  id char(36) NOT NULL PRIMARY KEY,
  material_number varchar(80) NOT NULL,
  description varchar(255) NOT NULL,
  uom varchar(20) NOT NULL,
  sap_plant varchar(20) NOT NULL,
  created_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_material_number_plant ON material (material_number, sap_plant);

CREATE TABLE supplier (
  id char(36) NOT NULL PRIMARY KEY,
  supplier_code varchar(80) NOT NULL UNIQUE,
  name varchar(255) NOT NULL,
  lead_time_minutes integer NOT NULL CHECK (lead_time_minutes >= 0),
  created_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sequence_calloff (
  id char(36) NOT NULL PRIMARY KEY,
  material_id char(36) NOT NULL,
  supplier_id char(36) NOT NULL,
  sequence_number integer NOT NULL,
  required_quantity numeric(18,3) NOT NULL CHECK (required_quantity > 0),
  required_at datetime NOT NULL,
  delivery_window_start datetime NOT NULL,
  delivery_window_end datetime NOT NULL,
  status varchar(50) NOT NULL DEFAULT 'draft',
  created_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_calloff_material FOREIGN KEY (material_id) REFERENCES material(id),
  CONSTRAINT fk_calloff_supplier FOREIGN KEY (supplier_id) REFERENCES supplier(id),
  CONSTRAINT chk_sequence_delivery_window CHECK (delivery_window_start < delivery_window_end)
);

CREATE INDEX idx_calloff_sequence ON sequence_calloff (sequence_number);
CREATE INDEX idx_calloff_required_at ON sequence_calloff (required_at);
CREATE INDEX idx_calloff_status ON sequence_calloff (status);

CREATE TABLE audit_log (
  id char(36) NOT NULL PRIMARY KEY,
  actor varchar(255) NOT NULL,
  action varchar(100) NOT NULL,
  resource_type varchar(100) NOT NULL,
  resource_id char(36) NULL,
  metadata json NOT NULL,
  created_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_log_actor ON audit_log (actor);
CREATE INDEX idx_audit_log_created_at ON audit_log (created_at);

