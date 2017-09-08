# UnderTheInfluence

UnderTheInfluence is a web application developed to help track the influence of lobbying in politics.

We use data from:

 * [ParlParse](parser.theyworkforyou.com) (MPs’ interests; politician metadata)
 * [The Electoral Commission](http://search.electoralcommission.org.uk) (registered donations)
 * [data.parliament](http://www.data.parliament.uk) (Lords’ interests)
 * [gov.uk](https://www.gov.uk) (ministerial meetings)
 * [APPC](http://www.appc.org.uk/members/register/) (register of lobbyists)
 * [EveryPolitician](http://everypolitician.org) (MP metadata)
 * [TheyWorkForYou](http://www.theyworkforyou.com) (politician metadata)
 * [Companies House](http://www.companieshouse.gov.uk) (company metadata)
 * [Powerbase](http://powerbase.info) (company and politician biographies)

We don’t currently import from [wikidata](https://www.wikidata.org) (only indirectly via EveryPolitician) but we should because it’s brilliant.

This project is built in [Django 1.8](https://www.djangoproject.com) and uses [Wagtail CMS](https://wagtail.io), [Django REST Framework](http://www.django-rest-framework.org) and other cool open source products.

## Dependencies

UnderTheInfluence requires:

 * [python 3.4](https://www.python.org)
 * [npm](https://www.npmjs.com)
 * [node.js](https://nodejs.org)
 * [bower](http://bower.io)
 * [elasticsearch](https://www.elastic.co/products/elasticsearch)

## Installation

 * Fetch this repo and all submodules

   ```
   git clone --recursive https://github.com/whoslobbying/undertheinfluence.git
   ```

 * Install the required python packages

   ```
   pip install -r requirements.txt
   ```

 * Copy the example config; update it as required

   ```
   cp conf/general.example.yml conf/general.yml
   ```

 * Fetch javascript dependencies with bower

   ```
   python manage.py bower_install
   ```

 * Migrate the database

   ```
   python manage.py migrate
   ```

## Importing data

This is a manual process at the moment :( Check the various management commands in `datafetch/management/commands`. Roughly you should run:

```
python manage.py import_parlparse --since 2010

python manage.py import_ministers --since 2010

# this is slow because it downloads lots of big images
python manage.py import_everypolitician

# electoral commission data
python manage.py import_ec

# current APPC register
python manage.py import_appc
```

## Running a local server

```
python manage.py runserver
```

## Deployment

See: http://github.com/spudmind/uti-deploy
