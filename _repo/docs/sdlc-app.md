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
node cli.js list --kind intent_aspirational
node cli.js add --kind intent_aspirational --json '{ "intent": { ... } }'
```

## Payloads
The API/UI/CLI accept JSON payloads. You can use the Web UI "Load Sample"
button to generate a valid payload for each kind.
