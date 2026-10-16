# Product Requirements Document — OpenML Studio

## Vision

Framework-agnostic experiment tracker for ML practitioners. Track what matters: hyperparameters, metrics, artifacts, reproducibility metadata. Compare runs. Find best models.

## Users

- ML researchers running experiments
- Data scientists comparing model variants
- Teams sharing training results

## Core User Journey

1. Create project → experiment
2. Training script logs params/metrics via SDK
3. View run in web UI
4. Compare multiple runs
5. Download artifacts
6. Reproduce best run

## P0 Requirements (MVP)

### Tracking
- Projects contain experiments
- Experiments contain runs
- Runs log: params (dict), metrics (time series), status, timestamps
- Runs reference: artifacts (files), dataset metadata, source commit

### Python SDK
- `Client(api_url)`
- `start_run(project, experiment)` context manager
- `log_params(dict)`, `log_metric(name, value, step)`, `log_artifact(path)`
- Retry on transient failures

### API
- REST API: create/list/get projects, experiments, runs
- POST metrics (batched)
- Upload/download artifacts
- Compare runs (filter, sort by metric)

### Web UI
- Project list
- Experiment list with run count
- Run detail: params, metric charts, artifacts
- Run comparison table (side-by-side params + final metrics)

### Storage
- SQLite database
- Local filesystem for artifacts (`artifacts/{run_id}/`)

## P1 (Post-MVP)

- Dataset versioning
- Model registry
- Tags and search
- Multi-user auth
- PostgreSQL support

## P2 (Future)

- Framework integrations (PyTorch, TF callbacks)
- Remote artifact storage (S3)
- Parallel coordinates plot
- Hyperparameter optimization integration

## Non-Functional

- **Performance**: Handle 10k runs per experiment
- **Reliability**: SDK retries 3x with backoff
- **Security**: Validate artifact paths (no traversal)
- **Portability**: Works on Windows/Mac/Linux

## Out of Scope (MVP)

- Distributed training coordination
- GPU/cluster management
- Automated hyperparameter tuning
- Built-in visualization beyond line charts
- User authentication (single-user MVP)

## Success Metrics

- Time to first tracked run: <5 minutes
- Can reproduce best run from metadata: yes/no
- API uptime: >99%
