CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE source_document (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  source_name varchar(255) NOT NULL,
  source_type varchar(50) NOT NULL,
  content_hash varchar(128) NOT NULL,
  storage_uri text,
  created_by varchar(255) NOT NULL,
  created_at timestamp NOT NULL DEFAULT now()
);

CREATE INDEX idx_source_document_content_hash ON source_document (content_hash);
CREATE INDEX idx_source_document_created_at ON source_document (created_at);

CREATE TABLE generated_solution (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  source_document_id uuid NOT NULL REFERENCES source_document(id),
  executive_summary text NOT NULL,
  status varchar(50) NOT NULL DEFAULT 'draft',
  artifact_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamp NOT NULL DEFAULT now(),
  updated_at timestamp NOT NULL DEFAULT now()
);

CREATE INDEX idx_generated_solution_source_document_id ON generated_solution (source_document_id);
CREATE INDEX idx_generated_solution_status ON generated_solution (status);

CREATE TABLE requirement (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  generated_solution_id uuid NOT NULL REFERENCES generated_solution(id),
  requirement_code varchar(50) NOT NULL,
  requirement_type varchar(50) NOT NULL,
  description text NOT NULL,
  priority varchar(20) NOT NULL,
  business_rule text,
  source_reference jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamp NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX idx_requirement_solution_code ON requirement (generated_solution_id, requirement_code);

CREATE TABLE material (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  material_number varchar(80) NOT NULL,
  description varchar(255) NOT NULL,
  uom varchar(20) NOT NULL,
  sap_plant varchar(20) NOT NULL,
  created_at timestamp NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX idx_material_number_plant ON material (material_number, sap_plant);

CREATE TABLE supplier (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  supplier_code varchar(80) NOT NULL UNIQUE,
  name varchar(255) NOT NULL,
  lead_time_minutes integer NOT NULL CHECK (lead_time_minutes >= 0),
  created_at timestamp NOT NULL DEFAULT now()
);

CREATE TABLE sequence_calloff (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  material_id uuid NOT NULL REFERENCES material(id),
  supplier_id uuid NOT NULL REFERENCES supplier(id),
  sequence_number integer NOT NULL,
  required_quantity numeric(18,3) NOT NULL CHECK (required_quantity > 0),
  required_at timestamp NOT NULL,
  delivery_window_start timestamp NOT NULL,
  delivery_window_end timestamp NOT NULL,
  status varchar(50) NOT NULL DEFAULT 'draft',
  created_at timestamp NOT NULL DEFAULT now(),
  CONSTRAINT chk_sequence_delivery_window CHECK (delivery_window_start < delivery_window_end)
);

CREATE INDEX idx_calloff_sequence ON sequence_calloff (sequence_number);
CREATE INDEX idx_calloff_required_at ON sequence_calloff (required_at);
CREATE INDEX idx_calloff_status ON sequence_calloff (status);

CREATE TABLE document_chunk (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  source_document_id uuid NOT NULL REFERENCES source_document(id),
  chunk_index integer NOT NULL,
  content text NOT NULL,
  embedding_provider varchar(80) NOT NULL,
  vector_id varchar(255) NOT NULL,
  created_at timestamp NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX idx_document_chunk_source_index ON document_chunk (source_document_id, chunk_index);
CREATE INDEX idx_document_chunk_vector_id ON document_chunk (vector_id);

CREATE TABLE conversation_turn (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id uuid NOT NULL,
  role varchar(30) NOT NULL,
  content text NOT NULL,
  citations jsonb NOT NULL DEFAULT '[]'::jsonb,
  created_at timestamp NOT NULL DEFAULT now()
);

CREATE INDEX idx_conversation_turn_session ON conversation_turn (session_id);
CREATE INDEX idx_conversation_turn_created_at ON conversation_turn (created_at);

CREATE TABLE integration_event (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  integration_type varchar(80) NOT NULL,
  correlation_id varchar(255) NOT NULL,
  payload jsonb NOT NULL,
  status varchar(50) NOT NULL DEFAULT 'pending',
  attempts integer NOT NULL DEFAULT 0,
  next_attempt_at timestamp,
  created_at timestamp NOT NULL DEFAULT now(),
  updated_at timestamp NOT NULL DEFAULT now()
);

CREATE INDEX idx_integration_event_status ON integration_event (status, next_attempt_at);
CREATE UNIQUE INDEX idx_integration_event_correlation ON integration_event (integration_type, correlation_id);

CREATE TABLE audit_log (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  actor varchar(255) NOT NULL,
  action varchar(100) NOT NULL,
  resource_type varchar(100) NOT NULL,
  resource_id uuid,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamp NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_log_actor ON audit_log (actor);
CREATE INDEX idx_audit_log_created_at ON audit_log (created_at);

