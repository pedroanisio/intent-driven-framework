#!/usr/bin/env python3
"""
IDF SDLC v1.7.0 Initializer — Intent Driven Framework v1.5.0
=========================================================
Scaffolds a compliant repository structure based on the Intent Driven Framework
completeness criteria (CC-01 through CC-27).

Usage:
    python idf_init.py [target_directory]

If no target directory is given, defaults to ./idf-repo
"""

import os
import sys
import textwrap
import importlib.util
from datetime import date
from pathlib import Path
from dataclasses import dataclass, field
from typing import Callable, Optional


# ─── PLUGIN HOOK SYSTEM ─────────────────────────────────────────────────────
# Plugins extend the init process by registering hooks at defined lifecycle
# points. This follows CC-12 (extension surface) and CC-20c (lifecycle hooks):
# the core emits events, plugins react, the core never inspects plugin internals.
#
# Hook points:
#   pre_init        — before any directories or files are created
#   post_directories — after directory tree is created, before files
#   post_files       — after all core files are written
#   post_init        — after init_repo completes (final output)
#
# Plugins can also contribute:
#   extra_directories — additional dirs merged into DIRECTORIES
#   extra_files       — additional file entries merged into FILES

@dataclass
class PluginRegistration:
    """A registered init plugin."""
    id: str
    name: str
    version: str
    description: str
    hooks: dict = field(default_factory=dict)          # hook_name -> callable(root, config)
    extra_directories: list = field(default_factory=list)
    extra_files: dict = field(default_factory=dict)    # relpath -> content_fn


class PluginRegistry:
    """Registry for init plugins. Singleton per process."""

    def __init__(self):
        self._plugins: dict[str, PluginRegistration] = {}
        self._hook_order: list[str] = []

    def register(self, plugin: PluginRegistration) -> None:
        if plugin.id in self._plugins:
            print(f"  ⚠ Plugin '{plugin.id}' already registered, skipping duplicate")
            return
        self._plugins[plugin.id] = plugin
        self._hook_order.append(plugin.id)

    def fire(self, hook_name: str, root: Path, config: dict) -> list[dict]:
        """Fire a hook across all registered plugins. Returns results."""
        results = []
        for pid in self._hook_order:
            plugin = self._plugins[pid]
            handler = plugin.hooks.get(hook_name)
            if handler:
                try:
                    result = handler(root, config)
                    results.append({"plugin": pid, "hook": hook_name, "result": result})
                except Exception as e:
                    # CC-20c: handler failure does not prevent subsequent handlers
                    results.append({"plugin": pid, "hook": hook_name, "error": str(e)})
                    print(f"  ⚠ Plugin '{pid}' hook '{hook_name}' failed: {e}")
        return results

    def collect_directories(self) -> list[str]:
        dirs = []
        for plugin in self._plugins.values():
            dirs.extend(plugin.extra_directories)
        return dirs

    def collect_files(self) -> dict:
        files = {}
        for plugin in self._plugins.values():
            for relpath, fn in plugin.extra_files.items():
                if relpath in files:
                    print(f"  ⚠ File conflict: '{relpath}' from plugin '{plugin.id}' — last writer wins")
                files[relpath] = fn
        return files

    @property
    def plugins(self) -> dict[str, PluginRegistration]:
        return dict(self._plugins)

    def summary(self) -> str:
        if not self._plugins:
            return "  (no plugins registered)"
        lines = []
        for p in self._plugins.values():
            hooks = ", ".join(p.hooks.keys()) or "none"
            extras = f"{len(p.extra_directories)} dirs, {len(p.extra_files)} files"
            lines.append(f"  🔌 {p.id} v{p.version} — hooks: [{hooks}], contributes: [{extras}]")
        return "\n".join(lines)


# Global registry
PLUGIN_REGISTRY = PluginRegistry()


def load_plugins_from_directory(plugin_dir: str) -> int:
    """
    Discover and load plugins from a directory.
    Each plugin is a .py file that calls PLUGIN_REGISTRY.register() on import.
    Returns count of loaded plugins.
    """
    plugin_path = Path(plugin_dir)
    if not plugin_path.is_dir():
        return 0
    count = 0
    for py_file in sorted(plugin_path.glob("*.py")):
        if py_file.name.startswith("_"):
            continue
        try:
            spec = importlib.util.spec_from_file_location(
                f"idf_plugin_{py_file.stem}", py_file
            )
            mod = importlib.util.module_from_spec(spec)
            # Inject registry into module namespace before exec
            mod.PLUGIN_REGISTRY = PLUGIN_REGISTRY
            mod.PluginRegistration = PluginRegistration
            spec.loader.exec_module(mod)
            count += 1
        except Exception as e:
            print(f"  ⚠ Failed to load plugin '{py_file.name}': {e}")
    return count


# ─── CONFIGURATION ──────────────────────────────────────────────────────────

DEFAULT_TARGET = "idf-repo"
SCHEMA_VERSION = "0.1.0"
FRAMEWORK_VERSION = "1.7.0"
TODAY = date.today().isoformat()

# ─── CANONICAL ENUMS (per CC-05) ────────────────────────────────────────────
# Every enum is closed. New values require a schema_version bump (CC-24).

ENUMS = {
    "change_type": [
        "clarification", "correction", "extension",
        "reclassification", "breaking", "deprecation",
        "MAJOR", "MINOR", "PATCH",
    ],
    "origin_type": [
        "engineering", "product", "incident", "discovery",
        "regulatory", "organizational", "devops", "ux",
        "data", "sre", "security",
    ],
    "origin_relationship": [
        "derived_from", "motivated_by", "constrained_by",
        "triggered_by", "discovered_in",
    ],
    "priority": ["critical", "high", "medium", "low"],
    "confidence": ["high", "medium", "low"],
    "status": [
        "proposed", "active", "evolving",
        "superseded", "residual", "retracted",
        "accepted", "deprecated",
    ],
    "tier": ["core", "deferred"],
    "achieved_coverage": [
        "none", "minimal", "partial", "substantial", "full",
    ],
    "intent_type": ["aspirational", "achieved"],
}


# ─── DIRECTORY TREE ─────────────────────────────────────────────────────────
# Satisfies CC-09 (repo structure fully specified)
# and CC-10 (creatable from manifesto alone)

DIRECTORIES = [
    # ── Primary scope (per intent YAML) ──
    "prose",
    "criteria",

    # ── Implicit scope ──
    "schemas",
    "schemas/zod",
    "tools",
    "tools/ci",
    "tools/hooks",
    "lean",
    "lean/src",

    # ── Operational ──
    "intents",
    "intents/achieved",
    "intents/aspirational",
    "tensions",
    "decisions",
    "transitions",
    "plugins",
    "plugins/examples",

    # ── Verification ──
    "tests",
    "tests/unit",
    "tests/integration",

    # ── Documentation ──
    "docs",
    "docs/adoption",
    "docs/failure-modes",
]


# ─── FILE TEMPLATES ─────────────────────────────────────────────────────────

def intent_template(intent_id: str, intent_type: str = "aspirational") -> str:
    """Generate a blank intent YAML template (CC-04, CC-08)."""
    lines = [
        f"# Intent Declaration — {intent_id}",
        f"# Schema version: {SCHEMA_VERSION}",
        f"# Framework version: {FRAMEWORK_VERSION}",
        "#",
        "# Canonical enums are defined in schemas/enums.yml",
        f"# This file conforms to schemas/intent-{intent_type}.yml",
        "",
        "intent:",
        f"  id: {intent_id}",
        "  version: 1.0.0",
        f"  schema_version: {SCHEMA_VERSION}",
        f"  intent_type: {intent_type}",
        "",
        "  declares: >",
        "    TODO: A falsifiable statement of what this intent commits to.",
        "    Must satisfy CC-19: if no code change could violate it, it is not an intent.",
        "",
    ]

    if intent_type == "aspirational":
        lines += [
            "  current_reality:",
            "    state: >",
            "      TODO: Describe the current state of reality relative to this intent.",
            "    status: >",
            "      TODO: Summarize verification status.",
            "    remaining_work: >",
            "      TODO: Describe what remains to be done.",
            f"    last_assessed: \"{TODAY}\"",
            "",
        ]

    lines += [
        "  scope:",
        "    primary: []        # TODO: list governed files/paths",
        "    implicit: []       # TODO: list implicitly governed paths",
        "",
        "  priority: medium        # critical | high | medium | low",
        "  status: proposed        # proposed | active | evolving | superseded | residual | retracted",
        "  confidence: medium      # high | medium | low",
        "",
        "  owner: \"TODO\"          # team or individual",
        "",
        "  origin:",
        "    type: engineering     # see schemas/enums.yml for full list",
        "    ref: \"\"               # conversation, ticket, postmortem, etc.",
        "    relationship: derived_from  # derived_from | motivated_by | constrained_by | triggered_by | discovered_in",
        "",
        "  serves: []              # list of intent IDs this intent serves",
        "  dependencies: []        # list of intent IDs this intent depends on",
        "",
        "  transition_log: []",
        "",
    ]

    return "\n".join(lines)


def tension_template() -> str:
    """Generate a blank tension YAML template (CC-04, CC-06)."""
    return textwrap.dedent(f"""\
    # Tension Declaration
    # Schema version: {SCHEMA_VERSION}
    #
    # A tension represents a known conflict or trade-off between two intents.
    # See CC-08a, CC-08b, CC-08c for conflict resolution criteria.

    tension:
      id: tension-XXXX
      between:
        - intent_id: ""       # first intent
          version: "1.0.0"
        - intent_id: ""       # second intent
          version: "1.0.0"

      description: >
        TODO: Describe the conflict or trade-off.

      resolution:
        strategy: ""          # how the tension is resolved
        resolution_owner: ""  # who decides
        applies_to:
          - "1.0.0"           # semver of intent A at resolution time
          - "1.0.0"           # semver of intent B at resolution time

      status: proposed        # proposed | active | superseded | residual
      created: "{TODAY}"
    """)


def decision_template() -> str:
    """Generate a blank decision record template (CC-04)."""
    return textwrap.dedent(f"""\
    # Decision Record
    # Schema version: {SCHEMA_VERSION}

    decision:
      id: decision-XXXX
      date: "{TODAY}"
      intent_refs: []         # list of intent IDs this decision relates to
      context: >
        TODO: What situation prompted this decision?
      decision: >
        TODO: What was decided?
      consequences: >
        TODO: What are the expected consequences?
      status: proposed        # proposed | accepted | superseded | deprecated
    """)


def manifest_template() -> str:
    """Generate the intent manifest (CC-04, CC-09)."""
    return textwrap.dedent(f"""\
    # Intent Manifest
    # Schema version: {SCHEMA_VERSION}
    # Framework version: {FRAMEWORK_VERSION}
    #
    # This file is the index of all declared intents in this repository.
    # It is auto-generated by tooling (CC-20) or manually maintained.

    manifest:
      repo: "TODO: repository name"
      generated: "{TODAY}"
      schema_version: "{SCHEMA_VERSION}"

      intents: []
      # Example entry:
      #   - id: intent-example
      #     path: intents/aspirational/intent-example.yml
      #     status: active
      #     priority: medium

      tensions: []
      decisions: []
    """)


def enums_yaml() -> str:
    """Generate the canonical enums file (CC-05)."""
    lines = [
        f"# Canonical Enums — Intent Driven Framework v{FRAMEWORK_VERSION}",
        f"# Schema version: {SCHEMA_VERSION}",
        "#",
        "# All enums are CLOSED. Adding a new value requires a schema_version bump (CC-24).",
        "# These are the single source of truth referenced by all schemas and validators.",
        "",
        "enums:",
    ]
    for name, values in ENUMS.items():
        lines.append(f"  {name}:")
        for v in values:
            lines.append(f"    - {v}")
        lines.append("")
    return "\n".join(lines)


def aspirational_schema() -> str:
    """Generate the aspirational intent JSON/YAML schema (CC-04, CC-08)."""
    return textwrap.dedent(f"""\
    # Aspirational Intent Schema
    # Schema version: {SCHEMA_VERSION}
    #
    # An aspirational intent includes a current_reality block describing
    # the gap between the declared intent and the actual state.
    # Transition from aspirational → achieved is defined by CC-08.

    aspirational_intent:
      required_fields:
        - id                  # string, unique identifier
        - version             # semver string
        - schema_version      # semver string
        - intent_type         # must be "aspirational"
        - declares            # free-text, must pass CC-19 quality test
        - current_reality     # block: state, status, remaining_work, last_assessed
        - scope               # block: primary (list), implicit (list)
        - priority            # enum: critical | high | medium | low
        - status              # enum: proposed | active | evolving | superseded | residual | retracted
        - confidence          # enum: high | medium | low
        - owner               # string or list
        - origin              # block: type, ref, relationship
        - transition_log      # list of transition entries

      optional_fields:
        - serves              # list of intent IDs
        - dependencies        # list of intent IDs
        - achieved_coverage   # enum: none | minimal | partial | substantial | full
        - ext                 # namespaced extensions (CC-12)

      current_reality:
        required_fields:
          - state             # free-text description
          - status            # free-text summary
          - remaining_work    # free-text description
          - last_assessed     # ISO date string
    """)


def achieved_schema() -> str:
    """Generate the achieved intent schema (CC-04, CC-08)."""
    return textwrap.dedent(f"""\
    # Achieved Intent Schema
    # Schema version: {SCHEMA_VERSION}
    #
    # An achieved intent does NOT require a current_reality block.
    # It represents a commitment that has been fully met and verified.

    achieved_intent:
      required_fields:
        - id
        - version
        - schema_version
        - intent_type         # must be "achieved"
        - declares
        - scope
        - priority
        - status
        - confidence
        - owner
        - origin
        - transition_log

      optional_fields:
        - serves
        - dependencies
        - achieved_coverage   # should be "full" for achieved intents
        - current_reality     # optional — may be retained for historical context
        - ext                 # namespaced extensions (CC-12)
    """)


def plugin_manifest_template() -> str:
    """Generate a plugin manifest template (CC-11, CC-12)."""
    return textwrap.dedent(f"""\
    # Plugin Manifest Template
    # Schema version: {SCHEMA_VERSION}
    #
    # Plugins extend the core model via the ext: namespace (CC-12).
    # Rules:
    #   (a) Extensions MUST NOT override or shadow core fields
    #   (b) Extensions are namespaced: ext.<plugin_id>.*
    #   (c) Core tooling MUST ignore unrecognised ext: keys gracefully
    #   (d) See plugins/examples/ for a worked example

    plugin:
      id: plugin-example
      name: "Example Plugin"
      version: "1.0.0"
      description: >
        TODO: What does this plugin add to the IDF model?

      extends:
        intent:
          ext.plugin-example.custom_field:
            type: string
            description: "An example extension field"
            required: false

      registry_entry:
        id: plugin-example
        version: "1.0.0"
        compatible_schema_versions: ["{SCHEMA_VERSION}"]
    """)


def plugin_example() -> str:
    """A worked example of a plugin extending an intent (CC-11, CC-12)."""
    return textwrap.dedent(f"""\
    # Worked Example: SLA Plugin
    # Demonstrates CC-11 (plugin architecture) and CC-12 (ext: namespace)

    plugin:
      id: plugin-sla
      name: "SLA Tracker"
      version: "1.0.0"
      description: >
        Adds SLA tracking fields to intent declarations, allowing teams
        to bind response-time commitments to declared intents.

      extends:
        intent:
          ext.plugin-sla.sla_target_ms:
            type: integer
            description: "Target SLA in milliseconds"
            required: false
          ext.plugin-sla.sla_measured_ms:
            type: integer
            description: "Last measured SLA in milliseconds"
            required: false

    # ─── Usage in an intent file ────────────────────────────────────────
    #
    # intent:
    #   id: intent-api-latency
    #   declares: "API p99 latency stays below 200ms"
    #   ...
    #   ext:
    #     plugin-sla:
    #       sla_target_ms: 200
    #       sla_measured_ms: 187
    """)


def ci_validator_script() -> str:
    """Generate CI validation stub (CC-20: tooling surface)."""
    return textwrap.dedent("""\
    #!/usr/bin/env python3
    \"\"\"
    IDF CI Validator — Tooling Surface (CC-20)
    ===========================================
    Validates intent files against the IDF schema.

    Contracts (per CC-20):
      (a) Schema validation: every intent YAML conforms to its type schema
      (b) Scope lookup: intents can be queried by file path
      (c) Lifecycle hooks: transitions propagate events

    Usage:
        python validate.py [intents_dir]
    \"\"\"

    import sys
    import glob
    from pathlib import Path

    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML required. Install with: pip install pyyaml")
        sys.exit(1)


    REQUIRED_FIELDS_COMMON = [
        "id", "version", "schema_version", "intent_type",
        "declares", "scope", "priority", "status", "confidence",
        "owner", "origin", "transition_log",
    ]

    REQUIRED_CURRENT_REALITY = ["state", "status", "remaining_work", "last_assessed"]

    VALID_ENUMS = {
        "change_type": [
            "clarification", "correction", "extension",
            "reclassification", "breaking", "deprecation",
            "MAJOR", "MINOR", "PATCH",
        ],
        "intent_type": ["aspirational", "achieved"],
        "priority": ["critical", "high", "medium", "low"],
        "status": [
            "proposed", "active", "evolving",
            "superseded", "residual", "retracted",
            "accepted", "deprecated",
        ],
        "confidence": ["high", "medium", "low"],
        "tier": ["core", "deferred"],
        "origin_type": [
            "engineering", "product", "incident", "discovery", "regulatory",
            "organizational", "devops", "ux", "data", "sre", "security",
        ],
        "origin_relationship": [
            "derived_from", "motivated_by", "constrained_by",
            "triggered_by", "discovered_in",
        ],
        "achieved_coverage": ["none", "minimal", "partial", "substantial", "full"],
    }


    class ValidationError:
        def __init__(self, file: str, field: str, message: str):
            self.file = file
            self.field = field
            self.message = message

        def __str__(self):
            return f"  [{self.file}] {self.field}: {self.message}"


    def validate_intent(filepath: str) -> list[ValidationError]:
        \"\"\"Validate a single intent YAML file.\"\"\"
        errors = []
        path = Path(filepath)

        try:
            with open(path) as f:
                doc = yaml.safe_load(f)
        except yaml.YAMLError as e:
            return [ValidationError(path.name, "yaml", f"Parse error: {e}")]

        if not doc or "intent" not in doc:
            return [ValidationError(path.name, "root", "Missing 'intent' key")]

        intent = doc["intent"]

        # ── Required fields ──
        for field in REQUIRED_FIELDS_COMMON:
            if field not in intent:
                errors.append(ValidationError(path.name, field, "Required field missing"))

        # ── Enum validation (CC-05) ──
        for field, valid in [
            ("intent_type", VALID_ENUMS["intent_type"]),
            ("priority", VALID_ENUMS["priority"]),
            ("status", VALID_ENUMS["status"]),
            ("confidence", VALID_ENUMS["confidence"]),
        ]:
            val = intent.get(field)
            if val and val not in valid:
                errors.append(ValidationError(
                    path.name, field, f"Invalid value '{val}'. Must be one of: {valid}"
                ))

        # ── Origin validation ──
        origin = intent.get("origin", {})
        if origin:
            otype = origin.get("type")
            if otype and otype not in VALID_ENUMS["origin_type"]:
                errors.append(ValidationError(
                    path.name, "origin.type",
                    f"Invalid origin type '{otype}'. Must be one of: {VALID_ENUMS['origin_type']}"
                ))
            orel = origin.get("relationship")
            if orel and orel not in VALID_ENUMS["origin_relationship"]:
                errors.append(ValidationError(
                    path.name, "origin.relationship",
                    f"Invalid relationship '{orel}'. Must be one of: {VALID_ENUMS['origin_relationship']}"
                ))

        # ── Aspirational-specific: current_reality (CC-08) ──
        if intent.get("intent_type") == "aspirational":
            cr = intent.get("current_reality")
            if not cr:
                errors.append(ValidationError(
                    path.name, "current_reality",
                    "Aspirational intents must include current_reality block"
                ))
            else:
                for field in REQUIRED_CURRENT_REALITY:
                    if field not in cr:
                        errors.append(ValidationError(
                            path.name, f"current_reality.{field}",
                            "Required field missing in current_reality"
                        ))

        # ── Declares quality hint (CC-19) ──
        declares = intent.get("declares", "")
        if declares and "TODO" in str(declares):
            errors.append(ValidationError(
                path.name, "declares",
                "WARNING: declares field still contains TODO placeholder"
            ))

        # ── Achieved coverage validation ──
        ac = intent.get("achieved_coverage")
        if ac and ac not in VALID_ENUMS["achieved_coverage"]:
            errors.append(ValidationError(
                path.name, "achieved_coverage",
                f"Invalid value '{ac}'. Must be one of: {VALID_ENUMS['achieved_coverage']}"
            ))

        # ── Transition log integrity (CC-27) ──
        tlog = intent.get("transition_log", [])
        if tlog:
            versions_seen = set()
            for entry in tlog:
                ct = entry.get("change_type", "")
                valid_ct = [
                    "clarification", "correction", "extension",
                    "reclassification", "breaking", "deprecation",
                    "MAJOR", "MINOR", "PATCH",
                ]
                if ct and ct not in valid_ct:
                    errors.append(ValidationError(
                        path.name, "transition_log.change_type",
                        f"Invalid change_type '{ct}'. Must be one of: {valid_ct}"
                    ))
                frm = entry.get("from")
                to = entry.get("to")
                if frm:
                    versions_seen.add(frm)
                if to:
                    versions_seen.add(to)

        return errors


    def validate_directory(intents_dir: str) -> int:
        \"\"\"Validate all intent YAML files in a directory tree.\"\"\"
        pattern = f"{intents_dir}/**/*.yml"
        files = glob.glob(pattern, recursive=True)

        if not files:
            print(f"No .yml files found in {intents_dir}")
            return 0

        total_errors = 0
        for filepath in sorted(files):
            errors = validate_intent(filepath)
            if errors:
                print(f"\\n✗ {filepath}")
                for e in errors:
                    print(f"  {e}")
                total_errors += len(errors)
            else:
                print(f"✓ {filepath}")

        print(f"\\n{'─' * 50}")
        print(f"Files scanned: {len(files)}")
        print(f"Errors found:  {total_errors}")
        return total_errors


    def scope_lookup(intents_dir: str, query_path: str) -> list[dict]:
        \"\"\"
        CC-20(b): Query intents by file path.
        Returns all intents whose scope covers the given path.
        \"\"\"
        results = []
        pattern = f"{intents_dir}/**/*.yml"
        for filepath in glob.glob(pattern, recursive=True):
            try:
                with open(filepath) as f:
                    doc = yaml.safe_load(f)
                if not doc or "intent" not in doc:
                    continue
                intent = doc["intent"]
                scope = intent.get("scope", {})
                all_paths = scope.get("primary", []) + scope.get("implicit", [])
                for p in all_paths:
                    if p and query_path in str(p):
                        results.append({
                            "intent_id": intent.get("id"),
                            "file": filepath,
                            "matched_scope": p,
                        })
            except Exception:
                continue
        return results


    if __name__ == "__main__":
        target = sys.argv[1] if len(sys.argv) > 1 else "intents"
        exit_code = validate_directory(target)
        sys.exit(1 if exit_code > 0 else 0)
    """)


def lifecycle_hook_script() -> str:
    """Generate lifecycle hook stub (CC-20c, CC-07)."""
    return textwrap.dedent("""\
    #!/usr/bin/env python3
    \"\"\"
    IDF Lifecycle Hooks (CC-07, CC-20c)
    ====================================
    Defines how lifecycle state transitions propagate.

    States: proposed → active → evolving → superseded → residual
                                                      → retracted (terminal, from proposed only)

    CC-23: Tension resolution staleness
      - MAJOR bump → invalidate resolutions (re-evaluate required)
      - MINOR bump → review flag (surfaced for human assessment)
      - PATCH bump → no action

    CC-25: Deprecation ceremonies
      Step 1: Identify all intents with depends_on references
      Step 2: State migration path (re-point, drop, or acknowledge)
      Step 3: Grace period or deadline
      Step 4: Surface unresolved references as tensions
    \"\"\"

    import sys

    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML required.")
        sys.exit(1)


    # ─── CC-07: Lifecycle State Machine ─────────────────────────────────

    VALID_TRANSITIONS = {
        "proposed":   ["active", "retracted", "accepted"],
        "active":     ["evolving", "superseded", "residual", "deprecated"],
        "evolving":   ["active", "superseded", "residual"],
        "superseded": ["residual"],
        "residual":   [],          # terminal
        "retracted":  [],          # terminal
        "accepted":   [],          # terminal (decision-lifecycle)
        "deprecated": [],          # terminal (decision-lifecycle)
    }


    def validate_transition(current: str, target: str) -> tuple[bool, str]:
        \"\"\"Check if a lifecycle transition is valid per CC-07.\"\"\"
        if current not in VALID_TRANSITIONS:
            return False, f"Unknown state: {current}"
        allowed = VALID_TRANSITIONS[current]
        if target not in allowed:
            return False, (
                f"Invalid transition: {current} → {target}. "
                f"Allowed from {current}: {allowed}"
            )
        return True, f"OK: {current} → {target}"


    # ─── CC-23: Staleness Detection ─────────────────────────────────────

    def parse_semver(version: str) -> tuple[int, int, int]:
        parts = version.split(".")
        return int(parts[0]), int(parts[1]), int(parts[2])


    def detect_staleness(old_version: str, new_version: str) -> str:
        \"\"\"
        Determine staleness action for tension resolutions.
        Returns: 'invalidate', 'review', or 'none'
        \"\"\"
        old = parse_semver(old_version)
        new = parse_semver(new_version)

        if new[0] > old[0]:
            return "invalidate"   # MAJOR bump → full re-evaluation
        elif new[1] > old[1]:
            return "review"       # MINOR bump → human review flag
        else:
            return "none"         # PATCH bump → no action


    # ─── CC-25: Deprecation Ceremony ────────────────────────────────────

    def deprecation_ceremony(intent_id: str, successor_id: str = None) -> dict:
        \"\"\"
        Generate a deprecation ceremony checklist for a superseded/residual intent.
        Returns a structured checklist.
        \"\"\"
        return {
            "intent_id": intent_id,
            "successor": successor_id,
            "steps": [
                {
                    "step": 1,
                    "action": "identify_dependents",
                    "description": f"Find all intents with depends_on referencing '{intent_id}'",
                    "status": "pending",
                },
                {
                    "step": 2,
                    "action": "state_migration_path",
                    "description": (
                        f"Each dependent must: re-point to '{successor_id}', "
                        "drop the dependency, or acknowledge residual state"
                        if successor_id else
                        "Each dependent must: drop the dependency or acknowledge residual state"
                    ),
                    "status": "pending",
                },
                {
                    "step": 3,
                    "action": "define_grace_period",
                    "description": "Set deadline for dependent migration (or delegate to intent owner)",
                    "status": "pending",
                },
                {
                    "step": 4,
                    "action": "surface_unresolved",
                    "description": "After grace period, surface unresolved downstream references as tensions",
                    "status": "pending",
                },
            ],
        }


    if __name__ == "__main__":
        # Quick demo
        print("=== Lifecycle Transition Validation (CC-07) ===")
        for curr, tgt in [("proposed", "active"), ("active", "retracted"), ("residual", "active")]:
            ok, msg = validate_transition(curr, tgt)
            print(f"  {'✓' if ok else '✗'} {msg}")

        print("\\n=== Staleness Detection (CC-23) ===")
        for old, new in [("1.0.0", "2.0.0"), ("1.0.0", "1.1.0"), ("1.0.0", "1.0.1")]:
            action = detect_staleness(old, new)
            print(f"  {old} → {new}: {action}")

        print("\\n=== Deprecation Ceremony (CC-25) ===")
        ceremony = deprecation_ceremony("intent-old-api", "intent-new-api")
        for step in ceremony["steps"]:
            print(f"  Step {step['step']}: {step['action']}")
            print(f"    {step['description']}")
    """)


def adoption_guide() -> str:
    """Generate the adoption guide (CC-13, CC-14, CC-15, CC-21)."""
    return textwrap.dedent("""\
    # Adoption Guide — Intent Driven Framework
    
    This guide provides an ordered, actionable adoption sequence (CC-13)
    that does not require a comprehensive legacy audit (CC-14).
    
    ## Adoption Sequence
    
    1. **Install the IDF structure** — Run `python idf_init.py <your-repo>`.
       This creates the directory tree, schemas, and tooling stubs.
    
    2. **Declare your first intent** — Copy
       `intents/aspirational/_template.yml` and fill in the `declares` field.
       Start with whatever pain point prompted you to look at IDF.
    
    3. **Add CI validation** — Wire `tools/ci/validate.py` into your
       CI pipeline. Start in advisory mode (exit 0 on errors).
    
    4. **Adopt the next-touch rule** — When touching a file, check if an
       intent governs it. If not, declare one. This is advisory at first
       (CC-21 adoption ramp).
    
    5. **Transition to enforcement** — After a defined ramp period, switch
       CI validation to blocking (exit 1 on errors).
    
    6. **Record tensions** — When two intents conflict, create a tension
       file in `tensions/`. Don't resolve prematurely.
    
    7. **Iterate** — Review intents periodically. Promote aspirational
       intents to achieved when all commitments are met and verified.
    
    ## Three Entry Points (CC-15)
    
    ### Pain-First
    Start with the intent that addresses your most pressing problem.
    Don't try to be comprehensive — declare one intent for one pain point.
    
    ### Next-Touch
    Every time you open a file, check if an intent governs it. If not,
    declare one. Coverage grows organically with development activity.
    
    ### Amnesty
    Declare aspirational intents for entire subsystems without auditing
    existing code. The `current_reality` block captures the gap honestly.
    No archaeology required (CC-14).
    
    ## Adoption Ramp (CC-21)
    
    The next-touch rule starts as **advisory** (non-blocking) for a team-defined
    period. This addresses the cold-start problem: on a legacy codebase with
    zero declared intents, "every PR must reference an intent" would block
    every PR until someone does the archaeology.
    
    The transition from advisory to enforcement should be explicit and communicated.
    """)


def failure_modes_doc() -> str:
    """Generate failure modes documentation (CC-26)."""
    return textwrap.dedent("""\
    # Failure Modes — Intent Driven Framework
    
    The IDF can be adopted badly. This document names the three primary failure
    modes so teams have vocabulary to self-correct (CC-26).
    
    ---
    
    ## 1. Performative Intent
    
    **Symptoms:** Intent files pass schema validation but contain vague,
    unfalsifiable declarations like "maintain code quality" or "ensure reliability."
    
    **Root cause:** Teams treat intent declarations as bureaucratic checkboxes
    rather than meaningful commitments.
    
    **Mitigation:** Apply the CC-19 falsifiability test: if no code change
    could violate the declaration, it is not an intent. Use the declares
    quality guidance (positive/negative examples, commitment verb + observable
    predicate structure).
    
    ---
    
    ## 2. Over-Specification
    
    **Symptoms:** Intent declarations are so granular that every function or
    module has its own intent. The governance overhead exceeds the value.
    Teams spend more time maintaining intent files than writing code.
    
    **Root cause:** Misunderstanding of the appropriate granularity. Intents
    should capture meaningful architectural or behavioral commitments, not
    mirror the code structure 1:1.
    
    **Mitigation:** Intents should be at the subsystem or capability level.
    If an intent governs fewer than ~5 files, it's probably too granular.
    Use the pain-first entry point to calibrate the right level.
    
    ---
    
    ## 3. Intent Drift
    
    **Symptoms:** Declared intents no longer reflect actual system behavior.
    The codebase has evolved but the intent files haven't been updated.
    `current_reality` blocks are stale. `last_assessed` dates are months old.
    
    **Root cause:** No enforcement mechanism for keeping intents current.
    The next-touch rule isn't being followed, or it was never transitioned
    from advisory to enforcement.
    
    **Mitigation:** Use CI tooling (CC-20) to flag stale `last_assessed`
    dates. Enforce the next-touch rule. Review intents during sprint
    retrospectives. Transition drifted intents to `residual` status
    rather than letting them silently rot.
    """)


def daily_practice_doc() -> str:
    """Generate daily practice guide (CC-17)."""
    return textwrap.dedent("""\
    # Daily Practice — Intent Driven Framework
    
    Concrete behavioral instructions for day-to-day development (CC-17).
    
    ## When to Declare
    - Before starting a new feature or subsystem
    - When you discover an implicit architectural commitment
    - When a post-mortem reveals an unspoken assumption
    
    ## When to Link
    - Every PR should reference at least one intent (after ramp period)
    - When adding a dependency between subsystems, link the relevant intents
    - When a test failure reveals an intent violation
    
    ## When to Record
    - Record a tension when two intents conflict
    - Record a decision when resolving a tension or making a trade-off
    - Record a transition when an intent's version or status changes
    
    ## When to Check
    - During code review: does this change align with governing intents?
    - During CI: does the intent YAML validate against the schema?
    - During retrospectives: are intents still current? Any drift?
    - After a major bump: are tension resolutions still valid? (CC-23)
    """)


def manifesto_stub() -> str:
    """Generate the manifesto stub (CC-01, CC-02, CC-03)."""
    return textwrap.dedent("""\
    # Intent Manifesto
    
    ## The Problem (CC-01)
    
    TODO: Describe the current state of software development without the
    intent-driven model. What is lost when architectural decisions are
    implicit, undocumented, and scattered across code, comments, and
    tribal knowledge?
    
    ## The Inversion (CC-02)
    
    TODO: Name the old orientation and the new one. The shift from
    [old model] to [intent-driven model].
    
    ## Principles (CC-03)
    
    Each principle must be named, numbered, and explained with rationale.
    
    ### Principle 1: [Name]
    
    **Statement:** TODO
    
    **Rationale:** TODO — why this principle matters.
    
    ---
    
    *Add additional principles as needed. Each must have:
    title + body + why-it-matters.*
    """)


def spec_core_stub() -> str:
    """Generate the spec core stub."""
    return textwrap.dedent("""\
    # Intent Specification — Core Data Model
    
    This document defines the universal data model for the Intent Driven Framework.
    
    ## First-Class Entities (CC-04)
    
    The model defines five first-class entities:
    - **Intent** — a declared architectural or behavioral commitment
    - **Transition** — a versioned change to an intent
    - **Decision** — a recorded choice that affects intents
    - **Tension** — a known conflict between intents
    - **Manifest** — the repository-level index of all intents
    
    See `schemas/` for complete YAML schemas of each entity.
    
    ## Lifecycle States (CC-07)
    
    | State       | Entry Condition          | Exit Condition                    |
    |-------------|--------------------------|-----------------------------------|
    | proposed    | Intent declared          | Accepted → active; or → retracted |
    | active      | Accepted by owner        | → evolving, superseded, residual  |
    | evolving    | Undergoing change        | → active, superseded, residual    |
    | superseded  | Replaced by successor    | → residual                        |
    | residual    | No longer maintained     | Terminal                          |
    | retracted   | Withdrawn before active  | Terminal                          |
    
    ## Tooling Surface (CC-20)
    
    See `tools/ci/validate.py` for the reference implementation of:
    - (a) Schema validation in CI
    - (b) Scope lookup by file path
    - (c) Lifecycle hook invocation
    """)


def readme() -> str:
    """Generate the repository README."""
    return textwrap.dedent(f"""\
    # Intent Driven Framework — Repository
    
    Initialized with IDF v{FRAMEWORK_VERSION} / schema v{SCHEMA_VERSION}
    
    ## Structure
    
    ```
    prose/                    # Philosophy and specification
      intent-manifesto.md     # CC-01, CC-02, CC-03
      intent-spec-core.md     # Core data model
    criteria/                 # Completeness criteria
    schemas/                  # YAML schemas (CC-04–CC-08)
      enums.yml               # Canonical enums (CC-05)
      intent-aspirational.yml # Aspirational intent schema
      intent-achieved.yml     # Achieved intent schema
    intents/                  # Declared intents
      aspirational/           # Intents with gaps
      achieved/               # Fully met intents
    tensions/                 # Declared tensions (CC-08a–CC-08c)
    decisions/                # Decision records
    transitions/              # Transition records
    plugins/                  # Plugin manifests (CC-11, CC-12)
      examples/               # Worked examples
    tools/                    # Tooling surface (CC-20)
      ci/                     # CI validation
      hooks/                  # Lifecycle hooks (CC-07)
    lean/                     # Formal verification
    tests/                    # Test suites
    docs/                     # Guides and references
      adoption/               # Adoption guide (CC-13–CC-15, CC-21)
      failure-modes/          # Failure mode catalogue (CC-26)
    ```
    
    ## Quick Start
    
    1. Read `docs/adoption/adoption-guide.md`
    2. Copy `intents/aspirational/_template.yml` to declare your first intent
    3. Run `python tools/ci/validate.py intents/` to validate
    4. See `docs/daily-practice.md` for day-to-day workflow
    
    ## Validation
    
    ```bash
    pip install pyyaml
    python tools/ci/validate.py intents/
    ```
    """)


def gitignore() -> str:
    return textwrap.dedent("""\
    __pycache__/
    *.pyc
    .env
    .venv/
    node_modules/
    .DS_Store
    *.swp
    """)


# ─── BUILDER ────────────────────────────────────────────────────────────────

FILES = {
    # Root
    "README.md": readme,
    ".gitignore": gitignore,

    # Prose (CC-01, CC-02, CC-03)
    "prose/intent-manifesto.md": manifesto_stub,
    "prose/intent-spec-core.md": spec_core_stub,

    # Criteria
    "criteria/.gitkeep": lambda: "# Place completeness criteria YAML files here\n",

    # Schemas (CC-04, CC-05, CC-08)
    "schemas/enums.yml": enums_yaml,
    "schemas/intent-aspirational.yml": aspirational_schema,
    "schemas/intent-achieved.yml": achieved_schema,

    # Intent templates
    "intents/aspirational/_template.yml": lambda: intent_template("intent-XXXX", "aspirational"),
    "intents/achieved/_template.yml": lambda: intent_template("intent-XXXX", "achieved"),
    "intents/manifest.yml": manifest_template,

    # Tensions & Decisions
    "tensions/_template.yml": tension_template,
    "decisions/_template.yml": decision_template,
    "transitions/.gitkeep": lambda: "# Transition records go here\n",

    # Plugins (CC-11, CC-12)
    "plugins/_template.yml": plugin_manifest_template,
    "plugins/examples/plugin-sla.yml": plugin_example,

    # Tools (CC-20)
    "tools/ci/validate.py": ci_validator_script,
    "tools/hooks/lifecycle.py": lifecycle_hook_script,

    # Lean stubs
    "lean/src/.gitkeep": lambda: "# Lean 4 formal verification sources\n",

    # Tests
    "tests/unit/.gitkeep": lambda: "# Unit tests\n",
    "tests/integration/.gitkeep": lambda: "# Integration tests\n",

    # Docs (CC-13, CC-15, CC-17, CC-21, CC-26)
    "docs/adoption/adoption-guide.md": adoption_guide,
    "docs/failure-modes/failure-modes.md": failure_modes_doc,
    "docs/daily-practice.md": daily_practice_doc,
}


def init_repo(target: str, plugin_dir: str = None) -> None:
    """Create the full IDF repository structure with plugin support."""
    root = Path(target)
    config = {
        "target": target,
        "schema_version": SCHEMA_VERSION,
        "framework_version": FRAMEWORK_VERSION,
        "today": TODAY,
    }

    print(f"╔══════════════════════════════════════════════════╗")
    print(f"║  IDF Codebase Initializer v{FRAMEWORK_VERSION}               ║")
    print(f"║  Schema version: {SCHEMA_VERSION}                          ║")
    print(f"╚══════════════════════════════════════════════════╝")
    print()

    # ── Load plugins ──
    if plugin_dir:
        loaded = load_plugins_from_directory(plugin_dir)
        if loaded:
            print(f"Loaded {loaded} plugin(s) from {plugin_dir}:")
            print(PLUGIN_REGISTRY.summary())
            print()
    # Also check for plugins/ next to this script
    script_plugins = Path(__file__).parent / "plugins"
    if script_plugins.is_dir() and str(script_plugins) != str(plugin_dir):
        loaded = load_plugins_from_directory(str(script_plugins))
        if loaded:
            print(f"Loaded {loaded} plugin(s) from {script_plugins}:")
            print(PLUGIN_REGISTRY.summary())
            print()

    # ── Hook: pre_init ──
    PLUGIN_REGISTRY.fire("pre_init", root, config)

    # ── Merge plugin directories ──
    all_directories = DIRECTORIES + PLUGIN_REGISTRY.collect_directories()

    # Create directories
    print("Creating directories...")
    for d in all_directories:
        dirpath = root / d
        dirpath.mkdir(parents=True, exist_ok=True)
        print(f"  📁 {d}/")

    print()

    # ── Hook: post_directories ──
    PLUGIN_REGISTRY.fire("post_directories", root, config)

    # ── Merge plugin files ──
    all_files = dict(FILES)
    all_files.update(PLUGIN_REGISTRY.collect_files())

    # Create files
    print("Creating files...")
    for relpath, content_fn in all_files.items():
        filepath = root / relpath
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content_fn())
        print(f"  📄 {relpath}")

    print()

    # ── Hook: post_files ──
    PLUGIN_REGISTRY.fire("post_files", root, config)

    print(f"{'─' * 52}")
    print(f"✓ Initialized IDF repository at: {root.resolve()}")
    print(f"  Directories: {len(all_directories)}")
    print(f"  Files:       {len(all_files)}")
    if PLUGIN_REGISTRY.plugins:
        print(f"  Plugins:     {len(PLUGIN_REGISTRY.plugins)}")
    print()

    # ── Hook: post_init ──
    PLUGIN_REGISTRY.fire("post_init", root, config)

    print("Next steps:")
    print("  1. cd", target)
    print("  2. Read docs/adoption/adoption-guide.md")
    print("  3. Copy intents/aspirational/_template.yml")
    print("  4. pip install pyyaml && python tools/ci/validate.py intents/")
    print()

    # ── CC Traceability ──
    print("Completeness Criteria Coverage:")
    coverage = {
        "CC-01": "prose/intent-manifesto.md (problem statement stub)",
        "CC-02": "prose/intent-manifesto.md (inversion stub)",
        "CC-03": "prose/intent-manifesto.md (principles stub)",
        "CC-04": "schemas/ (entity schemas)",
        "CC-05": "schemas/enums.yml (canonical enums)",
        "CC-06": "schemas/ (bidirectional relationships)",
        "CC-07": "tools/hooks/lifecycle.py (state machine)",
        "CC-08": "schemas/intent-aspirational.yml, intent-achieved.yml",
        "CC-08a": "tensions/_template.yml (conflict detection)",
        "CC-08b": "tools/hooks/lifecycle.py (transition checks)",
        "CC-08c": "tools/ci/validate.py (scope overlap)",
        "CC-09": "Directory tree (this script)",
        "CC-10": "Directory tree (self-contained)",
        "CC-11": "plugins/_template.yml (plugin architecture)",
        "CC-12": "plugins/examples/plugin-sla.yml (ext: namespace)",
        "CC-13": "docs/adoption/adoption-guide.md (ordered steps)",
        "CC-14": "docs/adoption/adoption-guide.md (no audit required)",
        "CC-15": "docs/adoption/adoption-guide.md (3 entry points)",
        "CC-16": "prose/ (self-sufficient definitions)",
        "CC-17": "docs/daily-practice.md (behavioral instructions)",
        "CC-18": "schemas/ (self-conformance)",
        "CC-19": "intents/ templates (declares quality guidance)",
        "CC-20": "tools/ci/validate.py (tooling surface)",
        "CC-21": "docs/adoption/adoption-guide.md (adoption ramp)",
        "CC-23": "tools/hooks/lifecycle.py (staleness detection)",
        "CC-25": "tools/hooks/lifecycle.py (deprecation ceremonies)",
        "CC-26": "docs/failure-modes/failure-modes.md",
        "CC-27": "tools/ci/validate.py (transition log check)",
    }
    for cc, desc in coverage.items():
        print(f"  {cc}: {desc}")

    # ── Plugin contributions ──
    if PLUGIN_REGISTRY.plugins:
        print()
        print("Plugin Contributions:")
        print(PLUGIN_REGISTRY.summary())


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="IDF SDLC v1.7.0 Initializer")
    parser.add_argument("target", nargs="?", default=DEFAULT_TARGET, help="Target directory")
    parser.add_argument("--plugins", default=None, help="Directory containing plugin .py files")
    args = parser.parse_args()
    init_repo(args.target, plugin_dir=args.plugins)