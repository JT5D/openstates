import re

from billy.scrape import NoDataForPeriod
from billy.scrape.legislators import LegislatorScraper, Legislator

import lxml.html


class AKLegislatorScraper(LegislatorScraper):
    state = 'ak'
    latest_only = True

    def scrape(self, chamber, term):
        if chamber == 'upper':
            chamber_abbr = 'S'
            url = 'http://senate.legis.state.ak.us/'
            search = 'senator'
        else:
            chamber_abbr = 'H'
            url = 'http://house.legis.state.ak.us/'
            search = 'rep'

        with self.urlopen(url) as page:
            page = lxml.html.fromstring(page)
            page.make_links_absolute(url)

            seen = set()
            for link in page.xpath("//a[contains(@href, '%s')]" % search):
                name = link.text_content()
                # Members of the leadership are linked twice three times:
                # one image link and two text links. Don't double/triple
                # scrape them
                if not name or link.attrib['href'] in seen:
                    continue
                seen.add(link.attrib['href'])

                self.scrape_legislator(chamber, term,
                                       link.xpath('string()').strip(),
                                       link.attrib['href'])

    def scrape_address(self, leg, doc, id):
        text = doc.xpath('//div[@id="{0}"]'.format(id))[0].text_content()
        address = ''
        for line in text.splitlines():
            if line == 'Session Contact':
                addr_type = 'capitol'
                addr_name = 'Session Office'
            elif line == 'Interim Contact':
                addr_type = 'district'
                addr_name = 'Interim Office'
            elif line.startswith('Phone:'):
                phone = line.split(': ')[-1]
            elif line.startswith('Fax:'):
                fax = line.split(': ')[-1]
            elif line:
                address += (line + '\n')

        leg.add_office(addr_type, addr_name, address=address.strip(),
                       phone=phone, fax=fax)


    def scrape_legislator(self, chamber, term, name, url):
        with self.urlopen(url) as page:
            page = lxml.html.fromstring(page)

            name = re.sub(r'\s+', ' ', name)

            info = page.xpath('string(//div[@id = "fullpage"])')

            district = re.search(r'District ([\w\d]+)', info).group(1)
            party = re.search(r'Party: (.+) Toll-Free', info).group(1).strip()
            email = re.search(r'Email: ([\w_]+@legis\.state\.ak\.us)',
                              info).group(1)

            # for consistency
            if party == 'Democrat':
                party = 'Democratic'

            leg = Legislator(term, chamber, district, name, party=party,
                             email=email, url=url)
            self.scrape_address(leg, page, 'bioleft')
            self.scrape_address(leg, page, 'bioright')
            leg.add_source(url)

            self.save_legislator(leg)
