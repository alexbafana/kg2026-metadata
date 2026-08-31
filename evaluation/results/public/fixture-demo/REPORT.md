# Synthetic fixture execution report

Executed 2026-08-31 with Python 3.9 and Apache Jena 6.2.0. These results use
three author-created examples and recorded fixture predictions. They establish
public exercisability of the evidence contract, not empirical NLP performance.

## Results

| Check | Result |
| --- | --- |
| Run-0 decisions | 2 accepted, 0 conditional, 1 rejected |
| Run-1 decisions | 2 accepted, 0 conditional, 1 rejected |
| Run-Var decisions | 1 accepted, 1 conditional, 1 rejected |
| Run-0 vs Run-1 core agreement | 3/3 |
| Run-0 vs Run-1 decision agreement | 3/3 |
| Run-0 vs Run-Var decision agreement | 2/3 |
| Explainable Run-Var differences | 1/1, caused by threshold 0.70 to 0.90 |
| Generated Turtle validated by RIOT | 9/9 |
| Generated Turtle conformed to trace SHACL shapes | 9/9 |
| Run-0 trace query | Source hash, run, ten ordered steps, model/version, contract, decision, and outcome recovered for 3/3 assertions |

The deliberately invalid job count was rejected. The loss case changed from
accepted to conditional under Run-Var because its confidence `0.84` fell below
the sole varied threshold `0.90`.
