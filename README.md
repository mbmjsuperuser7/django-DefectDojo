# prvis-ai — DefectDojo (stripped fork)

Vulnerability lifecycle management for the prvis platform.

## What was removed
- helm/ — Kubernetes charts
- tests/, unittests/ — test suites
- docs/, readme-docs/ — documentation
- Integration test configs and scripts
- Dev and HTTPS docker-compose overrides

## What was added
- prvis/docker-compose.yml — PostgreSQL backend (shared data layer), resource limits
- prvis/prvis-findings-webhook.py — Routes findings to TheHive, GRC, Mem0

## Key prvis integrations
- Receives findings from: Wazuh AI triage, FleetDM AI policy, OpenVAS, Semgrep, Trivy, Uniper EOL
- Routes high/critical to TheHive for case management
- Feeds all findings to prvis-grc for compliance mapping
- Triggers Mem0 context rebuild on new findings (customer context stays current)

## Resource requirements
- defectdojo: 1 GB RAM, 1 CPU
- celery worker: 512 MB RAM, 0.5 CPU
- Database: shared PostgreSQL on data layer
