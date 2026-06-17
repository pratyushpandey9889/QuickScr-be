from app.domain.schemas import KPI, NagareRuleSet


class NagareService:
    keywords = {"nagare", "jit", "sequence", "sequenced", "line feeding", "call-off", "calloff"}

    def applies(self, text: str) -> bool:
        lower = text.lower()
        return any(keyword in lower for keyword in self.keywords)

    def design_rules(self) -> NagareRuleSet:
        return NagareRuleSet(
            sequence_calloff_logic=[
                "Sort demand by production date, line, model, sequence number, and build slot.",
                "Calculate material requirement per sequence using BOM quantity multiplied by planned build quantity.",
                "Group call-offs by supplier, dock, route, material, delivery window, and container type.",
                "Freeze call-offs inside the firm window and require planner approval for sequence resequencing.",
            ],
            delivery_scheduling_logic=[
                "delivery_window_start = line_required_at - supplier_lead_time - unloading_time - safety_buffer",
                "delivery_window_end = delivery_window_start + allowed_window_minutes",
                "Escalate any call-off where confirmed_eta is outside the delivery window.",
            ],
            production_sequencing=[
                "Maintain FIFO within each production slot unless priority override is approved.",
                "Detect duplicate sequence numbers per production line and production date.",
                "Block release when BOM material is inactive, supplier is missing, or inventory projection is negative.",
            ],
            material_flow=[
                "Receive production sequence demand from SAP or MES.",
                "Explode BOM and map materials to supplier, route, supermarket, and line-side location.",
                "Generate replenishment tasks for warehouse staging and line feeding.",
            ],
            supplier_flow=[
                "Send sequenced call-off to supplier through API, EDI, portal, or SAP message.",
                "Capture supplier acknowledgment, ASN, dispatch timestamp, and exception reason.",
                "Compare ASN sequence and quantity to released call-off before dock acceptance.",
            ],
            warehouse_flow=[
                "Reserve dock capacity by delivery window.",
                "Validate inbound material, container, label, and sequence number at receiving.",
                "Stage containers by production line, build slot, and line-side point of use.",
            ],
            logistics_flow=[
                "Monitor route ETA and carrier status against required delivery window.",
                "Escalate route delay based on remaining safety buffer.",
                "Record proof of delivery, unloading completion, and line-feed handoff.",
            ],
            algorithms=[
                "ProjectedInventory(t) = OnHand + ConfirmedInbound(t) - SequencedDemand(t)",
                "CallOffQuantity = BuildQuantity * BOMQuantityPerUnit + ScrapAllowance",
                "SafetyBuffer = max(min_buffer_minutes, historical_delay_p95_minutes)",
                "PriorityScore = lateness_minutes * 5 + stockout_risk * 10 + line_stop_risk * 20",
            ],
            validation_logic=[
                "Sequence number must be unique for production line and build date.",
                "Required quantity must be greater than zero.",
                "Supplier must be active and mapped to material and plant.",
                "Delivery window start must be earlier than delivery window end.",
                "Projected inventory after call-off must not fall below safety stock without approval.",
            ],
            trigger_rules=[
                "Trigger call-off when production sequence enters the release horizon.",
                "Trigger exception when supplier acknowledgment is missing after SLA threshold.",
                "Trigger escalation when ETA exceeds delivery_window_end or projected inventory is negative.",
                "Trigger resequencing review when production line sequence changes inside freeze window.",
            ],
            inventory_rules=[
                "SafetyStock = average_consumption_per_hour * replenishment_risk_hours",
                "ReorderPoint = demand_during_lead_time + safety_stock",
                "Do not release call-off if material status is blocked or obsolete.",
                "Create shortage alert when ProjectedInventory(t) < SafetyStock.",
            ],
            line_feeding_logic=[
                "Pick by line, station, sequence number, and point of use.",
                "Deliver material to line-side no earlier than max_line_side_buffer and no later than takt-aligned requirement.",
                "Confirm consumption by sequence completion event from MES or SAP confirmation.",
            ],
            formulas_and_kpis=[
                KPI(
                    name="Sequence Delivery Adherence",
                    formula="on_sequence_deliveries / total_sequence_deliveries * 100",
                    target=">= 98%",
                    owner="Logistics Lead",
                ),
                KPI(
                    name="Line Stop Incidents",
                    formula="count(line_stop_events caused by material shortage)",
                    target="0 per month",
                    owner="Production Manager",
                ),
                KPI(
                    name="Supplier Acknowledgment SLA",
                    formula="acknowledged_calloffs_within_sla / released_calloffs * 100",
                    target=">= 99%",
                    owner="Supplier Coordinator",
                ),
                KPI(
                    name="Inventory Accuracy",
                    formula="system_quantity / physical_quantity * 100",
                    target="98% to 102%",
                    owner="Warehouse Lead",
                ),
            ],
        )

