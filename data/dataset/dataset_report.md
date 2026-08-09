# Training dataset report

- examples admitted: 6841 (train 6187, val 654)
- per scanner: {'nessus': 383, 'openvas': 5459, 'qualys': 910, 'zap': 89}
- dropped (scalar field not contained): 0
- trimmed paragraphs (not rendered in the PDF): 457 {'detection_result': 34, 'description': 423}
- source reports: 136
- contamination guard: 16 stems, 5 eval-only hosts; denied examples: {'host': 199, 'stem': 1208}
- prompt snapshots: {'nessus': 'b5a00fdb132d', 'openvas': 'bb8cf53e3275', 'qualys': 'f47bdc916c6c', 'zap': '350e0357f4cc'}

## Field fill rate

- block_id: 6841 (100%)
- Name: 6841 (100%)
- severity: 6841 (100%)
- description: 6828 (100%)
- detection_result: 5817 (85%)
- cvss: 5525 (81%)
- detection_method: 5459 (80%)
- port: 5435 (79%)
- protocol: 5435 (79%)
- references: 5406 (79%)
- solution: 5038 (74%)
- insight: 4059 (59%)
- product_detection_result: 3099 (45%)
- impact: 2357 (34%)
- plugin: 1382 (20%)
- category: 910 (13%)
- plugin_details: 383 (6%)
- instances: 89 (1%)
