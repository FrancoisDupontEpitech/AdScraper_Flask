from websites import *

websites = [
    {"url": "https://www.actionco.fr", "name": "actionco", "function_whitepaper": whitepaper_for_actionco, "function_ads": ads_for_actionco},   # ads KO : problème anti-bot detection
    {"url": "https://www.alliancy.fr", "name": "alliancy", "function_whitepaper": whitepaper_for_alliancy, "function_ads": ads_for_alliancy},   # ads OK
    {"url": "https://www.challenges.fr", "name": "challenges", "function_whitepaper": whitepaper_for_challenges, "function_ads": ads_for_challenges}, # ads OK (parfois problème de click sur les pubs)
    {"url": "https://www.channelnews.fr", "name": "channelnews", "function_whitepaper": whitepaper_for_channelnews, "function_ads": ads_for_channelnews}, # ads OK
    {"url": "https://www.itforbusiness.fr", "name": "itforbusiness", "function_whitepaper": whitepaper_for_itforbusiness, "function_ads": ads_for_itforbusiness}, # whitepaper OK
    {"url": "https://itrnews.com", "name": "itrnews", "function_whitepaper": whitepaper_for_itrnews, "function_ads": ads_for_itrnews}, # whitepaper OK
    {"url": "https://www.itsocial.fr", "name": "itsocial", "function_whitepaper": whitepaper_for_itsocial, "function_ads": ads_for_itsocial}, # whitepaper OK : il faut scroll pour que le js affiche les livres blancs suivant. 1
    {"url": "https://www.journaldunet.com", "name": "journaldunet", "function_whitepaper": whitepaper_for_journaldunet, "function_ads": ads_for_journaldunet}, # whitepaper OK
    {"url": "https://www.lemagit.fr", "name": "lemagit", "function_whitepaper": whitepaper_for_lemagit, "function_ads": ads_for_lemagit},  #  whitepaper OK
    {"url": "https://www.lemoniteur.fr", "name": "lemoniteur", "function_whitepaper": whitepaper_for_lemoniteur, "function_ads": ads_for_lemoniteur}, # whitepaper OK
    {"url": "https://www.lesechos.fr", "name": "lesechos", "function_whitepaper": whitepaper_for_lesechos, "function_ads": ads_for_lesechos}, # ads OK (je get les pubs mais pas toutes, pour l'instant a stock pas dans le json)
    # {"url": "https://www.linfocr.com", "name": "linfocr", "function_whitepaper": whitepaper_for_linfocr, "function_ads": ads_for_linfocr}, # c'est les meme pubs que sur linformaticien.com
    {"url": "https://www.linformaticien.com", "name": "linformaticien", "function_whitepaper": whitepaper_for_linformaticien, "function_ads": ads_for_linformaticien}, # whitepaper OK
    {"url": "https://www.optionfinance.fr", "name": "optionfinance", "function_whitepaper": whitepaper_for_optionfinance, "function_ads": ads_for_optionfinance}, # ads OK
    {"url": "https://www.silicon.fr", "name": "silicon", "function_whitepaper": whitepaper_for_silicon, "function_ads": ads_for_silicon}, # whitepaper OK
    {"url": "https://www.solutions-numeriques.com", "name": "solutions-numeriques", "function_whitepaper": whitepaper_for_solutionsnumeriques, "function_ads": ads_for_solutionsnumeriques}, # whitepaper OK
    {"url": "https://www.usine-digitale.fr", "name": "usine-digitale", "function_whitepaper": whitepaper_for_usinedigitale, "function_ads": ads_for_usinedigitale}, # ads OK
    {"url": "https://www.usinenouvelle.com", "name": "usinenouvelle", "function_whitepaper": whitepaper_for_usinenouvelle, "function_ads": ads_for_usinenouvelle}, # whitepaper OK
]