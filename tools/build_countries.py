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
            d = {k: v for k, v in i.items() if not k.startswith("_")}
            d["id"] = i["_v"].rsplit("/", 1)[-1]
            uniq.append(d)
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

report = []

# ---------- Currency: Unicode CLDR (via babel) is the primary source ----------
from babel.numbers import get_territory_currencies, get_currency_name
today = datetime.date.today()
for c in countries.values():
    wd_codes = sorted({x.get("code") for x in c["currency"] if x.get("code")})
    try:
        codes = get_territory_currencies(c["iso"], start_date=today, tender=True)
    except Exception:
        codes = []
    if codes:
        c["currency"] = [{"code": k, "en": get_currency_name(k, locale="en"),
                          "bn": (lambda b: b if b != k else "")(get_currency_name(k, locale="bn"))} for k in codes]
    if sorted(codes) != wd_codes:
        report.append(f"currency  {c['iso']}  CLDR={codes}  Wikidata={wd_codes}")

# ---------- Leaders: show only when two Wikidata records agree ----------
office_ids = sorted({o["id"] for c in countries.values() for o in c["headOfStateTitle"] + c["headOfGovTitle"]})
holders = {}
for i in range(0, len(office_ids), 150):
    chunk = " ".join("wd:" + o for o in office_ids[i:i+150])
    for b in query(f"""SELECT ?office ?p ?start ?end ?en ?bn WHERE {{
        VALUES ?office {{ {chunk} }}
        ?p p:P39 ?st. ?st ps:P39 ?office; wikibase:rank ?r. FILTER(?r != wikibase:DeprecatedRank)
        OPTIONAL {{ ?st pq:P580 ?start }} OPTIONAL {{ ?st pq:P582 ?end }}
        OPTIONAL {{ ?p rdfs:label ?en FILTER(lang(?en)="en") }}
        OPTIONAL {{ ?p rdfs:label ?bn FILTER(lang(?bn)="bn") }} }}"""):
        holders.setdefault(val(b, "office").rsplit("/", 1)[-1], []).append({
            "id": val(b, "p").rsplit("/", 1)[-1], "start": val(b, "start")[:10], "end": val(b, "end")[:10],
            "en": val(b, "en"), "bn": val(b, "bn")})

def verify(c, role, title_key):
    cands = c[role]
    rows = [h for o in c[title_key] for h in holders.get(o["id"], [])]
    open_ = {}
    for h in rows:
        if not h["end"]:
            open_.setdefault(h["id"], h)
    cand_ids = [x["id"] for x in cands]
    starts = [x.get("start") or (open_.get(x["id"]) or {}).get("start", "") for x in cands]
    others_later = [h for h in rows if h["id"] not in cand_ids and h["start"] and starts and all(s and h["start"] > s for s in starts)]
    if cands:
        ok = all(i in open_ for i in cand_ids) and not others_later
        if ok:
            for x, s in zip(cands, starts):
                if s: x["start"] = s
            return cands, "ok"
        newest = sorted(others_later, key=lambda h: h["start"])[-1:] if others_later else []
        report.append(f"{role:<11} {c['iso']}  country item says {[x['en'] for x in cands]}"
                      f"  office records say {[h['en'] + ' (' + h['start'] + ')' for h in newest] or 'holder has an end date'}")
        return [], "check"
    if open_:
        latest = max((h["start"] for h in open_.values() if h["start"]), default="")
        newer_closed = [h for h in rows if h["start"] and h["start"] > latest]
        pick = [h for h in open_.values() if latest and h["start"] == latest]
        if pick and not newer_closed:
            return [{k: h[k] for k in ("id", "en", "bn", "start")} for h in pick], "office"
    if rows or c[title_key]:
        report.append(f"{role:<11} {c['iso']}  no current holder found")
    return [], "missing"

for c in countries.values():
    c["headOfState"], c["hosStatus"] = verify(c, "headOfState", "headOfStateTitle")
    c["headOfGov"], c["hogStatus"] = verify(c, "headOfGov", "headOfGovTitle")
    if not c["capital"]:
        report.append(f"capital     {c['iso']}  missing")

# ---------- Hand-verified corrections ----------
here = __import__("os").path.dirname(__file__)
ov = json.load(open(__import__("os").path.join(here, "overrides.json"), encoding="utf-8"))
for field in ("currency", "headOfState", "headOfGov"):
    for iso, entry in ov.get(field, {}).items():
        age = (today - datetime.date.fromisoformat(entry["checked"])).days
        if age > 180:
            report.append(f"override    {iso}  {field} EXPIRED (checked {entry['checked']}); re-verify or remove")
            continue
        for c in countries.values():
            if c["iso"] == iso:
                status_key = {"headOfState": "hosStatus", "headOfGov": "hogStatus"}.get(field)
                if status_key and c.get(status_key) == "ok":
                    report.append(f"override    {iso}  {field} not needed: Wikidata now agrees on {[x['en'] for x in c[field]]}")
                    continue
                c[field] = entry["items"]
                if field != "currency":
                    c["hosStatus" if field == "headOfState" else "hogStatus"] = "verified"
                c.setdefault("checked", {})[field] = {"source": entry["source"], "date": entry["checked"]}
                report.append(f"override    {iso}  {field} -> {[x['en'] for x in entry['items']]} ({entry['checked']})")

for c in countries.values():
    for k in ("headOfStateTitle", "headOfGovTitle", "capital", "parliament", "currency", "headOfState", "headOfGov"):
        for x in c[k]:
            x.pop("id", None)

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

with open("report.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(sorted(report)) + "\n")
print(len(result), "countries;", len(report), "report lines")
print("\n".join(sorted(report)))
