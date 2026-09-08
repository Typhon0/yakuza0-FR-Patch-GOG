#!/usr/bin/env python3
"""
translate_phase1.py
-------------------
Phase 1: Localizes all 33 Restaurants, 5 Bars, and 6 Merchant/System files
inside wdr.par:
  - restaurant0000.bin to restaurant0032.bin
  - bar0000.bin to bar0004.bin
  - throw.bin, send.bin, sale0001.bin, sale0002.bin, ex_shop0000.bin, blacksmith.bin
"""

import os
import sys
import struct
import shutil

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'scratch'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from translate_shops import load_french_item_descriptions

TRANSLATIONS = {
    # UI & NPC
    "Order": "Commander",
    "Quantity": "Quantité",
    "Menu": "Menu",
    "-": "-",
    "Thank you. That'll be %s.": "Merci. Ca fera %s.",
    "Thanks. That comes to %s.": "Merci. Ca fera %s.",
    "(I haven't selected anything.)": "(Je n'ai rien choisi.)",
    "(Ain't got anything selected.)": "(Rien n'a été choisi.)",
    "(Looks like I'm a little short.)": "(On dirait que je suis un peu à court.)",
    "(Gonna need more cash.)": "(Je vais avoir besoin de plus d'argent.)",
    "(I'm way too full for this.)": "(Je suis bien trop plein pour ça.)",
    "(Any more and I'm gonna burst.)": "(Un peu plus et je vais éclater.)",
    "(I couldn't drink another drop.)": "(Je ne pouvais pas boire une autre goutte.)",
    "(I'm done drinkin' for now.)": "(J'ai fini de boire pour le moment.)",
    "Barkeeper": "Barman",
    "Barkeep": "Barman",
    "Mama": "Mama",

    # Reactions
    "(Mmm, delicious.)": "(Mmm, délicieux.)",
    "(This is good.)": "(C'est bon.)",
    "(This is tasty.)": "(C'est savoureux.)",
    "(That hit the spot.)": "(Ca fait du bien.)",
    "(I like this.)": "(J'aime ça.)",
    "(Mmm, this is great.)": "(Mmm, c'est excellent.)",
    "(This is great.)": "(C'est super.)",
    "(Just how I like it.)": "(Juste comme je l'aime.)",
    "(Love the flavor.)": "(J'adore la saveur.)",
    "(Pretty tasty.)": "(Plutôt savoureux.)",
    "(I could get used to this.)": "(Je pourrais m'y habituer.)",
    "(This tastes great.)": "(Ca a bon goût.)",
    "(Pretty damn good.)": "(Sacrément bon.)",
    "(Mouthwatering.)": "(Ca met l'eau à la bouche.)",
    "(This is damn tasty.)": "(C'est sacrément savoureux.)",
    "(This tastes amazing.)": "(Ca a un goût incroyable.)",
    "(Yep, this is heaven.)": "(Ouaip, c'est le paradis.)",
    "(Mmm, pretty good.)": "(Mmm, vraiment bon.)",
    "(Right up my alley.)": "(Tout à fait mon rayon.)",
    "(Hmm... Not really my thing.)": "(Hmm... Pas vraiment mon truc.)",
    "(Eh... Ain't my kinda thing.)": "(Eh... C'est pas mon genre de truc.)",

    # Bar Drink Titles
    "Yamazaki 18-year-old whisky.": "Whisky Yamazaki 18 ans d'âge.",
    "Yamazaki 12-year-old whisky.": "Whisky Yamazaki 12 ans d'âge.",
    "Suntory Old Whisky from Japan.": "Vieux Whisky Suntory du Japon.",
    "The Macallan 12-year-old Scotch.": "Whisky écossais The Macallan 12 ans d'âge.",
    "Glenfiddich 12-year-old Scotch.": "Whisky écossais Glenfiddich 12 ans d'âge.",
    "Bowmore 12-year-old Scotch.": "Whisky écossais Bowmore 12 ans d'âge.",
    "Ballantine's 17-year-old Scotch.": "Whisky écossais Ballantine's 17 ans d'âge.",
    "Laphroaig 10-year-old Scotch.": "Whisky écossais Laphroaig 10 ans d'âge.",
    "Malt's the Draft.": "Bière pression Malt's.",
    "Suntory Brandy V.S.O.P from Japan.": "Brandy japonais Suntory V.S.O.P.",
    "Courvoisier XO French cognac.": "Cognac français Courvoisier XO.",
    "Kyogetsu Green Korean soju.": "Soju vert sud-coréen Kyogetsu.",
    "Beefeater British gin.": "Gin britannique Beefeater.",
    "Kakubin Japanese whisky.": "Whisky japonais Kakubin.",
    "Suntory Rum Gold from Japan.": "Rhum japonais Suntory Gold.",
    "Suntory Kuromaru Shochu from Japan.": "Shochu japonais Suntory Kuromaru.",

    # Bar Monologues
    "Fans of Japanese whisky are on the rise, even\noverseas, and one big reason for that is this\nright here.":
        "Les amateurs de whisky japonais se multiplient,\nmême à l'étranger, et ce cru en est une raison\nmajeure.",
    "Yamazaki whiskies have always been prizewinners,\nbut the 18-year-old variety has earned the most\naccolades.":
        "Les whiskies Yamazaki ont toujours été primés,\nmais la cuvée 18 ans est celle qui a reçu\nle plus d'éloges.",
    "It has an irresistibly aged flavor with depth\nand a taste like dried fruit that comes from\nthe sherry barrels in which it is aged.":
        "Il possède une saveur vieillie irrésistible en\nprofondeur, aux notes de fruits secs héritées\ndes fûts de xérès où il a vieilli.",
    "This, along with its fragrant chocolate note,\nmakes for one full-bodied whisky.":
        "Tout cela, avec ses notes chocolatées parfumées,\nen fait un whisky particulièrement corsé.",

    "This is one of Japan's top single malt whiskies.":
        "C'est l'un des meilleurs whiskies single malt du Japon.",
    "They use carefully selected, perfectly matured\nmalts to get that great, smooth flavor.":
        "Des malts soigneusement choisis et parfaitement\nmûris sont utilisés pour obtenir cette saveur\nsi douce.",
    "This yields a bright aroma and a sweet fullness\nin the mouth, and the finish is deep and mellow.":
        "Cela procure un arôme éclatant et une rondeur\nsuave en bouche, avec une finale profonde et moelleuse.",

    "This is another extremely popular Japanese\nwhisky.":
        "C'est un autre whisky japonais extrêmement populaire.",
    "Spirits aged in sherry barrels at the Yamazaki\nDistillery are blended with carefully selected\nmalts and grains.":
        "Des alcools vieillis en fûts de xérès à la distillerie\nYamazaki sont assemblés avec des malts et grains\nsoigneusement sélectionnés.",
    "A lot of people call it Dharma because the\nbottle's round shape looks like a dharma doll.":
        "Beaucoup l'appellent Dharma en raison de sa bouteille\nronde qui ressemble à une poupée daruma.",

    "This is the standard of The Macallan line, aged\nentirely in sherry barrels.":
        "C'est la référence de la gamme The Macallan, vieilli\nexclusivement dans des fûts de xérès.",
    "It stands a cut above the rest of the single\nmalt 12-year-old whiskies.":
        "Il se hisse nettement au-dessus des autres whiskies\nsingle malt de 12 ans d'âge.",
    "It has a sweet aroma, depth, and full body.":
        "Il a un arôme suave, de la profondeur et du corps.",
    "It's become such a status symbol that whisky\naficionados the world over have heard of it.":
        "C'est devenu un tel symbole de prestige que les\namateurs du monde entier en ont entendu parler.",
    "It may be the standard of the line, but it's\nguaranteed to deliver \"The Macallan\" taste!":
        "C'est peut-être l'entrée de gamme, mais il garantit\nle goût inimitable de \"The Macallan\" !",
    "It's perfect for those looking to enjoy The\nMacallan without breaking the bank.":
        "C'est parfait pour savourer un Macallan sans se\nruiner.",

    "Glenfiddich 12 Years is the best-selling single\nmalt whisky in the world.":
        "Le Glenfiddich 12 ans est le whisky single malt\nle plus vendu au monde.",
    "This bottle set the industry standard for a\nsingle malt. You'll find it light and fresh.":
        "Cette bouteille a défini le standard du single malt.\nVous le trouverez léger et frais.",
    "Its light flavor makes it popular with anyone\nnew to single malt whiskies.":
        "Sa saveur légère le rend très apprécié des néophytes\nen matière de whiskies single malt.",
    "I urge you to experience its sweet, full flavor\nand bouquet for yourself.":
        "Je vous invite à découvrir par vous-même son goût\nsuave et son riche bouquet.",
    "You simply have to experience its sweet, full\nflavor and bouquet for yourself.":
        "Il faut absolument goûter par vous-même à sa saveur\nsuave et à son bouquet raffiné.",

    "This is the standard of the Bowmore line. Sherry\nbarrels give it its uniquely ripe, floral\novertones.":
        "C'est la référence de la gamme Bowmore. Les fûts de xérès\nlui confèrent des arômes mûrs et floraux uniques.",
    "It also has the distinctive seaweed and salt\nnotes of Islay, with a distinguished flavor that\nhas earned it the title of \"Queen of Islay.\"":
        "Il porte aussi les notes d'algues et d'embruns d'Islay,\navec une distinction qui lui vaut le titre de\n\"Reine d'Islay\".",
    "The bouquet is fruity and the finish clean,\nmaking it exceptionally easy to drink.":
        "Son bouquet est fruité et sa finale est nette,\nce qui le rend particulièrement agréable à boire.",

    "This is the ultimate blended whisky.":
        "C'est le nec plus ultra du whisky d'assemblage.",
    "This could very well be called the crown jewel\nof Ballantine's whisky-blending expertise.":
        "On pourrait bien le qualifier de joyau du savoir-faire\nde maître assembleur de Ballantine's.",
    "It boasts a flavor and aroma that can be created\nonly by combining over 40 single malts.":
        "Il possède un goût et un arôme qu'on ne peut créer\nqu'en combinant plus de 40 single malts.",
    "It's well loved the world over, to the point of\nsome calling it \"the\" Scotch. ":
        "Il est adoré dans le monde entier, au point que\ncertains l'appellent \"Le\" Scotch. ",

    "It's safe to say this 10-year Laphroaig is the\nstandard of the line.":
        "On peut dire sans hésiter que ce Laphroaig 10 ans\nest la référence de la gamme.",
    "It's characterized by an intensely smoky flavor\nand a smooth, dry body.":
        "Il se caractérise par une saveur intensément fumée\net un corps sec et velouté.",
    "It has more than its share of quirks, so most\npeople either love it or hate it.":
        "Il ne manque pas de caractère : la plupart des gens\nl'adorent ou le détestent.",
    "But if you end up loving this one, it'll be the\none you'll never forget.":
        "Mais si vous venez à l'aimer, ce sera celui que vous\nn'oublierez jamais.",

    "This Japanese beer has ridden a wave of\npopularity ever since it went on sale in '86.":
        "Cette bière japonaise surfe sur une vague de succès\ndepuis sa commercialisation en 1986.",
    "Made with 100% barley malts, infused with malt\nand hops, this draft beer strikes a perfect\nbalance of flavors.":
        "Brassée à 100% avec des malts d'orge et du houblon,\ncette bière pression offre un équilibre de saveurs idéal.",
    "Rich barley tones accented with sweet barley\nmalt and bitter hops are its main features.":
        "De riches notes d'orge rehaussées de malt doux et\nde houblon amer sont ses atouts majeurs.",
    "Once you've enjoyed its pleasant finish, you'll\nbe eager to crack open another before too long.":
        "Une fois sa finale savourée, vous n'aurez qu'une envie :\nen reprendre une autre bien vite.",

    "This is one of Japan's top brandies.":
        "C'est l'un des brandies les plus réputés du Japon.",
    "V.S.O.P stands for Very Superior Old Pale.":
        "V.S.O.P signifie \"Very Superior Old Pale\".",
    "This bestseller has won over countless people\nwith its bright, fruity aroma and smooth taste.":
        "Ce best-seller a conquis une foule d'amateurs par\nson arôme fruité et sa saveur onctueuse.",

    "Kyogetsu Green is a prime example of Korean\nsoju.":
        "Le Kyogetsu Green est un exemple parfait de soju\nsud-coréen.",
    "This is a prime example of Korean soju.":
        "C'est un exemple remarquable de soju coréen.",
    "A spring-water base gives it a clean taste\nwhile premium Korean barley adds a mellow,\nrounded feel.":
        "Une eau de source pure lui donne un goût franc,\ntandis que l'orge coréenne lui confère de la douceur.",
    "A spring-water base gives it a clean taste,\nwhile premium Korean barley adds a mellow,\nrounded feel.":
        "Une eau de source pure lui donne un goût franc,\ntandis que l'orge coréenne lui confère de la douceur.",
    "It is affordable and I'd say it offers excellent\nvalue for the price.":
        "Il reste très abordable et offre un excellent rapport\nqualité-prix.",
    "It's quite affordable, too. I'd give it an A+\nfor cost performance.":
        "Il est très abordable aussi. Je lui donnerais une note\nparfaite pour son rapport qualité-prix.",
    "I used to drink this all the time.":
        "J'en buvais tout le temps à une époque.",
    "I used to drink this all the time, and its taste\nis still as familiar as an old friend.":
        "J'en buvais souvent autrefois, et sa saveur m'est\ntoujours aussi familière que celle d'un vieil ami.",
    "Its taste is still as familiar as an old friend.\nIn that sense, this bottle has special\nmeaning to me.":
        "Son goût m'est toujours aussi familier qu'un vieil ami.\nEn ce sens, cette bouteille m'est très chère.",
    "It's even better, thanks to those fond memories.":
        "C'est encore meilleur grâce à ces doux souvenirs.",

    "A remarkable specimen from France, Courvoisier XO\nwon top prize in worldwide cognac tests.":
        "Remarquable cru de France, le Courvoisier XO a remporté\nle premier prix aux concours mondiaux de cognac.",
    "The pairing of the finest grapes with Borderies\nspirits produces a full but smooth palate.":
        "L'accord des meilleurs raisins et d'eaux-de-vie des\nBorderies produit une bouche ample et raffinée.",
    "You haven't had cognac until you've tried this\none.":
        "On n'a jamais vraiment bu de cognac avant de goûter\nà celui-ci.",

    "Beefeater is the gin drinker's gin, enjoyed in\n170 countries the world over.":
        "Beefeater est le gin par excellence, apprécié dans\nplus de 170 pays à travers le monde.",
    "It's got a full juniper flavor, with a fresh\ncitrus bite to it.":
        "Il offre une saveur prononcée de genièvre, avec une\ntouche vivifiante d'agrumes.",
    "It's popular straight up or in cocktails like\nthe martini.":
        "Il est réputé sec ou dans des cocktails comme\nle martini.",

    "This rectangular bottle is probably the most\npopular whisky in Japan.":
        "Cette bouteille rectangulaire renferme le whisky\nle plus populaire du Japon.",
    "As for the name...":
        "Quant à son nom...",
    "But did you know Kakubin isn't its official\nname? It's a nickname that means \"square\nbottle\" in Japanese.":
        "Saviez-vous que Kakubin n'est pas son nom officiel ?\nC'est un surnom qui signifie \"bouteille carrée\"\nen japonais.",
    "I'd bet that any bar you walk into has at least\none bottle of this stuff waiting.":
        "Je parie que chaque bar où vous entrerez possède\nau moins une bouteille prête à servir.",

    "Rum is made from sugar cane juice that has been\nboiled down until its sugar content crystallizes\ninto molasses.":
        "Le rhum est produit à partir du jus de canne à sucre\nréduit jusqu'à ce que le sucre cristallise en mélasse.",
    "It's graded by color and flavor, both of which\nvary by how it was made. This one's a gold rum,\nwhich means it has a medium body.":
        "On le classe par sa robe et sa saveur, qui varient selon\nla distillation. C'est un rhum ambré au corps équilibré.",
    "It's perfect for cocktails, and with its wallet-\nfriendly price, you can enjoy it guilt-free.":
        "Il est parfait en cocktail, et son prix très doux permet\nde le savourer sans aucun remords.",
    "But be careful. Rum-based cocktails are sweet\nand delicious, so it's easy to drink way too\nmuch before you know it.":
        "Mais prudence : les cocktails au rhum sont si doux et\nsavoureux qu'on en boit vite trop sans s'en rendre compte.",

    "Suntory Kuromaru Shochu is an exquisite blend of\ntwo types of shochu--one rich and strong, and\nthe other light and full of fruit aromas.":
        "Le shochu Suntory Kuromaru est un subtil assemblage de\ndeux types de shochu : l'un riche, l'autre fruité.",
    "A unique variety of sweet potato from the\nKagoshima region gives it a mild flavor and\nrefreshing, clean finish.":
        "Une variété unique de patate douce de Kagoshima lui\napporte une douceur suave et une finale rafraîchissante.",
    "It's highly rated worldwide.":
        "Il est hautement estimé dans le monde entier.",

    # Merchant & System Strings
    # throw.bin
    "Inventory": "Inventaire",
    "(No space, so I'd better drop something.)": "(Plus de place, je ferais mieux de jeter un objet.)",
    "(Outta space. Better drop something.)": "(Plus de place. Mieux vaut jeter quelque chose.)",
    "Are you sure you want to discard this?": "Voulez-vous vraiment jeter cet objet ?",
    "(It'd be a waste to just throw this away.)": "(Ce serait du gâchis de jeter ça.)",
    "(This is way too cool to toss.)": "(C'est bien trop précieux pour être jeté.)",
    "(This weapon is too valuable to toss.)": "(Cette arme a trop de valeur pour être jetée.)",
    "(I ain't about to dump this weapon.)": "(Pas question de me débarrasser de cette arme.)",
    "%s discarded.": "%s jeté.",

    # send.bin
    "Guess I'll send it to the Item Box.)": "(Je ferais mieux d'envoyer ça au Coffre.)",
    "(Guess I'll send it to the Item Box.)": "(Je ferais mieux d'envoyer ça au Coffre.)",
    "Are you sure you want to send this?": "Voulez-vous vraiment envoyer cet objet ?",
    "You sent %s to the Item Box.": "Vous avez envoyé %s au Coffre.",

    # sale0001.bin & sale0002.bin
    "Free": "Gratuit",
    "(I don't have anything to sell.)": "(Je n'ai rien à vendre.)",
    "(Got nothing on me to sell.)": "(J'ai rien sur moi à vendre.)",
    "Details": "Détails",
    "<Sign:1>Back": "<Sign:1>Retour",
    "<Sign:1>Next %d/%d": "<Sign:1>Suivant %d/%d",
    "That comes to %s.": "Ca fera un montant de %s.",
    "Rare stuff here. You sure you want to sell?": "C'est un objet rare. Vous voulez vraiment le vendre ?",
    "I'll give you %s for it.": "Je vous en donne %s.",
    "You okay parting with such rare stuff?": "D'accord pour vous séparer d'un objet si rare ?",

    # ex_shop0000.bin
    "Done": "Terminé",
    "Obtained": "Obtenu",
    "Is this what you want?": "Est-ce bien ce que vous voulez ?",
    "(I don't have any space.)": "(Je n'ai plus de place.)",
    "(All outta space.)": "(Plus du tout de place.)",
    "(I don't need this.)": "(Je n'ai pas besoin de ça.)",
    "(I ain't got no use for this.)": "(Je n'en ai aucune utilité.)",
    "(I already have this.)": "(J'ai déjà cet objet.)",
    "(Got this already.)": "(J'ai déjà ça.)",
    "Products": "Articles",

    # blacksmith.bin
    "None": "Aucun",
    "That'll be %s. Is that all right?": "Ca fera %s. Est-ce que ça vous convient ?",
    "It'll cost %s to make. Is that okay?": "Ca coûtera %s à fabriquer. C'est bon ?",
}


def translate_restaurant_binary(raw_bin, expls):
    """Translates a single restaurant*.bin binary."""
    shop_id, item_count = struct.unpack('>HH', raw_bin[4:8])
    rec_start = struct.unpack('>I', raw_bin[12:16])[0]  # 0x110

    # Read all UI pointers from 0x10 to 0xbc (43 pointers)
    num_ui_ptrs = (0xbc - 0x10) // 4
    ui_ptrs = [struct.unpack('>I', raw_bin[0x10 + i * 4 : 0x14 + i * 4])[0] for i in range(num_ui_ptrs)]
    ui_strings = []
    for ptr in ui_ptrs:
        if ptr == 0:
            ui_strings.append('')
        else:
            end = raw_bin.find(b'\x00', ptr)
            ui_strings.append(raw_bin[ptr:end].decode('latin1'))

    new_ui_strings = [TRANSLATIONS.get(s, s) for s in ui_strings]

    # Read item records
    items = []
    for i in range(item_count):
        rec_off = rec_start + i * 48
        item_id = struct.unpack('>H', raw_bin[rec_off : rec_off + 2])[0]
        desc_ptr = struct.unpack('>I', raw_bin[rec_off + 0x20 : rec_off + 0x24])[0]
        end = raw_bin.find(b'\x00', desc_ptr)
        en_desc = raw_bin[desc_ptr:end].decode('latin1')

        if item_id < len(expls) and expls[item_id].strip():
            fr_desc = expls[item_id]
        else:
            fr_desc = TRANSLATIONS.get(en_desc, en_desc)

        items.append((item_id, fr_desc))

    # Build new binary layout
    new_bin = bytearray(raw_bin[: rec_start + item_count * 48])

    # Align string block start to 4 bytes
    str_start = (len(new_bin) + 3) & ~3
    new_bin.extend(b'\x00' * (str_start - len(new_bin)))

    # Write UI strings
    for i, s in enumerate(new_ui_strings):
        if not s:
            struct.pack_into('>I', new_bin, 0x10 + i * 4, 0)
        else:
            ptr = len(new_bin)
            struct.pack_into('>I', new_bin, 0x10 + i * 4, ptr)
            new_bin.extend(s.encode('latin1') + b'\x00')

    # Write item descriptions & update pointers
    for i, (item_id, fr_desc) in enumerate(items):
        ptr = len(new_bin)
        rec_off = rec_start + i * 48
        struct.pack_into('>I', new_bin, rec_off + 0x20, ptr)
        new_bin.extend(fr_desc.encode('latin1') + b'\x00')

    # 4-byte padding alignment
    while len(new_bin) % 4 != 0:
        new_bin.append(0)

    return bytes(new_bin)


def translate_bar_binary(raw_bin):
    """Translates a single bar*.bin binary."""
    shop_id, item_count = struct.unpack('>HH', raw_bin[4:8])
    rec_start = struct.unpack('>I', raw_bin[12:16])[0]  # 0x110

    # Read UI pointers (0x10 to 0x110 = 64 pointers)
    num_ui_ptrs = (0x110 - 0x10) // 4
    ui_ptrs = [struct.unpack('>I', raw_bin[0x10 + i * 4 : 0x14 + i * 4])[0] for i in range(num_ui_ptrs)]
    ui_strings = []
    for ptr in ui_ptrs:
        if 0 < ptr < len(raw_bin):
            end = raw_bin.find(b'\x00', ptr)
            ui_strings.append(raw_bin[ptr:end].decode('latin1'))
        else:
            ui_strings.append('')

    new_ui_strings = [TRANSLATIONS.get(s, s) for s in ui_strings]

    # Read item records (88 bytes per record)
    # String pointer fields: 0x20 (title), 0x38, 0x3c, 0x40, 0x44, 0x48 (monologue paragraphs)
    items = []
    for i in range(item_count):
        rec_off = rec_start + i * 88
        item_ptrs_and_strs = []
        for f_off in [0x20, 0x38, 0x3c, 0x40, 0x44, 0x48]:
            p = struct.unpack('>I', raw_bin[rec_off + f_off : rec_off + f_off + 4])[0]
            if 0 < p < len(raw_bin):
                end = raw_bin.find(b'\x00', p)
                orig_s = raw_bin[p:end].decode('latin1')
                trans_s = TRANSLATIONS.get(orig_s, orig_s)
                item_ptrs_and_strs.append((f_off, trans_s))
            else:
                item_ptrs_and_strs.append((f_off, ''))
        items.append(item_ptrs_and_strs)

    # Build new binary layout
    new_bin = bytearray(raw_bin[: rec_start + item_count * 88])

    str_start = (len(new_bin) + 3) & ~3
    new_bin.extend(b'\x00' * (str_start - len(new_bin)))

    # Write UI strings
    for i, s in enumerate(new_ui_strings):
        if not s:
            # Preserve non-pointer values in UI table (e.g. sitcnt floats)
            if ui_ptrs[i] >= len(raw_bin) or ui_ptrs[i] == 0:
                pass  # Keep original byte values
            else:
                struct.pack_into('>I', new_bin, 0x10 + i * 4, 0)
        else:
            ptr = len(new_bin)
            struct.pack_into('>I', new_bin, 0x10 + i * 4, ptr)
            new_bin.extend(s.encode('latin1') + b'\x00')

    # Write item strings & update pointers
    for i, item_fields in enumerate(items):
        rec_off = rec_start + i * 88
        for f_off, s in item_fields:
            if not s:
                struct.pack_into('>I', new_bin, rec_off + f_off, 0)
            else:
                ptr = len(new_bin)
                struct.pack_into('>I', new_bin, rec_off + f_off, ptr)
                new_bin.extend(s.encode('latin1') + b'\x00')

    while len(new_bin) % 4 != 0:
        new_bin.append(0)

    return bytes(new_bin)


def translate_simple_table_binary(raw_bin, ptr_offsets):
    """Translates simple merchant binaries where a fixed list of pointer offsets points to strings."""
    # Find the earliest string pointer to know where the table ends and strings begin
    ptrs = []
    for off in ptr_offsets:
        p = struct.unpack('>I', raw_bin[off:off+4])[0]
        if 0 < p < len(raw_bin):
            end = raw_bin.find(b'\x00', p)
            s = raw_bin[p:end].decode('latin1')
            ptrs.append((off, p, s))
        else:
            ptrs.append((off, 0, ''))

    earliest_p = min((p for _, p, _ in ptrs if p > 0), default=len(raw_bin))
    new_bin = bytearray(raw_bin[:earliest_p])

    # Append translated strings
    str_map = {}
    for off, p, orig_s in ptrs:
        if not orig_s:
            struct.pack_into('>I', new_bin, off, 0)
            continue
        trans_s = TRANSLATIONS.get(orig_s, orig_s)
        if trans_s not in str_map:
            new_p = len(new_bin)
            str_map[trans_s] = new_p
            new_bin.extend(trans_s.encode('latin1') + b'\x00')
        struct.pack_into('>I', new_bin, off, str_map[trans_s])

    while len(new_bin) % 4 != 0:
        new_bin.append(0)

    return bytes(new_bin)


def patch_wdr_phase1(wdr_path, expls):
    print(f"\n[+] Opening wdr.par: {wdr_path}")
    with open(wdr_path, 'rb') as f:
        wdr_data = bytearray(f.read())

    folder_count, folder_table_offset, file_count, file_table_offset = struct.unpack('>4I', wdr_data[16:32])
    name_offset = 32 + folder_count * 64

    # Build entry dictionary
    entries = {}
    for i in range(file_count):
        fn = wdr_data[name_offset + i * 64 : name_offset + (i + 1) * 64].split(b'\x00')[0].decode('latin1')
        entry_off = file_table_offset + i * 32
        flags, u_sz, c_sz, f_off = struct.unpack('>4I', wdr_data[entry_off : entry_off + 16])
        entries[fn] = {
            'index': i,
            'entry_off': entry_off,
            'flags': flags,
            'u_sz': u_sz,
            'c_sz': c_sz,
            'f_off': f_off,
            'raw': bytes(wdr_data[f_off : f_off + c_sz])
        }

    # Backup wdr.par
    bak_path = wdr_path + ".phase1.bak"
    if not os.path.exists(bak_path):
        shutil.copyfile(wdr_path, bak_path)
        print(f"[+] Backup created: {bak_path}")

    # 1. Translate merchant files that fit in their existing slots or free padding
    # throw.bin (offsets 0x0c to 0x40)
    print("\n--- Translating Merchant / System files ---")
    throw_ptrs = [0x0c, 0x10, 0x14, 0x18, 0x1c, 0x20, 0x24, 0x28, 0x2c, 0x30, 0x34, 0x38, 0x3c, 0x40]
    throw_bin = translate_simple_table_binary(entries['throw.bin']['raw'], throw_ptrs)
    print(f"throw.bin: {len(entries['throw.bin']['raw'])} -> {len(throw_bin)} bytes")

    # send.bin (offsets 0x0c, 0x10, 0x14, 0x18, 0x24, 0x28, 0x2c, 0x30)
    send_ptrs = [0x0c, 0x10, 0x14, 0x18, 0x24, 0x28, 0x2c, 0x30]
    send_bin = translate_simple_table_binary(entries['send.bin']['raw'], send_ptrs)
    print(f"send.bin: {len(entries['send.bin']['raw'])} -> {len(send_bin)} bytes")

    # sale0001.bin (offsets 0x08 to 0x50)
    sale1_ptrs = list(range(0x08, 0x54, 4))
    sale1_bin = translate_simple_table_binary(entries['sale0001.bin']['raw'], sale1_ptrs)
    print(f"sale0001.bin: {len(entries['sale0001.bin']['raw'])} -> {len(sale1_bin)} bytes")

    # sale0002.bin (offsets 0x08 to 0x50)
    sale2_ptrs = list(range(0x08, 0x54, 4))
    sale2_bin = translate_simple_table_binary(entries['sale0002.bin']['raw'], sale2_ptrs)
    print(f"sale0002.bin: {len(entries['sale0002.bin']['raw'])} -> {len(sale2_bin)} bytes")

    # blacksmith.bin (offsets 0x10 to 0x9c)
    blacksmith_ptrs = list(range(0x10, 0xa0, 4))
    blacksmith_bin = translate_simple_table_binary(entries['blacksmith.bin']['raw'], blacksmith_ptrs)
    print(f"blacksmith.bin: {len(entries['blacksmith.bin']['raw'])} -> {len(blacksmith_bin)} bytes")

    # Inject merchant files in-place (verifying padding space)
    for name, new_data in [('throw.bin', throw_bin), ('send.bin', send_bin), ('sale0001.bin', sale1_bin), ('sale0002.bin', sale2_bin), ('blacksmith.bin', blacksmith_bin)]:
        info = entries[name]
        old_sz = info['c_sz']
        new_sz = len(new_data)
        # Check next file offset to make sure we do not overwrite anything
        # Find next file in order of f_off
        next_off = min(e['f_off'] for e in entries.values() if e['f_off'] > info['f_off'])
        available = next_off - info['f_off']
        assert new_sz <= available, f"{name} new size {new_sz} exceeds available space {available}!"
        wdr_data[info['f_off'] : info['f_off'] + new_sz] = new_data
        # Update entry table
        struct.pack_into('>4I', wdr_data, info['entry_off'], info['flags'], new_sz, new_sz, info['f_off'])
        print(f"  [+] Injected {name}: {new_sz} bytes (slot available: {available})")

    # 2. Translate all bars (bar0000.bin - bar0004.bin)
    print("\n--- Translating 5 Bars ---")
    bar_bins = {}
    for i in range(5):
        name = f'bar{i:04d}.bin'
        bar_bins[name] = translate_bar_binary(entries[name]['raw'])
        print(f"  [+] {name}: {len(entries[name]['raw'])} -> {len(bar_bins[name])} bytes")

    # 3. Translate ex_shop0000.bin
    print("\n--- Translating ex_shop0000.bin ---")
    ex_shop_ptrs = list(range(0x10, 0x78, 4))
    ex_shop_bin = translate_simple_table_binary(entries['ex_shop0000.bin']['raw'], ex_shop_ptrs)
    print(f"  [+] ex_shop0000.bin: {len(entries['ex_shop0000.bin']['raw'])} -> {len(ex_shop_bin)} bytes")

    # 4. Translate all 33 Restaurants (restaurant0000.bin - restaurant0032.bin)
    print("\n--- Translating 33 Restaurants ---")
    rest_bins = {}
    for i in range(33):
        name = f'restaurant{i:04d}.bin'
        rest_bins[name] = translate_restaurant_binary(entries[name]['raw'], expls)
        print(f"  [+] {name}: {len(entries[name]['raw'])} -> {len(rest_bins[name])} bytes")

    # 5. Repack tail block from bar0000.bin onwards
    # Files in tail block in order:
    # bar0000..0004, ex_shop0000, restaurant0000..0032, shop0000..0034
    tail_files = []
    for i in range(5):
        name = f'bar{i:04d}.bin'
        tail_files.append((name, bar_bins[name]))
    tail_files.append(('ex_shop0000.bin', ex_shop_bin))
    for i in range(33):
        name = f'restaurant{i:04d}.bin'
        tail_files.append((name, rest_bins[name]))
    for i in range(35):
        name = f'shop{i:04d}.bin'
        tail_files.append((name, entries[name]['raw']))

    tail_start_off = entries['bar0000.bin']['f_off']
    print(f"\n[+] Rebuilding tail block starting at 0x{tail_start_off:x} ({len(tail_files)} files)")

    rebuilt_wdr = wdr_data[:tail_start_off]
    current_off = tail_start_off

    for fn, data in tail_files:
        aligned_off = (current_off + 63) & ~63
        if aligned_off > len(rebuilt_wdr):
            rebuilt_wdr.extend(b'\x00' * (aligned_off - len(rebuilt_wdr)))

        f_offset = len(rebuilt_wdr)
        f_len = len(data)
        rebuilt_wdr.extend(data)
        current_off = len(rebuilt_wdr)

        entry_off = entries[fn]['entry_off']
        flags = entries[fn]['flags'] & ~0x80000000
        struct.pack_into('>4I', rebuilt_wdr, entry_off, flags, f_len, f_len, f_offset)

    print(f"[+] Rebuilt wdr.par size: {len(rebuilt_wdr)} bytes (original: {len(wdr_data)})")
    with open(wdr_path, 'wb') as f:
        f.write(rebuilt_wdr)

    print(f"[SUCCESS] wdr.par successfully patched with Phase 1 translations!")


def main():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    boot_par = os.path.join(repo_root, 'release_gog', 'data', 'bootpar', 'boot.par')
    wdr_par = os.path.join(repo_root, 'release_gog', 'data', 'wdr_par_c', 'wdr.par')

    expls = load_french_item_descriptions(boot_par)
    patch_wdr_phase1(wdr_par, expls)


if __name__ == '__main__':
    main()
