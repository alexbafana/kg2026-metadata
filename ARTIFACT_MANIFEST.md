# Research artifact manifest

| Artifact | Repository realization | Public fixture status | Real Section VI status |
| --- | --- | --- | --- |
| T1 — trajectory representation | `evaluation/contracts/v1/schemas/trajectory.schema.json`, generated trajectory JSON/RDF | Executed | Demonstrated for 12/12 controlled employment items |
| T2 — transformation and acceptance contract | `evaluation/contracts/v1/contract.json`, `acceptance-policy.json`, SHACL shapes | Executed | Demonstrated across 36 controlled run decisions |
| T3 — executable trace query | `evaluation/queries/statement-trace.rq` | Executed for 3 assertions | Demonstrated for 3/3 controlled walkthroughs |
| T4 — trace links | Assertion-centered RDF linking source, run, trajectory, model, contract, and decision | Executed for 3 assertions | Links are materialized for the controlled employment outputs; three walkthroughs are audited. A standalone trace-bundle index, digest, and ledger anchor are design elements, not demonstrated outputs. |
| Employment running case | Public author-created fixtures plus public 12-article ERR input sample and local-LLM pilot | Smoke test only | Source inputs reproducible; executed for 12 items; reference metrics provisional pending independent review |
| Legacy comparator | 162 retained RDF artifacts at restricted commit `234fd2fdb94cf005345f87573b317598979617f9` | Aggregate audit published | Executed baseline |

The public fixture exercises the representation and validation machinery and is
not an empirical employment-model result. The real pilot's exact 12 source PDFs,
manifest, and disclosure-screened aggregates are public; raw model I/O and
unreviewed item-level evidence remain controlled.
