#!/usr/bin/env python3
"""
Download disease images from Wikimedia Commons for the Diseases page.
Saves images to static/images/diseases/<slug>.jpg
"""

import os
import sys
import json
import time
import requests

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "static", "images", "diseases")
os.makedirs(OUTPUT_DIR, exist_ok=True)

WIKI_API = "https://commons.wikimedia.org/w/api.php"
HEADERS  = {"User-Agent": "ChilliCareEducationalApp/1.0 (plant-disease reference)"}

# ---------------------------------------------------------------------------
# Disease slug  →  prioritised list of Wikimedia Commons filenames to try.
# Falls back to API search if none succeed.
# ---------------------------------------------------------------------------
KNOWN_FILES = {
    # ── Fungal ──
    "anthracnose":          ["Colletotrichum_capsici.jpg",
                             "Chilli_anthracnose.jpg",
                             "Anthracnose_papaya.jpg"],
    "powdery-mildew":       ["5573619-PPT-powdery_mildew_(Leveillula_taurica).jpg",
                             "Powdery_mildew_on_Capsicum.jpg",
                             "Powdery_mildew2.jpg"],
    "cercospora-leaf-spot": ["Cercospora_capsici.jpg",
                             "Cercospora_leaf_spot.jpg",
                             "Cercospora_leaf_spot_chilli.jpg"],
    "phytophthora-blight":  ["P._capsici_blight_on_sweet_pepper.jpg",
                             "Phytophthora_capsici.jpg",
                             "Phytophthora_blight_pepper.jpg"],
    "fusarium-wilt":        ["Fusarium_wilt_tomato.jpg",
                             "Fusarium_oxysporum.jpg",
                             "Fusarium_wilt.jpg"],
    "damping-off":          ["Damping-off.jpg",
                             "Damping_off_seedlings.jpg",
                             "Pythium_damping_off.jpg"],
    "alternaria-leaf-spot": ["Alternaria_alternata.jpg",
                             "Alternaria_leaf_blight.jpg",
                             "Alternaria_solani.jpg"],
    "stem-rot":             ["Sclerotium_rolfsii.jpg",
                             "Southern_blight.jpg",
                             "White_mold_pepper.jpg"],
    "grey-mould":           ["Botrytis_riesling.jpg",
                             "Botrytis_cinerea_on_tomato.jpg",
                             "Botrytis_blight.jpg"],

    # ── Bacterial ──
    "bacterial-wilt":       ["Bacterial_wilt.jpg",
                             "Ralstonia_solanacearum.jpg",
                             "Bacterial_wilt_tomato.jpg"],
    "bacterial-leaf-spot":  ["Xanthomonas_campestris_pv_vesicatoria.jpg",
                             "Bacterial_leaf_spot_pepper.jpg",
                             "Xanthomonas_leaf_spot.jpg"],
    "bacterial-soft-rot":   ["Erwinia_soft_rot.jpg",
                             "Pectobacterium_carotovorum.jpg",
                             "Soft_rot_bacterial.jpg"],

    # ── Viral ──
    "leaf-curl-virus":      ["Leaf_curl_virus_chilli.jpg",
                             "Chilli_leaf_curl.jpg",
                             "Leaf_curl_begomovirus.jpg"],
    "cucumber-mosaic-virus":["Cucumber_mosaic_virus_on_capsicum.jpg",
                             "CMV_symptoms.jpg",
                             "Cucumber_mosaic_virus.jpg"],
    "pepper-mild-mottle":   ["Pepper_mild_mottle_virus.jpg",
                             "PMMoV_symptoms.jpg",
                             "Tobamovirus_pepper.jpg"],
    "tobacco-mosaic-virus": ["Tobacco_mosaic_virus_on_tobacco.jpg",
                             "TMV_symptoms.jpg",
                             "Tobacco_mosaic_virus.jpg"],
    "chilli-veinal-mottle": ["Chilli_veinal_mottle_virus.jpg",
                             "ChiVMV_symptoms.jpg",
                             "Potyvirus_leaf.jpg"],
    "gbnv":                 ["Groundnut_bud_necrosis_virus.jpg",
                             "GBNV_symptoms.jpg",
                             "Tospovirus_symptoms.jpg"],
    "tswv":                 ["Tomato_spotted_wilt_virus.jpg",
                             "TSWV_pepper.jpg",
                             "Spotted_wilt_tomato.jpg"],

    # ── Pests ──
    "whitefly":             ["Silverleaf_Whitefly_(Bemisia_tabaci)_adult.jpg",
                             "Bemisia_argentifolii_5194038.jpg",
                             "Bemisia_tabaci.jpg"],
    "chilli-yellowish":     ["Aphis_gossypii.jpg",
                             "Aphid_colony_pepper.jpg",
                             "Myzus_persicae.jpg"],
    "chilli-thrips":        ["Scirtothrips_dorsalis.jpg",
                             "Thrips_on_plant.jpg",
                             "Chilli_thrips.jpg"],
    "aphids":               ["Aphis_gossypii_(Cotton_aphids).jpg",
                             "Aphis_gossypii.jpg",
                             "Cotton_aphid.jpg"],
    "fruit-borer":          ["Helicoverpa_armigera_larva.jpg",
                             "Helicoverpa_armigera.jpg",
                             "Cotton_bollworm_larva.jpg"],
    "broad-mite":           ["Polyphagotarsonemus_latus.jpg",
                             "Broad_mite.jpg",
                             "Tarsonemidae.jpg"],
    "spider-mites":         ["Tetranychus_urticae_with_silk.jpg",
                             "Spider_mite_infestation.jpg",
                             "Tetranychus_urticae.jpg"],
    "mealybug":             ["Phenacoccus_solenopsis.jpg",
                             "Mealybug_cotton.jpg",
                             "Planococcus_citri.jpg"],

    # ── Physiological ──
    "blossom-end-rot":      ["Blossom_end_rot2.jpg",
                             "Blossom_end_rot_pepper.jpg",
                             "Blossom_end_rot.jpg"],
    "sunscald":             ["Sunscald_pepper.jpg",
                             "Sun_scald_tomato.jpg",
                             "Sunscald_tomato.jpg"],
    "nitrogen-deficiency":  ["Nitrogen_deficiency_pepper.jpg",
                             "Nitrogen_deficiency_plant.jpg",
                             "N_deficiency.jpg"],
    "tip-burn":             ["Tipburn.jpg",
                             "Calcium_deficiency_tip_burn.jpg",
                             "Tip_burn_leaves.jpg"],
}

# Search queries used as a last resort if all known filenames fail
SEARCH_QUERIES = {
    "anthracnose":          "Colletotrichum capsici anthracnose chilli fruit",
    "powdery-mildew":       "Leveillula taurica powdery mildew capsicum",
    "cercospora-leaf-spot": "Cercospora capsici leaf spot",
    "phytophthora-blight":  "Phytophthora capsici blight pepper",
    "fusarium-wilt":        "Fusarium oxysporum wilt pepper",
    "damping-off":          "damping off seedlings Pythium",
    "alternaria-leaf-spot": "Alternaria leaf spot pepper blight",
    "stem-rot":             "Sclerotium rolfsii southern blight",
    "grey-mould":           "Botrytis cinerea grey mould",
    "bacterial-wilt":       "Ralstonia solanacearum bacterial wilt",
    "bacterial-leaf-spot":  "Xanthomonas bacterial leaf spot pepper",
    "bacterial-soft-rot":   "Pectobacterium soft rot vegetable",
    "leaf-curl-virus":      "chilli leaf curl begomovirus symptoms",
    "cucumber-mosaic-virus":"cucumber mosaic virus CMV capsicum symptoms",
    "pepper-mild-mottle":   "pepper mild mottle tobamovirus symptoms",
    "tobacco-mosaic-virus": "tobacco mosaic virus TMV pepper",
    "chilli-veinal-mottle": "potyvirus chilli mosaic symptoms",
    "gbnv":                 "groundnut bud necrosis tospovirus thrips",
    "tswv":                 "tomato spotted wilt virus TSWV pepper",
    "whitefly":             "Bemisia tabaci whitefly pest adult",
    "chilli-yellowish":     "Aphis gossypii aphid cotton pepper",
    "chilli-thrips":        "Scirtothrips dorsalis chilli thrips",
    "aphids":               "Aphis gossypii aphid infestation",
    "fruit-borer":          "Helicoverpa armigera bollworm larva",
    "broad-mite":           "Polyphagotarsonemus latus broad mite",
    "spider-mites":         "Tetranychus urticae spider mite webbing",
    "mealybug":             "Phenacoccus solenopsis mealybug cotton",
    "blossom-end-rot":      "blossom end rot pepper calcium",
    "sunscald":             "sunscald pepper fruit sun damage",
    "nitrogen-deficiency":  "nitrogen deficiency plant yellowing chlorosis",
    "tip-burn":             "tip burn calcium deficiency lettuce pepper",
}


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def get_image_url(filename: str) -> str | None:
    """Return a thumbnail URL (≤600 px wide) for a Commons filename."""
    params = {
        "action":    "query",
        "titles":    f"File:{filename}",
        "prop":      "imageinfo",
        "iiprop":    "url|size|mime",
        "iiurlwidth": 600,
        "format":    "json",
    }
    try:
        r = requests.get(WIKI_API, params=params, headers=HEADERS, timeout=12)
        r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", {})
        for page in pages.values():
            if page.get("ns") == -1:        # page not found
                return None
            info = page.get("imageinfo", [])
            if info:
                mime = info[0].get("mime", "")
                if "image" not in mime:
                    return None
                return info[0].get("thumburl") or info[0].get("url")
    except Exception as e:
        print(f"    [warn] imageinfo error for '{filename}': {e}")
    return None


def search_commons(query: str) -> str | None:
    """Search Commons for a filename matching query; return best filename."""
    params = {
        "action":     "query",
        "list":       "search",
        "srsearch":   query,
        "srnamespace": "6",
        "srlimit":    5,
        "format":     "json",
    }
    try:
        r = requests.get(WIKI_API, params=params, headers=HEADERS, timeout=12)
        r.raise_for_status()
        results = r.json().get("query", {}).get("search", [])
        for result in results:
            title    = result["title"]
            filename = title.replace("File:", "")
            if any(filename.lower().endswith(ext) for ext in (".jpg", ".jpeg", ".png")):
                return filename
    except Exception as e:
        print(f"    [warn] search error for '{query}': {e}")
    return None


def download_image(url: str, out_path: str) -> bool:
    """Download image at url to out_path; return True on success."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=20, stream=True)
        r.raise_for_status()
        with open(out_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        size = os.path.getsize(out_path)
        if size < 1024:          # suspiciously small — probably an error page
            os.remove(out_path)
            return False
        return True
    except Exception as e:
        print(f"    [warn] download error from '{url}': {e}")
        if os.path.exists(out_path):
            os.remove(out_path)
        return False


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

results: dict[str, str | None] = {}
total   = len(KNOWN_FILES)

for i, (slug, filenames) in enumerate(KNOWN_FILES.items(), 1):
    out_path = os.path.join(OUTPUT_DIR, f"{slug}.jpg")

    if os.path.exists(out_path) and os.path.getsize(out_path) > 1024:
        print(f"[{i:02}/{total}] SKIP  {slug} (cached)")
        results[slug] = f"/static/images/diseases/{slug}.jpg"
        continue

    print(f"[{i:02}/{total}] {slug}")
    success = False

    # 1. Try each known filename
    for fname in filenames:
        url = get_image_url(fname)
        if url:
            print(f"         trying {fname} ...")
            if download_image(url, out_path):
                print(f"         OK via known file")
                results[slug] = f"/static/images/diseases/{slug}.jpg"
                success = True
                break
        time.sleep(0.25)

    # 2. Fall back to search
    if not success and slug in SEARCH_QUERIES:
        print(f"         falling back to search: {SEARCH_QUERIES[slug]}")
        fname = search_commons(SEARCH_QUERIES[slug])
        if fname:
            url = get_image_url(fname)
            if url:
                print(f"         trying search result: {fname}")
                if download_image(url, out_path):
                    print(f"         OK via search")
                    results[slug] = f"/static/images/diseases/{slug}.jpg"
                    success = True

    if not success:
        print(f"         FAILED — will use category icon fallback")
        results[slug] = None

    time.sleep(0.4)   # polite rate-limiting

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
ok_count   = sum(1 for v in results.values() if v)
fail_count = total - ok_count

print(f"\n{'='*55}")
print(f"Downloaded: {ok_count}/{total}  |  Fallback (icon): {fail_count}/{total}")
print(f"{'='*55}")

# Write results for reference
manifest_path = os.path.join(OUTPUT_DIR, "manifest.json")
with open(manifest_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nManifest saved to: {manifest_path}")
