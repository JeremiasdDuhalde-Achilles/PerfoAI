"""
Approval Agent for managing approval workflows.
"""
from app.agents.state import InvoiceProcessingState


class ApprovalAgent:
    """Agent responsible for approval workflow management."""

    def __init__(self):
        """Initialize approval agent."""
        # Approval thresholds by amount
        self.approval_thresholds = {
            "auto_approve": 1000,  # < $1,000 auto-approve if valid
            "manager": 5000,       # < $5,000 requires manager
            "director": 20000,     # < $20,000 requires director
            "cfo": float('inf')    # >= $20,000 requires CFO
        }

    def process(self, state: InvoiceProcessingState) -> InvoiceProcessingState:
        """
        Determine approval requirements.

        Args:
            state: Current processing state

        Returns:
            Updated state with approval requirements
        """
        total_amount = state.get("total_amount", 0)
        is_valid = state.get("is_valid", False)
        confidence_score = state.get("confidence_score", 0)

        # Determine if approval is required
        requires_approval = False
        approval_level = "none"

        # Auto-approve if:
        # 1. Amount is below threshold
        # 2. Validation passed
        # 3. Confidence score is high
        # 4. No fraud detected
        if (
            total_amount < self.approval_thresholds["auto_approve"]
            and is_valid
            and confidence_score >= 0.95
            and not state.get("fraud_detected", False)
            and state.get("po_matched", False)
        ):
            requires_approval = False
            approval_level = "auto"
            state["is_touchless"] = True

        else:
            requires_approval = True
            state["is_touchless"] = False

            # Determine approval level based on amount
            if total_amount < self.approval_thresholds["manager"]:
                approval_level = "manager"
            elif total_amount < self.approval_thresholds["director"]:
                approval_level = "director"
            else:
                approval_level = "cfo"

        # Special cases requiring approval
        if state.get("fraud_detected", False):
            requires_approval = True
            approval_level = "director"  # Escalate to director

        if state.get("duplicate_detected", False):
            requires_approval = True

        if state.get("validation_errors", []):
            requires_approval = True

        # Update state
        state["requires_approval"] = requires_approval
        state["approval_threshold"] = total_amount

        # In production, this would assign to specific approver
        # based on org chart, delegation rules, etc.
        if requires_approval:
            state["approver_id"] = self._assign_approver(approval_level)

        state["current_step"] = "approval_determined"

        return state

    def _assign_approver(self, approval_level: str) -> int:
        """
        Assign appropriate approver based on level.

        In production, this would:
        - Query organization hierarchy
        - Check delegation rules
        - Consider vacation/absence
        - Load balance across approvers
        """
        # Simulated approver assignment
        approver_map = {
            "manager": 2,   # User ID 2 (Finance Manager)
            "director": 3,  # User ID 3 (Approver)
            "cfo": 1        # User ID 1 (Admin/CFO)
        }

        return approver_map.get(approval_level, 1)
