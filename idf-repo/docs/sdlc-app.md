# SDLC App (Web + API + CLI)

This plugin scaffolds a minimal operational console for SDLC data:
intents, tensions, decisions, transitions, plugins, and manifest.

## Start API
```
cd apps/api
npm install
npm run dev
```

## Start Web
```
cd apps/web
npm install
npm run dev
```

## Use CLI
```
cd apps/cli
npm install
node cli.js help
```

### CLI Commands
| Command | Purpose |
|---------|---------|
| `kinds` | List all entity kinds |
| `list --kind KIND [--full]` | List records (add `--full` for payloads) |
| `get --kind KIND --id ID` | Get a single record |
| `add --kind KIND (--file\|--json\|--stdin)` | Add or update a record |
| `validate --kind KIND (--file\|--json\|--stdin)` | Validate without saving |
| `schema --kind KIND` | Introspect Zod schema for a kind |
| `delete --kind KIND --id ID` | Delete a record |
| `search --kind KIND --field F --value V` | Search records by field value |

### Output Format
By default all commands return JSON envelopes on stdout:
```json
{ "ok": true,  "data": ..., "meta": { "kind": "...", "count": 3 } }
{ "ok": false, "error": "...", "code": "NOT_FOUND", "details": [] }
```
Add `--text` for human-readable output.

### Agent Usage Examples
```bash
# Discover available entity kinds
node cli.js kinds

# Introspect schema to know required fields
node cli.js schema --kind intent_aspirational

# Validate a payload before writing (dry-run)
node cli.js validate --kind intent_aspirational --json '{"intent":{...}}'

# Add a record (from stdin for piping)
cat payload.json | node cli.js add --kind intent_aspirational --stdin

# List all records with full payloads
node cli.js list --kind intent_aspirational --full

# Search by field value
node cli.js search --kind intent_aspirational --field status --value proposed

# Delete a record
node cli.js delete --kind intent_aspirational --id my-intent-id
```

## Payloads
The API/UI/CLI accept JSON payloads. You can use the Web UI "Load Sample"
button to generate a valid payload for each kind.
