import requests
from .base_scraper import BaseScraper


class ColetorRedesSociais(BaseScraper):
    """
    Coletor que verifica a existência de um nome de usuário em diversas
    redes sociais e plataformas online (estilo Sherlock).

    Para cada plataforma, monta a URL do perfil e faz uma requisição HEAD/GET.
    Retorna a lista de perfis encontrados (status 200) e os links para
    investigação manual.
    """

    def __init__(self):
        super().__init__(rate_limit_range=(0.3, 1.0))
    # Cada plataforma define:
    #   "url"   : template com {usuario}
    #   "metodo": "status"  -> HTTP 200 = existe
    #             "redirect"-> HTTP 200 e NÃO redireciona para página genérica = existe
        self.plataformas = {
            # --- Redes Sociais (Principais) ---
            "Instagram": {"url": "https://www.instagram.com/{usuario}/", "metodo": "status"},
            "Twitter / X": {"url": "https://x.com/{usuario}", "metodo": "status"},
            "Facebook": {"url": "https://www.facebook.com/{usuario}", "metodo": "status"},
            "TikTok": {"url": "https://www.tiktok.com/@{usuario}", "metodo": "status"},
            "LinkedIn": {"url": "https://www.linkedin.com/in/{usuario}/", "metodo": "status"},
            "Pinterest": {"url": "https://www.pinterest.com/{usuario}/", "metodo": "status"},
            "Reddit": {"url": "https://www.reddit.com/user/{usuario}", "metodo": "status"},
            "Tumblr": {"url": "https://{usuario}.tumblr.com", "metodo": "status"},
            "Snapchat": {"url": "https://www.snapchat.com/add/{usuario}", "metodo": "status"},
            "Threads": {"url": "https://www.threads.net/@{usuario}", "metodo": "status"},
            "Bluesky": {"url": "https://bsky.app/profile/{usuario}", "metodo": "status"},
            "Mastodon.social": {"url": "https://mastodon.social/@{usuario}", "metodo": "status"},
            "WhatsApp": {"url": "https://wa.me/{usuario}", "metodo": "status"},  # número com código país
            "Signal": {"url": "https://signal.me/#p/{usuario}", "metodo": "status"},
            "Discord": {"url": "https://discord.com/users/{usuario}", "metodo": "status"},
            "Telegram": {"url": "https://t.me/{usuario}", "metodo": "status"},
            "WeChat": {"url": "https://wechat.com/{usuario}", "metodo": "status"},
            "VK": {"url": "https://vk.com/{usuario}", "metodo": "status"},
            "OK.ru": {"url": "https://ok.ru/{usuario}", "metodo": "status"},
            
            # --- Redes Sociais Alternativas ---
            "Myspace": {"url": "https://myspace.com/{usuario}", "metodo": "status"},
            "Flickr": {"url": "https://www.flickr.com/people/{usuario}/", "metodo": "status"},
            "500px": {"url": "https://500px.com/p/{usuario}", "metodo": "status"},
            "DeviantArt": {"url": "https://www.deviantart.com/{usuario}", "metodo": "status"},
            "Behance": {"url": "https://www.behance.net/{usuario}", "metodo": "status"},
            "Dribbble": {"url": "https://dribbble.com/{usuario}", "metodo": "status"},
            "ArtStation": {"url": "https://www.artstation.com/{usuario}", "metodo": "status"},
            "VSCO": {"url": "https://vsco.co/{usuario}/gallery", "metodo": "status"},
            "Ello": {"url": "https://ello.co/{usuario}", "metodo": "status"},

            # --- Redes Sociais (Adicionais) ---
            "Facebook Groups": {"url": "https://www.facebook.com/groups/{usuario}", "metodo": "status"},
            "Instagram Threads": {"url": "https://www.threads.net/@{usuario}", "metodo": "status"},  # já tem, mas reforçando
            "Twitter Lists": {"url": "https://x.com/i/lists/{usuario}", "metodo": "status"},
            "LinkedIn Company": {"url": "https://www.linkedin.com/company/{usuario}/", "metodo": "status"},
            "LinkedIn School": {"url": "https://www.linkedin.com/school/{usuario}/", "metodo": "status"},

            # --- Redes Sociais Chinesas (comunidade gigante) ---
            "WeChat Official": {"url": "https://weixin.qq.com/{usuario}", "metodo": "status"},
            "Weibo": {"url": "https://weibo.com/u/{usuario}", "metodo": "status"},
            "Douyin": {"url": "https://www.douyin.com/user/{usuario}", "metodo": "status"},
            "Xiaohongshu (RED)": {"url": "https://www.xiaohongshu.com/user/profile/{usuario}", "metodo": "status"},
            "Bilibili": {"url": "https://space.bilibili.com/{usuario}", "metodo": "status"},
            "QQ": {"url": "https://user.qzone.qq.com/{usuario}", "metodo": "status"},
            "Zhihu": {"url": "https://www.zhihu.com/people/{usuario}", "metodo": "status"},

            # --- Redes Sociais Russas / Leste Europeu ---
            "VKontakte (VK)": {"url": "https://vk.com/{usuario}", "metodo": "status"},  # já tem
            "Odnoklassniki (OK)": {"url": "https://ok.ru/profile/{usuario}", "metodo": "status"},  # já tem
            "Telegram (Russian)": {"url": "https://t.me/{usuario}", "metodo": "status"},
            "Yandex Zen": {"url": "https://zen.yandex.ru/id/{usuario}", "metodo": "status"},
            "Rutube": {"url": "https://rutube.ru/u/{usuario}/", "metodo": "status"},

            # --- Redes Sociais Japonesas ---
            "LINE": {"url": "https://line.me/ti/p/{usuario}", "metodo": "status"},
            "Twitter Japan": {"url": "https://twitter.com/{usuario}", "metodo": "status"},  # mesmo do X
            "Mixi": {"url": "https://mixi.jp/show_friend.pl?id={usuario}", "metodo": "status"},
            "Ameba": {"url": "https://ameblo.jp/{usuario}", "metodo": "status"},
            "Pixiv": {"url": "https://www.pixiv.net/users/{usuario}", "metodo": "status"},
            "Niconico": {"url": "https://www.nicovideo.jp/user/{usuario}", "metodo": "status"},

            # --- Redes Sociais Coreanas ---
            "KakaoTalk": {"url": "https://story.kakao.com/ch/{usuario}", "metodo": "status"},
            "Naver Cafe": {"url": "https://cafe.naver.com/{usuario}", "metodo": "status"},
            "Naver Blog": {"url": "https://blog.naver.com/{usuario}", "metodo": "status"},
            "Cyworld": {"url": "https://www.cyworld.com/{usuario}", "metodo": "status"},

            # --- Redes Sociais Latinas / Espanholas ---
            "Taringa": {"url": "https://www.taringa.net/{usuario}", "metodo": "status"},
            "Hi5": {"url": "https://hi5.com/profile/{usuario}", "metodo": "status"},
            "Sonico": {"url": "https://www.sonico.com/profile/{usuario}", "metodo": "status"},
            "Badoo": {"url": "https://badoo.com/en/{usuario}", "metodo": "status"},
            "Tuenti": {"url": "https://tuenti.com/{usuario}", "metodo": "status"},

            # --- Redes Sociais Indianas ---
            "ShareChat": {"url": "https://sharechat.com/profile/{usuario}", "metodo": "status"},
            "Josh": {"url": "https://josh.app/{usuario}", "metodo": "status"},
            "MX TakaTak": {"url": "https://takTak.com/{usuario}", "metodo": "status"},
            "Roposo": {"url": "https://roposo.com/{usuario}", "metodo": "status"},

            # --- Redes Sociais Árabes / Oriente Médio ---
            "Telegram (Arabic)": {"url": "https://t.me/{usuario}", "metodo": "status"},
            "Yalla": {"url": "https://yalla.com/{usuario}", "metodo": "status"},
            "PalTalk": {"url": "https://paltalk.com/{usuario}", "metodo": "status"},

            # --- Redes Sociais de Namoro / Relacionamento ---
            "Tinder": {"url": "https://tinder.com/@{usuario}", "metodo": "status"},
            "Bumble": {"url": "https://bumble.com/{usuario}", "metodo": "status"},
            "Hinge": {"url": "https://hinge.co/@{usuario}", "metodo": "status"},
            "Grindr": {"url": "https://grindr.com/profile/{usuario}", "metodo": "status"},
            "OKCupid": {"url": "https://okcupid.com/profile/{usuario}", "metodo": "status"},
            "Plenty of Fish": {"url": "https://pof.com/viewprofile.aspx?username={usuario}", "metodo": "status"},

            # --- Redes Sociais Profissionais / Nicho ---
            "ResearchGate": {"url": "https://www.researchgate.net/profile/{usuario}", "metodo": "status"},
            "Academia.edu": {"url": "https://independent.academia.edu/{usuario}", "metodo": "status"},
            "Google Scholar": {"url": "https://scholar.google.com/citations?user={usuario}", "metodo": "status"},
            "ORCID": {"url": "https://orcid.org/{usuario}", "metodo": "status"},
            "LinkedIn Learning": {"url": "https://www.linkedin.com/learning/instructors/{usuario}", "metodo": "status"},
            "Pluralsight": {"url": "https://app.pluralsight.com/profile/{usuario}", "metodo": "status"},
            "Coursera": {"url": "https://www.coursera.org/user/{usuario}", "metodo": "status"},
            "Udemy": {"url": "https://www.udemy.com/user/{usuario}/", "metodo": "status"},
            "Skillshare": {"url": "https://www.skillshare.com/user/{usuario}", "metodo": "status"},

            # --- Redes Sociais de Música / Artistas ---
            "Spotify Artist": {"url": "https://open.spotify.com/artist/{usuario}", "metodo": "status"},
            "Apple Music": {"url": "https://music.apple.com/us/artist/{usuario}", "metodo": "status"},
            "Deezer": {"url": "https://www.deezer.com/us/artist/{usuario}", "metodo": "status"},
            "Tidal": {"url": "https://tidal.com/browse/artist/{usuario}", "metodo": "status"},
            "Shazam": {"url": "https://www.shazam.com/artist/{usuario}", "metodo": "status"},
            "Genius": {"url": "https://genius.com/artists/{usuario}", "metodo": "status"},
            "Musical.ly": {"url": "https://musical.ly/{usuario}", "metodo": "status"},  # antigo TikTok

            # --- Redes Sociais de Streaming / Live ---
            "Facebook Gaming": {"url": "https://www.facebook.com/gaming/{usuario}", "metodo": "status"},
            "Trovo": {"url": "https://trovo.live/{usuario}", "metodo": "status"},
            "DLive": {"url": "https://dlive.tv/{usuario}", "metodo": "status"},
            "Bigo Live": {"url": "https://bigo.tv/{usuario}", "metodo": "status"},
            "Nonolive": {"url": "https://nonolive.com/{usuario}", "metodo": "status"},

            # --- Redes Sociais de Reviews / Lugares ---
            "Yelp": {"url": "https://www.yelp.com/user_details?userid={usuario}", "metodo": "status"},
            "TripAdvisor": {"url": "https://www.tripadvisor.com/Profile/{usuario}", "metodo": "status"},
            "Foursquare": {"url": "https://foursquare.com/user/{usuario}", "metodo": "status"},
            "Google Maps": {"url": "https://maps.google.com/contrib/{usuario}", "metodo": "status"},
            "Zomato": {"url": "https://www.zomato.com/user/{usuario}", "metodo": "status"},

            # --- Redes Sociais Antigas / Nostalgia ---
            "Orkut": {"url": "https://orkut.com/profile/{usuario}", "metodo": "status"},  # extinto mas alguns scrapers funcionam
            "MyYearbook": {"url": "https://myyearbook.com/user/{usuario}", "metodo": "status"},
            "Friendster": {"url": "https://friendster.com/{usuario}", "metodo": "status"},
            "Bebo": {"url": "https://bebo.com/profile/{usuario}", "metodo": "status"},
            "Google+": {"url": "https://plus.google.com/{usuario}", "metodo": "status"},  # extinto
            "Vine": {"url": "https://vine.co/u/{usuario}", "metodo": "status"},  # extinto
            "Periscope": {"url": "https://periscope.tv/{usuario}", "metodo": "status"},  # extinto

            # --- Redes Sociais de Perguntas e Respostas ---
            "Ask.fm": {"url": "https://ask.fm/{usuario}", "metodo": "status"},
            "Spring.me": {"url": "https://spring.me/{usuario}", "metodo": "status"},
            "Formspring": {"url": "https://formspring.me/{usuario}", "metodo": "status"},
            "Curious Cat": {"url": "https://curiouscat.me/{usuario}", "metodo": "status"},
            "Saraba1st": {"url": "https://bbs.saraba1st.com/2b/space-uid-{usuario}.html", "metodo": "status"},

            # --- Redes Sociais de Imagem efêmera ---
            "Snapchat Spotlight": {"url": "https://spotlight.snapchat.com/user/{usuario}", "metodo": "status"},
            "Instagram Stories": {"url": "https://www.instagram.com/stories/{usuario}/", "metodo": "status"},
            "Facebook Stories": {"url": "https://www.facebook.com/stories/{usuario}/", "metodo": "status"},

            # --- Redes Sociais Descentralizadas / Web3 ---
            "Minds": {"url": "https://www.minds.com/{usuario}/", "metodo": "status"},
            "Gab": {"url": "https://gab.com/{usuario}", "metodo": "status"},
            "Parler": {"url": "https://parler.com/user/{usuario}", "metodo": "status"},
            "Truth Social": {"url": "https://truthsocial.com/@{usuario}", "metodo": "status"},
            "Gettr": {"url": "https://gettr.com/user/{usuario}", "metodo": "status"},
            "Rumble Social": {"url": "https://rumble.com/c/{usuario}", "metodo": "status"},
            "Odysee": {"url": "https://odysee.com/@{usuario}", "metodo": "status"},
            "PeerTube": {"url": "https://peertube.tv/accounts/{usuario}", "metodo": "status"},
            "Lemmy": {"url": "https://lemmy.ml/u/{usuario}", "metodo": "status"},
            "Kbin": {"url": "https://kbin.social/u/{usuario}", "metodo": "status"},

            # --- Redes Sociais de Blogging Micro ---
            "Tumblr (blog)": {"url": "https://{usuario}.tumblr.com", "metodo": "status"},
            "Pillowfort": {"url": "https://www.pillowfort.social/{usuario}", "metodo": "status"},
            "Dreamwidth": {"url": "https://{usuario}.dreamwidth.org", "metodo": "status"},
            "LiveJournal": {"url": "https://{usuario}.livejournal.com", "metodo": "status"},
            "DeadJournal": {"url": "https://www.deadjournal.com/userinfo?user={usuario}", "metodo": "status"},

            # --- Redes Sociais de Links / Agregadores ---
            "Linktree (pro)": {"url": "https://linktr.ee/{usuario}", "metodo": "status"},
            "Beacons": {"url": "https://beacons.ai/{usuario}", "metodo": "status"},
            "Bio.fm": {"url": "https://bio.fm/{usuario}", "metodo": "status"},
            "ContactInBio": {"url": "https://contactinbio.com/{usuario}", "metodo": "status"},
            "Lnk.Bio": {"url": "https://lnk.bio/{usuario}", "metodo": "status"},
            "Shorby": {"url": "https://shor.by/{usuario}", "metodo": "status"},
            "Tap Bio": {"url": "https://tap.bio/@{usuario}", "metodo": "status"},
            "Milkshake": {"url": "https://msha.ke/{usuario}", "metodo": "status"},
            "Flow.page": {"url": "https://flow.page/{usuario}", "metodo": "status"},

            # --- Redes Sociais de Newsletter ---
            "Buttondown": {"url": "https://buttondown.email/{usuario}", "metodo": "status"},
            "ConvertKit": {"url": "https://app.convertkit.com/users/{usuario}", "metodo": "status"},
            "Revue": {"url": "https://www.getrevue.co/profile/{usuario}", "metodo": "status"},
            "TinyLetter": {"url": "https://tinyletter.com/{usuario}", "metodo": "status"},

            # --- Redes Sociais de Podcast ---
            "Spotify for Podcasters": {"url": "https://podcasters.spotify.com/pod/show/{usuario}", "metodo": "status"},
            "Anchor (profile)": {"url": "https://anchor.fm/@{usuario}", "metodo": "status"},
            "Podchaser": {"url": "https://www.podchaser.com/creators/{usuario}", "metodo": "status"},
            "Listen Notes": {"url": "https://www.listennotes.com/people/{usuario}/", "metodo": "status"},
            
            # --- Desenvolvimento / Tech ---
            "GitHub": {"url": "https://github.com/{usuario}", "metodo": "status"},
            "GitLab": {"url": "https://gitlab.com/{usuario}", "metodo": "status"},
            "Bitbucket": {"url": "https://bitbucket.org/{usuario}/", "metodo": "status"},
            "SourceForge": {"url": "https://sourceforge.net/u/{usuario}/", "metodo": "status"},
            "Codeberg": {"url": "https://codeberg.org/{usuario}", "metodo": "status"},
            "Gitee": {"url": "https://gitee.com/{usuario}", "metodo": "status"},
            "Stack Overflow": {"url": "https://stackoverflow.com/users/?tab=accounts&SearchText={usuario}", "metodo": "status"},
            "Dev.to": {"url": "https://dev.to/{usuario}", "metodo": "status"},
            "Hashnode": {"url": "https://hashnode.com/@{usuario}", "metodo": "status"},
            "Medium": {"url": "https://medium.com/@{usuario}", "metodo": "status"},
            "Substack": {"url": "https://{usuario}.substack.com", "metodo": "status"},
            "HackerNews": {"url": "https://news.ycombinator.com/user?id={usuario}", "metodo": "status"},
            "LeetCode": {"url": "https://leetcode.com/{usuario}/", "metodo": "status"},
            "Codeforces": {"url": "https://codeforces.com/profile/{usuario}", "metodo": "status"},
            "Codewars": {"url": "https://www.codewars.com/users/{usuario}", "metodo": "status"},
            "HackerRank": {"url": "https://www.hackerrank.com/{usuario}", "metodo": "status"},
            "Kaggle": {"url": "https://www.kaggle.com/{usuario}", "metodo": "status"},
            "Replit": {"url": "https://replit.com/@{usuario}", "metodo": "status"},
            "Glitch": {"url": "https://glitch.com/@{usuario}", "metodo": "status"},
            "CodePen": {"url": "https://codepen.io/{usuario}", "metodo": "status"},
            "JSFiddle": {"url": "https://jsfiddle.net/user/{usuario}/", "metodo": "status"},
            "npm": {"url": "https://www.npmjs.com/~{usuario}", "metodo": "status"},
            "PyPI": {"url": "https://pypi.org/user/{usuario}/", "metodo": "status"},
            "RubyGems": {"url": "https://rubygems.org/profiles/{usuario}", "metodo": "status"},
            "Docker Hub": {"url": "https://hub.docker.com/u/{usuario}", "metodo": "status"},
            
            # --- Conteúdo / Vídeo / Áudio ---
            "YouTube": {"url": "https://www.youtube.com/@{usuario}", "metodo": "status"},
            "Twitch": {"url": "https://www.twitch.tv/{usuario}", "metodo": "status"},
            "Kick": {"url": "https://kick.com/{usuario}", "metodo": "status"},
            "Rumble": {"url": "https://rumble.com/user/{usuario}", "metodo": "status"},
            "Spotify": {"url": "https://open.spotify.com/user/{usuario}", "metodo": "status"},
            "SoundCloud": {"url": "https://soundcloud.com/{usuario}", "metodo": "status"},
            "Mixcloud": {"url": "https://www.mixcloud.com/{usuario}/", "metodo": "status"},
            "Bandcamp": {"url": "https://bandcamp.com/{usuario}", "metodo": "status"},
            "Audius": {"url": "https://audius.co/{usuario}", "metodo": "status"},
            "Anchor": {"url": "https://anchor.fm/{usuario}", "metodo": "status"},
            "Podcast (Apple)": {"url": "https://podcasts.apple.com/us/podcast/id{usuario}", "metodo": "status"},
            "Vimeo": {"url": "https://vimeo.com/{usuario}", "metodo": "status"},
            "Dailymotion": {"url": "https://www.dailymotion.com/{usuario}", "metodo": "status"},
            
            # --- Gaming ---
            "Steam": {"url": "https://steamcommunity.com/id/{usuario}", "metodo": "status"},
            "Epic Games": {"url": "https://www.epicgames.com/id/{usuario}", "metodo": "status"},
            "Xbox Gamertag": {"url": "https://www.xbox.com/en-US/play/user/{usuario}", "metodo": "status"},
            "PlayStation": {"url": "https://psnprofiles.com/{usuario}", "metodo": "status"},
            "Nintendo": {"url": "https://www.nintendo.com/users/{usuario}", "metodo": "status"},
            "Battle.net": {"url": "https://www.battle.net/{usuario}", "metodo": "status"},
            "Riot Games": {"url": "https://na.op.gg/summoner/userName={usuario}", "metodo": "status"},
            "Discord (gaming)": {"url": "https://discord.id/{usuario}", "metodo": "status"},
            "Twitch (gaming)": {"url": "https://www.twitch.tv/{usuario}", "metodo": "status"},
            "Smash.gg": {"url": "https://smash.gg/u/{usuario}", "metodo": "status"},
            
            # --- Profissionais / Negócios ---
            "AngelList": {"url": "https://angel.co/u/{usuario}", "metodo": "status"},
            "Crunchbase": {"url": "https://www.crunchbase.com/person/{usuario}", "metodo": "status"},
            "About.me": {"url": "https://about.me/{usuario}", "metodo": "status"},
            "Linktree": {"url": "https://linktr.ee/{usuario}", "metodo": "status"},
            "Bio.link": {"url": "https://bio.link/{usuario}", "metodo": "status"},
            "Linkin.bio": {"url": "https://linkin.bio/{usuario}", "metodo": "status"},
            "Carrd": {"url": "https://{usuario}.carrd.co", "metodo": "status"},
            
            # --- Blogs / Publicações ---
            "WordPress.com": {"url": "https://{usuario}.wordpress.com", "metodo": "status"},
            "Blogger": {"url": "https://{usuario}.blogspot.com", "metodo": "status"},
            "Ghost": {"url": "https://{usuario}.ghost.io", "metodo": "status"},
            "Wix": {"url": "https://{usuario}.wixsite.com/home", "metodo": "status"},
            "Weebly": {"url": "https://{usuario}.weebly.com", "metodo": "status"},
            "Notion": {"url": "https://notion.so/{usuario}", "metodo": "status"},
            
            # --- Fóruns / Comunidades ---
            "Quora": {"url": "https://www.quora.com/profile/{usuario}", "metodo": "status"},
            "Product Hunt": {"url": "https://www.producthunt.com/@{usuario}", "metodo": "status"},
            "Indie Hackers": {"url": "https://indiehackers.com/u/{usuario}", "metodo": "status"},
            "Wattpad": {"url": "https://www.wattpad.com/user/{usuario}", "metodo": "status"},
            "Goodreads": {"url": "https://www.goodreads.com/user/show/{usuario}", "metodo": "status"},
            "Letterboxd": {"url": "https://letterboxd.com/{usuario}/", "metodo": "status"},
            "Last.fm": {"url": "https://www.last.fm/user/{usuario}", "metodo": "status"},
            "ReverbNation": {"url": "https://www.reverbnation.com/{usuario}", "metodo": "status"},
            
            # --- Imagem / Design ---
            "Imgur": {"url": "https://imgur.com/user/{usuario}", "metodo": "status"},
            "Figma": {"url": "https://figma.com/@{usuario}", "metodo": "status"},
            "Unsplash": {"url": "https://unsplash.com/@{usuario}", "metodo": "status"},
            "Pexels": {"url": "https://www.pexels.com/@{usuario}", "metodo": "status"},
            "Giphy": {"url": "https://giphy.com/{usuario}", "metodo": "status"},
            "Tenor": {"url": "https://tenor.com/users/{usuario}", "metodo": "status"},
            
            # --- E-commerce / Criadores ---
            "Etsy": {"url": "https://www.etsy.com/shop/{usuario}", "metodo": "status"},
            "Shopify": {"url": "https://{usuario}.myshopify.com", "metodo": "status"},
            "Gumroad": {"url": "https://gumroad.com/{usuario}", "metodo": "status"},
            "Ko-fi": {"url": "https://ko-fi.com/{usuario}", "metodo": "status"},
            "Buy Me a Coffee": {"url": "https://buymeacoffee.com/{usuario}", "metodo": "status"},
            "Patreon": {"url": "https://www.patreon.com/{usuario}", "metodo": "status"},
            "OnlyFans": {"url": "https://onlyfans.com/{usuario}", "metodo": "status"},
            "Fiverr": {"url": "https://www.fiverr.com/{usuario}", "metodo": "status"},
            "Upwork": {"url": "https://www.upwork.com/freelancers/{usuario}", "metodo": "status"},
            
            # --- Segurança / Identidade ---
            "Keybase": {"url": "https://keybase.io/{usuario}", "metodo": "status"},
            "Gravatar": {"url": "https://en.gravatar.com/{usuario}", "metodo": "status"},
            "Bugcrowd": {"url": "https://bugcrowd.com/{usuario}", "metodo": "status"},
            "HackerOne": {"url": "https://hackerone.com/{usuario}", "metodo": "status"},
            "Intigriti": {"url": "https://intigriti.com/profile/{usuario}", "metodo": "status"},
            
            # --- Outros ---
        }

    def verificar_usuario(self, usuario: str) -> list[dict]:
        """
        Verifica a existência do *usuario* em todas as plataformas
        cadastradas.

        Retorna uma lista de dicionários com as chaves:
            plataforma, url, encontrado (bool)
        """
        usuario = usuario.strip().lstrip("@")
        if not usuario:
            return []

        resultados = []

        for nome, cfg in self.plataformas.items():
            url = cfg["url"].format(usuario=usuario)
            encontrado = self._checar_url(url)
            resultados.append({
                "plataforma": nome,
                "url": url,
                "encontrado": encontrado,
            })

            status_txt = "ENCONTRADO" if encontrado else "não encontrado"
            print(f"  [{status_txt:>13}] {nome}: {url}")

        return resultados

    # ------------------------------------------------------------------
    def _checar_url(self, url: str) -> bool:
        """Faz uma requisição GET e retorna True se o perfil existir."""
        try:
            response = self.session.get(
                url,
                allow_redirects=True,
                timeout=10,
            )
            if response.status_code == 200:
                # Algumas plataformas retornam 200 mesmo para perfis
                # inexistentes. Verificamos palavras-chave na página que
                # indicam "não encontrado".
                corpo = response.text.lower()
                sinais_negativos = [
                    "page not found",
                    "this page isn't available",
                    "sorry, this page isn't available",
                    "the page you're looking for",
                    "essa página não está disponível",
                    "página não encontrada",
                    "this account does not exist",
                    "doesn't exist",
                    "user not found",
                    "404",
                    "no longer exists",
                ]
                for sinal in sinais_negativos:
                    if sinal in corpo:
                        return False
                return True
            return False
        except requests.exceptions.RequestException:
            return False

    def gerar_resumo(self, resultados: list[dict]) -> dict:
        """Retorna um resumo com plataformas encontradas e não encontradas."""
        encontrados = [r for r in resultados if r["encontrado"]]
        nao_encontrados = [r for r in resultados if not r["encontrado"]]
        return {
            "total_verificado": len(resultados),
            "total_encontrados": len(encontrados),
            "encontrados": encontrados,
            "nao_encontrados": nao_encontrados,
        }
