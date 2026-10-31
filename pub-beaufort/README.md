# Beaufort Lager : spot motion design « La fraîcheur qui rugit »

**Livrable :** `out/Beaufort_Lager_Pub_30s_9x16.mp4`, au format 1080×1920, 30 i/s, 30 s, en H.264 avec un son AAC normalisé à −14 LUFS.
**Diffusion :** Reels, TikTok, Stories et statuts WhatsApp.
**Ambiance :** fraîcheur glacée.

## Storyboard

| Temps | Plan | Texte à l'écran | Son |
|---|---|---|---|
| 0–5,8 s | Le givre envahit l'écran depuis les bords, puis la glace se fissure | *Quand la ville chauffe…* / **CHERCHE LE FRISSON.** | Vent glacé, craquements, montée |
| 5,8 s | La glace vole en éclats et révèle la bouteille givrée | | Impact grave, éclats de verre |
| 6–10,5 s | Le givre fond en gouttes de condensation, puis une lumière balaie la bouteille | **FROIDE.** *jusqu'à la dernière goutte.* | Groove en demi-temps |
| 10,5–12 s | Zoom sur le goulot, la capsule saute et un panache de CO₂ s'échappe | **PSSHT.** | Clic + « pssht », respiration |
| 12–17,6 s | La bière est servie dans le verre (jet, bulles, mousse) | **FRAÎCHE. / DORÉE. / PÉTILLANTE.** au tempo | Drop afro-house, glouglou, pétillement |
| 17,6–20 s | Le verre plein se couvre de condensation | *Une lager au caractère de lion.* | |
| 20–24 s | Gros plan sur l'étiquette, des glaçons tombent | Compteur **28°C → 4°C** (de l'orange au bleu glacier) / SERVIE BIEN FRAPPÉE | Tintements de glaçons |
| 24–28 s | Packshot de la bouteille et du verre sur un lit de glace, dans la brume | **LA FRAÎCHEUR QUI RUGIT.** | Impact, glaçons |
| 28–30 s | Carton final : lion doré, logo Beaufort, Lager, slogan | *La fraîcheur qui rugit.* / À servir très frais | Accord cristallin |

La mention légale *« L'abus d'alcool est dangereux pour la santé. À consommer avec modération. »* reste visible pendant tout le spot.

## Fabrication

Tout est généré par du code : il n'y a ni banque d'images, ni musique sous licence.

- `index.html` contient l'animation. La fonction `renderAt(t)` produit l'image exacte à l'instant `t`. Ouvert dans un navigateur, le fichier joue l'aperçu en boucle.
- `render.js` capture les images une à une dans Chromium et les envoie à ffmpeg, avec 4 rendus en parallèle.
- `audio.py` synthétise la musique originale à 120 BPM et le sound design avec numpy, de façon synchronisée avec l'image.
- `build.sh` reconstruit le tout : `./build.sh`

Prérequis : Node et Playwright (Chromium), Python 3 avec numpy, ffmpeg.

## Avant diffusion officielle

- La bouteille, l'étiquette et l'emblème du lion sont **recréés en vectoriel** d'après la photo. Pour une campagne officielle, il faut remplacer ces éléments par le logo et le packshot fournis par la marque, et obtenir l'accord du titulaire de la marque Beaufort.
- Il faut vérifier la mention sanitaire obligatoire et les règles de publicité pour l'alcool du pays de diffusion.

Polices utilisées : UnifrakturCook, Oswald et Cormorant Garamond, toutes sous licence SIL OFL.
