/* ============================================
   Diseases Page – diseases.js
   ============================================ */

/* ------------------------------------------------------------------
   Sri Lanka Chilli Disease Data — comprehensive reference (31 entries)
   ------------------------------------------------------------------ */
const SL_DISEASE_CATEGORIES = [
    {
        id: 'fungal',
        label: 'Fungal',
        icon: 'fas fa-circle-nodes',
        diseases: [
            {
                name: 'Anthracnose (Fruit Rot)',
                pathogen: 'Colletotrichum capsici / C. gloeosporioides',
                severity: 'high',
                inModel: true,
                symptoms: 'Sunken, circular, dark lesions on ripening fruits; orange-pink spore masses in humid conditions; premature fruit drop; severe post-harvest losses.',
                causes: [
                    'Fungal spores spread via rain splash, wind, and infected plant debris',
                    'Warm humid weather (25–30°C) with rainfall accelerates spread',
                    'Infected seeds and contaminated soil serve as primary inoculum sources',
                    'Insect-caused or mechanical fruit injuries provide fungal entry points',
                    'Dense canopy restricting air circulation'
                ],
                prevention: 'Use certified disease-free seeds; rotate crops with non-solanaceous plants (3-year rotation); apply Mancozeb or Copper Oxychloride fungicide at 10-day intervals; improve drainage; harvest fruits promptly; remove and destroy infected plant debris.',
            },
            {
                name: 'Powdery Mildew',
                pathogen: 'Leveillula taurica',
                severity: 'medium',
                inModel: false,
                symptoms: 'White powdery growth on undersides of leaves; upper leaf surface shows yellow spots; severe infection causes premature leaf fall and stunted growth.',
                causes: [
                    'Warm, dry conditions with low humidity (opposite of most fungi)',
                    'High nitrogen fertilization causing lush, susceptible growth',
                    'Overcrowded planting reduces air circulation and promotes spread',
                    'Wind dispersal of air-borne conidia between plants',
                    'Cool nights followed by warm dry days'
                ],
                prevention: 'Apply sulfur-based fungicides or Hexaconazole at first sign; maintain proper plant spacing; avoid excess nitrogen; use resistant varieties where available.',
            },
            {
                name: 'Cercospora Leaf Spot',
                pathogen: 'Cercospora capsici',
                severity: 'medium',
                inModel: false,
                symptoms: 'Circular spots (3–10 mm) with white-grey centres and dark brown borders on leaves; spots coalesce under severe infection; heavily infected leaves turn yellow and drop.',
                causes: [
                    'Warm temperatures (25–32°C) with high humidity above 80%',
                    'Fungal spores survive in infected crop debris and spread by wind and rain',
                    'Dense planting and poor field sanitation increase risk',
                    'Overhead irrigation wets foliage and promotes spore germination',
                    'Continuous cropping on same land without rotation'
                ],
                prevention: 'Remove and burn infected plant debris; use drip irrigation to keep foliage dry; apply Mancozeb or Copper fungicide preventively; rotate crops with non-solanaceous plants for 2 seasons.',
            },
            {
                name: 'Phytophthora Blight',
                pathogen: 'Phytophthora capsici',
                severity: 'high',
                inModel: false,
                symptoms: 'Water-soaked stem lesions at soil level causing sudden wilting; dark greasy lesions on fruits; root rot; white cottony mycelial growth in humid conditions.',
                causes: [
                    'Soil-borne pathogen thrives in waterlogged, poorly drained soils',
                    'Heavy rainfall and excessive irrigation spread motile zoospores rapidly',
                    'Monoculture and continuous chilli cultivation depletes soil suppressiveness',
                    'Movement of contaminated soil, tools, and irrigation water spreads inoculum',
                    'Warm humid conditions (25–30°C)'
                ],
                prevention: 'Ensure excellent field drainage; use raised beds; avoid waterlogging; apply Metalaxyl or Phosphonate fungicides; rotate crops for at least 3 years; use Phytophthora-tolerant rootstocks.',
            },
            {
                name: 'Fusarium Wilt',
                pathogen: 'Fusarium oxysporum f.sp. capsici',
                severity: 'high',
                inModel: false,
                symptoms: 'Yellowing and wilting starting from lower leaves; brown vascular discolouration visible in stem cross-section; complete plant collapse in severe cases.',
                causes: [
                    'Soil-borne fungus persists in soil for many years even without host plants',
                    'Enters plant through root wounds caused by nematodes or cultivation tools',
                    'Warm soil temperatures (28–32°C) and dry conditions favour the pathogen',
                    'Infected transplants and contaminated irrigation water spread the disease',
                    'Continuous chilli cultivation in same field increases soil inoculum'
                ],
                prevention: 'Solarise soil before planting; use Trichoderma spp. biocontrol; plant resistant varieties; remove and destroy infected plants with surrounding soil; avoid replanting chilli in infected fields for 3–4 years.',
            },
            {
                name: 'Damping Off',
                pathogen: 'Pythium aphanidermatum / Rhizoctonia solani',
                severity: 'high',
                inModel: false,
                symptoms: 'Pre-emergence: seed rots before germination. Post-emergence: stem turns brown and water-soaked at base; seedlings suddenly collapse and die at soil level.',
                causes: [
                    'Excessive moisture in seedling beds creates ideal conditions for fungi',
                    'Contaminated potting media or unsterilized seedling trays',
                    'High seedling density with poor air circulation promotes spread',
                    'Cool, cloudy weather after watering slows seedling drying',
                    'Reusing infected soil or trays from previous seasons'
                ],
                prevention: 'Use sterilised seedling media; treat seeds with Thiram or Captan before sowing; avoid overwatering; maintain good nursery ventilation; apply Trichoderma-based biocontrol to nursery soil.',
            },
            {
                name: 'Alternaria Leaf Spot',
                pathogen: 'Alternaria alternata / A. solani',
                severity: 'medium',
                inModel: false,
                symptoms: 'Dark brown to black lesions with concentric rings and yellow halo on leaves; spots may coalesce causing large blighted areas; black lesions on fruits near calyx; premature defoliation.',
                causes: [
                    'Airborne spores spread rapidly in warm (25–30°C), humid weather',
                    'Infected plant debris in soil serves as primary inoculum source',
                    'Physiologically stressed plants from drought or nutrient deficiency are more susceptible',
                    'Overhead irrigation and rain splash disperse spores between plants',
                    'Infected seeds introduce disease to new fields'
                ],
                prevention: 'Destroy crop debris after harvest; treat seeds with hot water (50°C for 25 min); apply Mancozeb or Chlorothalonil at 7-day intervals during wet weather; avoid wetting foliage; ensure adequate plant nutrition.',
            },
            {
                name: 'Stem Rot (Southern Blight)',
                pathogen: 'Sclerotium rolfsii',
                severity: 'medium',
                inModel: false,
                symptoms: 'White mycelial growth and small round brownish sclerotia at base of stem; stem rots at soil level causing rapid wilting and plant death.',
                causes: [
                    'Soil-borne pathogen survives as sclerotia for many years in soil',
                    'Warm (28–35°C), moist soil conditions trigger sclerotia germination',
                    'Burying infected debris during tillage spreads inoculum through field',
                    'Continuous chilli cultivation without crop rotation increases soil inoculum',
                    'High organic matter with slow decomposition creates favourable microclimate'
                ],
                prevention: 'Deep plough to bury debris; apply PCNB or thiophanate-methyl as soil drench; solarise soil during dry season; incorporate Trichoderma harzianum into soil; rotate with cereals or legumes.',
            },
            {
                name: 'Grey Mould (Botrytis Blight)',
                pathogen: 'Botrytis cinerea',
                severity: 'low',
                inModel: false,
                symptoms: 'Grey fuzzy fungal growth on flowers, fruits, and stems; water-soaked spots that collapse rapidly; blossom blight; stem cankers in cool, humid conditions.',
                causes: [
                    'Favoured by cool (15–20°C), humid conditions with poor air movement',
                    'Dead flowers and decaying plant tissue serve as entry points',
                    'Overhead irrigation and dense canopy create high-humidity microclimate',
                    'Wounds from insects, pruning, or hail facilitate fungal entry',
                    'High relative humidity above 90% for extended periods'
                ],
                prevention: 'Improve air circulation with correct plant spacing; remove dead flowers and plant material promptly; apply iprodione or fenhexamid fungicides when conditions are favourable; avoid overhead irrigation.',
            },
        ]
    },
    {
        id: 'bacterial',
        label: 'Bacterial',
        icon: 'fas fa-bacteria',
        diseases: [
            {
                name: 'Bacterial Wilt',
                pathogen: 'Ralstonia solanacearum',
                severity: 'high',
                inModel: false,
                symptoms: 'Sudden wilting of entire plant without yellowing; internal brown discolouration of stem vascular tissue; milky bacterial streaming from cut stem in water.',
                causes: [
                    'Infested soil — bacteria survive for years',
                    'Contaminated irrigation water or flood water',
                    'Soil temperature above 25°C favouring bacteria',
                    'Wounding by cultivation tools or insects',
                    'Movement of infested soil on tools and footwear'
                ],
                prevention: 'Use resistant or tolerant varieties; long crop rotation (3–4 years with non-hosts); sterilise tools; improve drainage; use clean irrigation water; soil solarisation before planting.',
            },
            {
                name: 'Bacterial Leaf Spot',
                pathogen: 'Xanthomonas campestris pv. vesicatoria',
                severity: 'medium',
                inModel: false,
                symptoms: 'Small water-soaked lesions turning brown with yellow halo on leaves; raised, scabby lesions on fruits; defoliation in severe cases.',
                causes: [
                    'Infected seed is primary source',
                    'Rain and wind splash spread bacteria',
                    'High temperatures (25–30°C) with frequent rain',
                    'Injuries from insects or hail create entry points',
                    'Dense plantings restrict airflow'
                ],
                prevention: 'Use certified seed; seed treatment with Copper hydroxide; apply Copper-based bactericides; avoid overhead irrigation; remove infected plant material.',
            },
            {
                name: 'Bacterial Soft Rot',
                pathogen: 'Pectobacterium carotovorum',
                severity: 'medium',
                inModel: false,
                symptoms: 'Water-soaked, soft, mushy lesions on fruits and stems; foul odour from rotting tissue; infected areas collapse quickly; particularly severe in post-harvest storage.',
                causes: [
                    'Wounds from insects, tools or harvesting',
                    'High humidity and poor ventilation in storage',
                    'Contaminated water sources',
                    'High temperature during harvest and handling',
                    'Delayed harvest of over-ripe fruits'
                ],
                prevention: 'Handle fruits carefully to prevent injury; harvest at right maturity; improve post-harvest storage ventilation; avoid waterlogging; apply Copper bactericides as preventive.',
            },
        ]
    },
    {
        id: 'viral',
        label: 'Viral',
        icon: 'fas fa-virus',
        diseases: [
            {
                name: 'Chilli Leaf Curl Virus',
                pathogen: 'Begomovirus (ChiLCV / CLCuV)',
                severity: 'high',
                inModel: true,
                symptoms: 'Severe upward or downward curling and crinkling of leaves; leaf thickening and vein distortion; shortened internodes causing bushy stunted plants; flower drop; significantly reduced yield.',
                causes: [
                    'Transmitted by whitefly (Bemisia tabaci) in a persistent circulative manner',
                    'High whitefly populations in warm dry weather',
                    'Infected transplants from unscreened nurseries introduce virus to new fields',
                    'Proximity to other infected solanaceous crops',
                    'No cure once plant is infected — prevention is the only strategy'
                ],
                prevention: 'Use virus-free transplants; control whiteflies with Imidacloprid or yellow sticky traps; use UV-reflective silver mulch to repel whiteflies; remove and destroy infected plants immediately; plant border crops to reduce whitefly migration.',
            },
            {
                name: 'Cucumber Mosaic Virus (CMV)',
                pathogen: 'Cucumovirus CMV',
                severity: 'high',
                inModel: false,
                symptoms: 'Mosaic pattern of light and dark green patches on leaves; leaf distortion and malformation; stunting; reduced and deformed fruit set.',
                causes: [
                    'Transmitted non-persistently by more than 80 aphid species',
                    'Spreads very rapidly — aphids acquire and transmit the virus in seconds',
                    'Wide host range including many weeds serving as virus reservoirs',
                    'Mechanical transmission during field operations',
                    'Infected transplanting tools and contaminated hands'
                ],
                prevention: 'Control aphid populations with mineral oil sprays (reduces non-persistent transmission); remove weed hosts around fields; use reflective mulches to deter aphids; rogue out infected plants early; avoid planting near cucurbit crops.',
            },
            {
                name: 'Pepper Mild Mottle Virus (PMMoV)',
                pathogen: 'Tobamovirus PMMoV',
                severity: 'medium',
                inModel: false,
                symptoms: 'Mild mosaic and mottling with light and dark green areas; chlorotic spots; slight leaf distortion; necrotic rings on fruits in susceptible varieties.',
                causes: [
                    'Seed-borne virus — infected seeds are the primary source of new infections',
                    'Extremely stable in soil, plant debris, and on equipment for long periods',
                    'Spreads easily through mechanical contact — hands, pruning, harvesting',
                    'No insect vector — mechanical means are the primary spread route',
                    'Tobacco products used by workers can carry the virus into fields'
                ],
                prevention: 'Use certified disease-free seed; disinfect tools with 10% skimmed milk or trisodium phosphate solution; remove and burn infected plants; prohibit tobacco use in the field; wash hands thoroughly before handling plants.',
            },
            {
                name: 'Tobacco Mosaic Virus (TMV)',
                pathogen: 'Tobamovirus TMV',
                severity: 'medium',
                inModel: false,
                symptoms: 'Mosaic yellowing on leaves; leaf distortion; dark green blistering (enations); stunted growth; fruit may show discolouration and necrosis.',
                causes: [
                    'Mechanically transmitted through sap during cultivation and harvesting',
                    'Infected crop residues in soil are long-lasting inoculum sources',
                    'Tobacco products used by farm workers are a notorious source of TMV',
                    'Contaminated tools spread virus from plant to plant during pruning',
                    'Highly stable virus — survives indefinitely in dry plant material'
                ],
                prevention: 'Use TMV-resistant varieties; disinfect all tools with bleach or trisodium phosphate; ban tobacco use in fields; destroy all infected crop residues; plant in fields with no history of solanaceous crop infection.',
            },
            {
                name: 'Chilli Veinal Mottle Virus (ChiVMV)',
                pathogen: 'Potyvirus ChiVMV',
                severity: 'medium',
                inModel: false,
                symptoms: 'Prominent yellowing along leaf veins (vein clearing and vein banding); mosaic; leaf distortion; stunted plants; reduced fruit quality and yield.',
                causes: [
                    'Transmitted semi-persistently by aphids, especially Myzus persicae and Aphis gossypii',
                    'Weed hosts in and around fields serve as perpetual virus reservoirs',
                    'Infected plant residues in soil maintain the virus between seasons',
                    'Introduction through infected transplants from infected nurseries',
                    'Warm weather with high aphid populations dramatically increases spread'
                ],
                prevention: 'Use aphid-free certified transplants; control aphid populations with insecticides or neem oil; remove weed hosts; rogue and destroy infected plants at first sign of symptoms.',
            },
            {
                name: 'Groundnut Bud Necrosis Virus (GBNV)',
                pathogen: 'Orthotospovirus GBNV',
                severity: 'high',
                inModel: false,
                symptoms: 'Necrosis of growing tips and buds; ring spots and chlorotic lesions on leaves; bud death and malformation; severe stunting; fruit necrosis and distortion.',
                causes: [
                    'Transmitted by thrips (Scirtothrips dorsalis, Frankliniella schultzei) in a persistent propagative manner',
                    'High thrips populations during dry season dramatically increase incidence',
                    'Wide weed host range maintains the virus throughout the year',
                    'Thrips acquire virus as larvae — management of early-stage thrips is critical',
                    'Common in Sri Lanka during inter-monsoon dry periods'
                ],
                prevention: 'Control thrips populations with Spinosad or Abamectin; use blue sticky traps for monitoring; apply reflective mulches to repel thrips; remove weedy vegetation from field edges; rogue infected plants early.',
            },
            {
                name: 'Tomato Spotted Wilt Virus (TSWV)',
                pathogen: 'Orthotospovirus TSWV',
                severity: 'high',
                inModel: false,
                symptoms: 'Bronze or purplish discolouration of young leaves; ring spots and necrotic patterns on older leaves; necrotic rings on fruits; stem tip necrosis; terminal bud dieback.',
                causes: [
                    'Transmitted by thrips (Frankliniella occidentalis, Thrips palmi) in a persistent manner',
                    'Wide host range including many weeds and ornamental plants as reservoirs',
                    'High thrips populations in warm dry conditions',
                    'Infected ornamental plants adjacent to fields are major sources',
                    'Acquisition feeding occurs only in larval thrips stage'
                ],
                prevention: 'Control thrips with Spinosad or Abamectin; use blue sticky traps; remove infected plants and weed hosts immediately; use thrips-resistant cultivars where available; avoid planting near ornamental flower crops.',
            },
        ]
    },
    {
        id: 'pest',
        label: 'Pests',
        icon: 'fas fa-bug',
        diseases: [
            {
                name: 'Whitefly (Bemisia tabaci)',
                pathogen: 'Bemisia tabaci / Trialeurodes vaporariorum',
                severity: 'high',
                inModel: true,
                symptoms: 'Yellow stippling and stunting from sap-sucking; sticky honeydew deposits causing sooty mould; whiteflies visible as white clouds when plants are disturbed; transmits Leaf Curl Virus.',
                causes: [
                    'Warm, dry weather above 28°C accelerates population buildup',
                    'Spreads through infested transplants from nurseries',
                    'Over-reliance on chemical insecticides leads to resistance',
                    'Proximity to other solanaceous crops provides continuous whitefly source',
                    'Lack of natural predators (Encarsia, ladybirds)'
                ],
                prevention: 'Use yellow sticky traps for monitoring; release biological control agents (Encarsia formosa); apply Imidacloprid or Spiromesifen; use UV-reflective silver mulch to repel; avoid planting near tomato or tobacco fields.',
            },
            {
                name: 'Chilli Yellowish (Aphid / Mite Stress)',
                pathogen: 'Aphis gossypii / Polyphagotarsonemus latus',
                severity: 'medium',
                inModel: true,
                symptoms: 'Yellowing, stunting, and distortion of leaves; bronze or purplish discolouration from broad mite feeding; sticky honeydew from aphid colonies; viral disease transmission.',
                causes: [
                    'Dry season conditions favouring rapid aphid population growth',
                    'High nitrogen fertilization attracting aphids to lush growth',
                    'Broad mites thrive in hot, dry conditions above 30°C',
                    'Lack of natural enemies from over-use of broad-spectrum pesticides',
                    'Overcrowded plantings creating humid microclimate'
                ],
                prevention: 'Inspect plants regularly especially young growth; spray water jets to dislodge aphids; apply Dimethoate or Thiamethoxam for aphids; apply Abamectin or Spiromesifen for mites; encourage natural enemies.',
            },
            {
                name: 'Chilli Thrips (Scirtothrips dorsalis)',
                pathogen: 'Scirtothrips dorsalis (Thysanoptera)',
                severity: 'high',
                inModel: false,
                symptoms: 'Upward leaf curling; bronze-coloured, distorted leaves and buds; silvery streaking on leaves and fruits; flower and fruit drop; transmits GBNV and TSWV viruses.',
                causes: [
                    'Thrives in hot, dry conditions — major pest during Sri Lankan dry season',
                    'Reproduces very rapidly — a generation completes in just 10–15 days',
                    'Resistance to many insecticides from over-application without rotation',
                    'Movement from weeds and alternate host plants into chilli fields',
                    'Larvae feed concealed inside developing buds and flowers'
                ],
                prevention: 'Apply Spinosad, Abamectin, or neem-based insecticides; use blue sticky traps; avoid water stress which weakens plant defences; rotate insecticide modes of action; remove weedy margins around fields.',
            },
            {
                name: 'Aphids',
                pathogen: 'Myzus persicae / Aphis gossypii',
                severity: 'medium',
                inModel: false,
                symptoms: 'Colonies on young shoots and leaf undersides; curling and yellowing of infested leaves; sticky honeydew and sooty mould; transmits CMV, ChiVMV, and other viruses non-persistently.',
                causes: [
                    'Warm temperatures (20–28°C) with low rainfall favour rapid population buildup',
                    'Ant colonies protect aphids from natural enemies in exchange for honeydew',
                    'Nitrogen-rich lush plants are preferred by aphids',
                    'Natural enemy disruption from broad-spectrum insecticide use',
                    'Winged forms migrate from other infected crops'
                ],
                prevention: 'Apply mineral oil sprays to reduce non-persistent virus transmission; use yellow sticky traps; conserve natural enemies (ladybirds, lacewings, parasitic wasps); apply Imidacloprid or neem oil when needed; control ants to expose aphids to predators.',
            },
            {
                name: 'Fruit Borer (Helicoverpa armigera)',
                pathogen: 'Helicoverpa armigera (Lepidoptera)',
                severity: 'high',
                inModel: false,
                symptoms: 'Circular entry holes in fruits with frass; internal feeding destroying seeds and flesh; premature fruit ripening and drop; secondary fungal infection at entry sites.',
                causes: [
                    'Adult moths lay eggs on tender plant parts and developing fruits at night',
                    'Larvae bore into fruits within 24–48 hours of hatching',
                    'High resistance to many synthetic insecticides due to widespread overuse',
                    'Migration of adult moths from cotton and maize crops nearby',
                    'Peak activity during hot dry periods with high moth populations'
                ],
                prevention: 'Install pheromone traps (5–6 traps/ha) for monitoring; apply Bacillus thuringiensis (Bt) at egg-hatching stage; use Spinosad or Indoxacarb insecticides; remove and destroy fallen infested fruits; conserve natural parasitoids (Trichogramma wasps).',
            },
            {
                name: 'Broad Mite',
                pathogen: 'Polyphagotarsonemus latus (Acari)',
                severity: 'high',
                inModel: false,
                symptoms: 'Downward curling and distortion of young leaves; bronze, greasy appearance of leaf undersides; bud distortion and drop; stunted growing tips; symptoms resemble virus infection.',
                causes: [
                    'Extremely small mites invisible to naked eye — often misdiagnosed as virus',
                    'Warm temperatures (28–32°C) with moderate humidity favour rapid multiplication',
                    'Wind and worker movement spread mites between plants rapidly',
                    'Natural enemies destroyed by excessive broad-spectrum pesticide use',
                    'Spreads easily through infested transplants'
                ],
                prevention: 'Apply Abamectin, Spiromesifen, or Dicofol miticides early morning; conserve predatory mites (Neoseiulus spp.); avoid over-fertilisation with nitrogen; inspect plants regularly especially new growth; use clean certified transplants.',
            },
            {
                name: 'Spider Mites (Tetranychus urticae)',
                pathogen: 'Tetranychus urticae (Two-spotted Spider Mite)',
                severity: 'medium',
                inModel: false,
                symptoms: 'Fine webbing on undersides of leaves; yellow stippling on upper leaf surface; bronze or reddish discolouration; premature leaf drop in severe infestations under drought stress.',
                causes: [
                    'Hot and dry weather above 30°C with low humidity — especially Sri Lankan dry season',
                    'Water-stressed plants are far more susceptible to mite damage',
                    'Dusty field conditions reduce natural enemy effectiveness',
                    'Resistance build-up from repeated use of the same miticide class',
                    'Destruction of predatory mites by insecticide overuse'
                ],
                prevention: 'Maintain adequate soil moisture to reduce plant stress; apply water sprays to undersides of leaves; use Abamectin or Bifenazate miticides; introduce predatory mites (Phytoseiidae); rotate miticide classes to manage resistance.',
            },
            {
                name: 'Mealybug',
                pathogen: 'Phenacoccus solenopsis / Planococcus citri',
                severity: 'medium',
                inModel: false,
                symptoms: 'White cottony masses at leaf axils, stem joints, and roots; yellowing and wilting of infested branches; honeydew deposits leading to sooty mould; overall plant decline.',
                causes: [
                    'Ant activity protects mealybugs from natural enemies in exchange for honeydew',
                    'Spreads through movement of infested plant material, tools, and workers',
                    'Hot, dry conditions reduce natural enemy effectiveness',
                    'Lack of crop rotation allows population buildup over successive seasons',
                    'Spreads from ornamental plants and weeds'
                ],
                prevention: 'Control ants with ant bait around plant base; apply neem oil, insecticidal soap, or Buprofezin sprays targeting nymphal stage; release mealybug parasitoid (Anagyrus lopezi); inspect transplants carefully before field planting.',
            },
        ]
    },
    {
        id: 'physiological',
        label: 'Physiological',
        icon: 'fas fa-seedling',
        diseases: [
            {
                name: 'Blossom End Rot',
                pathogen: 'Calcium deficiency (physiological)',
                severity: 'medium',
                inModel: false,
                symptoms: 'Dark brown to black, dry, sunken area at blossom end of fruit; lesion turns leathery and black; internal tissue remains firm; affected fruits may be invaded by secondary fungal rots.',
                causes: [
                    'Calcium deficiency in developing fruit tissue due to irregular watering',
                    'Drought stress reduces calcium uptake even when soil calcium levels are adequate',
                    'Excessive nitrogen or potassium fertilisation competing with calcium absorption',
                    'Shallow root systems limiting calcium uptake',
                    'Soil pH imbalance affecting calcium availability'
                ],
                prevention: 'Maintain consistent, regular irrigation — avoid wet-dry cycles; apply foliar calcium nitrate sprays (0.5%); ensure adequate but not excessive potassium; mulch to maintain soil moisture; lime soil to pH 6.0–6.5; use drip irrigation for stable water supply.',
            },
            {
                name: 'Sunscald',
                pathogen: 'UV radiation / heat stress (physiological)',
                severity: 'low',
                inModel: false,
                symptoms: 'Tan or white papery, blister-like patches on the sun-exposed side of fruits; bleached patches on leaves; affected areas may be colonised by secondary fungi.',
                causes: [
                    'Direct intense sunlight on exposed fruits after defoliation',
                    'Pest or disease defoliation that removes the natural fruit canopy',
                    'Improper pruning that exposes previously shaded fruits to full sun',
                    'High temperatures exceeding 32°C combined with low humidity',
                    'Extreme heat events during Sri Lankan dry season'
                ],
                prevention: 'Maintain healthy foliage canopy to shade fruits; avoid practices that cause sudden defoliation; use shade nets (30%) in exposed fields during peak summer; apply kaolin clay particle film on exposed fruits as reflective barrier.',
            },
            {
                name: 'Nitrogen Deficiency',
                pathogen: 'Nutrient deficiency (physiological)',
                severity: 'low',
                inModel: false,
                symptoms: 'General yellowing (chlorosis) starting from older/lower leaves progressing upward; stunted growth; pale green colour throughout plant; early leaf drop in severe cases.',
                causes: [
                    'Insufficient nitrogen fertiliser application',
                    'Leaching of nitrogen from sandy soils by heavy rainfall',
                    'Waterlogging reducing root activity and nitrogen uptake',
                    'Alkaline soil pH reducing nitrogen availability',
                    'High C:N ratio from over-application of undecomposed organic matter'
                ],
                prevention: 'Apply balanced NPK fertiliser at recommended rates; use split applications to reduce leaching; incorporate well-composted organic matter; maintain proper drainage; conduct soil tests and adjust fertilisation accordingly.',
            },
            {
                name: 'Tip Burn',
                pathogen: 'Calcium / Boron deficiency (physiological)',
                severity: 'low',
                inModel: false,
                symptoms: 'Brown, dead margins on young leaves starting at leaf tips; distorted, cupped leaves; buds may die; in severe cases, entire growing point and new flush are affected.',
                causes: [
                    'Low available boron in sandy or highly leached soils common in Sri Lanka',
                    'Calcium deficiency combined with inadequate transpiration in young leaves',
                    'High soil salinity reduces calcium and boron uptake by roots',
                    'Drought or waterlogging both reduce boron mobility in the soil',
                    'Excessive lime application reducing boron availability'
                ],
                prevention: 'Apply borax (0.3 kg/ha) to soil or foliar boron spray (0.1% boric acid); maintain consistent soil moisture; avoid excess lime application; conduct soil boron tests every 2–3 seasons; apply foliar calcium to actively growing tips.',
            },
        ]
    },
];

/* ------------------------------------------------------------------
   Disease image paths  (local files under static/images/diseases/)
   null = no image downloaded — category icon fallback is shown instead
   ------------------------------------------------------------------ */
const DISEASE_IMAGES = {
    // ── Fungal (9) ──
    'Anthracnose (Fruit Rot)':                '/static/images/diseases/anthracnose-fruit-rot.jpg',
    'Powdery Mildew':                         '/static/images/diseases/powdery-mildew.jpg',
    'Cercospora Leaf Spot':                   '/static/images/diseases/cercospora-leaf-spot.jpg',
    'Phytophthora Blight':                    '/static/images/diseases/phytophthora-blight.jpg',
    'Fusarium Wilt':                          '/static/images/diseases/fusarium-wilt.jpg',
    'Damping Off':                            '/static/images/diseases/damping-off.jpg',
    'Alternaria Leaf Spot':                   '/static/images/diseases/alternaria-leaf-spot.jpg',
    'Stem Rot (Southern Blight)':             '/static/images/diseases/stem-rot.jpg',
    'Grey Mould (Botrytis Blight)':           '/static/images/diseases/grey-mould.jpg',

    // ── Bacterial (3) ──
    'Bacterial Wilt':                         '/static/images/diseases/bacterial-wilt.jpg',
    'Bacterial Leaf Spot':                    '/static/images/diseases/bacterial-leaf-spot.jpg',
    'Bacterial Soft Rot':                     '/static/images/diseases/bacterial-soft-rot.jpg',

    // ── Viral (7) ──
    'Chilli Leaf Curl Virus':                 '/static/images/diseases/leaf-curl-virus.jpg',
    'Cucumber Mosaic Virus (CMV)':            '/static/images/diseases/cucumber-mosaic-virus.jpg',
    'Pepper Mild Mottle Virus (PMMoV)':       '/static/images/diseases/pepper-mild-mottle-virus.jpg',
    'Tobacco Mosaic Virus (TMV)':             '/static/images/diseases/tobacco-mosaic-virus.jpg',
    'Chilli Veinal Mottle Virus (ChiVMV)':    '/static/images/diseases/chilli-veinal-mottle-virus.jpg',
    'Groundnut Bud Necrosis Virus (GBNV)':   '/static/images/diseases/groundnut-bud-necrosis-virus.jpg',
    'Tomato Spotted Wilt Virus (TSWV)':      '/static/images/diseases/tomato-spotted-wilt-virus.jpg',

    // ── Pests (8) ──
    'Whitefly (Bemisia tabaci)':              '/static/images/diseases/whitefly.jpg',
    'Chilli Yellowish (Aphid / Mite Stress)': '/static/images/diseases/chilli-yellowish.jpg',
    'Chilli Thrips (Scirtothrips dorsalis)':  '/static/images/diseases/chilli-thrips.jpg',
    'Aphids':                                 '/static/images/diseases/aphids.jpg',
    'Fruit Borer (Helicoverpa armigera)':     '/static/images/diseases/fruit-borer.jpg',
    'Broad Mite':                             '/static/images/diseases/broad-mite.jpg',
    'Spider Mites (Tetranychus urticae)':     '/static/images/diseases/spider-mites.jpg',
    'Mealybug':                               '/static/images/diseases/mealybug.jpg',

    // ── Physiological (4) ──
    'Blossom End Rot':                        '/static/images/diseases/blossom-end-rot.jpg',
    'Sunscald':                               '/static/images/diseases/sunscald.jpg',
    'Nitrogen Deficiency':                    '/static/images/diseases/nitrogen-deficiency.jpg',
    'Tip Burn':                               '/static/images/diseases/tip-burn.jpg',
};

/* ------------------------------------------------------------------
   Category icon map
   ------------------------------------------------------------------ */
const CATEGORY_ICONS = {
    fungal:         'fas fa-circle-nodes',
    bacterial:      'fas fa-bacteria',
    viral:          'fas fa-virus',
    pest:           'fas fa-bug',
    physiological:  'fas fa-seedling',
};

/* ------------------------------------------------------------------
   Build flat disease list for easy filtering/searching
   ------------------------------------------------------------------ */
function buildFlatList() {
    const list = [];
    for (const cat of SL_DISEASE_CATEGORIES) {
        for (const d of cat.diseases) {
            list.push({
                ...d,
                categoryId:    cat.id,
                categoryLabel: cat.label,
                image:         DISEASE_IMAGES[d.name] || null,
            });
        }
    }
    return list;
}

const ALL_DISEASES = buildFlatList();

/* ------------------------------------------------------------------
   State
   ------------------------------------------------------------------ */
let activeFilter = 'all';
let searchQuery  = '';

/* ------------------------------------------------------------------
   Render
   ------------------------------------------------------------------ */
function renderCards() {
    const grid      = document.getElementById('diseasesGrid');
    const noResults = document.getElementById('noResults');
    const countEl   = document.getElementById('resultsCount');

    const q = searchQuery.toLowerCase().trim();

    const filtered = ALL_DISEASES.filter(d => {
        const matchFilter = activeFilter === 'all'
            ? true
            : activeFilter === 'model'
                ? d.inModel
                : d.categoryId === activeFilter;

        const matchSearch = q === '' || [
            d.name, d.pathogen, d.symptoms, d.categoryLabel,
            ...(d.causes || []), d.prevention || ''
        ].join(' ').toLowerCase().includes(q);

        return matchFilter && matchSearch;
    });

    countEl.textContent = filtered.length;

    if (filtered.length === 0) {
        grid.innerHTML = '';
        noResults.classList.remove('hidden');
        return;
    }

    noResults.classList.add('hidden');
    grid.innerHTML = filtered.map(buildCardHTML).join('');

    // Attach click handlers
    grid.querySelectorAll('.disease-card').forEach(card => {
        card.addEventListener('click', () => {
            const idx = parseInt(card.dataset.idx, 10);
            openModal(filtered[idx]);
        });
    });
}

function buildCardHTML(d, idx) {
    const sevClass   = `severity-${d.severity}`;
    const sevLabel   = d.severity.charAt(0).toUpperCase() + d.severity.slice(1) + ' Risk';
    const catClass   = `cat-${d.categoryId}`;
    const catIcon    = CATEGORY_ICONS[d.categoryId] || 'fas fa-circle';
    const stripCls   = `strip-${d.categoryId}`;
    const modelTag   = d.inModel
        ? `<span class="model-tag"><i class="fas fa-robot"></i> AI Detectable</span>`
        : '';
    const inModelCls = d.inModel ? ' in-model' : '';

    // Image section — img with onerror fallback to category-coloured gradient
    const imgTag = d.image
        ? `<img src="${escHtml(d.image)}" alt="${escHtml(d.name)}" loading="lazy"
               onerror="this.style.display='none';this.nextElementSibling.style.display='flex';" />`
        : '';
    const fallbackStyle = d.image ? 'display:none' : 'display:flex';
    const imageHTML = `
        <div class="card-image-wrap">
            ${imgTag}
            <div class="card-image-fallback fallback-${d.categoryId}" style="${fallbackStyle}">
                <i class="${catIcon}"></i>
                <span class="fallback-label">${escHtml(d.categoryLabel)}</span>
            </div>
        </div>`;

    return `
    <div class="disease-card${inModelCls}" data-idx="${idx}">
        ${imageHTML}
        <div class="card-strip ${stripCls}"></div>
        <div class="card-header">
            <div class="card-title-group">
                <div class="card-name">${escHtml(d.name)}</div>
                <div class="card-pathogen">${escHtml(d.pathogen)}</div>
            </div>
            <div class="card-badges">
                <span class="severity-badge ${sevClass}">${sevLabel}</span>
                <span class="category-badge ${catClass}">
                    <i class="${catIcon}"></i> ${escHtml(d.categoryLabel)}
                </span>
                ${modelTag}
            </div>
        </div>
        <div class="card-body">
            <div class="card-symptoms">
                <div class="card-section-label">Symptoms</div>
                <p>${escHtml(d.symptoms)}</p>
            </div>
        </div>
        <div class="card-footer">
            <span>View full details</span><i class="fas fa-arrow-right"></i>
        </div>
    </div>`;
}

/* ------------------------------------------------------------------
   Modal
   ------------------------------------------------------------------ */
function openModal(d) {
    const modal      = document.getElementById('diseaseModal');
    const body       = document.getElementById('diseaseModalBody');
    const sevClass   = `severity-${d.severity}`;
    const sevLabel   = d.severity.charAt(0).toUpperCase() + d.severity.slice(1) + ' Risk';
    const catClass   = `cat-${d.categoryId}`;
    const catIcon    = CATEGORY_ICONS[d.categoryId] || 'fas fa-circle';
    const modelTag   = d.inModel
        ? `<span class="model-tag"><i class="fas fa-robot"></i> AI Detectable</span>`
        : '';
    const causesHTML = (d.causes || []).map(c => `<li>${escHtml(c)}</li>`).join('');
    const prevHTML   = d.prevention ? `<p>${escHtml(d.prevention)}</p>` : '<p>No specific information available.</p>';

    const modalImageHTML = d.image
        ? `<div class="modal-image-wrap">
               <img src="${escHtml(d.image)}" alt="${escHtml(d.name)}" loading="lazy"
                    onerror="this.parentElement.style.display='none';" />
           </div>`
        : '';

    body.innerHTML = `
        ${modalImageHTML}
        <div class="modal-strip strip-${d.categoryId}"></div>
        <div class="modal-inner">
            <div class="modal-title-row">
                <div class="modal-icon icon-${d.categoryId}">
                    <i class="${catIcon}"></i>
                </div>
                <div class="modal-title-text">
                    <h2>${escHtml(d.name)}</h2>
                    <p class="modal-pathogen">${escHtml(d.pathogen)}</p>
                    <div class="modal-badges">
                        <span class="severity-badge ${sevClass}">${sevLabel}</span>
                        <span class="category-badge ${catClass}">
                            <i class="${catIcon}"></i> ${escHtml(d.categoryLabel)}
                        </span>
                        ${modelTag}
                    </div>
                </div>
            </div>

            <div class="modal-section">
                <div class="modal-section-title">
                    <i class="fas fa-notes-medical"></i> Symptoms
                </div>
                <p>${escHtml(d.symptoms)}</p>
            </div>

            <div class="modal-section">
                <div class="modal-section-title">
                    <i class="fas fa-virus"></i> Causes &amp; Risk Factors
                </div>
                <ul class="modal-causes-list">${causesHTML}</ul>
            </div>

            <div class="modal-section">
                <div class="modal-section-title">
                    <i class="fas fa-shield-alt"></i> Prevention &amp; Management
                </div>
                ${prevHTML}
            </div>
        </div>`;

    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    document.getElementById('diseaseModal').classList.add('hidden');
    document.body.style.overflow = '';
}

/* ------------------------------------------------------------------
   Utilities
   ------------------------------------------------------------------ */
function escHtml(str) {
    if (!str) return '';
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

/* ------------------------------------------------------------------
   Event Wiring
   ------------------------------------------------------------------ */
document.addEventListener('DOMContentLoaded', () => {
    // Initial render
    renderCards();

    // Search input
    const searchInput = document.getElementById('diseaseSearch');
    const searchClear = document.getElementById('searchClear');

    searchInput.addEventListener('input', () => {
        searchQuery = searchInput.value;
        searchClear.classList.toggle('hidden', searchQuery.trim() === '');
        renderCards();
    });

    searchClear.addEventListener('click', () => {
        searchInput.value = '';
        searchQuery = '';
        searchClear.classList.add('hidden');
        renderCards();
        searchInput.focus();
    });

    // Filter chips
    document.getElementById('filterChips').addEventListener('click', e => {
        const chip = e.target.closest('.chip');
        if (!chip) return;
        document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        activeFilter = chip.dataset.filter;
        renderCards();
    });

    // Clear filters button (no-results state)
    document.getElementById('clearFiltersBtn').addEventListener('click', () => {
        activeFilter = 'all';
        searchQuery  = '';
        searchInput.value = '';
        searchClear.classList.add('hidden');
        document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
        document.querySelector('.chip[data-filter="all"]').classList.add('active');
        renderCards();
    });

    // Modal close
    document.getElementById('diseaseModalClose').addEventListener('click', closeModal);
    document.getElementById('diseaseModalOverlay').addEventListener('click', closeModal);
    document.addEventListener('keydown', e => {
        if (e.key === 'Escape') closeModal();
    });

    // Update hero total count from real data
    document.getElementById('statTotal').textContent = ALL_DISEASES.length;
});
