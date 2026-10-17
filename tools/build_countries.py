"""Fetch current country facts from Wikidata and write countries.json for the app.

Run at build time on GitHub Actions (it needs internet). For each sovereign state:
name, capital, currency (+ISO code), head of state, head of government (with the
office titles), legislature and the ISO code (used to draw the flag emoji).
Only statements without an end date are kept; preferred-rank values win.
English and Bangla labels are both fetched.
"""
import datetime, json, sys, time, urllib.parse, urllib.request

EP = "https://query.wikidata.org/sparql"
UA = "NuzaimLearnsBuild/1.0 (https://github.com/asifircu5-spec/claude)"
BASE = """
  ?c wdt:P31 wd:Q3624078; wdt:P297 ?iso.
  FILTER NOT EXISTS { ?c wdt:P31 wd:Q3024240 }
  FILTER NOT EXISTS { ?c wdt:P576 ?dissolved }
"""

def query(sparql):
    data = urllib.parse.urlencode({"query": sparql, "format": "json"}).encode()
    req = urllib.request.Request(EP, data=data, headers={"User-Agent": UA, "Accept": "application/sparql-results+json"})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.load(r)["results"]["bindings"]
        except Exception as e:
            print("retry", attempt, e, file=sys.stderr)
            time.sleep(10 * (attempt + 1))
    raise SystemExit("Wikidata query failed")

def val(b, k):
    return b[k]["value"] if k in b else ""

def labels(b):
    return {"en": val(b, "en"), "bn": val(b, "bn")}

countries = {}
for b in query("SELECT ?c ?iso ?en ?bn WHERE {" + BASE + """
  OPTIONAL { ?c rdfs:label ?en FILTER(lang(?en)="en") }
  OPTIONAL { ?c rdfs:label ?bn FILTER(lang(?bn)="bn") } }"""):
    qid = val(b, "c").rsplit("/", 1)[-1]
    countries.setdefault(qid, {"qid": qid, "iso": val(b, "iso").upper(), "name": labels(b)})

def prop(pid, extra_vars="", extra=""):
    rows = query(f"""SELECT ?c ?v ?en ?bn ?rank {extra_vars} WHERE {{ {BASE}
      ?c p:{pid} ?st. ?st ps:{pid} ?v; wikibase:rank ?rank.
      FILTER(?rank != wikibase:DeprecatedRank)
      FILTER NOT EXISTS {{ ?st pq:P582 ?end }}
      {extra}
      OPTIONAL {{ ?v rdfs:label ?en FILTER(lang(?en)="en") }}
      OPTIONAL {{ ?v rdfs:label ?bn FILTER(lang(?bn)="bn") }} }}""")
    out = {}
    for b in rows:
        qid = val(b, "c").rsplit("/", 1)[-1]
        item = labels(b)
        item["_v"] = val(b, "v")
        item["_pref"] = val(b, "rank").endswith("PreferredRank")
        for k in ("code", "start"):
            if val(b, k):
                item[k] = val(b, k)[:10] if k == "start" else val(b, k)
        out.setdefault(qid, []).append(item)
    # keep preferred values if there are any; drop duplicates
    for qid, items in out.items():
        pref = [i for i in items if i["_pref"]]
        items = pref or items
        seen, uniq = set(), []
        for i in items:
            if i["_v"] in seen or not i["en"]:
                continue
            seen.add(i["_v"])
            uniq.append({k: v for k, v in i.items() if not k.startswith("_")})
        out[qid] = uniq
    return out

fields = {
    "capital": prop("P36"),
    "currency": prop("P38", "?code", "OPTIONAL { ?v wdt:P498 ?code }"),
    "headOfState": prop("P35", "?start", "OPTIONAL { ?st pq:P580 ?start }"),
    "headOfGov": prop("P6", "?start", "OPTIONAL { ?st pq:P580 ?start }"),
    "headOfStateTitle": prop("P1906"),
    "headOfGovTitle": prop("P1313"),
    "parliament": prop("P194"),
}
for qid, c in countries.items():
    for f, data in fields.items():
        c[f] = data.get(qid, [])

result = sorted(countries.values(), key=lambda c: c["name"]["en"] or c["iso"])
result = [c for c in result if len(c["iso"]) == 2 and c["name"]["en"]]
out = {
    "source": "Wikidata (wikidata.org), CC0",
    "fetched": datetime.date.today().isoformat(),
    "countries": result,
}
if len(result) < 150:
    raise SystemExit(f"Only {len(result)} countries found; refusing to ship incomplete data")
with open(sys.argv[1] if len(sys.argv) > 1 else "countries.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"))

bd = next(c for c in result if c["iso"] == "BD")
print(len(result), "countries")
print(json.dumps(bd, ensure_ascii=False, indent=1))
