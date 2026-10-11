# Failure Taxonomy for Agent Memory Systems

Classification code and per-question annotations for "Not All Failures Are Equal: A Failure Taxonomy for Agent Memory Systems Across Benchmarks".

## Files
- `classify_failures.py` - Classification script
- `longmemeval_per_question.json` - LongMemEval-S 500Q per-question results
- `locomo_per_question.json` - LoCoMo 82Q paired per-question results
- `taxonomy_longmemeval.json` - Classification output for LongMemEval
- `taxonomy_locomo.json` - Classification output for LoCoMo

## Reproduce
```bash
python classify_failures.py --benchmark longmemeval --input longmemeval_per_question.json --output taxonomy_longmemeval.json
python classify_failures.py --benchmark locomo --input locomo_per_question.json --output taxonomy_locomo.json
```