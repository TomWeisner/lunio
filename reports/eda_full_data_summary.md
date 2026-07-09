# Full Data: Placement Safety EDA

## Objective

This EDA focuses on the advertiser, topic, channel, and click-quality signals that matter for advertiser-specific placement safety.

## Dataset Shape

- Rows: 250

- Columns: 10

## Advertiser Summary

| company_name | rows | clicks | invalid_clicks | invalid_click_rate | click_share |
| --- | --- | --- | --- | --- | --- |
| Jen & Berry's Ice Cream | 53 | 266797 | 14026 | 0.053 | 20.6% |
| Moonbucks Coffee | 67 | 320660 | 16756 | 0.052 | 24.8% |
| Plush Cosmetics | 67 | 360290 | 15927 | 0.044 | 27.8% |
| Jet3 Holidays | 63 | 346950 | 14067 | 0.041 | 26.8% |

## Channel Summary

| channel_type | rows | clicks | invalid_clicks | invalid_click_rate |
| --- | --- | --- | --- | --- |
| Youtube | 50 | 230310 | 11354 | 0.049 |
| Paid Social | 44 | 229818 | 10777 | 0.047 |
| Shopping | 44 | 203872 | 9566 | 0.047 |
| Search | 41 | 217715 | 9693 | 0.045 |
| Display | 39 | 218649 | 10481 | 0.048 |
| PMax | 32 | 194333 | 8905 | 0.046 |

## Highest Invalid-Click-Rate Topics

| topic | rows | clicks | invalid_clicks | invalid_click_rate |
| --- | --- | --- | --- | --- |
| mrbeast | 10 | 45614 | 3596 | 0.079 |
| Politics (commentary/newsletters) | 5 | 25991 | 1982 | 0.076 |
| Art & art history | 5 | 26438 | 1847 | 0.070 |
| Youth vaping / nicotine | 5 | 19173 | 1327 | 0.069 |
| Gardening | 5 | 26125 | 1802 | 0.069 |
| Online content moderation (extremism) | 5 | 29612 | 2016 | 0.068 |
| World Baseball Classic 2026 | 5 | 14522 | 984 | 0.068 |

## Advertiser x Topic Click Concentration

This table normalises topic-level click volume against each advertiser's average placement. `click_index` above 1 means the topic receives more clicks per placement than that advertiser usually receives; `invalid_click_index` does the same for invalid click volume. `topic_click_index` compares the advertiser-topic average with the average clicks per placement for that same topic across every advertiser in the dataset; above 1 means this advertiser is over-indexing on that topic. `company_adjusted_topic_click_index` compares the advertiser-topic average with the expected average after accounting for both the advertiser's baseline click volume and the topic's baseline click volume.

Sorted by highest `company_adjusted_topic_click_index`.

| company_name | topic | rows | avg_clicks | company_avg_clicks | click_index | topic_avg_clicks | topic_click_index | company_adjusted_topic_click_index | avg_invalid_clicks | company_avg_invalid_clicks | invalid_click_index | topic_avg_invalid_clicks | topic_invalid_click_index | invalid_click_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Jet3 Holidays | alt right podcast | 1 | 9066.000 | 5507.143 | 1.646 | 4097.700 | 2.212 | 2.081 | 182.000 | 223.286 | 0.815 | 188.300 | 0.967 | 0.020 |
| Jet3 Holidays | Alt-right propaganda (analysis) | 1 | 9066.000 | 5507.143 | 1.646 | 4591.600 | 1.974 | 1.857 | 182.000 | 223.286 | 0.815 | 213.800 | 0.851 | 0.020 |
| Jen & Berry's Ice Cream | Tabagism / quitting smoking | 1 | 9447.000 | 5033.906 | 1.877 | 5288.200 | 1.786 | 1.838 | 425.000 | 264.642 | 1.606 | 275.800 | 1.541 | 0.045 |
| Jen & Berry's Ice Cream | Youth vaping / nicotine | 1 | 6737.000 | 5033.906 | 1.338 | 3834.600 | 1.757 | 1.807 | 599.000 | 264.642 | 2.263 | 265.400 | 2.257 | 0.089 |
| Moonbucks Coffee | Politics (commentary/newsletters) | 1 | 8263.000 | 4785.970 | 1.727 | 5198.200 | 1.590 | 1.720 | 718.000 | 250.090 | 2.871 | 396.400 | 1.811 | 0.087 |
| Jet3 Holidays | Music / album reviews | 1 | 6611.000 | 5507.143 | 1.200 | 3688.000 | 1.793 | 1.686 | 68.000 | 223.286 | 0.305 | 80.800 | 0.842 | 0.010 |
| Jen & Berry's Ice Cream | World Baseball Classic 2026 | 2 | 4679.000 | 5033.906 | 0.929 | 2904.400 | 1.611 | 1.657 | 389.500 | 264.642 | 1.472 | 196.800 | 1.979 | 0.085 |

## Advertiser x Topic Low Click Concentration

The same normalised view, sorted by lowest `company_adjusted_topic_click_index`. These rows show topics receiving fewer clicks per placement than expected after accounting for both advertiser and topic baselines.

| company_name | topic | rows | avg_clicks | company_avg_clicks | click_index | topic_avg_clicks | topic_click_index | company_adjusted_topic_click_index | avg_invalid_clicks | company_avg_invalid_clicks | invalid_click_index | topic_avg_invalid_clicks | topic_invalid_click_index | invalid_click_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Jen & Berry's Ice Cream | Maga rally | 2 | 57.500 | 5033.906 | 0.011 | 3943.100 | 0.015 | 0.015 | 1.500 | 264.642 | 0.006 | 147.900 | 0.010 | 0.029 |
| Plush Cosmetics | Alt-right propaganda (analysis) | 1 | 1022.000 | 5377.463 | 0.190 | 4591.600 | 0.223 | 0.214 | 91.000 | 237.716 | 0.383 | 213.800 | 0.426 | 0.089 |
| Moonbucks Coffee | Flight disasters (databases) | 1 | 1218.000 | 4785.970 | 0.254 | 5567.000 | 0.219 | 0.237 | 89.000 | 250.090 | 0.356 | 171.400 | 0.519 | 0.073 |
| Jet3 Holidays | Flight incidents / near-misses | 1 | 1458.000 | 5507.143 | 0.265 | 5498.800 | 0.265 | 0.249 | 3.000 | 223.286 | 0.013 | 205.200 | 0.015 | 0.002 |
| Plush Cosmetics | Tabagism / quitting smoking | 1 | 1539.000 | 5377.463 | 0.286 | 5288.200 | 0.291 | 0.280 | 2.000 | 237.716 | 0.008 | 275.800 | 0.007 | 0.001 |
| Jet3 Holidays | mrbeast | 1 | 1479.000 | 5507.143 | 0.269 | 4561.400 | 0.324 | 0.305 | 12.000 | 223.286 | 0.054 | 359.600 | 0.033 | 0.008 |
| Plush Cosmetics | Weapons / gun policy | 1 | 2184.000 | 5377.463 | 0.406 | 5060.000 | 0.432 | 0.416 | 179.000 | 237.716 | 0.753 | 213.200 | 0.840 | 0.082 |

## Topic x Advertiser Click Share

This table flips the perspective from advertiser-first to topic-first. Each row is a topic, each advertiser column is that advertiser's share of clicks for the topic, and `topic_clicks` is the total click volume for that topic. Rows are sorted by highest topic click volume.

| topic | topic_clicks | Jen & Berry's Ice Cream | Jet3 Holidays | Moonbucks Coffee | Plush Cosmetics |
| --- | --- | --- | --- | --- | --- |
| Travel blog | 66401 | 0.000 | 1.000 | 0.000 | 0.000 |
| mrbeast | 45614 | 0.243 | 0.032 | 0.363 | 0.362 |
| alt right podcast | 40977 | 0.260 | 0.221 | 0.303 | 0.215 |
| Maga rally | 39431 | 0.003 | 0.060 | 0.408 | 0.528 |
| comedian | 37887 | 0.255 | 0.433 | 0.178 | 0.135 |
| Startups / entrepreneurship | 36465 | 0.000 | 0.482 | 0.246 | 0.272 |
| Aviation safety explainers | 36060 | 0.467 | 0.000 | 0.106 | 0.427 |
| Video games | 35964 | 0.216 | 0.215 | 0.214 | 0.356 |
| Sport competitions (calendar) | 35327 | 0.000 | 0.402 | 0.163 | 0.436 |
| Mental health & wellbeing | 34983 | 0.000 | 0.000 | 0.745 | 0.255 |
| K-pop (2026 comebacks) | 33032 | 0.168 | 0.226 | 0.000 | 0.606 |
| Sports (football) | 32800 | 0.000 | 0.000 | 0.563 | 0.437 |
| Sex & relationships education (non-explicit) | 30909 | 0.749 | 0.000 | 0.000 | 0.251 |
| Books / literature | 30740 | 0.259 | 0.125 | 0.160 | 0.456 |
| Sport competitions (news) | 30474 | 0.301 | 0.202 | 0.217 | 0.280 |
| Immigration (UK policy & practice) | 29983 | 0.000 | 0.727 | 0.000 | 0.273 |
| Immigration (US policy) | 29633 | 0.502 | 0.284 | 0.000 | 0.213 |
| Online content moderation (extremism) | 29612 | 0.108 | 0.435 | 0.240 | 0.216 |
| Space / Mars | 29360 | 0.388 | 0.000 | 0.148 | 0.465 |
| Social media (trends 2026) | 29230 | 0.498 | 0.000 | 0.262 | 0.240 |
| K-pop (artist news) | 28451 | 0.202 | 0.400 | 0.398 | 0.000 |
| Flight disasters (databases) | 27835 | 0.162 | 0.507 | 0.044 | 0.287 |
| Flight incidents / near-misses | 27494 | 0.165 | 0.053 | 0.294 | 0.488 |
| Immigration (UK asylum) | 26971 | 0.436 | 0.347 | 0.217 | 0.000 |
| Tabagism / quitting smoking | 26441 | 0.357 | 0.091 | 0.493 | 0.058 |
| Art & art history | 26438 | 0.000 | 0.613 | 0.237 | 0.150 |
| Gardening | 26125 | 0.207 | 0.000 | 0.453 | 0.340 |
| Politics (commentary/newsletters) | 25991 | 0.000 | 0.314 | 0.318 | 0.368 |
| Cybersecurity / ransomware | 25785 | 0.429 | 0.000 | 0.571 | 0.000 |
| Cooking (one-pot pasta) | 25622 | 0.313 | 0.687 | 0.000 | 0.000 |
| Weapons / gun policy | 25300 | 0.000 | 0.622 | 0.292 | 0.086 |
| Travel / holidays | 25017 | 0.113 | 0.240 | 0.436 | 0.212 |
| Propaganda & disinformation (research) | 24688 | 0.000 | 0.420 | 0.119 | 0.461 |
| Technology (MWC / devices / trends) | 24037 | 0.160 | 0.142 | 0.000 | 0.698 |
| Flight disasters (investigations) | 23556 | 0.205 | 0.142 | 0.385 | 0.268 |
| Movies / streaming | 23538 | 0.205 | 0.356 | 0.000 | 0.438 |
| Travel blogs (2026 destinations) | 23276 | 0.000 | 0.209 | 0.410 | 0.380 |
| Alt-right propaganda (analysis) | 22958 | 0.118 | 0.395 | 0.443 | 0.045 |
| Climate & environment | 19827 | 0.206 | 0.000 | 0.273 | 0.521 |
| Youth vaping / nicotine | 19173 | 0.351 | 0.000 | 0.509 | 0.140 |
| Music / album reviews | 18440 | 0.194 | 0.359 | 0.294 | 0.153 |
| Tobacco marketing / industry tactics | 18019 | 0.565 | 0.000 | 0.347 | 0.089 |
| Education policy | 16238 | 0.206 | 0.000 | 0.466 | 0.328 |
| World Baseball Classic 2026 | 14522 | 0.644 | 0.190 | 0.166 | 0.000 |
| War / conflict (Ukraine / geopolitics) | 14073 | 0.283 | 0.000 | 0.000 | 0.717 |