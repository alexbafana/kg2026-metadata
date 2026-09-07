# ERR employment sample v1

This directory publishes the complete 12-article input sample used for the
Section VI employment-stage evaluation. Eesti Rahvusringhääling (ERR) granted
the research team written permission to make these article captures available
through the project repository and archival research release. Copyright remains
with ERR and the respective rights holders; the files are included for
non-commercial research verification and are not relicensed as open content.

[`sample-manifest.json`](sample-manifest.json) records the selection stratum,
publisher, original URL, publication date, capture details, byte size, and
SHA-256 checksum for every PDF. The checksums identify the exact print-to-PDF
inputs used in the reported experiment.

## Articles

| Record | Article | Original ERR page |
| --- | --- | --- |
| `err-344130` | [Peetri külla kerkib sügiseks Selver](articles/err-344130.pdf) | [ERR](https://www.err.ee/344130/peetri-kulla-kerkib-sugiseks-selver) |
| `err-321150` | [Loode-Pärnu tööstusküla ootab EAS-ilt rahasüsti](articles/err-321150.pdf) | [ERR](https://www.err.ee/321150/loode-parnu-toostuskula-ootab-eas-ilt-rahasusti) |
| `err-1609430101` | [Hoolimata poliitilistest riskidest kerkib Dresdeni Taiwani firma kiibitehas](articles/err-1609430101.pdf) | [ERR](https://www.err.ee/1609430101/hoolimata-poliitilistest-riskidest-kerkib-dresdeni-taiwani-firma-kiibitehas) |
| `err-1608098905` | [Narva tahab eakate ja puuetega inimeste olukorra parandamiseks rajada kolm sotsiaalobjekti](articles/err-1608098905.pdf) | [ERR](https://www.err.ee/1608098905/narva-tahab-eakate-ja-puuetega-inimeste-olukorra-parandamiseks-rajada-kolm-sotsiaalobjekti) |
| `err-1091798` | [Eesti pärimusmuusika keskus koondab 10 töötajat](articles/err-1091798.pdf) | [ERR](https://kultuur.err.ee/1091798/eesti-parimusmuusika-keskus-koondab-10-tootajat) |
| `err-1609005398` | [Kohtla-Järve linnavalitsuses kaob paarkümmend töökohta](articles/err-1609005398.pdf) | [ERR](https://www.err.ee/1609005398/kohtla-jarve-linnavalitsuses-kaob-paarkummend-tookohta) |
| `err-1011390` | [M.W. Wool koondab 125 töötajat](articles/err-1011390.pdf) | [ERR](https://www.err.ee/1011390/m-w-wool-koondab-125-tootajat) |
| `err-875707` | [Nordica sulgeb kolm lennuliini ja koondab kümmekond töötajat](articles/err-875707.pdf) | [ERR](https://www.err.ee/875707/nordica-sulgeb-kolm-lennuliini-ja-koondab-kummekond-tootajat) |
| `err-1609000901` | [Tervishoiutöötajate arv kasvas, perearste ja õdesid aga ikka napib](articles/err-1609000901.pdf) | [ERR](https://www.err.ee/1609000901/tervishoiutootajate-arv-kasvas-perearste-ja-odesid-aga-ikka-napib) |
| `err-1609541905` | [Loe täismahus: kliimaminister tutvustas valitsusele kliimaseadust](articles/err-1609541905.pdf) | [ERR](https://www.err.ee/1609541905/loe-taismahus-kliimaminister-tutvustas-valitsusele-kliimaseadust) |
| `err-1609504534` | [Majandusministeerium ei koonda tuleval aastal töökohti ega kärbi palku](articles/err-1609504534.pdf) | [ERR](https://www.err.ee/1609504534/majandusministeerium-ei-koonda-tuleval-aastal-tookohti-ega-karbi-palku) |
| `err-1609418458` | [Lottemaa kasum kasvas, kuid käive ja piletitulu langesid](articles/err-1609418458.pdf) | [ERR](https://www.err.ee/1609418458/lottemaa-kasum-kasvas-kuid-kaive-ja-piletitulu-langesid) |

## Recreate the normalized evaluation input

From the repository root, run:

```bash
python3 evaluation/stages/build_controlled_dataset.py \
  --manifest evaluation/data/employment-sample-v1/sample-manifest.json \
  --pdf-dir evaluation/data/employment-sample-v1/articles \
  --output /tmp/employment-sample-v1/articles.csv \
  --extraction-manifest /tmp/employment-sample-v1/extraction-manifest.json
```

The original extraction used `pdftotext` 25.07.0. The generated dataset should
have SHA-256 checksum
`dd4251ab0c5794ee942c98e21c02232bc5b414d7fce5d6d3c74ae581f815e9cf`.
