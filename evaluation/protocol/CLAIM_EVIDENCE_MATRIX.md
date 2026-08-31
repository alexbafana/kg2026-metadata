# Section VI claim-to-evidence matrix

This matrix is normative for the evaluation package. A result that does not
answer one of these claims is supporting evidence, not the main evaluation.

| ID | Paper claim | Required observation | Required retained evidence | Minimum report measure |
| --- | --- | --- | --- | --- |
| C1 | Processing sequences, intermediates, and algorithmic choices are explicit and PROV-compatible | A run records ordered steps, used/generated artifacts, agents/models, configurations, and contract | Run manifest, provenance JSON/RDF, trajectory JSON/RDF, contract version, RIOT result | Required-field coverage and query success |
| C2 | Trajectory metadata supports repeatability | Equivalent runs preserve core semantic output and acceptance decisions | Complete isolated Run-0 and Run-1 packages with frozen inputs/configuration | Core RDF agreement and decision agreement |
| C3 | Algorithmic or policy variation is explainable | One changed factor causes only attributable differences and is recorded in the trajectory | Complete Run-Var package and machine-readable comparison | Explainable-difference count/rate |
| C4 | The transformation contract systematically governs publication | Every candidate receives a rule-based accepted/conditional/rejected decision with evidence | Versioned schemas, policy, per-item validation reports, decision summaries | Outcome distribution and decision agreement |
| C5 | Individual RDF statements are traceable | A query traverses statement → run → trajectory/steps → model/config → source/intermediates → contract → decision | Trace RDF, query output, and three walkthroughs | Trace-link completeness and successful walkthroughs |
| C6 | The employment-event running case is functional | Job-gain/loss/no-event outputs, counts, and evidence are produced and checked against reviewed references | Frozen sample, reference labels, predictions, validation reports | Event/count agreement on the inspected sample; EMTAK remains outside this pilot |
| C7 | Traceability is improved over the legacy graph | Enhanced outputs expose inspectable links absent from the legacy baseline | Same competency-query results for legacy and enhanced RDF | Before/after trace-query coverage |

## Claim boundary

The experiment does not claim state-of-the-art NLP accuracy, legal permission
to redistribute source texts, scalability, or independent replication. Such
claims require separate evidence and must not be inferred from this package.
