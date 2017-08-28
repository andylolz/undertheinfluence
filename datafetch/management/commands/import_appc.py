import calendar
from datetime import datetime
from os.path import join
import re
from urllib.parse import urlencode

from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify
from bs4 import BeautifulSoup

from datafetch import models, helpers


class Command(BaseCommand):
    help = 'Import APPC register'
    base_url = "https://www.appc.org.uk"
    source_url_tmpl = "http://www.undertheinfluence.org.uk/appc-redirect/?{}"

    def add_arguments(self, parser):
        parser.add_argument('--refresh', action='store_true')

    def _fetch_company(self, company, path):
        # print("Fetching HTML for '{}' ...".format(company["name"]))
        url = "{}/register/profile/".format(self.base_url)
        filename = "{}.html".format(slugify(company["name"]))
        headers = {'User-Agent': 'Mozilla/5.0'}
        data = {"companyid": company["id"]}
        t = helpers.fetch_text(url, filename, path=path, headers=headers, data=data, method="post", refresh=self.refresh)
        return t

    def _scrape_company_html(self, html, date_range):
        soup = BeautifulSoup(html, "html5lib").find(class_="member-profile")
        agency_name = [x for x in soup.find("h1").stripped_strings][0]

        source_url = self.source_url_tmpl.format(urlencode({"company": agency_name}))

        agency_dict = {
            "name": agency_name,
            "classification": "Lobbying agency"
        }
        agency_obj = models.Organization.objects.get_or_create(
            name=agency_dict["name"],
            defaults=agency_dict,
        )[0]

        address_soups = soup.find(class_="profile-address").find_all("tr")[1:]
        contact_types = ["name", "phone", "email", "website"]
        for idx, address_soup in enumerate(address_soups):
            address, contact = [[x for x in y.stripped_strings] for y in address_soup.find_all("td")]
            if address != []:
                contact_dict = {
                    "value": ", ".join(address),
                    "contact_type": "address",
                }
                agency_obj.contact_details.add(models.ContactDetail.objects.get_or_create(**contact_dict)[0])
            if contact != []:
                contacts_dict = dict(zip(contact_types, contact))
                for contact_type, value in contacts_dict.items():
                    if contact_type in ["phone", "email"]:
                        contact_dict = {
                            "value": value,
                            "contact_type": contact_type,
                        }
                        agency_obj.contact_details.add(models.ContactDetail.objects.get_or_create(**contact_dict)[0])
                    elif contact_type == "website":
                        link_dict = {
                            "url": value,
                            "note": contact_type,
                        }
                        agency_obj.links.add(models.Link.objects.get_or_create(**link_dict)[0])

        # TODO
        country_soup = soup.find(class_="profile-country")
        countries = [x.text.strip().title() for x in country_soup.find_all("li")] if country_soup else []

        staff_soup = soup.find(class_="profile-staff")
        all_staff = [x.text.strip() for x in staff_soup.find_all("li")] if staff_soup else []
        for staff_name in all_staff:
            if staff_name.endswith(" *"):
                staff_name = staff_name[:-2].strip()
                # TODO: Somehow flag that these staff members have parliamentary passes
                agency_obj.add_member(models.Person.objects.get_or_create(name=staff_name)[0])
            else:
                agency_obj.add_member(models.Person.objects.get_or_create(name=staff_name)[0])

        client_soups = soup.find_all(class_="profile-clients")
        for client_soup in client_soups:
            client_table_heading = client_soup.find("th").text
            if "Pro-Bono Clients" in client_table_heading:
                client_type = "Pro-bono consultancy / monitoring"
            elif "UK PA consultancy" in client_table_heading:
                client_type = "Consultancy"
            elif "UK monitoring" in client_table_heading:
                client_type = "Monitoring"
            else:
                raise Exception("Unknown client type: '%s'" % client_table_heading)
            for client in client_soup.find_all("li"):
                client = [c for c in client.stripped_strings]
                client_dict = {
                    "name": client[0],
                    "summary": client[2] if len(client) > 1 else "",
                }
                client_obj = models.Organization.objects.get_or_create(
                    name=client_dict["name"],
                    defaults=client_dict,
                )[0]
                consultancy_obj = models.Consultancy.objects.get_or_create(
                    label=client_type,
                    client=client_obj,
                    agency=agency_obj,
                    source=source_url,
                    start_date=date_range[0],
                    end_date=date_range[1],
                )[0]

    # parse out a pair of dates (with a known format) from a string
    # returns a tuple of dates in the form YYYY-MM-DD
    def get_dates(self, text):
        months = "|".join(calendar.month_name[1:])
        date_range = re.findall(r"(\d+).*?(%s) (\d{4})" % months, text)
        return [str(datetime.strptime(" ".join(i for i in x), "%d %B %Y").date()) for x in date_range]

    def handle(self, *args, **options):
        self.refresh = options.get('refresh')

        helpers.create_data_folder("appc")

        index_url = "{}/register/current-register/".format(self.base_url)
        t = helpers.fetch_text(index_url, "index.html", path="appc", refresh=True)
        soup = BeautifulSoup(t, "html5lib")

        date_range = self.get_dates(soup.h1.text)

        path = join("appc", date_range[1])
        helpers.create_data_folder(path)

        companies = [{
            "id": x.find("input", {"name": "companyid"})["value"],
            "name": x.find("input", {"name": "company"})["value"],
        } for x in soup.find_all(class_="member-list-profile")]
        for company in companies:
            html = self._fetch_company(company, path)
            self._scrape_company_html(html, date_range)
