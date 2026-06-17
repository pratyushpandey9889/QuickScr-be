from dataclasses import dataclass

from app.domain.schemas import AccuracyProfile, AgentAccuracyLevel


@dataclass(frozen=True)
class AccuracyPolicy:
    label: str
    target_confidence: float
    validation_depth: str
    citation_policy: str
    retrieval_top_k: int
    model_temperature: float
    review_required: bool
    enabled_checks: tuple[str, ...]
    escalation_rules: tuple[str, ...]


class AccuracyService:
    policies: dict[AgentAccuracyLevel, AccuracyPolicy] = {
        AgentAccuracyLevel.FAST: AccuracyPolicy(
            label="Fast Draft",
            target_confidence=0.70,
            validation_depth="Baseline extraction with required-field checks",
            citation_policy="Citations recommended for source-backed answers",
            retrieval_top_k=4,
            model_temperature=0.20,
            review_required=False,
            enabled_checks=(
                "Document type validation",
                "Minimum text quality check",
                "Baseline requirement completeness check",
            ),
            escalation_rules=("Escalate only unsupported critical assumptions",),
        ),
        AgentAccuracyLevel.BALANCED: AccuracyPolicy(
            label="Balanced",
            target_confidence=0.82,
            validation_depth="Entity, workflow, API, database, and integration consistency checks",
            citation_policy="Citations required for business process, requirement, and integration claims",
            retrieval_top_k=6,
            model_temperature=0.10,
            review_required=True,
            enabled_checks=(
                "Document type validation",
                "Requirement completeness check",
                "Entity and API coverage check",
                "Integration keyword detection",
                "Assumption and risk review check",
            ),
            escalation_rules=("Escalate missing owners, missing source evidence, and high-impact assumptions",),
        ),
        AgentAccuracyLevel.HIGH: AccuracyPolicy(
            label="High Accuracy",
            target_confidence=0.90,
            validation_depth="Cross-artifact validation with source coverage and domain rule consistency",
            citation_policy="Citations required for every material requirement, business rule, and integration decision",
            retrieval_top_k=10,
            model_temperature=0.05,
            review_required=True,
            enabled_checks=(
                "Document type validation",
                "Requirement completeness check",
                "Entity, API, and SQL alignment check",
                "Nagare and SAP rule consistency check",
                "Security and RBAC coverage check",
                "Source evidence coverage check",
            ),
            escalation_rules=(
                "Escalate any uncited Must requirement",
                "Escalate generated SAP or Nagare rules without source evidence",
            ),
        ),
        AgentAccuracyLevel.AUDIT: AccuracyPolicy(
            label="Audit Grade",
            target_confidence=0.95,
            validation_depth="Regulated workflow validation with mandatory evidence, reviewer gates, and export controls",
            citation_policy="Dual evidence required for critical process, financial, SAP, and Nagare decisions",
            retrieval_top_k=12,
            model_temperature=0.00,
            review_required=True,
            enabled_checks=(
                "Document type validation",
                "Requirement completeness check",
                "Entity, API, and SQL alignment check",
                "Nagare and SAP rule consistency check",
                "Security and RBAC coverage check",
                "Source evidence coverage check",
                "Human approval gate check",
                "Audit export readiness check",
            ),
            escalation_rules=(
                "Block approval when source evidence is missing",
                "Block export until process owner and solution architect review is recorded",
                "Escalate conflicting SAP, SharePoint, or Nagare process statements",
            ),
        ),
    }

    def create_profile(self, level: AgentAccuracyLevel, text: str) -> AccuracyProfile:
        policy = self.policies[level]
        estimated_confidence = self._estimate_confidence(policy, text)
        return AccuracyProfile(
            level=level,
            label=policy.label,
            target_confidence=policy.target_confidence,
            estimated_confidence=estimated_confidence,
            validation_depth=policy.validation_depth,
            citation_policy=policy.citation_policy,
            retrieval_top_k=policy.retrieval_top_k,
            model_temperature=policy.model_temperature,
            review_required=policy.review_required,
            enabled_checks=list(policy.enabled_checks),
            escalation_rules=list(policy.escalation_rules),
        )

    def _estimate_confidence(self, policy: AccuracyPolicy, text: str) -> float:
        lower = text.lower()
        signals = 0.0
        signals += 0.08 if len(text) >= 500 else 0.0
        signals += 0.06 if len(text.splitlines()) >= 5 else 0.0
        signals += 0.05 if any(keyword in lower for keyword in ["goal", "objective", "target"]) else 0.0
        signals += 0.05 if any(keyword in lower for keyword in ["input", "output", "workflow"]) else 0.0
        signals += 0.05 if any(keyword in lower for keyword in ["rule", "validation", "approval"]) else 0.0
        signals += 0.05 if any(keyword in lower for keyword in ["kpi", "metric", "sla"]) else 0.0
        signals += 0.04 if any(keyword in lower for keyword in ["sap", "sharepoint", "api"]) else 0.0
        signals += 0.04 if any(keyword in lower for keyword in ["nagare", "jit", "sequence"]) else 0.0
        base = policy.target_confidence - 0.14
        confidence = min(policy.target_confidence, base + signals)
        return round(max(0.50, confidence), 2)

