"""Domain models for Decision Table technique (ISTQB v4).

Decision tables are used to test the implementation of system requirements that specify
how different combinations of conditions result in different outcomes. They are an 
effective way to record complex logic, such as business rules.

According to ISTQB v4:
- Limited Entry Tables: All condition and action values are boolean (T/F)
- Extended Entry Tables: Conditions and actions can take multiple values (ranges, equivalence partitions, discrete values)
- Notation:
  * Conditions: T (true), F (false), – (irrelevant), N/A (not feasible)
  * Actions: X (action should occur), blank (action should not occur)
- Coverage: (columns exercised / total feasible columns) * 100%
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from datetime import datetime


class ConditionType(Enum):
    """Type of condition in the decision table."""
    BOOLEAN = "boolean"          # Limited entry: T/F only
    ENUM = "enum"                # Extended entry: discrete values from enum
    RANGE = "range"              # Extended entry: numeric range
    FORMAT = "format"            # Extended entry: format validation (email, uuid, etc.)
    LENGTH = "length"            # Extended entry: string length
    REQUIRED = "required"        # Boolean: field present or not
    TYPE = "type"                # Extended entry: data type validation


class ConditionValue(Enum):
    """
    Condition values according to ISTQB v4 notation.
    
    - T: Condition is met (true)
    - F: Condition is not met (false)
    - IRRELEVANT: Condition value is irrelevant to the action result (–)
    - NOT_FEASIBLE: Condition is not feasible for this rule (N/A)
    """
    TRUE = "T"
    FALSE = "F"
    IRRELEVANT = "–"
    NOT_FEASIBLE = "N/A"


class ActionValue(Enum):
    """
    Action values according to ISTQB v4 notation.
    
    - EXECUTE: Action should occur (X)
    - NO_EXECUTE: Action should not occur (blank/empty)
    """
    EXECUTE = "X"
    NO_EXECUTE = ""


@dataclass
class DecisionCondition:
    """
    Represents a condition (row) in the decision table.
    
    A condition is a testable aspect of the system input that can influence
    the outcome. Each condition corresponds to a field or constraint from the
    Swagger specification.
    
    Attributes:
        condition_id: Unique identifier for this condition
        field_name: Name of the field being tested
        condition_type: Type of condition (boolean, enum, range, etc.)
        description: Human-readable description
        is_limited_entry: True for boolean conditions (T/F only)
        possible_values: For extended entry, list of possible values
        constraint_details: Original constraint data from Swagger
    """
    condition_id: str
    field_name: str
    condition_type: ConditionType
    description: str
    is_limited_entry: bool = True
    possible_values: List[Any] = field(default_factory=list)
    constraint_details: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate condition data."""
        if not self.condition_id:
            raise ValueError("condition_id cannot be empty")
        if not self.field_name:
            raise ValueError("field_name cannot be empty")
        
        # Extended entry must have possible values
        if not self.is_limited_entry and not self.possible_values:
            raise ValueError("Extended entry conditions must have possible_values")


@dataclass
class DecisionAction:
    """
    Represents an action (outcome) in the decision table.
    
    An action is a system response or outcome that results from a combination
    of conditions. Typically derived from HTTP response codes in the Swagger spec.
    
    Attributes:
        action_id: Unique identifier for this action
        description: Human-readable description
        expected_status_code: HTTP status code for this action
        expected_error: Optional error code/message
        metadata: Additional action metadata
    """
    action_id: str
    description: str
    expected_status_code: int
    expected_error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate action data."""
        if not self.action_id:
            raise ValueError("action_id cannot be empty")
        if not self.description:
            raise ValueError("description cannot be empty")


@dataclass
class DecisionRule:
    """
    Represents a decision rule (column) in the decision table.
    
    A rule defines a unique combination of condition values and the resulting
    actions. Each rule corresponds to one test case.
    
    According to ISTQB v4, coverage is measured by exercising all feasible rules.
    
    Attributes:
        rule_id: Unique identifier for this rule
        condition_values: Map of condition_id -> value (T/F/-/N/A or extended values)
        action_values: Map of action_id -> value (X or blank)
        is_feasible: Whether this combination of conditions is feasible
        test_data: Actual test data values for this rule
        priority: Test priority level
    """
    rule_id: str
    condition_values: Dict[str, Union[ConditionValue, Any]]
    action_values: Dict[str, ActionValue]
    is_feasible: bool = True
    test_data: Dict[str, Any] = field(default_factory=dict)
    priority: str = "medium"
    
    def __post_init__(self):
        """Validate rule data."""
        if not self.rule_id:
            raise ValueError("rule_id cannot be empty")
        if not self.condition_values:
            raise ValueError("condition_values cannot be empty")
        if not self.action_values:
            raise ValueError("action_values cannot be empty")


@dataclass
class DecisionTable:
    """
    Represents a complete decision table for an endpoint.
    
    A decision table organizes conditions (rows) and rules (columns) to show
    how different combinations of inputs lead to different outputs.
    
    According to ISTQB v4:
    - A complete table covers every combination of conditions
    - Tables can be simplified by removing infeasible combinations
    - Tables can be minimized by merging columns with irrelevant conditions
    
    Attributes:
        endpoint: API endpoint path
        http_method: HTTP method
        conditions: List of all conditions (rows)
        actions: List of all actions (outcomes)
        rules: List of all decision rules (columns)
        is_minimized: Whether the table has been minimized
        entry_type: "limited" or "extended"
    """
    endpoint: str
    http_method: str
    conditions: List[DecisionCondition]
    actions: List[DecisionAction]
    rules: List[DecisionRule]
    is_minimized: bool = False
    entry_type: str = "limited"  # "limited" or "extended"
    
    def __post_init__(self):
        """Validate table structure."""
        if not self.endpoint:
            raise ValueError("endpoint cannot be empty")
        if not self.http_method:
            raise ValueError("http_method cannot be empty")
        if not self.conditions:
            raise ValueError("conditions cannot be empty")
        if not self.actions:
            raise ValueError("actions cannot be empty")
        if not self.rules:
            raise ValueError("rules cannot be empty")
        
        # Determine entry type
        has_extended = any(not c.is_limited_entry for c in self.conditions)
        self.entry_type = "extended" if has_extended else "limited"
    
    def get_feasible_rules(self) -> List[DecisionRule]:
        """Get only feasible rules for coverage calculation."""
        return [rule for rule in self.rules if rule.is_feasible]
    
    def calculate_coverage(self, exercised_rules: List[str]) -> float:
        """
        Calculate coverage percentage according to ISTQB v4.
        
        Coverage = (columns exercised / total feasible columns) * 100
        
        Args:
            exercised_rules: List of rule IDs that have been exercised
            
        Returns:
            Coverage percentage (0-100)
        """
        feasible_rules = self.get_feasible_rules()
        if not feasible_rules:
            return 0.0
        
        exercised_count = sum(1 for rule in feasible_rules if rule.rule_id in exercised_rules)
        return (exercised_count / len(feasible_rules)) * 100.0


@dataclass
class DecisionTableTestCase:
    """
    Represents a test case generated from a decision rule.
    
    Each rule in the decision table corresponds to one test case.
    This model is compatible with UnifiedTestCase for integration.
    
    Attributes:
        test_case_id: Unique identifier
        test_name: Descriptive name
        rule_id: ID of the decision rule this test case exercises
        endpoint: API endpoint
        http_method: HTTP method
        test_data: Test input data
        expected_status_code: Expected HTTP response code
        expected_error: Expected error code/message (if any)
        priority: Test priority
        objective: What the test aims to verify
        condition_summary: Summary of condition values
        action_summary: Summary of actions executed
        tags: Tags for categorization
        metadata: Additional metadata
    """
    test_case_id: str
    test_name: str
    rule_id: str
    endpoint: str
    http_method: str
    test_data: Dict[str, Any]
    expected_status_code: int
    expected_error: Optional[str] = None
    priority: str = "medium"
    objective: str = ""
    condition_summary: Dict[str, Any] = field(default_factory=dict)
    action_summary: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate test case data."""
        if not self.test_case_id:
            raise ValueError("test_case_id cannot be empty")
        if not self.test_name:
            raise ValueError("test_name cannot be empty")
        if not self.rule_id:
            raise ValueError("rule_id cannot be empty")


@dataclass
class DecisionTableResult:
    """
    Result of Decision Table test generation for an endpoint.
    
    Contains the complete decision table, generated test cases, and metrics.
    This model follows the same structure as TestGenerationResult and BVAResult
    for consistency across techniques.
    
    Attributes:
        endpoint: API endpoint path
        http_method: HTTP method
        technique: Testing technique name
        decision_table: The complete decision table
        test_cases: Generated test cases
        metrics: Coverage and other metrics
        generated_at: Timestamp of generation
    """
    endpoint: str
    http_method: str
    technique: str = "Decision Table"
    decision_table: Optional[DecisionTable] = None
    test_cases: List[DecisionTableTestCase] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        """Calculate metrics after initialization."""
        if self.decision_table:
            self._calculate_metrics()
    
    def _calculate_metrics(self):
        """Calculate metrics for this result."""
        table = self.decision_table
        feasible_rules = table.get_feasible_rules()
        
        self.metrics = {
            "total_conditions": len(table.conditions),
            "total_actions": len(table.actions),
            "total_rules": len(table.rules),
            "feasible_rules": len(feasible_rules),
            "infeasible_rules": len(table.rules) - len(feasible_rules),
            "is_minimized": table.is_minimized,
            "entry_type": table.entry_type,
            "test_cases_generated": len(self.test_cases),
            "coverage_percentage": self._calculate_coverage()
        }
    
    def _calculate_coverage(self) -> float:
        """
        Calculate coverage percentage.
        
        Coverage = (test cases generated / feasible rules) * 100
        Assumes each test case exercises one rule.
        """
        if not self.decision_table:
            return 0.0
        
        feasible_rules = self.decision_table.get_feasible_rules()
        if not feasible_rules:
            return 0.0
        
        return (len(self.test_cases) / len(feasible_rules)) * 100.0
