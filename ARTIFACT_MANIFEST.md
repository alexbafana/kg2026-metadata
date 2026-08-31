# Research artifact manifest

| Artifact | Repository realization | Public fixture status | Real Section VI status |
| --- | --- | --- | --- |
| T1 — trajectory representation | `evaluation/contracts/v1/schemas/trajectory.schema.json`, generated trajectory JSON/RDF | Executed | Pending |
| T2 — transformation and acceptance contract | `evaluation/contracts/v1/contract.json`, `acceptance-policy.json`, SHACL shapes | Executed | Pending |
| T3 — executable trace query | `evaluation/queries/statement-trace.rq` | Executed for 3 assertions | Pending |
| T4 — trace bundle | Assertion-centered RDF linking source, run, trajectory, model, contract, and decision | Executed for 3 assertions | Pending |
| Employment running case | Public author-created fixtures and recorded fixture predictions | Smoke test only | Blocked pending suitable sample and genuine classifier execution |
| Legacy comparator | 162 retained RDF artifacts at restricted commit `234fd2fdb94cf005345f87573b317598979617f9` | Aggregate audit published | Executed baseline |

The public fixture exercises the representation and validation machinery. It is
not a replacement for the real controlled experiment and must not be used as an
empirical employment-model result.
