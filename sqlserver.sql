CREATE TABLE source_document (
  id uniqueidentifier NOT NULL DEFAULT newid() PRIMARY KEY,
  source_name nvarchar(255) NOT NULL,
  source_type nvarchar(50) NOT NULL,
  content_hash nvarchar(128) NOT NULL,
  storage_uri nvarchar(max) NULL,
  created_by nvarchar(255) NOT NULL,
  created_at datetime2 NOT NULL DEFAULT sysutcdatetime()
);

CREATE INDEX idx_source_document_content_hash ON source_document (content_hash);
CREATE INDEX idx_source_document_created_at ON source_document (created_at);

CREATE TABLE generated_solution (
  id uniqueidentifier NOT NULL DEFAULT newid() PRIMARY KEY,
  source_document_id uniqueidentifier NOT NULL,
  executive_summary nvarchar(max) NOT NULL,
  status nvarchar(50) NOT NULL DEFAULT 'draft',
  artifact_json nvarchar(max) NOT NULL DEFAULT '{}',
  created_at datetime2 NOT NULL DEFAULT sysutcdatetime(),
  updated_at datetime2 NOT NULL DEFAULT sysutcdatetime(),
  CONSTRAINT fk_generated_solution_source_document FOREIGN KEY (source_document_id) REFERENCES source_document(id)
);

CREATE INDEX idx_generated_solution_source_document_id ON generated_solution (source_document_id);
CREATE INDEX idx_generated_solution_status ON generated_solution (status);

CREATE TABLE requirement (
  id uniqueidentifier NOT NULL DEFAULT newid() PRIMARY KEY,
  generated_solution_id uniqueidentifier NOT NULL,
  requirement_code nvarchar(50) NOT NULL,
  requirement_type nvarchar(50) NOT NULL,
  description nvarchar(max) NOT NULL,
  priority nvarchar(20) NOT NULL,
  business_rule nvarchar(max) NULL,
  source_reference nvarchar(max) NOT NULL DEFAULT '{}',
  created_at datetime2 NOT NULL DEFAULT sysutcdatetime(),
  CONSTRAINT fk_requirement_generated_solution FOREIGN KEY (generated_solution_id) REFERENCES generated_solution(id)
);

CREATE UNIQUE INDEX idx_requirement_solution_code ON requirement (generated_solution_id, requirement_code);

CREATE TABLE material (
  id uniqueidentifier NOT NULL DEFAULT newid() PRIMARY KEY,
  material_number nvarchar(80) NOT NULL,
  description nvarchar(255) NOT NULL,
  uom nvarchar(20) NOT NULL,
  sap_plant nvarchar(20) NOT NULL,
  created_at datetime2 NOT NULL DEFAULT sysutcdatetime()
);

CREATE UNIQUE INDEX idx_material_number_plant ON material (material_number, sap_plant);

CREATE TABLE supplier (
  id uniqueidentifier NOT NULL DEFAULT newid() PRIMARY KEY,
  supplier_code nvarchar(80) NOT NULL UNIQUE,
  name nvarchar(255) NOT NULL,
  lead_time_minutes integer NOT NULL CHECK (lead_time_minutes >= 0),
  created_at datetime2 NOT NULL DEFAULT sysutcdatetime()
);

CREATE TABLE sequence_calloff (
  id uniqueidentifier NOT NULL DEFAULT newid() PRIMARY KEY,
  material_id uniqueidentifier NOT NULL,
  supplier_id uniqueidentifier NOT NULL,
  sequence_number integer NOT NULL,
  required_quantity numeric(18,3) NOT NULL CHECK (required_quantity > 0),
  required_at datetime2 NOT NULL,
  delivery_window_start datetime2 NOT NULL,
  delivery_window_end datetime2 NOT NULL,
  status nvarchar(50) NOT NULL DEFAULT 'draft',
  created_at datetime2 NOT NULL DEFAULT sysutcdatetime(),
  CONSTRAINT fk_calloff_material FOREIGN KEY (material_id) REFERENCES material(id),
  CONSTRAINT fk_calloff_supplier FOREIGN KEY (supplier_id) REFERENCES supplier(id),
  CONSTRAINT chk_sequence_delivery_window CHECK (delivery_window_start < delivery_window_end)
);

CREATE INDEX idx_calloff_sequence ON sequence_calloff (sequence_number);
CREATE INDEX idx_calloff_required_at ON sequence_calloff (required_at);
CREATE INDEX idx_calloff_status ON sequence_calloff (status);

CREATE TABLE audit_log (
  id uniqueidentifier NOT NULL DEFAULT newid() PRIMARY KEY,
  actor nvarchar(255) NOT NULL,
  action nvarchar(100) NOT NULL,
  resource_type nvarchar(100) NOT NULL,
  resource_id uniqueidentifier NULL,
  metadata nvarchar(max) NOT NULL DEFAULT '{}',
  created_at datetime2 NOT NULL DEFAULT sysutcdatetime()
);

CREATE INDEX idx_audit_log_actor ON audit_log (actor);
CREATE INDEX idx_audit_log_created_at ON audit_log (created_at);

